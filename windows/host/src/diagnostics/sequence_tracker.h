#pragma once

#include <cstdint>

namespace wlt::host::diagnostics {

struct SequenceObservation {
  std::uint32_t sequence;
  bool first_packet;
  bool has_gap;
  bool out_of_order_or_duplicate;
  std::uint32_t expected_sequence;
  std::uint32_t missing_count;
};

class SequenceTracker {
public:
  SequenceObservation observe(std::uint32_t sequence);

private:
  bool initialized_ = false;
  std::uint32_t next_expected_ = 0;
};

} // namespace wlt::host::diagnostics
