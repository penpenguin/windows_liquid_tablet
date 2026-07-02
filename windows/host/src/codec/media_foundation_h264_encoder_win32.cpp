#include "codec/media_foundation_h264_encoder_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <mfapi.h>
#include <mferror.h>
#include <mfidl.h>
#include <objbase.h>
#include <codecapi.h>
#include <dshow.h>
#include <wmcodecdsp.h>
#include <wrl/client.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <utility>
#include <vector>

namespace wlt::host::codec {

namespace {

using Microsoft::WRL::ComPtr;

bool succeeded(HRESULT result) {
  return SUCCEEDED(result);
}

void release_activates(IMFActivate** activates, UINT32 count) {
  if (activates == nullptr) {
    return;
  }
  for (UINT32 index = 0; index < count; ++index) {
    if (activates[index] != nullptr) {
      activates[index]->Release();
    }
  }
  CoTaskMemFree(activates);
}

bool has_h264_encoder_mft() {
  MFT_REGISTER_TYPE_INFO output_type{};
  output_type.guidMajorType = MFMediaType_Video;
  output_type.guidSubtype = MFVideoFormat_H264;

  IMFActivate** activates = nullptr;
  UINT32 count = 0;
  const auto result = MFTEnumEx(
      MFT_CATEGORY_VIDEO_ENCODER,
      MFT_ENUM_FLAG_HARDWARE | MFT_ENUM_FLAG_SORTANDFILTER,
      nullptr,
      &output_type,
      &activates,
      &count);
  release_activates(activates, count);
  return succeeded(result) && count > 0;
}

bool set_video_size(IMFMediaType& type, const H264EncoderConfig& config) {
  return succeeded(MFSetAttributeSize(&type, MF_MT_FRAME_SIZE, config.width, config.height)) &&
      succeeded(MFSetAttributeRatio(&type, MF_MT_FRAME_RATE, config.target_fps, 1)) &&
      succeeded(MFSetAttributeRatio(&type, MF_MT_PIXEL_ASPECT_RATIO, 1, 1));
}

bool create_media_type(const H264EncoderConfig& config, bool output, IMFMediaType** media_type) {
  ComPtr<IMFMediaType> type;
  if (!succeeded(MFCreateMediaType(&type))) {
    return false;
  }

  if (!succeeded(type->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video))) {
    return false;
  }
  if (!succeeded(type->SetGUID(MF_MT_SUBTYPE, output ? MFVideoFormat_H264 : MFVideoFormat_NV12))) {
    return false;
  }
  if (!succeeded(type->SetUINT32(MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive))) {
    return false;
  }
  if (output && !succeeded(type->SetUINT32(MF_MT_AVG_BITRATE, config.target_bitrate_kbps * 1000))) {
    return false;
  }
  if (!set_video_size(*type.Get(), config)) {
    return false;
  }

  *media_type = type.Detach();
  return true;
}

void set_codec_bool(ICodecAPI& codec_api, const GUID& key, bool enabled) {
  VARIANT value{};
  value.vt = VT_BOOL;
  value.boolVal = enabled ? VARIANT_TRUE : VARIANT_FALSE;
  (void)codec_api.SetValue(&key, &value);
}

void set_codec_uint32(ICodecAPI& codec_api, const GUID& key, std::uint32_t data) {
  VARIANT value{};
  value.vt = VT_UI4;
  value.ulVal = data;
  (void)codec_api.SetValue(&key, &value);
}

void apply_h264_low_latency_policy(IMFTransform& transform, const H264EncoderConfig& config) {
  ComPtr<ICodecAPI> codec_api;
  if (!succeeded(transform.QueryInterface(IID_PPV_ARGS(&codec_api)))) {
    return;
  }

  set_codec_bool(*codec_api.Get(), CODECAPI_AVLowLatencyMode, !config.allow_b_frames);
  set_codec_uint32(
      *codec_api.Get(),
      CODECAPI_AVEncMPVDefaultBPictureCount,
      config.max_b_frame_count);
}

std::vector<std::byte> sample_payload(IMFSample& sample) {
  ComPtr<IMFMediaBuffer> buffer;
  if (!succeeded(sample.ConvertToContiguousBuffer(&buffer))) {
    return {};
  }

  BYTE* data = nullptr;
  DWORD max_length = 0;
  DWORD current_length = 0;
  if (!succeeded(buffer->Lock(&data, &max_length, &current_length))) {
    return {};
  }

  std::vector<std::byte> payload(
      reinterpret_cast<std::byte*>(data),
      reinterpret_cast<std::byte*>(data) + current_length);
  buffer->Unlock();
  return payload;
}

} // namespace

