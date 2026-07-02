#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "#include <hidclass.h>",
        "#define IOCTL_HID_GET_DEVICE_DESCRIPTOR HID_CTL_CODE(0)",
        "#define IOCTL_HID_SEND_IDLE_NOTIFICATION_REQUEST HID_CTL_CODE(10)",
        "#define IOCTL_UMDF_HID_GET_INPUT_REPORT HID_CTL_CODE(23)",
        "#include \"hid_request_handler.h\"",
        "struct HidDeviceContext",
        "wlt::hid::HidDeviceState state;",
        "WDFQUEUE manual_queue = nullptr;",
        "WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(",
        "WindowsLiquidTabletHidGetContext",
        "WindowsLiquidTabletHidCompleteBytes",
        "WdfRequestRetrieveOutputMemory(",
        "WdfMemoryCopyFromBuffer(",
        "WdfRequestSetInformation(",
        "WdfRequestCompleteWithInformation(",
        "WindowsLiquidTabletHidCompleteNextPendingRead",
        "WdfIoQueueGetDevice(queue)",
        "IOCTL_HID_GET_REPORT_DESCRIPTOR",
        "HidRequestKind::ReportDescriptor",
        "IOCTL_HID_READ_REPORT",
        "WdfRequestForwardToIoQueue(request, context->manual_queue)",
        "WdfIoQueueRetrieveNextRequest(context->manual_queue",
        "HidRequestKind::InputReport",
        "IOCTL_GET_PHYSICAL_DESCRIPTOR",
        "IOCTL_HID_SEND_IDLE_NOTIFICATION_REQUEST",
        "STATUS_NOT_IMPLEMENTED",
        "handle_hid_device_request(context->state",
        "STATUS_NOT_SUPPORTED",
        "WDF_IO_QUEUE_CONFIG_INIT(&manual_queue_config, WdfIoQueueDispatchManual);",
        "WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE",
        "WdfIoQueueCreate(",
    ],
    "windows/hid_driver_optional/README.md": [
        "WDF default queue",
        "UMDF HID mapper device-control requests",
        "`mshidumdf.sys` converts HID internal IOCTLs to device-control requests",
        "IOCTL_HID_GET_REPORT_DESCRIPTOR",
        "IOCTL_HID_READ_REPORT",
        "manual read queue",
        "forwarded to the manual queue",
        "HID request handler",
    ],
    "README.md": [
        "verify_m9_hid_wdf_queue.py",
        "optional HID WDF queue",
    ],
    "docs/testing.md": [
        "verify_m9_hid_wdf_queue.py",
    ],
    "docs/milestones.md": [
        "Optional HID WDF default queue routes report descriptor requests through the testable HID request handler and forwards read-report IOCTLs to a manual read queue.",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "#include <ntddk.h>",
        "#include <hidport.h>",
        "KeQueryPerformanceCounter(",
        "WdfRequestRetrieveOutputBuffer(",
        "EvtIoInternalDeviceControl =",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID WDF queue verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID WDF queue verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain HID WDF queue-incompatible token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID WDF queue artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
