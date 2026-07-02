#include "hid_device_state.h"

namespace wlt::hid {

HidDeviceState::HidDeviceState()
    : hid_descriptor_(wlt::hid::hid_descriptor()),
      device_attributes_(hid_device_attributes()),
      report_descriptor_(pen_report_descriptor()),
      last_report_(make_pen_hid_release_report(PenHidReport{
          .report_id = kPenReportId,
          .buttons = 0,
          .x = 0,
          .y = 0,
          .pressure = 0,
          .tilt_x = 0,
          .tilt_y = 0,
      })),
      active_(false) {}

bool HidDeviceState::is_active() const {
  return active_;
}

void HidDeviceState::activate() {
  active_ = true;
}

void HidDeviceState::deactivate() {
  active_ = false;
}

const std::array<std::uint8_t, kHidDescriptorSize>& HidDeviceState::hid_descriptor()
    const {
  return hid_descriptor_;
}

const std::array<std::uint8_t, kHidDeviceAttributesSize>& HidDeviceState::device_attributes()
    const {
  return device_attributes_;
}

std::optional<HidStringResponse> HidDeviceState::hid_string_response(
    std::uint16_t string_id) const {
  return wlt::hid::hid_string_response(string_id);
}

const std::array<std::uint8_t, kPenReportDescriptorSize>& HidDeviceState::report_descriptor()
    const {
  return report_descriptor_;
}

PenHidReport HidDeviceState::last_report() const {
  return last_report_;
}

std::array<std::uint8_t, kPenHidReportWireSize> HidDeviceState::serialized_last_report()
    const {
  return serialize_pen_hid_report(last_report_);
}

std::optional<PenHidReport> HidDeviceState::apply_serialized_report(
    const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes) {
  const auto report = deserialize_pen_hid_report(report_bytes);
  if (!report.has_value()) {
    return std::nullopt;
  }

  last_report_ = *report;
  return last_report_;
}

PenHidReport HidDeviceState::apply_sample(PenHidSample sample) {
  last_report_ = make_pen_hid_report(sample);
  return last_report_;
}

PenHidReport HidDeviceState::release_contact() {
  last_report_ = make_pen_hid_release_report(last_report_);
  return last_report_;
}

} // namespace wlt::hid
