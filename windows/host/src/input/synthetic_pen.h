#pragma once

#include "input/pen_injector.h"
#include "input/pen_session.h"
#include "mapping/coordinate_mapping.h"

#include <cstdint>
#include <memory>
#include <vector>

namespace wlt::host::input {

struct SyntheticPenFrame {
  PenAction action;
  int x;
  int y;
  std::uint32_t pressure;
  std::int16_t tilt_x;
  std::int16_t tilt_y;
  bool forced;
};

class SyntheticPenSink {
public:
  virtual ~SyntheticPenSink() = default;
  virtual bool inject(const SyntheticPenFrame& frame) = 0;
};

class SyntheticPen : public PenInjector {
public:
  SyntheticPen(SyntheticPenSink& sink, mapping::VirtualScreenRect target);

  bool accept(PenAction action, const PenSample& sample) override;
  bool force_up() override;
  bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) override;
  bool set_target(mapping::VirtualScreenRect target);
  bool is_active() const override;

private:
  bool inject_events(const std::vector<PenEvent>& events);
  SyntheticPenFrame to_frame(const PenEvent& event) const;

  SyntheticPenSink& sink_;
  mapping::VirtualScreenRect target_;
  PenSession session_;
};

#ifdef _WIN32
std::unique_ptr<SyntheticPenSink> make_win32_synthetic_pen_sink();
#endif

} // namespace wlt::host::input
