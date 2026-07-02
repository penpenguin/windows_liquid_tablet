#include "../src/hid_device_state.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  wlt::hid::HidDeviceState state;

  if (int code = expect(!state.is_active(), 20); code != 0) {
    return code;
  }
  state.activate();
  if (int code = expect(state.is_active(), 21); code != 0) {
    return code;
  }
  state.deactivate();
  if (int code = expect(!state.is_active(), 22); code != 0) {
    return code;
  }

  if (int code = expect(wlt::hid::is_valid_hid_descriptor(state.hid_descriptor()), 16);
      code != 0) {
    return code;
  }

  if (int code = expect(wlt::hid::is_valid_hid_device_attributes(state.device_attributes()), 17);
      code != 0) {
    return code;
  }

  const auto product_string = state.hid_string_response(wlt::hid::kHidStringIdProduct);
  if (int code = expect(product_string.has_value(), 18); code != 0) {
    return code;
  }
  if (int code = expect(wlt::hid::is_valid_hid_string_response(*product_string), 19);
      code != 0) {
    return code;
  }

  if (int code = expect(wlt::hid::is_valid_pen_report_descriptor(state.report_descriptor()), 1);
      code != 0) {
    return code;
  }

  if (int code = expect(state.last_report().report_id == wlt::hid::kPenReportId, 2);
      code != 0) {
    return code;
  }
  if (int code = expect(state.last_report().buttons == 0, 3); code != 0) {
    return code;
  }
  if (int code = expect(state.last_report().pressure == 0, 4); code != 0) {
    return code;
  }

  const auto contact = state.apply_sample(wlt::hid::PenHidSample{
      .x = 0.5F,
      .y = 0.25F,
      .pressure = 0.75F,
      .tilt_x = 12,
      .tilt_y = -24,
      .tip_switch = true,
      .in_range = true,
  });
  if (int code = expect(wlt::hid::is_valid_pen_hid_report(contact), 5); code != 0) {
    return code;
  }
  if (int code = expect(state.last_report().buttons ==
          (wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit), 6);
      code != 0) {
    return code;
  }
  if (int code = expect(state.last_report().pressure > 0, 7); code != 0) {
    return code;
  }

  const auto wire = state.serialized_last_report();
  if (int code = expect(wire[0] == wlt::hid::kPenReportId, 8); code != 0) {
    return code;
  }
  if (int code = expect(wire[1] == state.last_report().buttons, 9); code != 0) {
    return code;
  }

  const auto serialized_contact = wlt::hid::serialize_pen_hid_report(contact);
  state.release_contact();
  const auto serialized_update = state.apply_serialized_report(serialized_contact);
  if (int code = expect(serialized_update.has_value(), 23); code != 0) {
    return code;
  }
  if (int code = expect(state.last_report().x == contact.x, 24); code != 0) {
    return code;
  }
  if (int code = expect(state.serialized_last_report()[2] == serialized_contact[2], 25);
      code != 0) {
    return code;
  }

  const auto release = state.release_contact();
  if (int code = expect(release.buttons == 0, 10); code != 0) {
    return code;
  }
  if (int code = expect(release.pressure == 0, 11); code != 0) {
    return code;
  }
  if (int code = expect(release.x == contact.x, 12); code != 0) {
    return code;
  }
  if (int code = expect(release.y == contact.y, 13); code != 0) {
    return code;
  }

  const auto release_wire = state.serialized_last_report();
  if (int code = expect(release_wire[1] == 0, 14); code != 0) {
    return code;
  }
  if (int code = expect(release_wire[6] == 0 && release_wire[7] == 0, 15); code != 0) {
    return code;
  }

  return 0;
}