class MediaFoundationH264Encoder::Impl {
public:
  explicit Impl(const H264EncoderConfig& config) : config_(config) {
    if (!is_valid_h264_encoder_config(config_)) {
      return;
    }
    const auto co_result = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (SUCCEEDED(co_result)) {
      com_initialized_ = true;
    } else if (co_result != RPC_E_CHANGED_MODE) {
      return;
    }

    if (!succeeded(MFStartup(MF_VERSION))) {
      return;
    }
    media_foundation_started_ = true;

    // Prefer the platform's H.264 encoder MFT, but keep the CLSID path explicit for deterministic startup.
    (void)has_h264_encoder_mft();
    if (!succeeded(CoCreateInstance(
            CLSID_CMSH264EncoderMFT,
            nullptr,
            CLSCTX_INPROC_SERVER,
            IID_PPV_ARGS(&transform_)))) {
      return;
    }
    apply_h264_low_latency_policy(*transform_.Get(), config_);

    ComPtr<IMFMediaType> output_type;
    ComPtr<IMFMediaType> input_type;
    if (!create_media_type(config_, true, &output_type) ||
        !create_media_type(config_, false, &input_type)) {
      transform_.Reset();
      return;
    }
    if (!succeeded(transform_->SetOutputType(0, output_type.Get(), 0)) ||
        !succeeded(transform_->SetInputType(0, input_type.Get(), 0))) {
      transform_.Reset();
      return;
    }

    // MFT payload input is expected to be NV12; the emitted wire codec is H264AnnexB.
    transform_->ProcessMessage(MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
    ready_ = true;
  }

  ~Impl() {
    transform_.Reset();
    if (media_foundation_started_) {
      MFShutdown();
    }
    if (com_initialized_) {
      CoUninitialize();
    }
  }

  bool ready() const {
    return ready_;
  }

  EncodedVideoFrame encode(const capture::VideoFrame& frame) {
    if (!ready_) {
      return empty_frame(frame);
    }

    ComPtr<IMFSample> input_sample;
    ComPtr<IMFMediaBuffer> input_buffer;
    if (!succeeded(MFCreateSample(&input_sample)) ||
        !succeeded(MFCreateMemoryBuffer(static_cast<DWORD>(frame.payload.size()), &input_buffer))) {
      return empty_frame(frame);
    }

    BYTE* input_data = nullptr;
    DWORD max_length = 0;
    DWORD current_length = 0;
    if (!succeeded(input_buffer->Lock(&input_data, &max_length, &current_length))) {
      return empty_frame(frame);
    }
    std::memcpy(input_data, frame.payload.data(), frame.payload.size());
    input_buffer->Unlock();
    input_buffer->SetCurrentLength(static_cast<DWORD>(frame.payload.size()));
    input_sample->AddBuffer(input_buffer.Get());

    if (!succeeded(transform_->ProcessInput(0, input_sample.Get(), 0))) {
      return empty_frame(frame);
    }

    ComPtr<IMFSample> output_sample;
    ComPtr<IMFMediaBuffer> output_buffer;
    const auto output_capacity = static_cast<DWORD>(
        std::max<std::size_t>(frame.payload.size(), config_.width * config_.height));
    if (!succeeded(MFCreateSample(&output_sample)) ||
        !succeeded(MFCreateMemoryBuffer(output_capacity, &output_buffer))) {
      return empty_frame(frame);
    }
    output_sample->AddBuffer(output_buffer.Get());

    MFT_OUTPUT_DATA_BUFFER output{};
    output.dwStreamID = 0;
    output.pSample = output_sample.Get();
    DWORD status = 0;
    const auto result = transform_->ProcessOutput(0, 1, &output, &status);
    if (result == MF_E_TRANSFORM_NEED_MORE_INPUT || !succeeded(result)) {
      return empty_frame(frame);
    }

    return EncodedVideoFrame{
        .codec = protocol::VideoCodecV1::H264AnnexB,
        .sequence = frame.sequence,
        .width = frame.width,
        .height = frame.height,
        .capture_timestamp_ns = frame.capture_timestamp_ns,
        .encode_timestamp_ns = frame.capture_timestamp_ns,
        .payload = sample_payload(*output_sample.Get()),
    };
  }

private:
  EncodedVideoFrame empty_frame(const capture::VideoFrame& frame) const {
    return EncodedVideoFrame{
        .codec = protocol::VideoCodecV1::H264AnnexB,
        .sequence = frame.sequence,
        .width = frame.width,
        .height = frame.height,
        .capture_timestamp_ns = frame.capture_timestamp_ns,
        .encode_timestamp_ns = frame.capture_timestamp_ns,
        .payload = {},
    };
  }

  H264EncoderConfig config_{};
  bool com_initialized_ = false;
  bool media_foundation_started_ = false;
  bool ready_ = false;
  ComPtr<IMFTransform> transform_;
};

MediaFoundationH264Encoder::MediaFoundationH264Encoder(const H264EncoderConfig& config)
    : impl_(std::make_unique<Impl>(config)) {
}

MediaFoundationH264Encoder::~MediaFoundationH264Encoder() = default;

bool MediaFoundationH264Encoder::ready() const {
  return impl_ != nullptr && impl_->ready();
}

EncodedVideoFrame MediaFoundationH264Encoder::encode(const capture::VideoFrame& frame) {
  return impl_->encode(frame);
}

std::unique_ptr<VideoEncoder> make_media_foundation_h264_encoder(
    const H264EncoderConfig& config) {
  if (!is_valid_h264_encoder_config(config)) {
    return nullptr;
  }

  auto encoder = std::make_unique<MediaFoundationH264Encoder>(config);
  if (!encoder->ready()) {
    return nullptr;
  }

  std::unique_ptr<VideoEncoder> result = std::move(encoder);
  return result;
}

} // namespace wlt::host::codec
