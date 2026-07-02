#include "diagnostics/fps_counter.h"

#include <cmath>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

bool near(double actual, double expected) {
  return std::fabs(actual - expected) < 0.0001;
}

} // namespace

int main() {
  using wlt::host::diagnostics::FpsCounter;

  FpsCounter counter;
  counter.add_frame_timestamp_ns(0);
  counter.add_frame_timestamp_ns(500'000'000);
  counter.add_frame_timestamp_ns(1'000'000'000);

  if (int code = expect(counter.frame_count() == 3, 1); code != 0) {
    return code;
  }
  if (int code = expect(near(counter.frames_per_second(), 3.0), 2); code != 0) {
    return code;
  }

  counter.add_frame_timestamp_ns(2'000'000'000);
  if (int code = expect(near(counter.frames_per_second(), 2.0), 3); code != 0) {
    return code;
  }

  return 0;
}
