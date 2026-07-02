#pragma once

#include "codec/h264_encoder_config.h"
#include "codec/video_encoder.h"

#include <memory>

namespace wlt::host::codec {

class MediaFoundationH264Encoder final : public VideoEncoder {
public:
  explicit MediaFoundationH264Encoder(const H264EncoderConfig& config);
  ~MediaFoundationH264Encoder() override;

  bool ready() const;
  EncodedVideoFrame encode(const capture::VideoFrame& frame) override;

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

std::unique_ptr<VideoEncoder> make_media_foundation_h264_encoder(
    const H264EncoderConfig& config);

} // namespace wlt::host::codec
