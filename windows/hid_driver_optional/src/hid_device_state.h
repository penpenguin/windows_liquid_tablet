#pragma once

#include "hid_report_descriptor.h"

#include <array>
#include <cstdint>

namespace wlt::hid {

class HidDeviceState {
 public:
  HidDeviceState();

  bool is_active() const;
  void activate();
  void deactivate();
  const std::array<std::uint8_t, kHidDescriptorSize>& hid_descriptor() const;
  const std::array<std::uint8_t, kHidDeviceAttributesSize>& device_attributes() const;
  std::optional<HidStringResponse> hid_string_response(std::uint16_t string_id) const;
  const std::array<std::uint8_t, kPenReportDescriptorSize>& report_descriptor() const;
  PenHidReport last_report() const;
  std::array<std::uint8_t, kPenHidReportWireSize> serialized_last_report() const;
  std::optional<PenHidReport> apply_serialized_report(
      const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes);
  PenHidReport apply_sample(PenHidSample sample);
  PenHidReport release_contact();

 private:
  std::array<std::uint8_t, kHidDescriptorSize> hid_descriptor_;
  std::array<std::uint8_t, kHidDeviceAttributesSize> device_attributes_;
  std::array<std::uint8_t, kPenReportDescriptorSize> report_descriptor_;
  PenHidReport last_report_;
  bool active_;
};

} // namespace wlt::hid
