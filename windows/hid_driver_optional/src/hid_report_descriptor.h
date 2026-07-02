#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace wlt::hid {

constexpr std::uint8_t kReportFieldX = 0x30;
constexpr std::uint8_t kReportFieldY = 0x31;
constexpr std::uint8_t kReportFieldPressure = 0x30;
constexpr std::uint8_t kReportFieldXTilt = 0x3D;
constexpr std::uint8_t kReportFieldYTilt = 0x3E;
constexpr std::uint8_t kPenTopLevelUsage = 0x01;
constexpr std::uint8_t kPenReportId = 0x02;
constexpr std::uint8_t kHidTipSwitchBit = 0x01;
constexpr std::uint8_t kHidBarrelSwitchBit = 0x02;
constexpr std::uint8_t kHidInvertBit = 0x04;
constexpr std::uint8_t kHidEraserBit = 0x08;
constexpr std::uint8_t kHidInRangeBit = 0x20;
constexpr std::uint8_t kHidKnownButtonBits =
    kHidTipSwitchBit | kHidBarrelSwitchBit | kHidInvertBit | kHidEraserBit | kHidInRangeBit;
constexpr std::uint16_t kHidCoordinateMax = 32767;
constexpr std::uint16_t kHidPressureMax = 1023;
constexpr std::uint8_t kHidDescriptorType = 0x21;
constexpr std::uint8_t kHidReportDescriptorType = 0x22;
constexpr std::size_t kHidDescriptorSize = 9;
constexpr std::size_t kHidDeviceAttributesSize = 32;
constexpr std::uint16_t kHidDevelopmentVendorId = 0xFFFE;
constexpr std::uint16_t kHidDevelopmentProductId = 0x574C;
constexpr std::uint16_t kHidDevelopmentVersionNumber = 0x0001;
constexpr std::size_t kPenReportDescriptorSize = 103;
constexpr std::size_t kHidStringResponseMaxBytes = kPenReportDescriptorSize;
constexpr std::size_t kPenHidReportWireSize = 10;
constexpr std::uint16_t kHidStringIdManufacturer = 14;
constexpr std::uint16_t kHidStringIdProduct = 15;
constexpr std::uint16_t kHidStringIdSerialNumber = 16;

struct PenHidSample {
  float x;
  float y;
  float pressure;
  std::int16_t tilt_x;
  std::int16_t tilt_y;
  bool tip_switch;
  bool in_range;
};

struct PenHidReport {
  std::uint8_t report_id;
  std::uint8_t buttons;
  std::uint16_t x;
  std::uint16_t y;
  std::uint16_t pressure;
  std::int8_t tilt_x;
  std::int8_t tilt_y;
};

struct HidStringResponse {
  std::array<std::uint8_t, kHidStringResponseMaxBytes> bytes;
  std::size_t byte_count;
};

// HID digitizer report fields: Tip Switch, Barrel, Invert, Eraser, In Range, X, Y, Pressure, X Tilt, Y Tilt.
std::array<std::uint8_t, kHidDescriptorSize> hid_descriptor();
bool is_valid_hid_descriptor(
    const std::array<std::uint8_t, kHidDescriptorSize>& descriptor);
std::array<std::uint8_t, kHidDeviceAttributesSize> hid_device_attributes();
bool is_valid_hid_device_attributes(
    const std::array<std::uint8_t, kHidDeviceAttributesSize>& attributes);
std::optional<HidStringResponse> hid_string_response(std::uint16_t string_id);
bool is_valid_hid_string_response(const HidStringResponse& response);
std::array<std::uint8_t, kPenReportDescriptorSize> pen_report_descriptor();
bool is_valid_pen_report_descriptor(
    const std::array<std::uint8_t, kPenReportDescriptorSize>& descriptor);
PenHidReport make_pen_hid_report(PenHidSample sample);
PenHidReport make_pen_hid_release_report(PenHidReport previous_report);
bool is_valid_pen_hid_report(PenHidReport report);
std::array<std::uint8_t, kPenHidReportWireSize> serialize_pen_hid_report(
    PenHidReport report);
std::optional<std::array<std::uint8_t, kPenHidReportWireSize>> serialize_valid_pen_hid_report(
    PenHidReport report);
std::optional<PenHidReport> deserialize_pen_hid_report(
    const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes);

} // namespace wlt::hid
