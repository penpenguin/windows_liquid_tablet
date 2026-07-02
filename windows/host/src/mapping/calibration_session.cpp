#include "mapping/calibration_session.h"

#include <utility>

namespace wlt::host::mapping {

CalibrationSession::CalibrationSession(std::vector<NormalizedPoint> expected)
    : expected_(std::move(expected)) {
}

std::optional<NormalizedPoint> CalibrationSession::current_target() const {
  if (is_complete()) {
    return std::nullopt;
  }

  return expected_[samples_.size()];
}

bool CalibrationSession::record_sample(NormalizedPoint measured) {
  if (is_complete()) {
    return false;
  }

  samples_.push_back(measured);
  return true;
}

std::size_t CalibrationSession::remaining_count() const {
  return expected_.size() - samples_.size();
}

bool CalibrationSession::is_complete() const {
  return samples_.size() >= expected_.size();
}

std::optional<CalibrationResult> CalibrationSession::result() const {
  if (!is_complete() || expected_.empty()) {
    return std::nullopt;
  }

  float total_x = 0.0F;
  float total_y = 0.0F;
  for (std::size_t index = 0; index < expected_.size(); ++index) {
    total_x += samples_[index].x - expected_[index].x;
    total_y += samples_[index].y - expected_[index].y;
  }

  const auto count = static_cast<float>(expected_.size());
  return CalibrationResult{
      .offset = NormalizedPoint{.x = total_x / count, .y = total_y / count},
      .sample_count = expected_.size(),
  };
}

} // namespace wlt::host::mapping
