#include "hid_request_handler.h"

namespace wlt::hid {
namespace {

void copy_report_bytes(
    HidRequestResponse& response,
    const std::array<std::uint8_t, kPenHidReportWireSize>& report_bytes) {
  response.bytes.fill(0);
  for (std::size_t index = 0; index < report_bytes.size(); ++index) {
    response.bytes[index] = report_bytes[index];
  }
  response.byte_count = kPenHidReportWireSize;
}

void copy_hid_descriptor_bytes(
    HidRequestResponse& response,
    const std::array<std::uint8_t, kHidDescriptorSize>& descriptor_bytes) {
  response.bytes.fill(0);
  for (std::size_t index = 0; index < descriptor_bytes.size(); ++index) {
    response.bytes[index] = descriptor_bytes[index];
  }
  response.byte_count = kHidDescriptorSize;
}

void copy_hid_device_attributes_bytes(
    HidRequestResponse& response,
    const std::array<std::uint8_t, kHidDeviceAttributesSize>& attributes_bytes) {
  response.bytes.fill(0);
  for (std::size_t index = 0; index < attributes_bytes.size(); ++index) {
    response.bytes[index] = attributes_bytes[index];
  }
  response.byte_count = kHidDeviceAttributesSize;
}

void copy_hid_string_response_bytes(
    HidRequestResponse& response,
    const HidStringResponse& string_response) {
  response.bytes.fill(0);
  for (std::size_t index = 0; index < string_response.byte_count; ++index) {
    response.bytes[index] = string_response.bytes[index];
  }
  response.byte_count = string_response.byte_count;
}

} // namespace

HidRequestResponse handle_hid_device_request(
    HidDeviceState& state,
    HidRequest request) {
  HidRequestResponse response{
      .bytes = {},
      .byte_count = 0,
      .report = state.last_report(),
      .active = state.is_active(),
      .accepted = true,
  };

  switch (request.kind) {
    case HidRequestKind::Activate: {
      state.activate();
      response.active = state.is_active();
      return response;
    }
    case HidRequestKind::Deactivate: {
      state.deactivate();
      response.active = state.is_active();
      return response;
    }
    case HidRequestKind::DeviceDescriptor: {
      response.report = state.last_report();
      copy_hid_descriptor_bytes(response, state.hid_descriptor());
      return response;
    }
    case HidRequestKind::DeviceAttributes: {
      response.report = state.last_report();
      copy_hid_device_attributes_bytes(response, state.device_attributes());
      return response;
    }
    case HidRequestKind::String: {
      response.report = state.last_report();
      const auto string_response = state.hid_string_response(request.string_id);
      if (string_response.has_value()) {
        copy_hid_string_response_bytes(response, *string_response);
      }
      return response;
    }
    case HidRequestKind::ReportDescriptor: {
      response.bytes = state.report_descriptor();
      response.byte_count = kPenReportDescriptorSize;
      response.report = state.last_report();
      return response;
    }
    case HidRequestKind::InputReport: {
      response.report = state.last_report();
      copy_report_bytes(response, state.serialized_last_report());
      return response;
    }
    case HidRequestKind::ApplySerializedReport: {
      const auto report = state.apply_serialized_report(request.report_bytes);
      response.accepted = report.has_value();
      response.report = state.last_report();
      return response;
    }
    case HidRequestKind::ApplySample: {
      response.report = state.apply_sample(request.sample);
      copy_report_bytes(response, state.serialized_last_report());
      return response;
    }
    case HidRequestKind::ReleaseContact: {
      response.report = state.release_contact();
      copy_report_bytes(response, state.serialized_last_report());
      return response;
    }
  }

  return response;
}

} // namespace wlt::hid
