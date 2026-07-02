#pragma once

#include "diagnostics/stage_latency_telemetry.h"

#include <string>

namespace wlt::host::diagnostics {

std::string format_latency_report(LatencyStage stage, StageLatencyReport report);
std::string format_latency_report(const std::string& stage_name, StageLatencyReport report);

} // namespace wlt::host::diagnostics
