#include "input/synthetic_pen.h"

#include <cstdint>
#include <vector>

namespace {

class RecordingSink final : public wlt::host::input::SyntheticPenSink {
public:
  bool inject(const wlt::host::input::SyntheticPenFrame& frame) override {
    frames.push_back(frame);
    if (fail_next) {
      fail_next = false;
      return false;
    }
    return true;
  }

  std::vector<wlt::host::input::SyntheticPenFrame> frames;
  bool fail_next = false;
};

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

wlt::host::input::PenSample sample(
    float x,
    float y,
    float pressure = 0.5F,
    std::uint64_t timestamp_ns = 100,
    std::int16_t tilt_x = 11,
    std::int16_t tilt_y = -12) {
  return wlt::host::input::PenSample{
      .x = x,
      .y = y,
      .pressure = pressure,
      .tilt_x = tilt_x,
      .tilt_y = tilt_y,
      .timestamp_ns = timestamp_ns,
  };
}

} // namespace

int main() {
  using wlt::host::input::PenAction;
  using wlt::host::input::SyntheticPen;
  using wlt::host::mapping::VirtualScreenRect;

  RecordingSink sink;
  SyntheticPen pen(sink, VirtualScreenRect{.left = 100, .top = 200, .width = 1920, .height = 1080});

  if (int code = expect(pen.accept(PenAction::Down, sample(0.0F, 0.0F, 0.25F)), 1); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].action == PenAction::Down, 3); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].x == 100, 4); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].y == 200, 5); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].pressure == 256, 6); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].tilt_x == 11, 7); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].tilt_y == -12, 8); code != 0) {
    return code;
  }

  if (int code = expect(pen.accept(PenAction::Move, sample(1.0F, 1.0F, 1.0F)), 9); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].x == 2019, 10); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].y == 1279, 11); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].pressure == 1024, 12); code != 0) {
    return code;
  }

  if (int code = expect(pen.force_up(), 13); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[2].action == PenAction::Up, 14); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[2].forced, 15); code != 0) {
    return code;
  }
  if (int code = expect(!pen.force_up(), 29); code != 0) {
    return code;
  }

  pen.accept(PenAction::Down, sample(0.5F, 0.5F));
  sink.fail_next = true;
  if (int code = expect(!pen.accept(PenAction::Move, sample(0.6F, 0.6F)), 16); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().action == PenAction::Up, 17); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().forced, 18); code != 0) {
    return code;
  }
  if (int code = expect(!pen.is_active(), 19); code != 0) {
    return code;
  }

  if (int code = expect(pen.accept(PenAction::Down, sample(0.2F, 0.3F, 0.5F, 1'000)), 20);
      code != 0) {
    return code;
  }
  if (int code = expect(!pen.force_up_if_idle(1'199, 200), 21); code != 0) {
    return code;
  }
  if (int code = expect(pen.force_up_if_idle(1'200, 200), 22); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().action == PenAction::Up, 23); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().forced, 24); code != 0) {
    return code;
  }
  if (int code = expect(!pen.is_active(), 25); code != 0) {
    return code;
  }

  if (int code = expect(pen.accept(PenAction::Down, sample(0.4F, 0.4F, 0.5F, 2'000, 120, -130)), 26);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().tilt_x == 90, 27); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.back().tilt_y == -90, 28); code != 0) {
    return code;
  }

  RecordingSink remap_sink;
  SyntheticPen remap_pen(remap_sink, VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  if (int code = expect(remap_pen.accept(PenAction::Down, sample(0.5F, 0.5F)), 30); code != 0) {
    return code;
  }
  if (int code = expect(remap_pen.set_target(
      VirtualScreenRect{.left = 200, .top = 50, .width = 100, .height = 100}), 31); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink.frames[1].action == PenAction::Up, 32); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink.frames[1].forced, 33); code != 0) {
    return code;
  }
  if (int code = expect(!remap_pen.is_active(), 34); code != 0) {
    return code;
  }
  if (int code = expect(remap_pen.accept(PenAction::Down, sample(0.5F, 0.5F)), 35); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink.frames[2].x == 250, 36); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink.frames[2].y == 100, 37); code != 0) {
    return code;
  }
  if (int code = expect(remap_pen.force_up(), 39); code != 0) {
    return code;
  }
  if (int code = expect(!remap_pen.set_target(
      VirtualScreenRect{.left = 300, .top = 75, .width = 100, .height = 100}), 38); code != 0) {
    return code;
  }

  return 0;
}
