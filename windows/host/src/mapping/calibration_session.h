#pragma once

#include "mapping/coordinate_mapping.h"

#include <cstddef>
#include <optional>
#include <vector>

namespace wlt::host::mapping {

struct CalibrationResult {
  NormalizedPoint offset;
  std::size_t sample_count;
};

class CalibrationSession {
public:
  explicit CalibrationSession(std::vector<NormalizedPoint> expected);

  std::optional<NormalizedPoint> current_target() const;
  bool record_sample(NormalizedPoint measured);
  std::size_t remaining_count() const;
  bool is_complete() const;
  std::optional<CalibrationResult> result() const;

private:
  std::vector<NormalizedPoint> expected_;
  std::vector<NormalizedPoint> samples_;
};

} // namespace wlt::host::mapping
