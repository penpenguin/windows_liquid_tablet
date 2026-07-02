#include "net/tcp_byte_stream_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <winsock2.h>
#include <ws2tcpip.h>

#include <array>
#include <cstddef>
#include <memory>
#include <utility>
#include <vector>

namespace wlt::host::net {

namespace {

// Winsock adapter for the user-mode host; networking is intentionally kept outside drivers.
class WinsockSession {
public:
  WinsockSession() {
    WSADATA data{};
    ok_ = WSAStartup(MAKEWORD(2, 2), &data) == 0;
  }

  ~WinsockSession() {
    if (ok_) {
      WSACleanup();
    }
  }

  bool ok() const {
    return ok_;
  }

private:
  bool ok_ = false;
};

class SocketHandle {
public:
  SocketHandle() = default;
  explicit SocketHandle(SOCKET socket) : socket_(socket) {
  }

  SocketHandle(const SocketHandle&) = delete;
  SocketHandle& operator=(const SocketHandle&) = delete;

  ~SocketHandle() {
    close();
  }

  SOCKET get() const {
    return socket_;
  }

  SOCKET release() {
    const auto released = socket_;
    socket_ = INVALID_SOCKET;
    return released;
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

class TcpSocketByteStreamReader final : public ByteStreamReader {
public:
  TcpSocketByteStreamReader(SOCKET socket, std::shared_ptr<WinsockSession> winsock)
      : socket_(socket), winsock_(std::move(winsock)) {
  }

  ByteStreamReadResult read_some() override {
    std::array<std::byte, 4096> buffer{};
    const auto received = recv(
        socket_.get(),
        reinterpret_cast<char*>(buffer.data()),
        static_cast<int>(buffer.size()),
        0);

    if (received > 0) {
      return ByteStreamReadResult{
          .status = ByteStreamReadStatus::Data,
          .bytes = std::vector<std::byte>(buffer.begin(), buffer.begin() + received),
      };
    }

    if (received == 0) {
      return ByteStreamReadResult{.status = ByteStreamReadStatus::Closed, .bytes = {}};
    }

    const auto error = WSAGetLastError();
    if (error == WSAEWOULDBLOCK) {
      return ByteStreamReadResult{.status = ByteStreamReadStatus::WouldBlock, .bytes = {}};
    }

    return ByteStreamReadResult{.status = ByteStreamReadStatus::Error, .bytes = {}};
  }

private:
  SocketHandle socket_;
  std::shared_ptr<WinsockSession> winsock_;
};

bool fill_sockaddr(const std::string& host, std::uint16_t port, sockaddr_in& address) {
  address = sockaddr_in{};
  address.sin_family = AF_INET;
  address.sin_port = htons(port);

  if (host == "0.0.0.0") {
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    return true;
  }

  return InetPtonA(AF_INET, host.c_str(), &address.sin_addr) == 1;
}

bool set_nonblocking(SOCKET socket) {
  u_long nonblocking = 1;
  return ioctlsocket(socket, FIONBIO, &nonblocking) == 0;
}

std::shared_ptr<WinsockSession> start_winsock() {
  auto winsock = std::make_shared<WinsockSession>();
  return winsock->ok() ? winsock : nullptr;
}

} // namespace

class TcpByteStreamListener::Impl {
public:
  explicit Impl(const TcpListenConfig& config) {
    if (!is_valid_tcp_listen_config(config)) {
      return;
    }

    winsock_ = start_winsock();
    if (!winsock_) {
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

  std::unique_ptr<ByteStreamReader> accept() {
    if (!listening_) {
      return nullptr;
    }

    SocketHandle client(::accept(listener_.get(), nullptr, nullptr));
    if (client.get() == INVALID_SOCKET) {
      return nullptr;
    }
    if (!set_nonblocking(client.get())) {
      return nullptr;
    }

    return std::make_unique<TcpSocketByteStreamReader>(client.release(), winsock_);
  }

private:
  std::shared_ptr<WinsockSession> winsock_;
  SocketHandle listener_;
  bool listening_ = false;
};

std::unique_ptr<ByteStreamReader> connect_tcp_byte_stream(const TcpEndpoint& endpoint) {
  if (!is_valid_tcp_endpoint(endpoint)) {
    return nullptr;
  }

  auto winsock = start_winsock();
  if (!winsock) {
    return nullptr;
  }

  sockaddr_in address{};
  if (!fill_sockaddr(endpoint.host, endpoint.port, address)) {
    return nullptr;
  }

  SocketHandle socket(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
  if (socket.get() == INVALID_SOCKET) {
    return nullptr;
  }

  if (::connect(socket.get(), reinterpret_cast<const sockaddr*>(&address), sizeof(address)) == SOCKET_ERROR) {
    return nullptr;
  }
  if (!set_nonblocking(socket.get())) {
    return nullptr;
  }

  return std::make_unique<TcpSocketByteStreamReader>(socket.release(), std::move(winsock));
}

TcpByteStreamListener::TcpByteStreamListener(const TcpListenConfig& config)
    : impl_(std::make_unique<Impl>(config)) {
}

TcpByteStreamListener::~TcpByteStreamListener() = default;

bool TcpByteStreamListener::is_listening() const {
  return impl_ && impl_->is_listening();
}

std::unique_ptr<ByteStreamReader> TcpByteStreamListener::accept() {
  return impl_ ? impl_->accept() : nullptr;
}

std::unique_ptr<TcpByteStreamListener> listen_tcp_byte_stream(const TcpListenConfig& config) {
  auto listener = std::make_unique<TcpByteStreamListener>(config);
  if (!listener->is_listening()) {
    return nullptr;
  }
  return listener;
}

std::unique_ptr<ByteStreamReader> accept_tcp_byte_stream(const TcpListenConfig& config) {
  auto listener = listen_tcp_byte_stream(config);
  if (!listener) {
    return nullptr;
  }
  return listener->accept();
}

} // namespace wlt::host::net
