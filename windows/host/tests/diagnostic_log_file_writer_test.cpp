#include "diagnostics/diagnostic_log_file_writer.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <system_error>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

std::string read_text(const std::filesystem::path& path) {
  std::ifstream input(path);
  std::ostringstream out;
  out << input.rdbuf();
  return out.str();
}

bool create_test_file_symlink(
    const std::filesystem::path& target,
    const std::filesystem::path& symlink_path) {
  std::error_code ec;
  std::filesystem::create_symlink(target, symlink_path, ec);
  return !ec;
}

bool create_test_directory_symlink(
    const std::filesystem::path& target,
    const std::filesystem::path& symlink_path) {
  std::error_code ec;
  std::filesystem::create_directory_symlink(target, symlink_path, ec);
  return !ec;
}

} // namespace

int main() {
  using wlt::host::diagnostics::DiagnosticEvent;
  using wlt::host::diagnostics::DiagnosticLog;
  using wlt::host::diagnostics::DiagnosticSeverity;
  using wlt::host::diagnostics::write_diagnostic_log_text;

  DiagnosticLog log;
  log.add(DiagnosticEvent{
      .timestamp_ns = 100,
      .severity = DiagnosticSeverity::Info,
      .category = "connection",
      .message = "connected",
  });

  const auto path = std::filesystem::temp_directory_path() / "wlt_diagnostic_log_test.txt";
  if (int code = expect(write_diagnostic_log_text(log, path), 1); code != 0) {
    return code;
  }

  const auto exported = read_text(path);
  if (int code = expect(exported.find("connected") != std::string::npos, 2); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("No screen contents") != std::string::npos, 3); code != 0) {
    return code;
  }

  const auto symlink_root =
      std::filesystem::temp_directory_path() / "wlt_diagnostic_log_symlink_test";
  std::filesystem::remove_all(symlink_root);
  std::filesystem::create_directories(symlink_root);

  const auto symlink_target = symlink_root / "target.txt";
  const auto symlink_path = symlink_root / "linked-output.txt";
  {
    std::ofstream target_output(symlink_target, std::ios::binary);
    target_output << "unchanged";
  }

  if (create_test_file_symlink(symlink_target, symlink_path)) {
    if (int code = expect(!write_diagnostic_log_text(log, symlink_path), 4); code != 0) {
      return code;
    }
    if (int code = expect(read_text(symlink_target) == "unchanged", 5); code != 0) {
      return code;
    }
  }

  const auto real_parent = symlink_root / "real-parent";
  const auto symlink_parent = symlink_root / "linked-parent";
  std::filesystem::create_directories(real_parent);
  if (create_test_directory_symlink(real_parent, symlink_parent)) {
    const auto symlink_child_path = symlink_parent / "child-output.txt";
    if (int code = expect(!write_diagnostic_log_text(log, symlink_child_path), 6); code != 0) {
      return code;
    }
    if (int code = expect(!std::filesystem::exists(real_parent / "child-output.txt"), 7);
        code != 0) {
      return code;
    }
  }

  std::filesystem::remove_all(symlink_root);

  return 0;
}
