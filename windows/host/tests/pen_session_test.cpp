#include "input/pen_session.h"
#include "mapping/pen_mapping.h"

#include <cstdint>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

wlt::host::input::PenSample sample(
    float x,
    float y,
    std::uint64_t timestamp_ns = 100) {
  return wlt::host::input::PenSample{
      .x = x,
      .y = y,
      .pressure = 0.5F,
      .tilt_x = 10,
      .tilt_y = -10,
      .timestamp_ns = timestamp_ns,
  };
}

} // namespace

int main() {
  using wlt::host::input::PenAction;
  using wlt::host::input::PenEvent;
  using wlt::host::input::PenSession;
  using wlt::host::mapping::map_pressure_to_windows;

  PenSession session;

  auto events = session.accept(PenAction::Move, sample(0.1F, 0.2F));
  if (int code = expect(events.empty(), 1); code != 0) {
    return code;
  }

  events = session.accept(PenAction::Hover, sample(0.2F, 0.3F));
  if (int code = expect(events.size() == 1, 23); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Hover, 24); code != 0) {
    return code;
  }
  if (int code = expect(!session.is_active(), 25); code != 0) {
    return code;
  }

  events = session.accept(PenAction::Down, sample(0.1F, 0.2F));
  if (int code = expect(events.size() == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Down, 3); code != 0) {
    return code;
  }
  if (int code = expect(session.is_active(), 4); code != 0) {
    return code;
  }

  events = session.accept(PenAction::Down, sample(0.3F, 0.4F));
  if (int code = expect(events.size() == 2, 5); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Up, 6); code != 0) {
    return code;
  }
  if (int code = expect(events[1].action == PenAction::Down, 7); code != 0) {
    return code;
  }

  events = session.accept(PenAction::Cancel, sample(0.3F, 0.4F));
  if (int code = expect(events.size() == 1, 8); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Up, 9); code != 0) {
    return code;
  }
  if (int code = expect(!session.is_active(), 10); code != 0) {
    return code;
  }

  events = session.force_up();
  if (int code = expect(events.empty(), 11); code != 0) {
    return code;
  }

  session.accept(PenAction::Down, sample(0.5F, 0.6F));
  events = session.force_up();
  if (int code = expect(events.size() == 1, 12); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Up, 13); code != 0) {
    return code;
  }

  session.accept(PenAction::Down, sample(0.7F, 0.8F, 1'000));
  events = session.force_up_if_idle(1'199, 200);
  if (int code = expect(events.empty(), 14); code != 0) {
    return code;
  }
  if (int code = expect(session.is_active(), 15); code != 0) {
    return code;
  }

  events = session.force_up_if_idle(1'200, 200);
  if (int code = expect(events.size() == 1, 16); code != 0) {
    return code;
  }
  if (int code = expect(events[0].action == PenAction::Up, 17); code != 0) {
    return code;
  }
  if (int code = expect(events[0].forced, 18); code != 0) {
    return code;
  }
  if (int code = expect(!session.is_active(), 19); code != 0) {
    return code;
  }

  if (int code = expect(map_pressure_to_windows(-1.0F) == 0, 20); code != 0) {
    return code;
  }
  if (int code = expect(map_pressure_to_windows(0.5F) == 512, 21); code != 0) {
    return code;
  }
  if (int code = expect(map_pressure_to_windows(2.0F) == 1024, 22); code != 0) {
    return code;
  }

  return 0;
}
