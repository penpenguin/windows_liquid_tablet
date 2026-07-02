#pragma once

#include "input/pen_session.h"

#include <cstdint>

namespace wlt::host::input {

class PenInjector {
public:
  virtual ~PenInjector() = default;

  virtual bool accept(PenAction action, const PenSample& sample) = 0;
  virtual bool force_up() = 0;
  virtual bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) = 0;
  virtual bool is_active() const = 0;
};

} // namespace wlt::host::input
