// Optional UMDF HID minidriver skeleton. This is not part of the default MVP.

#include "hid_request_handler.h"

#include <windows.h>
#include <hidclass.h>
#include <wudfwdm.h>
#include <wdf.h>

#include <cstdint>
#include <new>

#ifndef IOCTL_HID_GET_DEVICE_DESCRIPTOR
#define IOCTL_HID_GET_DEVICE_DESCRIPTOR HID_CTL_CODE(0)
#define IOCTL_HID_GET_REPORT_DESCRIPTOR HID_CTL_CODE(1)
#define IOCTL_HID_READ_REPORT HID_CTL_CODE(2)
#define IOCTL_HID_GET_STRING HID_CTL_CODE(4)
#define IOCTL_HID_ACTIVATE_DEVICE HID_CTL_CODE(7)
#define IOCTL_HID_DEACTIVATE_DEVICE HID_CTL_CODE(8)
#define IOCTL_HID_GET_DEVICE_ATTRIBUTES HID_CTL_CODE(9)
#define IOCTL_HID_SEND_IDLE_NOTIFICATION_REQUEST HID_CTL_CODE(10)
#define IOCTL_UMDF_HID_GET_INPUT_REPORT HID_CTL_CODE(23)
#endif

extern "C" DRIVER_INITIALIZE DriverEntry;

namespace {

constexpr ULONG kWindowsLiquidTabletHidApplyReportIoctl =
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_WRITE_DATA);

struct HidDeviceContext {
  wlt::hid::HidDeviceState state;
  WDFQUEUE manual_queue = nullptr;
};

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(HidDeviceContext, WindowsLiquidTabletHidGetContext)

void WindowsLiquidTabletHidCompleteBytes(
    WDFREQUEST request,
    const wlt::hid::HidRequestResponse& response) {
  WDFMEMORY output_memory = nullptr;
  NTSTATUS status = WdfRequestRetrieveOutputMemory(request, &output_memory);
  if (!NT_SUCCESS(status)) {
    WdfRequestComplete(request, status);
    return;
  }

  size_t output_buffer_length = 0;
  (void)WdfMemoryGetBuffer(output_memory, &output_buffer_length);
  if (output_buffer_length < response.byte_count) {
    WdfRequestComplete(request, STATUS_BUFFER_TOO_SMALL);
    return;
  }

  status = WdfMemoryCopyFromBuffer(
      output_memory,
      0,
      const_cast<std::uint8_t*>(response.bytes.data()),
      response.byte_count);
  if (!NT_SUCCESS(status)) {
    WdfRequestComplete(request, status);
    return;
  }

  WdfRequestSetInformation(request, response.byte_count);
  WdfRequestComplete(request, STATUS_SUCCESS);
}

void WindowsLiquidTabletHidCompleteEmpty(WDFREQUEST request) {
  WdfRequestCompleteWithInformation(request, STATUS_SUCCESS, 0);
}

void WindowsLiquidTabletHidCompleteNextPendingRead(HidDeviceContext* context) {
  WDFREQUEST pending_read = nullptr;
  NTSTATUS status = WdfIoQueueRetrieveNextRequest(context->manual_queue, &pending_read);
  if (!NT_SUCCESS(status)) {
    return;
  }

  const auto response = wlt::hid::handle_hid_device_request(context->state,
      wlt::hid::HidRequest{
          .kind = wlt::hid::HidRequestKind::InputReport,
          .sample = {},
      });
  WindowsLiquidTabletHidCompleteBytes(pending_read, response);
}

bool WindowsLiquidTabletHidTryGetStringId(
    WDFREQUEST request,
    std::uint16_t* string_id) {
  void* input_buffer = nullptr;
  NTSTATUS status = WdfRequestRetrieveInputBuffer(
      request,
      sizeof(ULONG),
      &input_buffer,
      nullptr);
  if (!NT_SUCCESS(status)) {
    return false;
  }

  const ULONG composite_string_id = *static_cast<ULONG*>(input_buffer);
  *string_id = static_cast<std::uint16_t>(composite_string_id & 0xFFFFU);
  return true;
}

