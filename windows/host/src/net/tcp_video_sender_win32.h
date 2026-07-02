#pragma once

#include "net/tcp_endpoint.h"
#include "net/video_sender.h"

#include <memory>

namespace wlt::host::net {

class TcpVideoSenderListener;

class TcpVideoSender final : public VideoSender {
public:
  explicit TcpVideoSender(const TcpEndpoint& endpoint);
  ~TcpVideoSender() override;

  TcpVideoSender(const TcpVideoSender&) = delete;
  TcpVideoSender& operator=(const TcpVideoSender&) = delete;

  bool is_connected() const;
  bool send(const codec::EncodedVideoFrame& frame) override;

private:
  class Impl;
  explicit TcpVideoSender(std::unique_ptr<Impl> impl);
  friend class TcpVideoSenderListener;
  friend std::unique_ptr<VideoSender> accept_tcp_video_sender(const TcpListenConfig& config);

  std::unique_ptr<Impl> impl_;
};

class TcpVideoSenderListener final {
public:
  explicit TcpVideoSenderListener(const TcpListenConfig& config);
  ~TcpVideoSenderListener();

  TcpVideoSenderListener(const TcpVideoSenderListener&) = delete;
  TcpVideoSenderListener& operator=(const TcpVideoSenderListener&) = delete;

  bool is_listening() const;
  std::unique_ptr<VideoSender> accept();

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

std::unique_ptr<TcpVideoSenderListener> listen_tcp_video_sender(const TcpListenConfig& config);
std::unique_ptr<VideoSender> accept_tcp_video_sender(const TcpListenConfig& config);

} // namespace wlt::host::net
