#include "app/debug_stroke.h"

#include <cstddef>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::app::DebugStrokeRect;
  using wlt::host::app::make_fixed_rectangle_stroke;
  using wlt::host::app::make_rectangle_stroke;
  using wlt::host::input::PenAction;

  const auto stroke = make_fixed_rectangle_stroke();

  if (int code = expect(stroke.size() == 6, 1); code != 0) {
    return code;
  }
  if (int code = expect(stroke.front().action == PenAction::Down, 2); code != 0) {
    return code;
  }
  if (int code = expect(stroke.back().action == PenAction::Up, 3); code != 0) {
    return code;
  }
  if (int code = expect(stroke[0].sample.x == 0.25F && stroke[0].sample.y == 0.25F, 4); code != 0) {
    return code;
  }
  if (int code = expect(stroke[2].sample.x == 0.75F && stroke[2].sample.y == 0.75F, 5); code != 0) {
    return code;
  }
  if (int code = expect(stroke[3].sample.pressure == 1.0F, 6); code != 0) {
    return code;
  }
  if (int code = expect(stroke[1].sample.tilt_x == 20 && stroke[1].sample.tilt_y == -20, 7); code != 0) {
    return code;
  }
  if (int code = expect(stroke[3].sample.tilt_x == -25 && stroke[3].sample.tilt_y == 30, 8); code != 0) {
    return code;
  }
  if (int code = expect(stroke.back().sample.tilt_x == 0 && stroke.back().sample.tilt_y == 0, 9); code != 0) {
    return code;
  }

  for (std::size_t i = 1; i < stroke.size(); ++i) {
    if (int code = expect(stroke[i - 1].sample.timestamp_ns < stroke[i].sample.timestamp_ns, 10 + static_cast<int>(i)); code != 0) {
      return code;
    }
  }

  const auto custom_stroke = make_rectangle_stroke(DebugStrokeRect{
      .left = 0.10F,
      .top = 0.20F,
      .right = 0.90F,
      .bottom = 0.80F,
  });
  if (int code = expect(custom_stroke.size() == 6, 20); code != 0) {
    return code;
  }
  if (int code = expect(
          custom_stroke[0].sample.x == 0.10F && custom_stroke[0].sample.y == 0.20F,
          21);
      code != 0) {
    return code;
  }
  if (int code = expect(
          custom_stroke[2].sample.x == 0.90F && custom_stroke[2].sample.y == 0.80F,
          22);
      code != 0) {
    return code;
  }
  if (int code = expect(
          custom_stroke[4].sample.x == 0.10F && custom_stroke[4].sample.y == 0.20F,
          23);
      code != 0) {
    return code;
  }

  return 0;
}