bool WindowsLiquidTabletHidTryGetHostReportBytes(
    WDFREQUEST request,
    std::array<std::uint8_t, wlt::hid::kPenHidReportWireSize>* report_bytes) {
  void* input_buffer = nullptr;
  NTSTATUS status = WdfRequestRetrieveInputBuffer(
      request,
      wlt::hid::kPenHidReportWireSize,
      &input_buffer,
      nullptr);
  if (!NT_SUCCESS(status)) {
    return false;
  }

  const auto* bytes = static_cast<const std::uint8_t*>(input_buffer);
  for (std::size_t index = 0; index < report_bytes->size(); ++index) {
    (*report_bytes)[index] = bytes[index];
  }
  return true;
}

void WindowsLiquidTabletHidHandleHidIoctl(
    WDFQUEUE queue,
    WDFREQUEST request,
    size_t output_buffer_length,
    size_t input_buffer_length,
    ULONG io_control_code);

void WindowsLiquidTabletHidEvtIoDeviceControl(
    WDFQUEUE queue,
    WDFREQUEST request,
    size_t output_buffer_length,
    size_t input_buffer_length,
    ULONG io_control_code) {
  WDFDEVICE device = WdfIoQueueGetDevice(queue);
  auto* context = WindowsLiquidTabletHidGetContext(device);

  switch (io_control_code) {
    case kWindowsLiquidTabletHidApplyReportIoctl: {
      std::array<std::uint8_t, wlt::hid::kPenHidReportWireSize> report_bytes{};
      if (!WindowsLiquidTabletHidTryGetHostReportBytes(request, &report_bytes)) {
        WdfRequestComplete(request, STATUS_INVALID_PARAMETER);
        return;
      }

      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::ApplySerializedReport,
              .sample = {},
              .report_bytes = report_bytes,
          });
      if (!response.accepted) {
        WdfRequestComplete(request, STATUS_INVALID_PARAMETER);
        return;
      }
      WindowsLiquidTabletHidCompleteNextPendingRead(context);
      WindowsLiquidTabletHidCompleteEmpty(request);
      return;
    }
    default:
      WindowsLiquidTabletHidHandleHidIoctl(queue, request, output_buffer_length, input_buffer_length, io_control_code);
      return;
  }
}

void WindowsLiquidTabletHidHandleHidIoctl(
    WDFQUEUE queue,
    WDFREQUEST request,
    size_t output_buffer_length,
    size_t input_buffer_length,
    ULONG io_control_code) {
  UNREFERENCED_PARAMETER(output_buffer_length);
  UNREFERENCED_PARAMETER(input_buffer_length);

  WDFDEVICE device = WdfIoQueueGetDevice(queue);
  auto* context = WindowsLiquidTabletHidGetContext(device);

  switch (io_control_code) {
    case IOCTL_HID_ACTIVATE_DEVICE: {
      (void)wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::Activate,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteEmpty(request);
      return;
    }
    case IOCTL_HID_DEACTIVATE_DEVICE: {
      (void)wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::Deactivate,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteEmpty(request);
      return;
    }
    case IOCTL_HID_GET_DEVICE_DESCRIPTOR: {
      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::DeviceDescriptor,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteBytes(request, response);
      return;
    }
    case IOCTL_HID_GET_DEVICE_ATTRIBUTES: {
      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::DeviceAttributes,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteBytes(request, response);
      return;
    }
    case IOCTL_HID_GET_STRING: {
      std::uint16_t string_id = 0;
      if (!WindowsLiquidTabletHidTryGetStringId(request, &string_id)) {
        WdfRequestComplete(request, STATUS_INVALID_PARAMETER);
        return;
      }

      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::String,
              .string_id = string_id,
              .sample = {},
          });
      if (response.byte_count == 0) {
        WdfRequestComplete(request, STATUS_NOT_SUPPORTED);
        return;
      }
      WindowsLiquidTabletHidCompleteBytes(request, response);
      return;
    }
    case IOCTL_HID_GET_REPORT_DESCRIPTOR: {
      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::ReportDescriptor,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteBytes(request, response);
      return;
    }
    case IOCTL_HID_READ_REPORT: {
      const NTSTATUS status = WdfRequestForwardToIoQueue(request, context->manual_queue);
      if (!NT_SUCCESS(status)) {
        WdfRequestComplete(request, status);
      }
      return;
    }
    case IOCTL_UMDF_HID_GET_INPUT_REPORT: {
      const auto response = wlt::hid::handle_hid_device_request(context->state,
          wlt::hid::HidRequest{
              .kind = wlt::hid::HidRequestKind::InputReport,
              .sample = {},
          });
      WindowsLiquidTabletHidCompleteBytes(request, response);
      return;
    }
    case IOCTL_GET_PHYSICAL_DESCRIPTOR:
    case IOCTL_HID_SEND_IDLE_NOTIFICATION_REQUEST:
      WdfRequestComplete(request, STATUS_NOT_IMPLEMENTED);
      return;
    default:
      WdfRequestComplete(request, STATUS_NOT_SUPPORTED);
      return;
  }
}

