#include "input/hid_pen_report_writer.h"

#include <vector>

namespace {

class RecordingHidSink final : public wlt::host::input::HidPenReportSink {
public:
  bool write_report(const wlt::host::input::HidPenReportBytes& report) override {
    reports.push_back(report);
    if (fail_next) {
      fail_next = false;
      return false;
    }
    return true;
  }

  std::vector<wlt::host::input::HidPenReportBytes> reports;
  bool fail_next = false;
};

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

wlt::host::input::PenSample sample(
    float x,
    float y,
    float pressure = 0.5F,
    std::int16_t tilt_x = 12,
    std::int16_t tilt_y = -12) {
  return wlt::host::input::PenSample{
      .x = x,
      .y = y,
      .pressure = pressure,
      .tilt_x = tilt_x,
      .tilt_y = tilt_y,
      .timestamp_ns = 100,
  };
}

} // namespace

int main() {
  using wlt::host::input::HidPenReportWriter;
  using wlt::host::input::PenAction;

  RecordingHidSink sink;
  HidPenReportWriter writer(sink);

  if (int code = expect(writer.accept(PenAction::Down, sample(0.5F, 1.0F, 0.5F)), 1);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.reports.size() == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(sink.reports[0][0] == wlt::host::input::kHidPenReportId, 3);
      code != 0) {
    return code;
  }
  if (int code = expect(wlt::host::input::kHidPenReportId == 0x02, 17); code != 0) {
    return code;
  }
  const bool down_buttons =
      sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit);
  if (int code = expect(down_buttons, 4); code != 0) {
    return code;
  }
  if (int code = expect(sink.reports[0][2] == 0x00 && sink.reports[0][3] == 0x40, 5);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.reports[0][4] == 0xFF && sink.reports[0][5] == 0x7F, 6);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.reports[0][6] == 0x00 && sink.reports[0][7] == 0x02, 7);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.reports[0][8] == 12, 8); code != 0) {
    return code;
  }
  if (int code = expect(static_cast<std::int8_t>(sink.reports[0][9]) == -12, 9);
      code != 0) {
    return code;
  }

  if (int code = expect(writer.force_up(), 10); code != 0) {
    return code;
  }
  if (int code = expect(sink.reports.back()[1] == 0, 11); code != 0) {
    return code;
  }
  if (int code = expect(sink.reports.back()[6] == 0 && sink.reports.back()[7] == 0, 12);
      code != 0) {
    return code;
  }

  writer.accept(PenAction::Down, sample(0.25F, 0.25F, 0.75F));
  sink.fail_next = true;
  if (int code = expect(!writer.accept(PenAction::Move, sample(0.30F, 0.30F, 0.80F)), 13);
      code != 0) {
    return code;
  }
  if (int code = expect(sink.reports.back()[1] == 0, 14); code != 0) {
    return code;
  }
  if (int code = expect(!writer.is_active(), 15); code != 0) {
    return code;
  }

  if (int code = expect(wlt::host::input::kWindowsLiquidTabletHidApplyReportIoctl == 0x0022A004U, 16);
      code != 0) {
    return code;
  }

  return 0;
}
