#include "net/tcp_video_sender_win32.h"

#include "net/video_packet_writer.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <winsock2.h>
#include <ws2tcpip.h>

#include <climits>
#include <cstddef>
#include <memory>
#include <string>
#include <utility>
#include <vector>

namespace wlt::host::net {

namespace {

class SocketHandle {
public:
  SocketHandle() = default;
  explicit SocketHandle(SOCKET socket) : socket_(socket) {
  }

  ~SocketHandle() {
    close();
  }

  SOCKET get() const {
    return socket_;
  }

  SOCKET release() {
    const auto socket = socket_;
    socket_ = INVALID_SOCKET;
    return socket;
  }

  void reset(SOCKET socket) {
    close();
    socket_ = socket;
  }

  void close() {
    if (socket_ != INVALID_SOCKET) {
      closesocket(socket_);
      socket_ = INVALID_SOCKET;
    }
  }

private:
  SOCKET socket_ = INVALID_SOCKET;
};

class WinsockSession {
public:
  bool start() {
    if (WSAStartup(MAKEWORD(2, 2), &data_) != 0) {
      return false;
    }
    active_ = true;
    return true;
  }

  void release() {
    active_ = false;
  }

  ~WinsockSession() {
    if (active_) {
      WSACleanup();
    }
  }

private:
  WSADATA data_{};
  bool active_ = false;
};

bool fill_sockaddr(const std::string& host, std::uint16_t port, sockaddr_in& address) {
  address = sockaddr_in{};
  address.sin_family = AF_INET;
  address.sin_port = htons(port);
  return InetPtonA(AF_INET, host.c_str(), &address.sin_addr) == 1;
}

bool fill_sockaddr(const TcpEndpoint& endpoint, sockaddr_in& address) {
  return fill_sockaddr(endpoint.host, endpoint.port, address);
}

bool send_all(SOCKET socket, const std::vector<std::byte>& bytes) {
  std::size_t sent_total = 0;
  while (sent_total < bytes.size()) {
    const auto remaining = bytes.size() - sent_total;
    const auto chunk_size = remaining > static_cast<std::size_t>(INT_MAX)
        ? INT_MAX
        : static_cast<int>(remaining);
    const auto sent = ::send(
        socket,
        reinterpret_cast<const char*>(bytes.data() + sent_total),
        chunk_size,
        0);
    if (sent <= 0) {
      return false;
    }
    sent_total += static_cast<std::size_t>(sent);
  }

  return true;
}

} // namespace

class TcpVideoSender::Impl {
public:
  Impl(SOCKET socket, bool winsock_started)
      : winsock_started_(winsock_started), socket_(socket) {
  }

  explicit Impl(const TcpEndpoint& endpoint) {
    if (!is_valid_tcp_endpoint(endpoint)) {
      return;
    }

    // Winsock adapter for the user-mode host; networking is intentionally kept outside drivers.
    WSADATA data{};
    if (WSAStartup(MAKEWORD(2, 2), &data) != 0) {
      return;
    }
    winsock_started_ = true;

    sockaddr_in address{};
    if (!fill_sockaddr(endpoint, address)) {
      return;
    }

    socket_ = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (socket_ == INVALID_SOCKET) {
      return;
    }
    if (::connect(socket_, reinterpret_cast<const sockaddr*>(&address), sizeof(address)) == SOCKET_ERROR) {
      close_socket();
    }
  }

  ~Impl() {
    close_socket();
    if (winsock_started_) {
      WSACleanup();
    }
  }

  bool is_connected() const {
    return socket_ != INVALID_SOCKET;
  }

  bool send(const codec::EncodedVideoFrame& frame) {
    if (!is_connected()) {
      return false;
    }

    auto packet = try_serialize_video_packet(frame);
    if (!packet.has_value()) {
      return false;
    }
    return send_all(socket_, *packet);
  }

private:
  void close_socket() {
    if (socket_ != INVALID_SOCKET) {
      closesocket(socket_);
      socket_ = INVALID_SOCKET;
    }
  }

  bool winsock_started_ = false;
  SOCKET socket_ = INVALID_SOCKET;
};

TcpVideoSender::TcpVideoSender(const TcpEndpoint& endpoint)
    : impl_(std::make_unique<Impl>(endpoint)) {
}

TcpVideoSender::TcpVideoSender(std::unique_ptr<Impl> impl)
    : impl_(std::move(impl)) {
}

TcpVideoSender::~TcpVideoSender() = default;

bool TcpVideoSender::is_connected() const {
  return impl_ && impl_->is_connected();
}

bool TcpVideoSender::send(const codec::EncodedVideoFrame& frame) {
  return impl_ && impl_->send(frame);
}

class TcpVideoSenderListener::Impl {
public:
  explicit Impl(const TcpListenConfig& config) {
    if (!is_valid_tcp_listen_config(config)) {
      return;
    }

    if (!winsock_.start()) {
      return;
    }

    sockaddr_in address{};
    if (!fill_sockaddr(config.bind_address, config.port, address)) {
      return;
    }

    listener_.reset(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    if (listener_.get() == INVALID_SOCKET) {
      return;
    }
    if (::bind(listener_.get(), reinterpret_cast<const sockaddr*>(&address), sizeof(address)) == SOCKET_ERROR) {
      return;
    }
    if (::listen(listener_.get(), config.backlog) == SOCKET_ERROR) {
      return;
    }

    listening_ = true;
  }

  bool is_listening() const {
    return listening_;
  }

  SOCKET accept_socket() {
    if (!listening_) {
      return INVALID_SOCKET;
    }

    SocketHandle client(::accept(listener_.get(), nullptr, nullptr));
    if (client.get() == INVALID_SOCKET) {
      return INVALID_SOCKET;
    }

    const auto accepted_socket = client.release();
    listener_.close();
    winsock_.release();
    return accepted_socket;
  }

private:
  WinsockSession winsock_;
  SocketHandle listener_;
  bool listening_ = false;
};

TcpVideoSenderListener::TcpVideoSenderListener(const TcpListenConfig& config)
    : impl_(std::make_unique<Impl>(config)) {
}

TcpVideoSenderListener::~TcpVideoSenderListener() = default;

bool TcpVideoSenderListener::is_listening() const {
  return impl_ && impl_->is_listening();
}

std::unique_ptr<VideoSender> TcpVideoSenderListener::accept() {
  if (!impl_) {
    return nullptr;
  }

  const auto client = impl_->accept_socket();
  if (client == INVALID_SOCKET) {
    return nullptr;
  }
  return std::unique_ptr<VideoSender>(new TcpVideoSender(
      std::make_unique<TcpVideoSender::Impl>(client, true)));
}

std::unique_ptr<TcpVideoSenderListener> listen_tcp_video_sender(const TcpListenConfig& config) {
  auto listener = std::make_unique<TcpVideoSenderListener>(config);
  if (!listener->is_listening()) {
    return nullptr;
  }
  return listener;
}

std::unique_ptr<VideoSender> accept_tcp_video_sender(const TcpListenConfig& config) {
  auto listener = listen_tcp_video_sender(config);
  if (!listener) {
    return nullptr;
  }
  return listener->accept();
}

} // namespace wlt::host::net
