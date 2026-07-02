#include "hid_report_descriptor.h"

#include <algorithm>
#include <cmath>
#include <string_view>

namespace wlt::hid {

namespace {

std::uint16_t map_normalized_to_u16(float normalized, std::uint16_t maximum) {
  const float clamped = std::clamp(normalized, 0.0F, 1.0F);
  return static_cast<std::uint16_t>(std::lround(clamped * static_cast<float>(maximum)));
}

std::int8_t map_tilt_to_i8(std::int16_t degrees) {
  return static_cast<std::int8_t>(std::clamp<std::int16_t>(degrees, -90, 90));
}

template <std::size_t Size>
void append_u16_le(
    std::array<std::uint8_t, Size>& output,
    std::size_t offset,
    std::uint16_t value) {
  output[offset] = static_cast<std::uint8_t>(value & 0xFF);
  output[offset + 1] = static_cast<std::uint8_t>((value >> 8) & 0xFF);
}

std::uint16_t read_u16_le(
    const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes,
    std::size_t offset) {
  return static_cast<std::uint16_t>(
      static_cast<std::uint16_t>(report_bytes[offset]) |
      (static_cast<std::uint16_t>(report_bytes[offset + 1]) << 8));
}

template <std::size_t Size>
void append_u32_le(
    std::array<std::uint8_t, Size>& output,
    std::size_t offset,
    std::uint32_t value) {
  output[offset] = static_cast<std::uint8_t>(value & 0xFF);
  output[offset + 1] = static_cast<std::uint8_t>((value >> 8) & 0xFF);
  output[offset + 2] = static_cast<std::uint8_t>((value >> 16) & 0xFF);
  output[offset + 3] = static_cast<std::uint8_t>((value >> 24) & 0xFF);
}

std::optional<HidStringResponse> make_utf16le_string_response(std::string_view value) {
  const std::size_t byte_count = (value.size() + 1) * 2;
  if (byte_count > kHidStringResponseMaxBytes) {
    return std::nullopt;
  }

  HidStringResponse response{
      .bytes = {},
      .byte_count = 0,
  };
  response.byte_count = (value.size() + 1) * 2;
  for (std::size_t index = 0; index < value.size(); ++index) {
    response.bytes[index * 2] = static_cast<std::uint8_t>(value[index]);
    response.bytes[(index * 2) + 1] = 0x00;
  }
  response.bytes[value.size() * 2] = 0x00;
  response.bytes[(value.size() * 2) + 1] = 0x00;
  return response;
}

} // namespace

std::array<std::uint8_t, kHidDescriptorSize> hid_descriptor() {
  return {
      static_cast<std::uint8_t>(kHidDescriptorSize),
      kHidDescriptorType,
      0x11,
      0x01,
      0x00,
      0x01,
      kHidReportDescriptorType,
      static_cast<std::uint8_t>(kPenReportDescriptorSize & 0xFF),
      static_cast<std::uint8_t>((kPenReportDescriptorSize >> 8) & 0xFF),
  };
}

bool is_valid_hid_descriptor(
    const std::array<std::uint8_t, kHidDescriptorSize>& descriptor) {
  return descriptor[0] == kHidDescriptorSize &&
      descriptor[1] == kHidDescriptorType &&
      descriptor[2] == 0x11 &&
      descriptor[3] == 0x01 &&
      descriptor[4] == 0x00 &&
      descriptor[5] == 0x01 &&
      descriptor[6] == kHidReportDescriptorType &&
      descriptor[7] == static_cast<std::uint8_t>(kPenReportDescriptorSize & 0xFF) &&
      descriptor[8] == static_cast<std::uint8_t>((kPenReportDescriptorSize >> 8) & 0xFF);
}

std::array<std::uint8_t, kHidDeviceAttributesSize> hid_device_attributes() {
  std::array<std::uint8_t, kHidDeviceAttributesSize> output{};
  append_u32_le(output, 0, static_cast<std::uint32_t>(kHidDeviceAttributesSize));
  append_u16_le(output, 4, kHidDevelopmentVendorId);
  append_u16_le(output, 6, kHidDevelopmentProductId);
  append_u16_le(output, 8, kHidDevelopmentVersionNumber);
  return output;
}

bool is_valid_hid_device_attributes(
    const std::array<std::uint8_t, kHidDeviceAttributesSize>& attributes) {
  if (attributes[0] != kHidDeviceAttributesSize ||
      attributes[1] != 0 ||
      attributes[2] != 0 ||
      attributes[3] != 0 ||
      attributes[4] != static_cast<std::uint8_t>(kHidDevelopmentVendorId & 0xFF) ||
      attributes[5] != static_cast<std::uint8_t>((kHidDevelopmentVendorId >> 8) & 0xFF) ||
      attributes[6] != static_cast<std::uint8_t>(kHidDevelopmentProductId & 0xFF) ||
      attributes[7] != static_cast<std::uint8_t>((kHidDevelopmentProductId >> 8) & 0xFF) ||
      attributes[8] != static_cast<std::uint8_t>(kHidDevelopmentVersionNumber & 0xFF) ||
      attributes[9] != static_cast<std::uint8_t>((kHidDevelopmentVersionNumber >> 8) & 0xFF)) {
    return false;
  }

  for (std::size_t index = 10; index < attributes.size(); ++index) {
    if (attributes[index] != 0) {
      return false;
    }
  }
  return true;
}

std::optional<HidStringResponse> hid_string_response(std::uint16_t string_id) {
  switch (string_id) {
    case kHidStringIdManufacturer:
      return make_utf16le_string_response("Windows Liquid Tablet");
    case kHidStringIdProduct:
      return make_utf16le_string_response("Windows Liquid Tablet Optional HID Pen");
    case kHidStringIdSerialNumber:
      return make_utf16le_string_response("WLT-HID-DEV-0001");
    default:
      return std::nullopt;
  }
}

bool is_valid_hid_string_response(const HidStringResponse& response) {
  if (response.byte_count < 2 ||
      response.byte_count > response.bytes.size() ||
      (response.byte_count % 2) != 0) {
    return false;
  }
  if (response.bytes[response.byte_count - 2] != 0x00 ||
      response.bytes[response.byte_count - 1] != 0x00) {
    return false;
  }

  for (std::size_t index = 1; index < response.byte_count; index += 2) {
    if (response.bytes[index] != 0x00) {
      return false;
    }
  }
  return true;
}

std::array<std::uint8_t, kPenReportDescriptorSize> pen_report_descriptor() {
  return {
      0x05, 0x0D,       // Usage Page (Digitizers)
      0x09, kPenTopLevelUsage, // Usage (External Pen)
      0xA1, 0x01,       // Collection (Application)
      0x85, kPenReportId, // Report ID (Pen)
      0x09, 0x20,       // Usage (Stylus)
      0xA1, 0x00,       // Collection (Physical)
      0x09, 0x42,       // Usage (Tip Switch)
      0x09, 0x44,       // Usage (Barrel Switch)
      0x09, 0x3C,       // Usage (Invert)
      0x09, 0x45,       // Usage (Eraser Switch)
      0x15, 0x00,       // Logical Minimum (0)
      0x25, 0x01,       // Logical Maximum (1)
      0x75, 0x01,       // Report Size (1)
      0x95, 0x04,       // Report Count (4)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0x95, 0x01,       // Report Count (1)
      0x81, 0x03,       // Input (Const,Var,Abs)
      0x09, 0x32,       // Usage (In Range)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0x95, 0x02,       // Report Count (2)
      0x81, 0x03,       // Input (Const,Var,Abs)
      0x05, 0x01,       // Usage Page (Generic Desktop)
      0x09, kReportFieldX, // Usage (X)
      0x75, 0x10,       // Report Size (16)
      0x95, 0x01,       // Report Count (1)
      0xA4,             // Push
      0x55, 0x0D,       // Unit Exponent (-3)
      0x65, 0x13,       // Unit (Inch, English Linear)
      0x35, 0x00,       // Physical Minimum (0)
      0x46, 0xFF, 0x7F, // Physical Maximum (32767)
      0x26, 0xFF, 0x7F, // Logical Maximum (32767)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0x09, kReportFieldY, // Usage (Y)
      0x46, 0xFF, 0x7F, // Physical Maximum (32767)
      0x26, 0xFF, 0x7F, // Logical Maximum (32767)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0xB4,             // Pop
      0x05, 0x0D,       // Usage Page (Digitizers)
      0x09, kReportFieldPressure, // Usage (Tip Pressure)
      0x26, 0xFF, 0x03, // Logical Maximum (1023)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0x75, 0x08,       // Report Size (8)
      0x09, kReportFieldXTilt, // Usage (X Tilt)
      0x09, kReportFieldYTilt, // Usage (Y Tilt)
      0x16, 0xA6, 0xFF, // Logical Minimum (-90)
      0x26, 0x5A, 0x00, // Logical Maximum (90)
      0x95, 0x02,       // Report Count (2)
      0x81, 0x02,       // Input (Data,Var,Abs)
      0xC0,             // End Collection
      0xC0,             // End Collection
  };
}

bool is_valid_pen_report_descriptor(
    const std::array<std::uint8_t, kPenReportDescriptorSize>& descriptor) {
  return descriptor[0] == 0x05 &&
      descriptor[1] == 0x0D &&
      descriptor[2] == 0x09 &&
      descriptor[3] == kPenTopLevelUsage &&
      descriptor[6] == 0x85 &&
      descriptor[7] == kPenReportId &&
      descriptor[12] == 0x09 &&
      descriptor[13] == 0x42 &&
      descriptor[14] == 0x09 &&
      descriptor[15] == 0x44 &&
      descriptor[16] == 0x09 &&
      descriptor[17] == 0x3C &&
      descriptor[18] == 0x09 &&
      descriptor[19] == 0x45 &&
      descriptor[26] == 0x95 &&
      descriptor[27] == 0x04 &&
      descriptor[34] == 0x09 &&
      descriptor[35] == 0x32 &&
      descriptor[38] == 0x95 &&
      descriptor[39] == 0x02 &&
      descriptor[44] == 0x09 &&
      descriptor[45] == kReportFieldX &&
      descriptor[48] == 0x95 &&
      descriptor[49] == 0x01 &&
      descriptor[50] == 0xA4 &&
      descriptor[51] == 0x55 &&
      descriptor[52] == 0x0D &&
      descriptor[53] == 0x65 &&
      descriptor[54] == 0x13 &&
      descriptor[55] == 0x35 &&
      descriptor[56] == 0x00 &&
      descriptor[57] == 0x46 &&
      descriptor[58] == 0xFF &&
      descriptor[59] == 0x7F &&
      descriptor[63] == 0x81 &&
      descriptor[64] == 0x02 &&
      descriptor[65] == 0x09 &&
      descriptor[66] == kReportFieldY &&
      descriptor[73] == 0x81 &&
      descriptor[74] == 0x02 &&
      descriptor[75] == 0xB4 &&
      descriptor[80] == 0x26 &&
      descriptor[81] == 0xFF &&
      descriptor[82] == 0x03 &&
      descriptor[91] == 0x16 &&
      descriptor[92] == 0xA6 &&
      descriptor[93] == 0xFF &&
      descriptor[94] == 0x26 &&
      descriptor[95] == 0x5A &&
      descriptor[96] == 0x00;
}

PenHidReport make_pen_hid_report(PenHidSample sample) {
  std::uint8_t buttons = 0;
  if (sample.tip_switch) {
    buttons |= kHidTipSwitchBit;
  }
  if (sample.in_range || sample.tip_switch) {
    buttons |= kHidInRangeBit;
  }

  return PenHidReport{
      .report_id = kPenReportId,
      .buttons = buttons,
      .x = map_normalized_to_u16(sample.x, kHidCoordinateMax),
      .y = map_normalized_to_u16(sample.y, kHidCoordinateMax),
      .pressure = map_normalized_to_u16(sample.tip_switch ? sample.pressure : 0.0F, kHidPressureMax),
      .tilt_x = map_tilt_to_i8(sample.tilt_x),
      .tilt_y = map_tilt_to_i8(sample.tilt_y),
  };
}

PenHidReport make_pen_hid_release_report(PenHidReport previous_report) {
  previous_report.buttons = 0;
  previous_report.pressure = 0;
  return previous_report;
}

bool is_valid_pen_hid_report(PenHidReport report) {
  if (report.report_id != kPenReportId) {
    return false;
  }
  if ((report.buttons & ~kHidKnownButtonBits) != 0) {
    return false;
  }

  const bool tip_switch = (report.buttons & kHidTipSwitchBit) != 0;
  const bool in_range = (report.buttons & kHidInRangeBit) != 0;
  if (tip_switch && !in_range) {
    return false;
  }
  if (!tip_switch && report.pressure != 0) {
    return false;
  }

  return report.x <= kHidCoordinateMax &&
      report.y <= kHidCoordinateMax &&
      report.pressure <= kHidPressureMax &&
      report.tilt_x >= -90 &&
      report.tilt_x <= 90 &&
      report.tilt_y >= -90 &&
      report.tilt_y <= 90;
}

std::array<std::uint8_t, kPenHidReportWireSize> serialize_pen_hid_report(
    PenHidReport report) {
  std::array<std::uint8_t, kPenHidReportWireSize> output{};
  output[0] = report.report_id;
  output[1] = report.buttons;
  append_u16_le(output, 2, report.x);
  append_u16_le(output, 4, report.y);
  append_u16_le(output, 6, report.pressure);
  output[8] = static_cast<std::uint8_t>(report.tilt_x);
  output[9] = static_cast<std::uint8_t>(report.tilt_y);
  return output;
}

std::optional<std::array<std::uint8_t, kPenHidReportWireSize>> serialize_valid_pen_hid_report(
    PenHidReport report) {
  if (!is_valid_pen_hid_report(report)) {
    return std::nullopt;
  }
  return serialize_pen_hid_report(report);
}

std::optional<PenHidReport> deserialize_pen_hid_report(
    const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes) {
  const PenHidReport report{
      .report_id = report_bytes[0],
      .buttons = report_bytes[1],
      .x = read_u16_le(report_bytes, 2),
      .y = read_u16_le(report_bytes, 4),
      .pressure = read_u16_le(report_bytes, 6),
      .tilt_x = static_cast<std::int8_t>(report_bytes[8]),
      .tilt_y = static_cast<std::int8_t>(report_bytes[9]),
  };

  if (!is_valid_pen_hid_report(report)) {
    return std::nullopt;
  }
  return report;
}

} // namespace wlt::hid
