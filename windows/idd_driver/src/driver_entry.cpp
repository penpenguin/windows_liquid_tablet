// WDK-only IddCx skeleton. This file is not part of the user-mode host build.

#define NOMINMAX
#include <windows.h>
#include <avrt.h>
#include <bugcodes.h>
#include <wudfwdm.h>
#include <wdf.h>
#include <iddcx.h>
#include <d3d11_2.h>
#include <dxgi.h>
#include <dxgi1_5.h>

#include "iddcx_device_add_flow.h"
#include "iddcx_device_add_status.h"
#include "iddcx_driver_start.h"
#include "iddcx_ntstatus_bridge.h"

extern "C" DRIVER_INITIALIZE DriverEntry;

namespace {

EVT_WDF_DRIVER_DEVICE_ADD WindowsLiquidTabletEvtDeviceAdd;
EVT_WDF_DEVICE_D0_ENTRY WindowsLiquidTabletEvtDeviceD0Entry;
EVT_WDF_DEVICE_D0_EXIT WindowsLiquidTabletEvtDeviceD0Exit;
EVT_IDD_CX_ADAPTER_INIT_FINISHED WindowsLiquidTabletEvtAdapterInitFinished;
EVT_IDD_CX_ADAPTER_COMMIT_MODES WindowsLiquidTabletEvtAdapterCommitModes;
EVT_IDD_CX_PARSE_MONITOR_DESCRIPTION WindowsLiquidTabletEvtParseMonitorDescription;
EVT_IDD_CX_MONITOR_GET_DEFAULT_DESCRIPTION_MODES WindowsLiquidTabletEvtMonitorGetDefaultDescriptionModes;
EVT_IDD_CX_MONITOR_QUERY_TARGET_MODES WindowsLiquidTabletEvtMonitorQueryTargetModes;
EVT_IDD_CX_MONITOR_ASSIGN_SWAPCHAIN WindowsLiquidTabletEvtMonitorAssignSwapChain;
EVT_IDD_CX_MONITOR_UNASSIGN_SWAPCHAIN WindowsLiquidTabletEvtMonitorUnassignSwapChain;

NTSTATUS WindowsLiquidTabletConfigureSwapChainDevice(IDXGIDevice* dxgi_device);
NTSTATUS WindowsLiquidTabletPumpAvailableSwapChainFrame();
DWORD WINAPI WindowsLiquidTabletSwapChainFramePumpThread(LPVOID context);
NTSTATUS WindowsLiquidTabletStartSwapChainFramePump();
void WindowsLiquidTabletStopSwapChainFramePump();

struct WindowsLiquidTabletSwapChainState {
  IDDCX_SWAPCHAIN active_swapchain;
  HANDLE next_surface_available;
  HANDLE frame_pump_thread;
  HANDLE frame_pump_stop_event;
  LUID render_adapter_luid;
  UINT64 acquired_frame_count;
  UINT64 completed_frame_count;
  UINT64 pumped_frame_count;
  UINT64 pending_frame_count;
  UINT64 failed_frame_count;
  UINT64 system_memory_acquired_frame_count;
  UINT64 frame_pump_thread_start_count;
  UINT64 frame_pump_thread_stop_count;
  UINT64 frame_pump_mmcss_enter_count;
  UINT64 frame_pump_mmcss_revert_count;
  UINT64 frame_pump_mmcss_failed_count;
  UINT64 reported_frame_count;
  UINT64 frame_statistics_failed_count;
  UINT64 last_frame_acquire_qpc_time;
  UINT last_dirty_rect_count;
  UINT last_move_region_count;
  UINT last_presentation_frame_number;
  UINT last_processed_pixel_count;
  UINT last_frame_size_bytes;
  UINT last_system_buffer_pitch;
  UINT last_system_buffer_width;
  UINT last_system_buffer_height;
  DXGI_FORMAT last_system_buffer_format;
  bool swapchain_device_ready;
  bool memory_placement_known;
  bool buffers_in_system_memory;
  bool use_system_memory_acquire;
  bool last_system_buffer_pointer_valid;
  bool frame_pump_running;
  bool frame_pump_mmcss_active;
  bool assigned;
};

WindowsLiquidTabletSwapChainState g_swapchain_state = {};

struct WindowsLiquidTabletCommittedPathState {
  IDDCX_MONITOR monitor;
  DISPLAYCONFIG_VIDEO_SIGNAL_INFO target_video_signal;
  bool active;
};

WindowsLiquidTabletCommittedPathState g_committed_path_state = {};

struct WindowsLiquidTabletMonitorState {
  IDDCX_MONITOR monitor;
  UINT64 departure_count;
  UINT64 departure_failed_count;
  bool arrived;
};

WindowsLiquidTabletMonitorState g_monitor_state = {};

UINT64 WindowsLiquidTabletQueryPerformanceCounterTicks() {
  LARGE_INTEGER counter = {};
  if (!QueryPerformanceCounter(&counter)) {
    return 0;
  }
  return static_cast<UINT64>(counter.QuadPart);
}

NTSTATUS WindowsLiquidTabletStartSwapChainFramePump() {
  if (!g_swapchain_state.assigned ||
      g_swapchain_state.active_swapchain == nullptr ||
      g_swapchain_state.next_surface_available == nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }
  if (g_swapchain_state.frame_pump_thread != nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }

  g_swapchain_state.frame_pump_stop_event = CreateEventW(nullptr, TRUE, FALSE, nullptr);
  if (g_swapchain_state.frame_pump_stop_event == nullptr) {
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.frame_pump_thread = CreateThread(
      nullptr,
      0,
      WindowsLiquidTabletSwapChainFramePumpThread,
      nullptr,
      0,
      nullptr);
  if (g_swapchain_state.frame_pump_thread == nullptr) {
    CloseHandle(g_swapchain_state.frame_pump_stop_event);
    g_swapchain_state.frame_pump_stop_event = nullptr;
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.frame_pump_running = true;
  g_swapchain_state.frame_pump_thread_start_count += 1;
  return STATUS_SUCCESS;
}

void WindowsLiquidTabletStopSwapChainFramePump() {
  const bool was_running = g_swapchain_state.frame_pump_running;

  if (g_swapchain_state.frame_pump_stop_event != nullptr) {
    SetEvent(g_swapchain_state.frame_pump_stop_event);
  }
  if (g_swapchain_state.frame_pump_thread != nullptr) {
    WaitForSingleObject(g_swapchain_state.frame_pump_thread, INFINITE);
    CloseHandle(g_swapchain_state.frame_pump_thread);
    g_swapchain_state.frame_pump_thread = nullptr;
  }
  if (g_swapchain_state.frame_pump_stop_event != nullptr) {
    CloseHandle(g_swapchain_state.frame_pump_stop_event);
    g_swapchain_state.frame_pump_stop_event = nullptr;
  }

  if (was_running) {
    g_swapchain_state.frame_pump_thread_stop_count += 1;
  }
  g_swapchain_state.frame_pump_running = false;
}

void ReleaseActiveSwapChain() {
  WindowsLiquidTabletStopSwapChainFramePump();
  if (g_swapchain_state.active_swapchain != nullptr) {
    WdfObjectDelete(reinterpret_cast<WDFOBJECT>(g_swapchain_state.active_swapchain));
  }
  g_swapchain_state = {};
}

bool SameAdapterLuid(LUID left, LUID right) {
  return left.HighPart == right.HighPart && left.LowPart == right.LowPart;
}

HRESULT WindowsLiquidTabletCreateDxgiDeviceForRenderAdapter(
    LUID render_adapter_luid,
    IDXGIDevice** dxgi_device) {
  if (dxgi_device == nullptr) {
    return E_INVALIDARG;
  }
  *dxgi_device = nullptr;

  IDXGIFactory1* factory = nullptr;
  HRESULT status =
      CreateDXGIFactory1(__uuidof(IDXGIFactory1), reinterpret_cast<void**>(&factory));
  if (FAILED(status)) {
    return status;
  }

  IDXGIAdapter1* selected_adapter = nullptr;
  for (UINT adapter_index = 0;; ++adapter_index) {
    IDXGIAdapter1* adapter = nullptr;
    status = factory->EnumAdapters1(adapter_index, &adapter);
    if (status == DXGI_ERROR_NOT_FOUND) {
      break;
    }
    if (FAILED(status)) {
      factory->Release();
      return status;
    }

    DXGI_ADAPTER_DESC1 adapter_desc = {};
    status = adapter->GetDesc1(&adapter_desc);
    if (SUCCEEDED(status) && SameAdapterLuid(adapter_desc.AdapterLuid, render_adapter_luid)) {
      selected_adapter = adapter;
      break;
    }
    adapter->Release();
  }

  if (selected_adapter == nullptr) {
    factory->Release();
    return DXGI_ERROR_NOT_FOUND;
  }

  ID3D11Device* d3d_device = nullptr;
  D3D_FEATURE_LEVEL feature_level = {};
  status = D3D11CreateDevice(
      selected_adapter,
      D3D_DRIVER_TYPE_UNKNOWN,
      nullptr,
      D3D11_CREATE_DEVICE_BGRA_SUPPORT,
      nullptr,
      0,
      D3D11_SDK_VERSION,
      &d3d_device,
      &feature_level,
      nullptr);
  if (SUCCEEDED(status) && d3d_device != nullptr) {
    status = d3d_device->QueryInterface(__uuidof(IDXGIDevice), reinterpret_cast<void**>(dxgi_device));
  } else if (SUCCEEDED(status)) {
    status = E_FAIL;
  }

  if (d3d_device != nullptr) {
    d3d_device->Release();
  }
  selected_adapter->Release();
  factory->Release();
  return status;
}

void FillVideoSignalInfo(
    DISPLAYCONFIG_VIDEO_SIGNAL_INFO& signal,
    const wlt::idd::VirtualMonitorMode& mode,
    bool monitor_mode) {
  signal = {};
  signal.totalSize.cx = mode.width;
  signal.totalSize.cy = mode.height;
  signal.activeSize.cx = mode.width;
  signal.activeSize.cy = mode.height;
  signal.vSyncFreq.Numerator = mode.refresh_rate_millihz;
  signal.vSyncFreq.Denominator = 1000;
  signal.hSyncFreq.Numerator = mode.refresh_rate_millihz * mode.height;
  signal.hSyncFreq.Denominator = 1000;
  signal.AdditionalSignalInfo.vSyncFreqDivider = monitor_mode ? 0 : 1;
  signal.AdditionalSignalInfo.videoStandard = 255;
  signal.scanLineOrdering = DISPLAYCONFIG_SCANLINE_ORDERING_PROGRESSIVE;
  signal.pixelRate =
      static_cast<UINT64>(mode.width) * mode.height * mode.refresh_rate_millihz / 1000;
}

IDDCX_MONITOR_MODE MakeMonitorMode(
    const wlt::idd::VirtualMonitorMode& virtual_mode,
    IDDCX_MONITOR_MODE_ORIGIN origin) {
  IDDCX_MONITOR_MODE mode = {};
  mode.Size = sizeof(mode);
  mode.Origin = origin;
  FillVideoSignalInfo(mode.MonitorVideoSignalInfo, virtual_mode, true);
  return mode;
}

IDDCX_TARGET_MODE MakeTargetMode(const wlt::idd::VirtualMonitorMode& virtual_mode) {
  IDDCX_TARGET_MODE mode = {};
  mode.Size = sizeof(mode);
  FillVideoSignalInfo(mode.TargetVideoSignalInfo.targetVideoSignalInfo, virtual_mode, false);
  mode.RequiredBandwidth = 0;
  return mode;
}

NTSTATUS CopyMonitorModes(
    UINT buffer_count,
    IDDCX_MONITOR_MODE* buffer,
    IDDCX_MONITOR_MODE_ORIGIN origin) {
  const auto modes = wlt::idd::default_virtual_monitor_modes();
  if (buffer == nullptr || buffer_count == 0) {
    return STATUS_SUCCESS;
  }
  if (buffer_count < modes.size()) {
    return STATUS_BUFFER_TOO_SMALL;
  }

  for (UINT index = 0; index < modes.size(); ++index) {
    buffer[index] = MakeMonitorMode(modes[index], origin);
  }
  return STATUS_SUCCESS;
}

NTSTATUS CopyTargetModes(UINT buffer_count, IDDCX_TARGET_MODE* buffer) {
  const auto modes = wlt::idd::default_virtual_monitor_modes();
  if (buffer == nullptr || buffer_count == 0) {
    return STATUS_SUCCESS;
  }
  if (buffer_count < modes.size()) {
    return STATUS_BUFFER_TOO_SMALL;
  }

  for (UINT index = 0; index < modes.size(); ++index) {
    buffer[index] = MakeTargetMode(modes[index]);
  }
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletDepartActiveMonitor() {
  if (!g_monitor_state.arrived || g_monitor_state.monitor == nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }

  ReleaseActiveSwapChain();
  const NTSTATUS departure_status = IddCxMonitorDeparture(g_monitor_state.monitor);
  if (!NT_SUCCESS(departure_status)) {
    g_monitor_state.departure_failed_count += 1;
    return departure_status;
  }

  g_monitor_state.departure_count += 1;
  g_monitor_state.monitor = nullptr;
  g_monitor_state.arrived = false;
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletEvtParseMonitorDescription(
    const IDARG_IN_PARSEMONITORDESCRIPTION* pInArgs,
    IDARG_OUT_PARSEMONITORDESCRIPTION* pOutArgs) {
  if (pInArgs == nullptr || pOutArgs == nullptr) {
    return STATUS_INVALID_PARAMETER;
  }

  const auto modes = wlt::idd::default_virtual_monitor_modes();
  pOutArgs->MonitorModeBufferOutputCount = static_cast<UINT>(modes.size());
  pOutArgs->PreferredMonitorModeIdx = 3;
  return CopyMonitorModes(
      pInArgs->MonitorModeBufferInputCount,
      pInArgs->pMonitorModes,
      IDDCX_MONITOR_MODE_ORIGIN_MONITORDESCRIPTOR);
}

NTSTATUS WindowsLiquidTabletEvtMonitorGetDefaultDescriptionModes(
    IDDCX_MONITOR monitor,
    const IDARG_IN_GETDEFAULTDESCRIPTIONMODES* pInArgs,
    IDARG_OUT_GETDEFAULTDESCRIPTIONMODES* pOutArgs) {
  UNREFERENCED_PARAMETER(monitor);

  if (pInArgs == nullptr || pOutArgs == nullptr) {
    return STATUS_INVALID_PARAMETER;
  }

  const auto modes = wlt::idd::default_virtual_monitor_modes();
  pOutArgs->DefaultMonitorModeBufferOutputCount = static_cast<UINT>(modes.size());
  pOutArgs->PreferredMonitorModeIdx = 3;
  return CopyMonitorModes(
      pInArgs->DefaultMonitorModeBufferInputCount,
      pInArgs->pDefaultMonitorModes,
      IDDCX_MONITOR_MODE_ORIGIN_DRIVER);
}

NTSTATUS WindowsLiquidTabletEvtMonitorQueryTargetModes(
    IDDCX_MONITOR monitor,
    const IDARG_IN_QUERYTARGETMODES* pInArgs,
    IDARG_OUT_QUERYTARGETMODES* pOutArgs) {
  UNREFERENCED_PARAMETER(monitor);

  if (pInArgs == nullptr || pOutArgs == nullptr) {
    return STATUS_INVALID_PARAMETER;
  }

  const auto modes = wlt::idd::default_virtual_monitor_modes();
  pOutArgs->TargetModeBufferOutputCount = static_cast<UINT>(modes.size());
  return CopyTargetModes(pInArgs->TargetModeBufferInputCount, pInArgs->pTargetModes);
}

NTSTATUS WindowsLiquidTabletEvtMonitorAssignSwapChain(
    IDDCX_MONITOR monitor,
    const IDARG_IN_SETSWAPCHAIN* pInArgs) {
  UNREFERENCED_PARAMETER(monitor);

  if (pInArgs == nullptr ||
      pInArgs->hSwapChain == nullptr ||
      pInArgs->hNextSurfaceAvailable == nullptr) {
    return STATUS_INVALID_PARAMETER;
  }

  ReleaseActiveSwapChain();
  g_swapchain_state.active_swapchain = pInArgs->hSwapChain;
  g_swapchain_state.next_surface_available = pInArgs->hNextSurfaceAvailable;
  g_swapchain_state.render_adapter_luid = pInArgs->RenderAdapterLuid;
  g_swapchain_state.assigned = true;

  IDXGIDevice* dxgi_device = nullptr;
  const HRESULT device_status =
      WindowsLiquidTabletCreateDxgiDeviceForRenderAdapter(pInArgs->RenderAdapterLuid, &dxgi_device);
  if (FAILED(device_status)) {
    ReleaseActiveSwapChain();
    return STATUS_UNSUCCESSFUL;
  }

  const NTSTATUS configure_status = WindowsLiquidTabletConfigureSwapChainDevice(dxgi_device);
  dxgi_device->Release();
  if (!NT_SUCCESS(configure_status)) {
    ReleaseActiveSwapChain();
    return configure_status;
  }

  const NTSTATUS pump_status = WindowsLiquidTabletStartSwapChainFramePump();
  if (!NT_SUCCESS(pump_status)) {
    ReleaseActiveSwapChain();
    return pump_status;
  }

  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletConfigureSwapChainDevice(IDXGIDevice* dxgi_device) {
  if (!g_swapchain_state.assigned ||
      g_swapchain_state.active_swapchain == nullptr ||
      dxgi_device == nullptr) {
    return STATUS_INVALID_PARAMETER;
  }

  IDARG_IN_SWAPCHAINSETDEVICE set_device = {};
  set_device.pDevice = dxgi_device;

  const HRESULT set_device_status =
      IddCxSwapChainSetDevice(g_swapchain_state.active_swapchain, &set_device);
  if (FAILED(set_device_status)) {
    return STATUS_UNSUCCESSFUL;
  }
  g_swapchain_state.swapchain_device_ready = true;

  BOOL buffers_in_system_memory = FALSE;
  const HRESULT memory_status =
      IddCxSwapChainInSystemMemory(g_swapchain_state.active_swapchain, &buffers_in_system_memory);
  if (FAILED(memory_status)) {
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.memory_placement_known = true;
  g_swapchain_state.buffers_in_system_memory = buffers_in_system_memory == TRUE;
  g_swapchain_state.use_system_memory_acquire = buffers_in_system_memory == TRUE;
  return STATUS_SUCCESS;
}

UINT CalculateCommittedPathPixelCount() {
  if (!g_committed_path_state.active) {
    return 0;
  }
  const UINT width =
      static_cast<UINT>(g_committed_path_state.target_video_signal.activeSize.cx);
  const UINT height =
      static_cast<UINT>(g_committed_path_state.target_video_signal.activeSize.cy);
  return width * height;
}

NTSTATUS WindowsLiquidTabletReportCompletedFrameStatistics() {
  if (!g_swapchain_state.assigned || g_swapchain_state.active_swapchain == nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }

  IDARG_IN_REPORTFRAMESTATISTICS report = {};
  report.FrameStatistics.Size = sizeof(report.FrameStatistics);
  report.FrameStatistics.PresentationFrameNumber = g_swapchain_state.last_presentation_frame_number;
  report.FrameStatistics.FrameStatus = IDDCX_FRAME_STATUS_COMPLETED;
  report.FrameStatistics.FrameSliceTotal = 1;
  report.FrameStatistics.CurrentSlice = 0;
  report.FrameStatistics.FrameAcquireQpcTime = g_swapchain_state.last_frame_acquire_qpc_time;
  report.FrameStatistics.Flags = IDDCX_FRAME_STATISTICS_FLAGS_NONE;
  report.FrameStatistics.ProcessedPixelCount = g_swapchain_state.last_processed_pixel_count;
  report.FrameStatistics.FrameSizeInBytes = g_swapchain_state.last_frame_size_bytes;

  const NTSTATUS report_status =
      IddCxSwapChainReportFrameStatistics(g_swapchain_state.active_swapchain, &report);
  if (!NT_SUCCESS(report_status)) {
    g_swapchain_state.frame_statistics_failed_count += 1;
    return report_status;
  }

  g_swapchain_state.reported_frame_count += 1;
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletRecordAcquiredFrameMetadata(const IDDCX_METADATA& metadata) {
  g_swapchain_state.last_frame_acquire_qpc_time = WindowsLiquidTabletQueryPerformanceCounterTicks();
  g_swapchain_state.last_presentation_frame_number = metadata.PresentationFrameNumber;
  g_swapchain_state.last_dirty_rect_count = metadata.DirtyRectCount;
  g_swapchain_state.last_move_region_count = metadata.MoveRegionCount;
  g_swapchain_state.last_processed_pixel_count = CalculateCommittedPathPixelCount();
  g_swapchain_state.last_frame_size_bytes = g_swapchain_state.last_processed_pixel_count * 4;
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletAcquireNextDxgiSwapChainFrame() {
  IDARG_OUT_RELEASEANDACQUIREBUFFER acquired_buffer = {};
  const HRESULT acquire_status =
      IddCxSwapChainReleaseAndAcquireBuffer(g_swapchain_state.active_swapchain, &acquired_buffer);
  if (acquire_status == E_PENDING) {
    return STATUS_PENDING;
  }
  if (FAILED(acquire_status)) {
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.acquired_frame_count += 1;
  const NTSTATUS record_status =
      WindowsLiquidTabletRecordAcquiredFrameMetadata(acquired_buffer.MetaData);
  if (!NT_SUCCESS(record_status)) {
    return record_status;
  }

  if (acquired_buffer.MetaData.pSurface != nullptr) {
    acquired_buffer.MetaData.pSurface->Release();
  }

  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletAcquireNextSystemMemorySwapChainFrame() {
  IDDCX_METADATA metadata = {};
  IDDCX_SYSTEM_BUFFER_INFO system_buffer_info = {};
  system_buffer_info.Size = sizeof(system_buffer_info);
  IDARG_OUT_RELEASEANDACQUIRESYSTEMBUFFER acquired_buffer = {&metadata, &system_buffer_info};

  const HRESULT acquire_status =
      IddCxSwapChainReleaseAndAcquireSystemBuffer(g_swapchain_state.active_swapchain, &acquired_buffer);
  if (acquire_status == E_PENDING) {
    return STATUS_PENDING;
  }
  if (FAILED(acquire_status)) {
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.acquired_frame_count += 1;
  g_swapchain_state.system_memory_acquired_frame_count += 1;
  const NTSTATUS record_status = WindowsLiquidTabletRecordAcquiredFrameMetadata(metadata);
  if (!NT_SUCCESS(record_status)) {
    return record_status;
  }

  g_swapchain_state.last_system_buffer_pitch = system_buffer_info.Pitch;
  g_swapchain_state.last_system_buffer_width = system_buffer_info.Width;
  g_swapchain_state.last_system_buffer_height = system_buffer_info.Height;
  g_swapchain_state.last_system_buffer_format = system_buffer_info.Format;
  g_swapchain_state.last_system_buffer_pointer_valid = system_buffer_info.pBuffer != nullptr;
  g_swapchain_state.last_frame_size_bytes = system_buffer_info.Pitch * system_buffer_info.Height;
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletProcessNextSwapChainFrame() {
  if (!g_swapchain_state.assigned || g_swapchain_state.active_swapchain == nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }
  if (!g_swapchain_state.swapchain_device_ready || !g_swapchain_state.memory_placement_known) {
    return STATUS_DEVICE_NOT_READY;
  }

  const NTSTATUS acquire_status = g_swapchain_state.use_system_memory_acquire
      ? WindowsLiquidTabletAcquireNextSystemMemorySwapChainFrame()
      : WindowsLiquidTabletAcquireNextDxgiSwapChainFrame();
  if (acquire_status == STATUS_PENDING) {
    return STATUS_PENDING;
  }
  if (!NT_SUCCESS(acquire_status)) {
    return acquire_status;
  }

  const HRESULT finished_status =
      IddCxSwapChainFinishedProcessingFrame(g_swapchain_state.active_swapchain);
  if (FAILED(finished_status)) {
    return STATUS_UNSUCCESSFUL;
  }

  g_swapchain_state.completed_frame_count += 1;
  return WindowsLiquidTabletReportCompletedFrameStatistics();
}

NTSTATUS WindowsLiquidTabletPumpAvailableSwapChainFrame() {
  if (!g_swapchain_state.assigned ||
      g_swapchain_state.active_swapchain == nullptr ||
      g_swapchain_state.next_surface_available == nullptr) {
    return STATUS_INVALID_DEVICE_STATE;
  }

  const NTSTATUS frame_status = WindowsLiquidTabletProcessNextSwapChainFrame();
  if (frame_status == STATUS_PENDING) {
    g_swapchain_state.pending_frame_count += 1;
    return frame_status;
  }
  if (!NT_SUCCESS(frame_status)) {
    g_swapchain_state.failed_frame_count += 1;
    return frame_status;
  }

  g_swapchain_state.pumped_frame_count += 1;
  return STATUS_SUCCESS;
}

HANDLE WindowsLiquidTabletEnterFramePumpMmcss() {
  DWORD av_task_index = 0;
  HANDLE mmcss_task_handle =
      AvSetMmThreadCharacteristicsW(L"Distribution", &av_task_index);
  if (mmcss_task_handle == nullptr) {
    g_swapchain_state.frame_pump_mmcss_failed_count += 1;
    return nullptr;
  }

  g_swapchain_state.frame_pump_mmcss_active = true;
  g_swapchain_state.frame_pump_mmcss_enter_count += 1;
  return mmcss_task_handle;
}

void WindowsLiquidTabletLeaveFramePumpMmcss(HANDLE mmcss_task_handle) {
  if (mmcss_task_handle == nullptr) {
    g_swapchain_state.frame_pump_mmcss_active = false;
    return;
  }

  if (AvRevertMmThreadCharacteristics(mmcss_task_handle)) {
    g_swapchain_state.frame_pump_mmcss_revert_count += 1;
  }
  g_swapchain_state.frame_pump_mmcss_active = false;
}

DWORD WindowsLiquidTabletRunSwapChainFramePumpLoop() {
  HANDLE wait_handles[] = {
      g_swapchain_state.frame_pump_stop_event,
      g_swapchain_state.next_surface_available,
  };

  if (wait_handles[0] == nullptr || wait_handles[1] == nullptr) {
    g_swapchain_state.failed_frame_count += 1;
    return 1;
  }

  for (;;) {
    const DWORD wait_status = WaitForMultipleObjects(2, wait_handles, FALSE, INFINITE);
    if (wait_status == WAIT_OBJECT_0) {
      return 0;
    }
    if (wait_status == WAIT_OBJECT_0 + 1) {
      WindowsLiquidTabletPumpAvailableSwapChainFrame();
      continue;
    }

    g_swapchain_state.failed_frame_count += 1;
    return 1;
  }
}

DWORD WINAPI WindowsLiquidTabletSwapChainFramePumpThread(LPVOID context) {
  UNREFERENCED_PARAMETER(context);

  HANDLE mmcss_task_handle = WindowsLiquidTabletEnterFramePumpMmcss();
  const DWORD thread_status = WindowsLiquidTabletRunSwapChainFramePumpLoop();
  WindowsLiquidTabletLeaveFramePumpMmcss(mmcss_task_handle);
  return thread_status;
}

NTSTATUS WindowsLiquidTabletEvtAdapterCommitModes(
    IDDCX_ADAPTER adapter,
    const IDARG_IN_COMMITMODES* pInArgs) {
  UNREFERENCED_PARAMETER(adapter);

  if (pInArgs == nullptr || (pInArgs->PathCount > 0 && pInArgs->pPaths == nullptr)) {
    return STATUS_INVALID_PARAMETER;
  }

  g_committed_path_state = {};
  for (UINT path_index = 0; path_index < pInArgs->PathCount; ++path_index) {
    const IDDCX_PATH& path = pInArgs->pPaths[path_index];
    if ((path.Flags & IDDCX_PATH_FLAGS_ACTIVE) != 0) {
      g_committed_path_state.monitor = path.MonitorObject;
      g_committed_path_state.target_video_signal = path.TargetVideoSignalInfo;
      g_committed_path_state.active = true;
      break;
    }
  }

  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletEvtMonitorUnassignSwapChain(IDDCX_MONITOR monitor) {
  UNREFERENCED_PARAMETER(monitor);

  ReleaseActiveSwapChain();
  return STATUS_SUCCESS;
}

class WindowsLiquidTabletMonitorRegistrar final : public wlt::idd::IddcxMonitorRegistrar {
public:
  explicit WindowsLiquidTabletMonitorRegistrar(IDDCX_ADAPTER adapter) : adapter_(adapter) {}

  bool register_monitor(const wlt::idd::IddcxMonitorReport& report) override {
    WDF_OBJECT_ATTRIBUTES monitor_attributes;
    WDF_OBJECT_ATTRIBUTES_INIT(&monitor_attributes);

    IDDCX_MONITOR_INFO monitor_info = {};
    monitor_info.Size = sizeof(monitor_info);
    monitor_info.MonitorType = DISPLAYCONFIG_OUTPUT_TECHNOLOGY_HDMI;
    monitor_info.ConnectorIndex = 0;
    monitor_info.MonitorDescription.Size = sizeof(monitor_info.MonitorDescription);
    monitor_info.MonitorDescription.Type = IDDCX_MONITOR_DESCRIPTION_TYPE_EDID;
    monitor_info.MonitorDescription.DataSize = static_cast<UINT>(report.edid.size());
    monitor_info.MonitorDescription.pData =
        reinterpret_cast<PVOID>(const_cast<unsigned char*>(report.edid.data()));
    monitor_info.MonitorContainerId = {
        0x6a947a3f,
        0x3c41,
        0x4f84,
        {0x9b, 0x43, 0x57, 0x4c, 0x54, 0x00, 0x00, 0x01},
    };

    IDARG_IN_MONITORCREATE create_args = {};
    create_args.ObjectAttributes = &monitor_attributes;
    create_args.pMonitorInfo = &monitor_info;

    IDARG_OUT_MONITORCREATE create_out = {};
    NTSTATUS status = IddCxMonitorCreate(adapter_, &create_args, &create_out);
    if (!NT_SUCCESS(status)) {
      return false;
    }

    IDARG_OUT_MONITORARRIVAL arrival_out = {};
    status = IddCxMonitorArrival(create_out.MonitorObject, &arrival_out);
    if (NT_SUCCESS(status)) {
      g_monitor_state.monitor = create_out.MonitorObject;
      g_monitor_state.arrived = true;
    }
    return NT_SUCCESS(status);
  }

private:
  IDDCX_ADAPTER adapter_;
};

NTSTATUS WindowsLiquidTabletEvtDeviceD0Entry(
    WDFDEVICE device,
    WDF_POWER_DEVICE_STATE previous_state) {
  UNREFERENCED_PARAMETER(previous_state);

  IDDCX_ENDPOINT_VERSION endpoint_version = {};
  endpoint_version.Size = sizeof(endpoint_version);
  endpoint_version.MajorVer = 1;
  endpoint_version.MinorVer = 0;

  IDDCX_ADAPTER_CAPS adapter_caps = {};
  adapter_caps.Size = sizeof(adapter_caps);
  adapter_caps.MaxMonitorsSupported = 1;
  adapter_caps.EndPointDiagnostics.Size = sizeof(adapter_caps.EndPointDiagnostics);
  adapter_caps.EndPointDiagnostics.GammaSupport = IDDCX_FEATURE_IMPLEMENTATION_NONE;
  adapter_caps.EndPointDiagnostics.TransmissionType = IDDCX_TRANSMISSION_TYPE_WIRED_OTHER;
  adapter_caps.EndPointDiagnostics.pEndPointFriendlyName = L"Windows Liquid Tablet";
  adapter_caps.EndPointDiagnostics.pEndPointManufacturerName = L"WindowsLiquidTablet";
  adapter_caps.EndPointDiagnostics.pEndPointModelName = L"Virtual iPad Display";
  adapter_caps.EndPointDiagnostics.pFirmwareVersion = &endpoint_version;
  adapter_caps.EndPointDiagnostics.pHardwareVersion = &endpoint_version;

  WDF_OBJECT_ATTRIBUTES adapter_attributes;
  WDF_OBJECT_ATTRIBUTES_INIT(&adapter_attributes);

  IDARG_IN_ADAPTER_INIT adapter_init = {};
  adapter_init.WdfDevice = device;
  adapter_init.pCaps = &adapter_caps;
  adapter_init.ObjectAttributes = &adapter_attributes;

  IDARG_OUT_ADAPTER_INIT adapter_init_out = {};
  return IddCxAdapterInitAsync(&adapter_init, &adapter_init_out);
}

NTSTATUS WindowsLiquidTabletEvtDeviceD0Exit(
    WDFDEVICE device,
    WDF_POWER_DEVICE_STATE target_state) {
  UNREFERENCED_PARAMETER(device);
  UNREFERENCED_PARAMETER(target_state);

  ReleaseActiveSwapChain();
  return STATUS_SUCCESS;
}

NTSTATUS WindowsLiquidTabletEvtAdapterInitFinished(
    IDDCX_ADAPTER adapter,
    const IDARG_IN_ADAPTER_INIT_FINISHED* init_finished) {
  if (init_finished != nullptr && !NT_SUCCESS(init_finished->AdapterInitStatus)) {
    return STATUS_SUCCESS;
  }

  // The driver owns only the virtual display surface; networking is intentionally not implemented here.
  // run_default_iddcx_device_add_flow uses start_default_virtual_monitor_device,
  // map_driver_start_to_device_add_status, DeviceAddNtStatus, and to_ntstatus
  // before this WDK callback returns the resulting NTSTATUS.
  WindowsLiquidTabletMonitorRegistrar registrar(adapter);
  const auto flow = run_default_iddcx_device_add_flow(registrar);
  return static_cast<NTSTATUS>(flow.nt_status);
}

NTSTATUS WindowsLiquidTabletEvtDeviceAdd(
    WDFDRIVER driver,
    PWDFDEVICE_INIT device_init) {
  UNREFERENCED_PARAMETER(driver);

  WDF_PNPPOWER_EVENT_CALLBACKS pnp_power_callbacks;
  WDF_PNPPOWER_EVENT_CALLBACKS_INIT(&pnp_power_callbacks);
  pnp_power_callbacks.EvtDeviceD0Entry = WindowsLiquidTabletEvtDeviceD0Entry;
  pnp_power_callbacks.EvtDeviceD0Exit = WindowsLiquidTabletEvtDeviceD0Exit;
  WdfDeviceInitSetPnpPowerEventCallbacks(device_init, &pnp_power_callbacks);

  IDD_CX_CLIENT_CONFIG idd_config;
  IDD_CX_CLIENT_CONFIG_INIT(&idd_config);
  idd_config.EvtIddCxAdapterInitFinished = WindowsLiquidTabletEvtAdapterInitFinished;
  idd_config.EvtIddCxAdapterCommitModes = WindowsLiquidTabletEvtAdapterCommitModes;
  idd_config.EvtIddCxParseMonitorDescription = WindowsLiquidTabletEvtParseMonitorDescription;
  idd_config.EvtIddCxMonitorGetDefaultDescriptionModes = WindowsLiquidTabletEvtMonitorGetDefaultDescriptionModes;
  idd_config.EvtIddCxMonitorQueryTargetModes = WindowsLiquidTabletEvtMonitorQueryTargetModes;
  idd_config.EvtIddCxMonitorAssignSwapChain = WindowsLiquidTabletEvtMonitorAssignSwapChain;
  idd_config.EvtIddCxMonitorUnassignSwapChain = WindowsLiquidTabletEvtMonitorUnassignSwapChain;

  NTSTATUS status = IddCxDeviceInitConfig(device_init, &idd_config);
  if (!NT_SUCCESS(status)) {
    return status;
  }

  WDF_OBJECT_ATTRIBUTES device_attributes;
  WDF_OBJECT_ATTRIBUTES_INIT(&device_attributes);

  WDFDEVICE device = nullptr;
  status = WdfDeviceCreate(&device_init, &device_attributes, &device);
  if (!NT_SUCCESS(status)) {
    return status;
  }

  return IddCxDeviceInitialize(device);
}

} // namespace

extern "C" BOOL WINAPI DllMain(
    _In_ HINSTANCE hInstance,
    _In_ UINT dwReason,
    _In_opt_ LPVOID lpReserved) {
  UNREFERENCED_PARAMETER(hInstance);
  UNREFERENCED_PARAMETER(dwReason);
  UNREFERENCED_PARAMETER(lpReserved);

  return TRUE;
}

_Use_decl_annotations_
extern "C" NTSTATUS DriverEntry(
    PDRIVER_OBJECT driver_object,
    PUNICODE_STRING registry_path) {
  WDF_DRIVER_CONFIG config;
  WDF_DRIVER_CONFIG_INIT(&config, WindowsLiquidTabletEvtDeviceAdd);

  WDF_OBJECT_ATTRIBUTES driver_attributes;
  WDF_OBJECT_ATTRIBUTES_INIT(&driver_attributes);

  return WdfDriverCreate(
      driver_object,
      registry_path,
      &driver_attributes,
      &config,
      WDF_NO_HANDLE);
}
