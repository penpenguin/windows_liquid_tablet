#pragma once

#include "hid_device_state.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace wlt::hid {

enum class HidRequestKind {
  Activate,
  Deactivate,
  DeviceDescriptor,
  DeviceAttributes,
  String,
  ReportDescriptor,
  InputReport,
  ApplySerializedReport,
  ApplySample,
  ReleaseContact,
};

struct HidRequest {
  HidRequestKind kind;
  std::uint16_t string_id;
  PenHidSample sample;
  std::array<std::uint8_t, kPenHidReportWireSize> report_bytes;
};

struct HidRequestResponse {
  std::array<std::uint8_t, kPenReportDescriptorSize> bytes;
  std::size_t byte_count;
  PenHidReport report;
  bool active;
  bool accepted;
};

HidRequestResponse handle_hid_device_request(
    HidDeviceState& state,
    HidRequest request);

} // namespace wlt::hid
