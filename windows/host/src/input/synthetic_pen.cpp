#include "input/synthetic_pen.h"

#include "mapping/pen_mapping.h"

namespace wlt::host::input {

SyntheticPen::SyntheticPen(SyntheticPenSink& sink, mapping::VirtualScreenRect target)
    : sink_(sink), target_(target) {
}

bool SyntheticPen::accept(PenAction action, const PenSample& sample) {
  return inject_events(session_.accept(action, sample));
}

bool SyntheticPen::force_up() {
  return inject_events(session_.force_up());
}

bool SyntheticPen::force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) {
  const auto events = session_.force_up_if_idle(now_ns, idle_timeout_ns);
  if (events.empty()) {
    return false;
  }
  return inject_events(events);
}

bool SyntheticPen::set_target(mapping::VirtualScreenRect target) {
  const bool forced_up = force_up();
  target_ = target;
  return forced_up;
}

bool SyntheticPen::is_active() const {
  return session_.is_active();
}

bool SyntheticPen::inject_events(const std::vector<PenEvent>& events) {
  if (events.empty()) {
    return false;
  }

  for (const auto& event : events) {
    if (!sink_.inject(to_frame(event))) {
      const auto forced_events = session_.force_up();
      for (const auto& forced_event : forced_events) {
        sink_.inject(to_frame(forced_event));
      }
      return false;
    }
  }

  return true;
}

SyntheticPenFrame SyntheticPen::to_frame(const PenEvent& event) const {
  const auto point = mapping::map_normalized_to_virtual_screen(
      mapping::NormalizedPoint{.x = event.sample.x, .y = event.sample.y},
      target_);

  return SyntheticPenFrame{
      .action = event.action,
      .x = point.x,
      .y = point.y,
      .pressure = mapping::map_pressure_to_windows(event.sample.pressure),
      .tilt_x = mapping::map_tilt_to_windows(event.sample.tilt_x),
      .tilt_y = mapping::map_tilt_to_windows(event.sample.tilt_y),
      .forced = event.forced,
  };
}

} // namespace wlt::host::input
