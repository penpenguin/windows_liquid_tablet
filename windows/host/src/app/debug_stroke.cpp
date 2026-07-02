#include "app/debug_stroke.h"

#include <cstdint>

namespace wlt::host::app {

namespace {

input::PenSample sample(
    float x,
    float y,
    float pressure,
    std::int16_t tilt_x,
    std::int16_t tilt_y,
    std::uint64_t timestamp_ns) {
  return input::PenSample{
      .x = x,
      .y = y,
      .pressure = pressure,
      .tilt_x = tilt_x,
      .tilt_y = tilt_y,
      .timestamp_ns = timestamp_ns,
  };
}

} // namespace

std::vector<DebugPenCommand> make_rectangle_stroke(DebugStrokeRect rect) {
  return {
      DebugPenCommand{.action = input::PenAction::Down, .sample = sample(rect.left, rect.top, 0.25F, 0, 0, 1'000'000)},
      DebugPenCommand{.action = input::PenAction::Move, .sample = sample(rect.right, rect.top, 0.50F, 20, -20, 2'000'000)},
      DebugPenCommand{.action = input::PenAction::Move, .sample = sample(rect.right, rect.bottom, 0.75F, 35, 15, 3'000'000)},
      DebugPenCommand{.action = input::PenAction::Move, .sample = sample(rect.left, rect.bottom, 1.00F, -25, 30, 4'000'000)},
      DebugPenCommand{.action = input::PenAction::Move, .sample = sample(rect.left, rect.top, 0.50F, -40, -30, 5'000'000)},
      DebugPenCommand{.action = input::PenAction::Up, .sample = sample(rect.left, rect.top, 0.00F, 0, 0, 6'000'000)},
  };
}

std::vector<DebugPenCommand> make_fixed_rectangle_stroke() {
  return make_rectangle_stroke(DebugStrokeRect{
      .left = 0.25F,
      .top = 0.25F,
      .right = 0.75F,
      .bottom = 0.75F,
  });
}

} // namespace wlt::host::app
