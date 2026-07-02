#include "capture/windows_graphics_capture_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <d3d11.h>
#include <windows.graphics.capture.interop.h>
#include <windows.graphics.directx.direct3d11.interop.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Graphics.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <winrt/Windows.Graphics.DirectX.h>
#include <winrt/Windows.Graphics.DirectX.Direct3D11.h>
#include <wrl/client.h>

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace wlt::host::capture {

namespace {

using Microsoft::WRL::ComPtr;
using winrt::Windows::Graphics::SizeInt32;
using winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool;
using winrt::Windows::Graphics::Capture::GraphicsCaptureItem;
using winrt::Windows::Graphics::Capture::GraphicsCaptureSession;
using winrt::Windows::Graphics::DirectX::DirectXPixelFormat;
using winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice;
using DxgiInterfaceAccess =
    ::Windows::Graphics::DirectX::Direct3D11::IDirect3DDxgiInterfaceAccess;

constexpr int k_frame_pool_buffer_count = 2;

bool succeeded(HRESULT result) {
  return SUCCEEDED(result);
}

std::uint64_t now_ns() {
  const auto now = std::chrono::steady_clock::now().time_since_epoch();
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
}

bool create_capture_device(ID3D11Device* d3d_device, IDirect3DDevice& capture_device) {
  if (d3d_device == nullptr) {
    return false;
  }

  ComPtr<IDXGIDevice> dxgi_device;
  if (!succeeded(d3d_device->QueryInterface(IID_PPV_ARGS(&dxgi_device)))) {
    return false;
  }

  winrt::com_ptr<::IInspectable> inspectable;
  if (!succeeded(CreateDirect3D11DeviceFromDXGIDevice(dxgi_device.Get(), inspectable.put()))) {
    return false;
  }

  capture_device = inspectable.as<IDirect3DDevice>();
  return capture_device != nullptr;
}

std::string narrow_device_name(const WCHAR* value) {
  if (value == nullptr || value[0] == L'\0') {
    return {};
  }

  const int required = WideCharToMultiByte(CP_UTF8, 0, value, -1, nullptr, 0, nullptr, nullptr);
  if (required <= 1) {
    return {};
  }

  std::string output(static_cast<std::size_t>(required - 1), '\0');
  WideCharToMultiByte(CP_UTF8, 0, value, -1, output.data(), required, nullptr, nullptr);
  return output;
}

struct MonitorLookupState {
  std::string display_id;
  HMONITOR monitor = nullptr;
};

BOOL CALLBACK match_monitor_by_device_name(
    HMONITOR monitor,
    HDC,
    LPRECT,
    LPARAM user_data) {
  auto* state = reinterpret_cast<MonitorLookupState*>(user_data);
  if (state == nullptr || state->monitor != nullptr) {
    return FALSE;
  }

  MONITORINFOEXW info{};
  info.cbSize = sizeof(info);
  if (GetMonitorInfoW(monitor, &info) == FALSE) {
    return TRUE;
  }

  if (narrow_device_name(info.szDevice) == state->display_id) {
    state->monitor = monitor;
    return FALSE;
  }
  return TRUE;
}

HMONITOR find_monitor_by_display_id(const std::string& display_id) {
  if (display_id.empty()) {
    return nullptr;
  }

  MonitorLookupState state{
      .display_id = display_id,
  };
  EnumDisplayMonitors(
      nullptr,
      nullptr,
      match_monitor_by_device_name,
      reinterpret_cast<LPARAM>(&state));
  return state.monitor;
}

GraphicsCaptureItem create_capture_item_for_display(const std::string& display_id) {
  const HMONITOR monitor = find_monitor_by_display_id(display_id);
  if (monitor == nullptr) {
    return GraphicsCaptureItem{nullptr};
  }

  try {
    auto interop = winrt::get_activation_factory<GraphicsCaptureItem, IGraphicsCaptureItemInterop>();
    winrt::com_ptr<ABI::Windows::Graphics::Capture::IGraphicsCaptureItem> item_abi;
    if (!succeeded(interop->CreateForMonitor(
            monitor,
            __uuidof(ABI::Windows::Graphics::Capture::IGraphicsCaptureItem),
            item_abi.put_void()))) {
      return GraphicsCaptureItem{nullptr};
    }
    if (!item_abi) {
      return GraphicsCaptureItem{nullptr};
    }
    return item_abi.as<GraphicsCaptureItem>();
  } catch (...) {
    return GraphicsCaptureItem{nullptr};
  }
}

} // namespace

class WindowsGraphicsCaptureSource::Impl {
public:
  explicit Impl(const WindowsGraphicsCaptureConfig& config) : config_(config) {
    if (!is_valid_windows_graphics_capture_config(config_)) {
      return;
    }

    winrt::init_apartment(winrt::apartment_type::multi_threaded);

    D3D_FEATURE_LEVEL feature_level{};
    if (!succeeded(D3D11CreateDevice(
            nullptr,
            D3D_DRIVER_TYPE_HARDWARE,
            nullptr,
            D3D11_CREATE_DEVICE_BGRA_SUPPORT,
            nullptr,
            0,
            D3D11_SDK_VERSION,
            &device_,
            &feature_level,
            &context_))) {
      return;
    }

    if (!create_capture_device(device_.Get(), capture_device_)) {
      return;
    }

    GraphicsCaptureItem item = create_capture_item_for_display(config_.display_id);
    if (item == nullptr) {
      return;
    }

    try {
      frame_size_ = item.Size();
      frame_pool_ = Direct3D11CaptureFramePool::CreateFreeThreaded(
          capture_device_,
          DirectXPixelFormat::B8G8R8A8UIntNormalized,
          k_frame_pool_buffer_count,
          frame_size_);
      if (frame_pool_ == nullptr) {
        return;
      }

      session_ = frame_pool_.CreateCaptureSession(item);
      if (session_ == nullptr) {
        return;
      }
      session_.IsCursorCaptureEnabled(config_.include_cursor);
      session_.StartCapture();
      ready_ = true;
    } catch (...) {
      ready_ = false;
    }

    (void)config_.target_fps;
  }

  bool ready() const {
    return ready_;
  }

  void recreate_frame_pool_if_needed(SizeInt32 content_size) {
    if (content_size.Width <= 0 || content_size.Height <= 0) {
      return;
    }
    if (content_size.Width == frame_size_.Width && content_size.Height == frame_size_.Height) {
      return;
    }

    frame_size_ = content_size;
    frame_pool_.Recreate(
        capture_device_,
        DirectXPixelFormat::B8G8R8A8UIntNormalized,
        k_frame_pool_buffer_count,
        frame_size_);
  }

  std::optional<VideoFrame> capture_next() {
    if (!ready_) {
      return std::nullopt;
    }

    try {
      auto frame = frame_pool_.TryGetNextFrame();
      if (frame == nullptr || frame.Surface() == nullptr) {
        return std::nullopt;
      }
      const auto content_size = frame.ContentSize();

      auto access = frame.Surface().as<DxgiInterfaceAccess>();
      ComPtr<ID3D11Texture2D> texture;
      if (!access || !succeeded(access->GetInterface(IID_PPV_ARGS(&texture)))) {
        return std::nullopt;
      }

      D3D11_TEXTURE2D_DESC desc{};
      texture->GetDesc(&desc);
      if (desc.Format != DXGI_FORMAT_B8G8R8A8_UNORM) {
        return std::nullopt;
      }

      D3D11_TEXTURE2D_DESC staging_desc = desc;
      staging_desc.BindFlags = 0;
      staging_desc.MiscFlags = 0;
      staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
      staging_desc.Usage = D3D11_USAGE_STAGING;

      ComPtr<ID3D11Texture2D> staging;
      if (!succeeded(device_->CreateTexture2D(&staging_desc, nullptr, &staging))) {
        return std::nullopt;
      }

      context_->CopyResource(staging.Get(), texture.Get());

      D3D11_MAPPED_SUBRESOURCE mapped{};
      if (!succeeded(context_->Map(staging.Get(), 0, D3D11_MAP_READ, 0, &mapped))) {
        return std::nullopt;
      }

      const auto bytes_per_pixel = 4u;
      std::vector<std::byte> payload(desc.Width * desc.Height * bytes_per_pixel);
      for (std::uint32_t row = 0; row < desc.Height; ++row) {
        const auto* source = reinterpret_cast<const std::byte*>(mapped.pData) +
            row * mapped.RowPitch;
        auto* destination = payload.data() + row * desc.Width * bytes_per_pixel;
        std::memcpy(destination, source, desc.Width * bytes_per_pixel);
      }
      context_->Unmap(staging.Get(), 0);
      recreate_frame_pool_if_needed(content_size);

      return VideoFrame{
          .sequence = next_sequence_++,
          .width = desc.Width,
          .height = desc.Height,
          .capture_timestamp_ns = now_ns(),
          .payload = std::move(payload),
      };
    } catch (...) {
      return std::nullopt;
    }
  }

private:
  WindowsGraphicsCaptureConfig config_;
  bool ready_ = false;
  std::uint32_t next_sequence_ = 1;
  ComPtr<ID3D11Device> device_;
  ComPtr<ID3D11DeviceContext> context_;
  IDirect3DDevice capture_device_{nullptr};
  SizeInt32 frame_size_{};
  Direct3D11CaptureFramePool frame_pool_{nullptr};
  GraphicsCaptureSession session_{nullptr};
};

WindowsGraphicsCaptureSource::WindowsGraphicsCaptureSource(
    const WindowsGraphicsCaptureConfig& config)
    : impl_(std::make_unique<Impl>(config)) {
}

WindowsGraphicsCaptureSource::~WindowsGraphicsCaptureSource() = default;

bool WindowsGraphicsCaptureSource::ready() const {
  return impl_ != nullptr && impl_->ready();
}

std::optional<VideoFrame> WindowsGraphicsCaptureSource::capture_next() {
  return impl_->capture_next();
}

std::unique_ptr<VideoCaptureSource> make_windows_graphics_capture_source(
    const WindowsGraphicsCaptureConfig& config) {
  if (!is_valid_windows_graphics_capture_config(config)) {
    return nullptr;
  }

  auto source = std::make_unique<WindowsGraphicsCaptureSource>(config);
  if (!source->ready()) {
    return nullptr;
  }

  std::unique_ptr<VideoCaptureSource> result = std::move(source);
  return result;
}

} // namespace wlt::host::capture
