#include "input/hid_device_path_list.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::input::HidDeviceAttributes;
  using wlt::host::input::HidDevicePathEntry;
  using wlt::host::input::kWindowsLiquidTabletHidProductId;
  using wlt::host::input::kWindowsLiquidTabletHidVendorId;
  using wlt::host::input::kWindowsLiquidTabletHidVersionNumber;
  using wlt::host::input::select_windows_liquid_tablet_hid_device_path;

  const HidDevicePathEntry without_attributes{.device_path = L"\\\\?\\hid#unknown"};
  if (int code = expect(!without_attributes.is_windows_liquid_tablet_optional_hid(), 1);
      code != 0) {
    return code;
  }

  const HidDevicePathEntry matching{
      .device_path = L"\\\\?\\hid#vid_fffe&pid_574c#dev",
      .attributes = HidDeviceAttributes{
          .vendor_id = kWindowsLiquidTabletHidVendorId,
          .product_id = kWindowsLiquidTabletHidProductId,
          .version_number = kWindowsLiquidTabletHidVersionNumber,
      },
  };
  if (int code = expect(matching.is_windows_liquid_tablet_optional_hid(), 2); code != 0) {
    return code;
  }

  const HidDevicePathEntry wrong_product{
      .device_path = L"\\\\?\\hid#vid_fffe&pid_0001#dev",
      .attributes = HidDeviceAttributes{
          .vendor_id = kWindowsLiquidTabletHidVendorId,
          .product_id = 0x0001,
          .version_number = kWindowsLiquidTabletHidVersionNumber,
      },
  };
  if (int code = expect(!wrong_product.is_windows_liquid_tablet_optional_hid(), 3); code != 0) {
    return code;
  }

  const auto selected = select_windows_liquid_tablet_hid_device_path({
      without_attributes,
      wrong_product,
      matching,
  });
  if (int code = expect(selected.has_value(), 4); code != 0) {
    return code;
  }
  if (int code = expect(selected == matching.device_path, 5); code != 0) {
    return code;
  }

  const auto empty_selection = select_windows_liquid_tablet_hid_device_path({
      without_attributes,
      wrong_product,
  });
  if (int code = expect(!empty_selection.has_value(), 6); code != 0) {
    return code;
  }

  return 0;
}
