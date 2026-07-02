#pragma once

#include <cstdint>
#include <optional>
#include <vector>

namespace wlt::host::input {

enum class PenAction {
  Down,
  Move,
  Up,
  Hover,
  Cancel,
};

struct PenSample {
  float x;
  float y;
  float pressure;
  std::int16_t tilt_x;
  std::int16_t tilt_y;
  std::uint64_t timestamp_ns;
};

struct PenEvent {
  PenAction action;
  PenSample sample;
  bool forced;
};

class PenSession {
public:
  std::vector<PenEvent> accept(PenAction action, const PenSample& sample);
  std::vector<PenEvent> force_up();
  std::vector<PenEvent> force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns);
  bool is_active() const;

private:
  PenEvent make_event(PenAction action, const PenSample& sample, bool forced) const;

  bool active_ = false;
  std::optional<PenSample> last_sample_;
};

// PenAction::Cancel is treated as a fail-safe UP when a stroke is active.

} // namespace wlt::host::input