NTSTATUS WindowsLiquidTabletHidEvtDeviceAdd(
    WDFDRIVER driver,
    PWDFDEVICE_INIT device_init) {
  UNREFERENCED_PARAMETER(driver);

  WdfFdoInitSetFilter(device_init);

  WDF_OBJECT_ATTRIBUTES device_attributes;
  WDF_OBJECT_ATTRIBUTES_INIT(&device_attributes);
  WDF_OBJECT_ATTRIBUTES_SET_CONTEXT_TYPE(&device_attributes, HidDeviceContext);

  WDFDEVICE device = nullptr;
  NTSTATUS status = WdfDeviceCreate(&device_init, &device_attributes, &device);
  if (!NT_SUCCESS(status)) {
    return status;
  }

  new (WindowsLiquidTabletHidGetContext(device)) HidDeviceContext();
  auto* context = WindowsLiquidTabletHidGetContext(device);

  WDF_IO_QUEUE_CONFIG manual_queue_config;
  WDF_IO_QUEUE_CONFIG_INIT(&manual_queue_config, WdfIoQueueDispatchManual);
  status = WdfIoQueueCreate(
      device,
      &manual_queue_config,
      WDF_NO_OBJECT_ATTRIBUTES,
      &context->manual_queue);
  if (!NT_SUCCESS(status)) {
    return status;
  }

  WDF_IO_QUEUE_CONFIG queue_config;
  WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&queue_config, WdfIoQueueDispatchSequential);
  queue_config.EvtIoDeviceControl = WindowsLiquidTabletHidEvtIoDeviceControl;

  return WdfIoQueueCreate(device, &queue_config, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
}

} // namespace

extern "C" BOOL WINAPI DllMain(
    HINSTANCE instance,
    DWORD reason,
    LPVOID reserved) {
  UNREFERENCED_PARAMETER(instance);
  UNREFERENCED_PARAMETER(reason);
  UNREFERENCED_PARAMETER(reserved);

  // HID minidriver implementation is optional and should only be completed if
  // Synthetic Pointer compatibility is insufficient.
  return TRUE;
}

_Use_decl_annotations_
extern "C" NTSTATUS DriverEntry(
    PDRIVER_OBJECT driver_object,
    PUNICODE_STRING registry_path) {
  WDF_DRIVER_CONFIG config;
  WDF_DRIVER_CONFIG_INIT(&config, WindowsLiquidTabletHidEvtDeviceAdd);

  WDF_OBJECT_ATTRIBUTES driver_attributes;
  WDF_OBJECT_ATTRIBUTES_INIT(&driver_attributes);

  return WdfDriverCreate(
      driver_object,
      registry_path,
      &driver_attributes,
      &config,
      WDF_NO_HANDLE);
}
