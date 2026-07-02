#include "input/hid_device_path_list.h"

#ifndef _WIN32
#error hid_device_path_list_win32.cpp must only be built on Windows.
#endif

#include <windows.h>

#include <hidsdi.h>
#include <setupapi.h>

#include <cstdlib>
#include <memory>
#include <optional>
#include <vector>

namespace wlt::host::input {
namespace {

class DeviceInfoSet final {
public:
  explicit DeviceInfoSet(HDEVINFO handle) : handle_(handle) {}

  ~DeviceInfoSet() {
    if (handle_ != INVALID_HANDLE_VALUE) {
      SetupDiDestroyDeviceInfoList(handle_);
    }
  }

  DeviceInfoSet(const DeviceInfoSet&) = delete;
  DeviceInfoSet& operator=(const DeviceInfoSet&) = delete;

  HDEVINFO get() const {
    return handle_;
  }

private:
  HDEVINFO handle_ = INVALID_HANDLE_VALUE;
};

class DeviceHandle final {
public:
  explicit DeviceHandle(HANDLE handle) : handle_(handle) {}

  ~DeviceHandle() {
    if (handle_ != INVALID_HANDLE_VALUE) {
      CloseHandle(handle_);
    }
  }

  DeviceHandle(const DeviceHandle&) = delete;
  DeviceHandle& operator=(const DeviceHandle&) = delete;

  HANDLE get() const {
    return handle_;
  }

private:
  HANDLE handle_ = INVALID_HANDLE_VALUE;
};

std::optional<HidDeviceAttributes> read_hid_device_attributes(const wchar_t* device_path) {
  DeviceHandle device(CreateFileW(
      device_path,
      0,
      FILE_SHARE_READ | FILE_SHARE_WRITE,
      nullptr,
      OPEN_EXISTING,
      FILE_ATTRIBUTE_NORMAL,
      nullptr));
  if (device.get() == INVALID_HANDLE_VALUE) {
    return std::nullopt;
  }

  HIDD_ATTRIBUTES attributes{};
  attributes.Size = sizeof(HIDD_ATTRIBUTES);
  if (HidD_GetAttributes(device.get(), &attributes) == FALSE) {
    return std::nullopt;
  }

  return HidDeviceAttributes{
      .vendor_id = attributes.VendorID,
      .product_id = attributes.ProductID,
      .version_number = attributes.VersionNumber,
  };
}

} // namespace

std::vector<HidDevicePathEntry> list_win32_hid_device_paths() {
  GUID hid_guid{};
  HidD_GetHidGuid(&hid_guid);

  DeviceInfoSet device_info(SetupDiGetClassDevsW(
      &hid_guid,
      nullptr,
      nullptr,
      DIGCF_DEVICEINTERFACE | DIGCF_PRESENT));
  if (device_info.get() == INVALID_HANDLE_VALUE) {
    return {};
  }

  std::vector<HidDevicePathEntry> entries;
  for (DWORD index = 0;; ++index) {
    SP_DEVICE_INTERFACE_DATA interface_data{};
    interface_data.cbSize = sizeof(interface_data);
    if (SetupDiEnumDeviceInterfaces(
            device_info.get(),
            nullptr,
            &hid_guid,
            index,
            &interface_data) == FALSE) {
      break;
    }

    DWORD required_size = 0;
    SetupDiGetDeviceInterfaceDetailW(
        device_info.get(),
        &interface_data,
        nullptr,
        0,
        &required_size,
        nullptr);
    if (required_size == 0) {
      continue;
    }

    std::unique_ptr<void, decltype(&std::free)> detail_storage(
        std::malloc(required_size),
        std::free);
    if (!detail_storage) {
      continue;
    }

    auto* detail_data = static_cast<SP_DEVICE_INTERFACE_DETAIL_DATA_W*>(
        detail_storage.get());
    detail_data->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W);

    if (SetupDiGetDeviceInterfaceDetailW(
            device_info.get(),
            &interface_data,
            detail_data,
            required_size,
            nullptr,
            nullptr) == FALSE) {
      continue;
    }

    entries.push_back(HidDevicePathEntry{
        .device_path = detail_data->DevicePath,
        .attributes = read_hid_device_attributes(detail_data->DevicePath),
    });
  }

  return entries;
}

} // namespace wlt::host::input
