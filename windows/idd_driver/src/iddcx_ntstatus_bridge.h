#pragma once

#include "iddcx_device_add_status.h"

#include <cstdint>
#include <string_view>

namespace wlt::idd {

using NtStatusValue = std::uint32_t;

inline constexpr NtStatusValue kNtStatusSuccess = 0x00000000;
inline constexpr NtStatusValue kNtStatusDeviceConfigurationError = 0xC0000182;
inline constexpr NtStatusValue kNtStatusInvalidDeviceState = 0xC0000184;

NtStatusValue to_ntstatus(DeviceAddNtStatus status);
NtStatusValue device_add_result_to_ntstatus(const DeviceAddStatusResult& result);
std::string_view ntstatus_symbol(NtStatusValue status);

} // namespace wlt::idd
