#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>

namespace wlt::host::mapping {

inline std::uint32_t map_pressure_to_windows(float normalized_pressure) {
  const float clamped = std::clamp(normalized_pressure, 0.0F, 1.0F);
  return static_cast<std::uint32_t>(std::lround(clamped * 1024.0F));
}

inline std::int16_t map_tilt_to_windows(std::int16_t tilt_degrees) {
  return std::clamp<std::int16_t>(tilt_degrees, -90, 90);
}

} // namespace wlt::host::mapping
