#include "diagnostics/sequence_tracker.h"

namespace wlt::host::diagnostics {

SequenceObservation SequenceTracker::observe(std::uint32_t sequence) {
  if (!initialized_) {
    initialized_ = true;
    next_expected_ = sequence + 1;
    return SequenceObservation{
        .sequence = sequence,
        .first_packet = true,
        .has_gap = false,
        .out_of_order_or_duplicate = false,
        .expected_sequence = sequence,
        .missing_count = 0,
    };
  }

  if (sequence < next_expected_) {
    return SequenceObservation{
        .sequence = sequence,
        .first_packet = false,
        .has_gap = false,
        .out_of_order_or_duplicate = true,
        .expected_sequence = next_expected_,
        .missing_count = 0,
    };
  }

  if (sequence > next_expected_) {
    const std::uint32_t expected = next_expected_;
    next_expected_ = sequence + 1;
    return SequenceObservation{
        .sequence = sequence,
        .first_packet = false,
        .has_gap = true,
        .out_of_order_or_duplicate = false,
        .expected_sequence = expected,
        .missing_count = sequence - expected,
    };
  }

  next_expected_ = sequence + 1;
  return SequenceObservation{
      .sequence = sequence,
      .first_packet = false,
      .has_gap = false,
      .out_of_order_or_duplicate = false,
      .expected_sequence = sequence,
      .missing_count = 0,
  };
}

} // namespace wlt::host::diagnostics
