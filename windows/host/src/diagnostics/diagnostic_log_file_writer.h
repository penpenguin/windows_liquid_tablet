#pragma once

#include "diagnostics/diagnostic_log.h"

#include <filesystem>

namespace wlt::host::diagnostics {

bool diagnostic_log_path_is_safe(const std::filesystem::path& path);
bool write_diagnostic_log_text(const DiagnosticLog& log, const std::filesystem::path& path);

} // namespace wlt::host::diagnostics
