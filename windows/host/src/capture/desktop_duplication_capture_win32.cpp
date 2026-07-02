#include "capture/desktop_duplication_capture_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <d3d11.h>
#include <dxgi1_2.h>
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

bool succeeded(HRESULT result) {
  return SUCCEEDED(result);
}

std::uint64_t now_ns() {
  const auto now = std::chrono::steady_clock::now().time_since_epoch();
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
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

std::optional<std::uint32_t> select_output_index(
    IDXGIAdapter& adapter,
    const DesktopDuplicationCaptureConfig& config) {
  std::vector<DesktopDuplicationOutputRecord> outputs;
  for (std::uint32_t index = 0;; ++index) {
    ComPtr<IDXGIOutput> output;
    const auto enum_result = adapter.EnumOutputs(index, &output);
    if (enum_result == DXGI_ERROR_NOT_FOUND) {
      break;
    }
    if (!succeeded(enum_result)) {
      return std::nullopt;
    }

    DXGI_OUTPUT_DESC desc{};
    if (!succeeded(output->GetDesc(&desc))) {
      return std::nullopt;
    }

    outputs.push_back(DesktopDuplicationOutputRecord{
        .output_index = index,
        .device_name = narrow_device_name(desc.DeviceName),
        .attached_to_desktop = desc.AttachedToDesktop != FALSE,
    });
  }

  return select_desktop_duplication_output_index(
      outputs,
      config.output_device_name,
      config.output_index);
}

} // namespace

class DesktopDuplicationCaptureSource::Impl {
public:
  explicit Impl(const DesktopDuplicationCaptureConfig& config) : config_(config) {
    if (!is_valid_desktop_duplication_capture_config(config_)) {
      return;
    }

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

    ComPtr<IDXGIDevice> dxgi_device;
    ComPtr<IDXGIAdapter> adapter;
    ComPtr<IDXGIOutput> output;
    ComPtr<IDXGIOutput1> output1;
    std::optional<std::uint32_t> selected_output_index;
    if (!succeeded(device_.As(&dxgi_device)) ||
        !succeeded(dxgi_device->GetAdapter(&adapter))) {
      return;
    }
    selected_output_index = select_output_index(*adapter.Get(), config_);
    if (!selected_output_index.has_value() ||
        !succeeded(adapter->EnumOutputs(*selected_output_index, &output)) ||
        !succeeded(output.As(&output1)) ||
        !succeeded(output1->DuplicateOutput(device_.Get(), &duplication_))) {
      return;
    }

    ready_ = true;
  }

  bool ready() const {
    return ready_;
  }

  std::optional<VideoFrame> capture_next() {
    if (!ready_) {
      return std::nullopt;
    }

    DXGI_OUTDUPL_FRAME_INFO frame_info{};
    ComPtr<IDXGIResource> resource;
    const auto acquire_result = duplication_->AcquireNextFrame(
        config_.timeout_ms,
        &frame_info,
        &resource);
    if (acquire_result == DXGI_ERROR_WAIT_TIMEOUT) {
      return std::nullopt;
    }
    if (!succeeded(acquire_result)) {
      return std::nullopt;
    }

    auto release_frame = [this] {
      duplication_->ReleaseFrame();
    };

    ComPtr<ID3D11Texture2D> texture;
    if (!succeeded(resource.As(&texture))) {
      release_frame();
      return std::nullopt;
    }

    D3D11_TEXTURE2D_DESC desc{};
    texture->GetDesc(&desc);
    if (desc.Format != DXGI_FORMAT_B8G8R8A8_UNORM) {
      release_frame();
      return std::nullopt;
    }

    D3D11_TEXTURE2D_DESC staging_desc = desc;
    staging_desc.BindFlags = 0;
    staging_desc.MiscFlags = 0;
    staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
    staging_desc.Usage = D3D11_USAGE_STAGING;

    ComPtr<ID3D11Texture2D> staging;
    if (!succeeded(device_->CreateTexture2D(&staging_desc, nullptr, &staging))) {
      release_frame();
      return std::nullopt;
    }

    context_->CopyResource(staging.Get(), texture.Get());

    D3D11_MAPPED_SUBRESOURCE mapped{};
    if (!succeeded(context_->Map(staging.Get(), 0, D3D11_MAP_READ, 0, &mapped))) {
      release_frame();
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
    release_frame();

    return VideoFrame{
        .sequence = next_sequence_++,
        .width = desc.Width,
        .height = desc.Height,
        .capture_timestamp_ns = now_ns(),
        .payload = std::move(payload),
    };
  }

private:
  DesktopDuplicationCaptureConfig config_{};
  bool ready_ = false;
  std::uint32_t next_sequence_ = 1;
  ComPtr<ID3D11Device> device_;
  ComPtr<ID3D11DeviceContext> context_;
  ComPtr<IDXGIOutputDuplication> duplication_;
};

DesktopDuplicationCaptureSource::DesktopDuplicationCaptureSource(
    const DesktopDuplicationCaptureConfig& config)
    : impl_(std::make_unique<Impl>(config)) {
}

DesktopDuplicationCaptureSource::~DesktopDuplicationCaptureSource() = default;

bool DesktopDuplicationCaptureSource::ready() const {
  return impl_ != nullptr && impl_->ready();
}

std::optional<VideoFrame> DesktopDuplicationCaptureSource::capture_next() {
  return impl_->capture_next();
}

std::unique_ptr<VideoCaptureSource> make_desktop_duplication_capture_source(
    const DesktopDuplicationCaptureConfig& config) {
  if (!is_valid_desktop_duplication_capture_config(config)) {
    return nullptr;
  }

  auto source = std::make_unique<DesktopDuplicationCaptureSource>(config);
  if (!source->ready()) {
    return nullptr;
  }

  std::unique_ptr<VideoCaptureSource> result = std::move(source);
  return result;
}

} // namespace wlt::host::capture
