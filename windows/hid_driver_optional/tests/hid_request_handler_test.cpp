#include "../src/hid_request_handler.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

wlt::hid::HidRequest request(wlt::hid::HidRequestKind kind) {
  return wlt::hid::HidRequest{
      .kind = kind,
      .sample = wlt::hid::PenHidSample{
          .x = 0.0F,
          .y = 0.0F,
          .pressure = 0.0F,
          .tilt_x = 0,
          .tilt_y = 0,
          .tip_switch = false,
          .in_range = false,
      },
  };
}

} // namespace

int main() {
  wlt::hid::HidDeviceState state;

  const auto activate_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::Activate));
  if (int code = expect(activate_response.byte_count == 0, 25); code != 0) {
    return code;
  }
  if (int code = expect(activate_response.active, 26); code != 0) {
    return code;
  }
  if (int code = expect(state.is_active(), 27); code != 0) {
    return code;
  }

  const auto deactivate_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::Deactivate));
  if (int code = expect(deactivate_response.byte_count == 0, 28); code != 0) {
    return code;
  }
  if (int code = expect(!deactivate_response.active, 29); code != 0) {
    return code;
  }
  if (int code = expect(!state.is_active(), 30); code != 0) {
    return code;
  }

  const auto device_descriptor_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::DeviceDescriptor));
  if (int code = expect(device_descriptor_response.byte_count == wlt::hid::kHidDescriptorSize, 15);
      code != 0) {
    return code;
  }
  if (int code = expect(device_descriptor_response.bytes[1] == wlt::hid::kHidDescriptorType, 16);
      code != 0) {
    return code;
  }
  if (int code = expect(
          device_descriptor_response.bytes[6] == wlt::hid::kHidReportDescriptorType, 17);
      code != 0) {
    return code;
  }

  const auto attributes_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::DeviceAttributes));
  if (int code = expect(attributes_response.byte_count == wlt::hid::kHidDeviceAttributesSize, 18);
      code != 0) {
    return code;
  }
  if (int code = expect(attributes_response.bytes[4] == 0xFE && attributes_response.bytes[5] == 0xFF, 19);
      code != 0) {
    return code;
  }
  if (int code = expect(attributes_response.bytes[6] == 0x4C && attributes_response.bytes[7] == 0x57, 20);
      code != 0) {
    return code;
  }
  if (int code = expect(attributes_response.bytes[8] == 0x01 && attributes_response.bytes[9] == 0x00, 21);
      code != 0) {
    return code;
  }

  auto string_request = request(wlt::hid::HidRequestKind::String);
  string_request.string_id = wlt::hid::kHidStringIdProduct;
  const auto string_response = wlt::hid::handle_hid_device_request(state, string_request);
  if (int code = expect(string_response.byte_count > 0, 22); code != 0) {
    return code;
  }
  if (int code = expect(string_response.bytes[0] == 'W' && string_response.bytes[1] == 0x00, 23);
      code != 0) {
    return code;
  }
  if (int code = expect(
          string_response.bytes[string_response.byte_count - 2] == 0x00 &&
              string_response.bytes[string_response.byte_count - 1] == 0x00,
          24);
      code != 0) {
    return code;
  }

  const auto descriptor_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::ReportDescriptor));
  if (int code = expect(descriptor_response.byte_count == wlt::hid::kPenReportDescriptorSize, 1);
      code != 0) {
    return code;
  }
  if (int code = expect(descriptor_response.bytes[0] == 0x05, 2); code != 0) {
    return code;
  }
  if (int code = expect(descriptor_response.bytes[1] == 0x0D, 3); code != 0) {
    return code;
  }

  const auto report_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::InputReport));
  if (int code = expect(report_response.byte_count == wlt::hid::kPenHidReportWireSize, 4);
      code != 0) {
    return code;
  }
  if (int code = expect(report_response.bytes[0] == wlt::hid::kPenReportId, 5); code != 0) {
    return code;
  }
  if (int code = expect(report_response.bytes[1] == 0, 6); code != 0) {
    return code;
  }

  auto sample_request = request(wlt::hid::HidRequestKind::ApplySample);
  sample_request.sample = wlt::hid::PenHidSample{
      .x = 0.5F,
      .y = 0.5F,
      .pressure = 0.5F,
      .tilt_x = 8,
      .tilt_y = -8,
      .tip_switch = true,
      .in_range = true,
  };
  const auto apply_response = wlt::hid::handle_hid_device_request(state, sample_request);
  if (int code = expect(apply_response.byte_count == wlt::hid::kPenHidReportWireSize, 7);
      code != 0) {
    return code;
  }
  if (int code = expect(apply_response.report.buttons ==
          (wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit), 8);
      code != 0) {
    return code;
  }
  if (int code = expect(apply_response.bytes[1] == apply_response.report.buttons, 9);
      code != 0) {
    return code;
  }

  const auto serialized_contact = wlt::hid::make_pen_hid_report(wlt::hid::PenHidSample{
      .x = 0.25F,
      .y = 0.75F,
      .pressure = 0.60F,
      .tilt_x = 16,
      .tilt_y = -16,
      .tip_switch = true,
      .in_range = true,
  });
  auto serialized_request = request(wlt::hid::HidRequestKind::ApplySerializedReport);
  serialized_request.report_bytes = wlt::hid::serialize_pen_hid_report(serialized_contact);
  const auto serialized_response = wlt::hid::handle_hid_device_request(state, serialized_request);
  if (int code = expect(serialized_response.accepted, 31); code != 0) {
    return code;
  }
  if (int code = expect(serialized_response.byte_count == 0, 32); code != 0) {
    return code;
  }
  const auto updated_report_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::InputReport));
  if (int code = expect(updated_report_response.bytes[2] == serialized_request.report_bytes[2], 33);
      code != 0) {
    return code;
  }
  if (int code = expect(updated_report_response.bytes[6] == serialized_request.report_bytes[6], 34);
      code != 0) {
    return code;
  }

  const auto release_response = wlt::hid::handle_hid_device_request(
      state,
      request(wlt::hid::HidRequestKind::ReleaseContact));
  if (int code = expect(release_response.byte_count == wlt::hid::kPenHidReportWireSize, 10);
      code != 0) {
    return code;
  }
  if (int code = expect(release_response.report.buttons == 0, 11); code != 0) {
    return code;
  }
  if (int code = expect(release_response.report.pressure == 0, 12); code != 0) {
    return code;
  }
  if (int code = expect(release_response.bytes[1] == 0, 13); code != 0) {
    return code;
  }
  if (int code = expect(release_response.bytes[6] == 0 && release_response.bytes[7] == 0, 14);
      code != 0) {
    return code;
  }

  return 0;
}
