#include "diagnostics/sequence_tracker.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::SequenceTracker;

  SequenceTracker tracker;

  auto observation = tracker.observe(10);
  if (int code = expect(observation.first_packet, 1); code != 0) {
    return code;
  }
  if (int code = expect(!observation.has_gap, 2); code != 0) {
    return code;
  }

  observation = tracker.observe(11);
  if (int code = expect(!observation.first_packet, 3); code != 0) {
    return code;
  }
  if (int code = expect(!observation.has_gap, 4); code != 0) {
    return code;
  }

  observation = tracker.observe(14);
  if (int code = expect(observation.has_gap, 5); code != 0) {
    return code;
  }
  if (int code = expect(observation.expected_sequence == 12, 6); code != 0) {
    return code;
  }
  if (int code = expect(observation.missing_count == 2, 7); code != 0) {
    return code;
  }

  observation = tracker.observe(14);
  if (int code = expect(observation.out_of_order_or_duplicate, 8); code != 0) {
    return code;
  }

  return 0;
}
