#include "input/hid_pen_report_writer.h"

#ifndef _WIN32
#error hid_pen_report_writer_win32.cpp must only be built on Windows.
#endif

#include <windows.h>

#include <memory>
#include <stdexcept>
#include <string>

namespace wlt::host::input {
namespace {

class Win32HidPenReportSink final : public HidPenReportSink {
public:
  explicit Win32HidPenReportSink(const std::wstring& device_path)
      : device_(CreateFileW(
            device_path.c_str(),
            GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            nullptr,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            nullptr)) {
    if (device_ == INVALID_HANDLE_VALUE) {
      throw std::runtime_error("CreateFileW failed for optional HID pen device");
    }
  }

  ~Win32HidPenReportSink() override {
    if (device_ != INVALID_HANDLE_VALUE) {
      CloseHandle(device_);
    }
  }

  Win32HidPenReportSink(const Win32HidPenReportSink&) = delete;
  Win32HidPenReportSink& operator=(const Win32HidPenReportSink&) = delete;

  bool write_report(const HidPenReportBytes& report) override {
    DWORD bytes_returned = 0;
    return DeviceIoControl(
        device_,
        kWindowsLiquidTabletHidApplyReportIoctl,
        const_cast<std::uint8_t*>(report.data()),
        static_cast<DWORD>(report.size()),
        nullptr,
        0,
        &bytes_returned,
        nullptr) != FALSE;
  }

private:
  HANDLE device_ = INVALID_HANDLE_VALUE;
};

} // namespace

std::unique_ptr<HidPenReportSink> make_win32_hid_pen_report_sink(
    const std::wstring& device_path) {
  return std::make_unique<Win32HidPenReportSink>(device_path);
}

} // namespace wlt::host::input
