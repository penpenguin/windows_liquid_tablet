#pragma once

#include "input/pen_injector.h"
#include "input/pen_session.h"

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace wlt::host::input {

constexpr std::uint32_t kWindowsLiquidTabletHidApplyReportIoctl = 0x0022A004U;
constexpr std::size_t kHidPenReportWireSize = 10;
constexpr std::uint8_t kHidPenReportId = 0x02;
constexpr std::uint8_t kHidTipSwitchBit = 0x01;
constexpr std::uint8_t kHidBarrelSwitchBit = 0x02;
constexpr std::uint8_t kHidInvertBit = 0x04;
constexpr std::uint8_t kHidEraserBit = 0x08;
constexpr std::uint8_t kHidInRangeBit = 0x20;
constexpr std::uint16_t kHidCoordinateMax = 32767;
constexpr std::uint16_t kHidPressureMax = 1023;

using HidPenReportBytes = std::array<std::uint8_t, kHidPenReportWireSize>;

class HidPenReportSink {
public:
  virtual ~HidPenReportSink() = default;
  virtual bool write_report(const HidPenReportBytes& report) = 0;
};

class HidPenReportWriter : public PenInjector {
public:
  explicit HidPenReportWriter(HidPenReportSink& sink);
  explicit HidPenReportWriter(std::unique_ptr<HidPenReportSink> sink);

  bool accept(PenAction action, const PenSample& sample) override;
  bool force_up() override;
  bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) override;
  bool is_active() const override;

private:
  bool write_events(const std::vector<PenEvent>& events);

  std::unique_ptr<HidPenReportSink> owned_sink_;
  HidPenReportSink& sink_;
  PenSession session_;
};

HidPenReportBytes serialize_hid_pen_event(const PenEvent& event);

#ifdef _WIN32
std::unique_ptr<HidPenReportSink> make_win32_hid_pen_report_sink(
    const std::wstring& device_path);
#endif

} // namespace wlt::host::input
