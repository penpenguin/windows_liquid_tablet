#include "diagnostics/diagnostic_log_file_writer.h"

#include <fstream>
#include <system_error>

namespace wlt::host::diagnostics {

namespace {

bool diagnostic_log_path_has_symlink_component(const std::filesystem::path& path) {
  std::filesystem::path candidate = path;
  while (!candidate.empty()) {
    std::error_code ec;
    const auto status = std::filesystem::symlink_status(candidate, ec);
    if (!ec && std::filesystem::is_symlink(status)) {
      return true;
    }

    const auto parent = candidate.parent_path();
    if (parent.empty() || parent == candidate) {
      break;
    }
    candidate = parent;
  }

  return false;
}

} // namespace

bool diagnostic_log_path_is_safe(const std::filesystem::path& path) {
  return !diagnostic_log_path_has_symlink_component(path);
}

bool write_diagnostic_log_text(const DiagnosticLog& log, const std::filesystem::path& path) {
  if (!diagnostic_log_path_is_safe(path)) {
    return false;
  }

  std::ofstream output(path, std::ios::binary);
  if (!output) {
    return false;
  }

  output << log.export_text();
  // export_text documents that No screen contents or personal data are included.
  return output.good();
}

} // namespace wlt::host::diagnostics
