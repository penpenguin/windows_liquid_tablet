#include "../src/hid_report_descriptor.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  const auto hid_descriptor = wlt::hid::hid_descriptor();
  if (int code = expect(wlt::hid::is_valid_hid_descriptor(hid_descriptor), 51); code != 0) {
    return code;
  }
  if (int code = expect(hid_descriptor[0] == wlt::hid::kHidDescriptorSize, 52); code != 0) {
    return code;
  }
  if (int code = expect(hid_descriptor[1] == wlt::hid::kHidDescriptorType, 53); code != 0) {
    return code;
  }
  if (int code = expect(hid_descriptor[6] == wlt::hid::kHidReportDescriptorType, 54); code != 0) {
    return code;
  }
  if (int code = expect(hid_descriptor[7] == wlt::hid::kPenReportDescriptorSize, 55); code != 0) {
    return code;
  }

  const auto attributes = wlt::hid::hid_device_attributes();
  if (int code = expect(wlt::hid::is_valid_hid_device_attributes(attributes), 56); code != 0) {
    return code;
  }
  if (int code = expect(attributes[0] == wlt::hid::kHidDeviceAttributesSize, 57); code != 0) {
    return code;
  }
  if (int code = expect(attributes[4] == 0xFE && attributes[5] == 0xFF, 58); code != 0) {
    return code;
  }
  if (int code = expect(attributes[6] == 0x4C && attributes[7] == 0x57, 59); code != 0) {
    return code;
  }
  if (int code = expect(attributes[8] == 0x01 && attributes[9] == 0x00, 60); code != 0) {
    return code;
  }

  const auto manufacturer = wlt::hid::hid_string_response(wlt::hid::kHidStringIdManufacturer);
  if (int code = expect(manufacturer.has_value(), 61); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_hid_string_response(*manufacturer), 62); code != 0) {
    return code;
  }
  if (int code = expect(manufacturer->bytes[0] == 'W' && manufacturer->bytes[1] == 0x00, 63);
      code != 0) {
    return code;
  }
  if (int code = expect(
          manufacturer->bytes[manufacturer->byte_count - 2] == 0x00 &&
              manufacturer->bytes[manufacturer->byte_count - 1] == 0x00,
          64);
      code != 0) {
    return code;
  }

  const auto product = wlt::hid::hid_string_response(wlt::hid::kHidStringIdProduct);
  if (int code = expect(product.has_value(), 65); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_hid_string_response(*product), 66); code != 0) {
    return code;
  }
  if (int code = expect(product->bytes[0] == 'W' && product->bytes[1] == 0x00, 67);
      code != 0) {
    return code;
  }

  const auto serial = wlt::hid::hid_string_response(wlt::hid::kHidStringIdSerialNumber);
  if (int code = expect(serial.has_value(), 68); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_hid_string_response(*serial), 69); code != 0) {
    return code;
  }
  if (int code = expect(serial->bytes[0] == 'W' && serial->bytes[1] == 0x00, 70);
      code != 0) {
    return code;
  }
  if (int code = expect(!wlt::hid::hid_string_response(0xFFFF).has_value(), 71); code != 0) {
    return code;
  }

  const auto descriptor = wlt::hid::pen_report_descriptor();

  if (int code = expect(descriptor.size() > 0, 1); code != 0) {
    return code;
  }
  if (int code = expect(descriptor.size() == wlt::hid::kPenReportDescriptorSize, 42); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_pen_report_descriptor(descriptor), 38); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[0] == 0x05 && descriptor[1] == 0x0D, 39); code != 0) {
    return code;
  }
  if (int code = expect(
          descriptor[2] == 0x09 && descriptor[3] == wlt::hid::kPenTopLevelUsage,
          82);
      code != 0) {
    return code;
  }
  if (int code = expect(descriptor[6] == 0x85 && descriptor[7] == wlt::hid::kPenReportId, 40); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kPenReportId == 0x02, 94); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[12] == 0x09 && descriptor[13] == 0x42, 83); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[14] == 0x09 && descriptor[15] == 0x44, 84); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[16] == 0x09 && descriptor[17] == 0x3C, 85); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[18] == 0x09 && descriptor[19] == 0x45, 86); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[26] == 0x95 && descriptor[27] == 0x04, 87); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[34] == 0x09 && descriptor[35] == 0x32, 88); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[38] == 0x95 && descriptor[39] == 0x02, 89); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[44] == 0x09 && descriptor[45] == wlt::hid::kReportFieldX, 95);
      code != 0) {
    return code;
  }
  if (int code = expect(descriptor[48] == 0x95 && descriptor[49] == 0x01, 96); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[63] == 0x81 && descriptor[64] == 0x02, 97); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[65] == 0x09 && descriptor[66] == wlt::hid::kReportFieldY, 98);
      code != 0) {
    return code;
  }
  if (int code = expect(descriptor[73] == 0x81 && descriptor[74] == 0x02, 99); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[75] == 0xB4, 81); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[50] == 0xA4, 76); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[51] == 0x55 && descriptor[52] == 0x0D, 77); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[53] == 0x65 && descriptor[54] == 0x13, 78); code != 0) {
    return code;
  }
  if (int code = expect(descriptor[55] == 0x35 && descriptor[56] == 0x00, 79); code != 0) {
    return code;
  }
  if (int code = expect(
          descriptor[57] == 0x46 && descriptor[58] == 0xFF && descriptor[59] == 0x7F,
          80);
      code != 0) {
    return code;
  }
  auto invalid_descriptor = descriptor;
  invalid_descriptor[7] = 0x01;
  if (int code = expect(!wlt::hid::is_valid_pen_report_descriptor(invalid_descriptor), 41); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kReportFieldX == 0x30, 2); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kReportFieldY == 0x31, 3); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kReportFieldPressure == 0x30, 4); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kReportFieldXTilt == 0x3D, 5); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kReportFieldYTilt == 0x3E, 6); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kHidBarrelSwitchBit == 0x02, 90); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kHidInvertBit == 0x04, 91); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kHidEraserBit == 0x08, 92); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::kHidInRangeBit == 0x20, 93); code != 0) {
    return code;
  }

  const auto clamped_report = wlt::hid::make_pen_hid_report(wlt::hid::PenHidSample{
      .x = 0.5F,
      .y = 1.2F,
      .pressure = 0.5F,
      .tilt_x = 120,
      .tilt_y = -120,
      .tip_switch = true,
      .in_range = true,
  });
  if (int code = expect(clamped_report.report_id == wlt::hid::kPenReportId, 7); code != 0) {
    return code;
  }
  if (int code = expect(
          clamped_report.buttons == (wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit),
          8);
      code != 0) {
    return code;
  }
  if (int code = expect(clamped_report.x == 16384, 9); code != 0) {
    return code;
  }
  if (int code = expect(clamped_report.y == 32767, 10); code != 0) {
    return code;
  }
  if (int code = expect(clamped_report.pressure == 512, 11); code != 0) {
    return code;
  }
  if (int code = expect(clamped_report.tilt_x == 90, 12); code != 0) {
    return code;
  }
  if (int code = expect(clamped_report.tilt_y == -90, 13); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_pen_hid_report(clamped_report), 28); code != 0) {
    return code;
  }

  const auto clamped_wire = wlt::hid::serialize_pen_hid_report(clamped_report);
  if (int code = expect(clamped_wire.size() == wlt::hid::kPenHidReportWireSize, 17); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[0] == wlt::hid::kPenReportId, 18); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[1] == clamped_report.buttons, 19); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[2] == 0x00 && clamped_wire[3] == 0x40, 20); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[4] == 0xFF && clamped_wire[5] == 0x7F, 21); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[6] == 0x00 && clamped_wire[7] == 0x02, 22); code != 0) {
    return code;
  }
  if (int code = expect(clamped_wire[8] == 90, 23); code != 0) {
    return code;
  }
  if (int code = expect(static_cast<std::int8_t>(clamped_wire[9]) == -90, 24); code != 0) {
    return code;
  }
  const auto decoded_report = wlt::hid::deserialize_pen_hid_report(clamped_wire);
  if (int code = expect(decoded_report.has_value(), 72); code != 0) {
    return code;
  }
  if (int code = expect(decoded_report->x == clamped_report.x, 73); code != 0) {
    return code;
  }
  if (int code = expect(decoded_report->pressure == clamped_report.pressure, 74); code != 0) {
    return code;
  }
  auto invalid_wire = clamped_wire;
  invalid_wire[0] = 0x01;
  if (int code = expect(!wlt::hid::deserialize_pen_hid_report(invalid_wire).has_value(), 75);
      code != 0) {
    return code;
  }
  const auto checked_clamped_wire = wlt::hid::serialize_valid_pen_hid_report(clamped_report);
  if (int code = expect(checked_clamped_wire.has_value(), 35); code != 0) {
    return code;
  }
  if (int code = expect((*checked_clamped_wire)[0] == wlt::hid::kPenReportId, 36); code != 0) {
    return code;
  }

  const auto released_report = wlt::hid::make_pen_hid_report(wlt::hid::PenHidSample{
      .x = -0.25F,
      .y = 0.0F,
      .pressure = -1.0F,
      .tilt_x = 0,
      .tilt_y = 0,
      .tip_switch = false,
      .in_range = false,
  });
  if (int code = expect(released_report.buttons == 0, 14); code != 0) {
    return code;
  }
  if (int code = expect(released_report.x == 0, 15); code != 0) {
    return code;
  }
  if (int code = expect(released_report.pressure == 0, 16); code != 0) {
    return code;
  }

  const auto contact_without_range = wlt::hid::make_pen_hid_report(wlt::hid::PenHidSample{
      .x = 0.25F,
      .y = 0.25F,
      .pressure = 0.25F,
      .tilt_x = 0,
      .tilt_y = 0,
      .tip_switch = true,
      .in_range = false,
  });
  if (int code = expect(
          contact_without_range.buttons == (wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit),
          25);
      code != 0) {
    return code;
  }

  const auto hover_report = wlt::hid::make_pen_hid_report(wlt::hid::PenHidSample{
      .x = 0.25F,
      .y = 0.25F,
      .pressure = 1.0F,
      .tilt_x = 0,
      .tilt_y = 0,
      .tip_switch = false,
      .in_range = true,
  });
  if (int code = expect(hover_report.buttons == wlt::hid::kHidInRangeBit, 26); code != 0) {
    return code;
  }
  if (int code = expect(hover_report.pressure == 0, 27); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_pen_hid_report(hover_report), 29); code != 0) {
    return code;
  }

  if (int code = expect(!wlt::hid::is_valid_pen_hid_report(wlt::hid::PenHidReport{
          .report_id = 1,
          .buttons = wlt::hid::kHidInRangeBit,
          .x = 0,
          .y = 0,
          .pressure = 0,
          .tilt_x = 0,
          .tilt_y = 0,
      }), 30); code != 0) {
    return code;
  }

  if (int code = expect(!wlt::hid::is_valid_pen_hid_report(wlt::hid::PenHidReport{
          .report_id = wlt::hid::kPenReportId,
          .buttons = 0x80,
          .x = 0,
          .y = 0,
          .pressure = 0,
          .tilt_x = 0,
          .tilt_y = 0,
      }), 31); code != 0) {
    return code;
  }

  if (int code = expect(!wlt::hid::is_valid_pen_hid_report(wlt::hid::PenHidReport{
          .report_id = wlt::hid::kPenReportId,
          .buttons = wlt::hid::kHidTipSwitchBit,
          .x = 0,
          .y = 0,
          .pressure = 1,
          .tilt_x = 0,
          .tilt_y = 0,
      }), 32); code != 0) {
    return code;
  }

  if (int code = expect(!wlt::hid::is_valid_pen_hid_report(wlt::hid::PenHidReport{
          .report_id = wlt::hid::kPenReportId,
          .buttons = wlt::hid::kHidInRangeBit,
          .x = 0,
          .y = 0,
          .pressure = 1,
          .tilt_x = 0,
          .tilt_y = 0,
      }), 33); code != 0) {
    return code;
  }

  if (int code = expect(!wlt::hid::is_valid_pen_hid_report(wlt::hid::PenHidReport{
          .report_id = wlt::hid::kPenReportId,
          .buttons = wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit,
          .x = 40000,
          .y = 0,
          .pressure = 1,
          .tilt_x = 0,
          .tilt_y = 0,
      }), 34); code != 0) {
    return code;
  }

  const auto rejected_wire = wlt::hid::serialize_valid_pen_hid_report(wlt::hid::PenHidReport{
      .report_id = 1,
      .buttons = wlt::hid::kHidInRangeBit,
      .x = 0,
      .y = 0,
      .pressure = 0,
      .tilt_x = 0,
      .tilt_y = 0,
  });
  if (int code = expect(!rejected_wire.has_value(), 37); code != 0) {
    return code;
  }

  const auto release_report = wlt::hid::make_pen_hid_release_report(clamped_report);
  if (int code = expect(release_report.buttons == 0, 43); code != 0) {
    return code;
  }
  if (int code = expect(release_report.pressure == 0, 44); code != 0) {
    return code;
  }
  if (int code = expect(release_report.x == clamped_report.x, 45); code != 0) {
    return code;
  }
  if (int code = expect(release_report.y == clamped_report.y, 46); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_pen_hid_report(release_report), 47); code != 0) {
    return code;
  }
  const auto release_wire = wlt::hid::serialize_valid_pen_hid_report(release_report);
  if (int code = expect(release_wire.has_value(), 48); code != 0) {
    return code;
  }
  if (int code = expect((*release_wire)[1] == 0, 49); code != 0) {
    return code;
  }
  if (int code = expect((*release_wire)[6] == 0x00 && (*release_wire)[7] == 0x00, 50); code != 0) {
    return code;
  }

  return 0;
}
