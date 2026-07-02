#include "input/hid_pen_report_writer.h"

#include <algorithm>
#include <cmath>
#include <utility>

namespace wlt::host::input {
namespace {

std::uint16_t map_normalized_to_u16(float normalized, std::uint16_t maximum) {
  const float clamped = std::clamp(normalized, 0.0F, 1.0F);
  return static_cast<std::uint16_t>(std::lround(clamped * static_cast<float>(maximum)));
}

std::uint16_t map_pressure_to_hid(float pressure) {
  return map_normalized_to_u16(pressure, kHidPressureMax);
}

std::int8_t map_tilt_to_hid(std::int16_t degrees) {
  return static_cast<std::int8_t>(std::clamp<std::int16_t>(degrees, -90, 90));
}

void append_u16_le(HidPenReportBytes& report, std::size_t offset, std::uint16_t value) {
  report[offset] = static_cast<std::uint8_t>(value & 0xFFU);
  report[offset + 1] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
}

} // namespace

HidPenReportWriter::HidPenReportWriter(HidPenReportSink& sink)
    : owned_sink_(nullptr),
      sink_(sink) {
}

HidPenReportWriter::HidPenReportWriter(std::unique_ptr<HidPenReportSink> sink)
    : owned_sink_(std::move(sink)),
      sink_(*owned_sink_) {
}

bool HidPenReportWriter::accept(PenAction action, const PenSample& sample) {
  return write_events(session_.accept(action, sample));
}

bool HidPenReportWriter::force_up() {
  return write_events(session_.force_up());
}

bool HidPenReportWriter::force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) {
  const auto events = session_.force_up_if_idle(now_ns, idle_timeout_ns);
  if (events.empty()) {
    return false;
  }
  return write_events(events);
}

bool HidPenReportWriter::is_active() const {
  return session_.is_active();
}

bool HidPenReportWriter::write_events(const std::vector<PenEvent>& events) {
  if (events.empty()) {
    return false;
  }

  for (const auto& event : events) {
    if (!sink_.write_report(serialize_hid_pen_event(event))) {
      const auto forced_events = session_.force_up();
      for (const auto& forced_event : forced_events) {
        sink_.write_report(serialize_hid_pen_event(forced_event));
      }
      return false;
    }
  }
  return true;
}

HidPenReportBytes serialize_hid_pen_event(const PenEvent& event) {
  const PenAction action = event.action;
  const PenSample& sample = event.sample;
  const std::uint16_t x = map_normalized_to_u16(sample.x, kHidCoordinateMax);
  const std::uint16_t y = map_normalized_to_u16(sample.y, kHidCoordinateMax);
  const std::uint16_t pressure = map_pressure_to_hid(action == PenAction::Down || action == PenAction::Move ? sample.pressure : 0.0F);

  std::uint8_t buttons = 0;
  if (action == PenAction::Down || action == PenAction::Move) {
    buttons = kHidTipSwitchBit | kHidInRangeBit;
  } else if (action == PenAction::Hover) {
    buttons = kHidInRangeBit;
  }

  HidPenReportBytes report{};
  report[0] = kHidPenReportId;
  report[1] = buttons;
  append_u16_le(report, 2, x);
  append_u16_le(report, 4, y);
  append_u16_le(report, 6, pressure);
  report[8] = static_cast<std::uint8_t>(map_tilt_to_hid(sample.tilt_x));
  report[9] = static_cast<std::uint8_t>(map_tilt_to_hid(sample.tilt_y));
  return report;
}

} // namespace wlt::host::input
