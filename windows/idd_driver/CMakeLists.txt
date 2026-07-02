add_library(windows_idd_driver_modes
  src/virtual_monitor_modes.cpp
)

add_library(windows_idd_driver_identity
  src/virtual_monitor_identity.cpp
)

add_library(windows_idd_driver_descriptor
  src/virtual_monitor_descriptor.cpp
)

add_library(windows_idd_driver_iddcx_report
  src/iddcx_monitor_report.cpp
)

add_library(windows_idd_driver_registration
  src/iddcx_monitor_registration.cpp
)

add_library(windows_idd_driver_start
  src/iddcx_driver_start.cpp
)

add_library(windows_idd_driver_device_add_status
  src/iddcx_device_add_status.cpp
)

add_library(windows_idd_driver_ntstatus_bridge
  src/iddcx_ntstatus_bridge.cpp
)

add_library(windows_idd_driver_device_add_flow
  src/iddcx_device_add_flow.cpp
)

target_include_directories(windows_idd_driver_modes PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_identity PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_descriptor PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_iddcx_report PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_registration PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_start PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_device_add_status PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_ntstatus_bridge PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_include_directories(windows_idd_driver_device_add_flow PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(windows_idd_driver_descriptor PUBLIC
  windows_idd_driver_identity
  windows_idd_driver_modes
)

target_link_libraries(windows_idd_driver_iddcx_report PUBLIC
  windows_idd_driver_descriptor
)

target_link_libraries(windows_idd_driver_registration PUBLIC
  windows_idd_driver_iddcx_report
)

target_link_libraries(windows_idd_driver_start PUBLIC
  windows_idd_driver_registration
)

target_link_libraries(windows_idd_driver_device_add_status PUBLIC
  windows_idd_driver_start
)

target_link_libraries(windows_idd_driver_ntstatus_bridge PUBLIC
  windows_idd_driver_device_add_status
)

target_link_libraries(windows_idd_driver_device_add_flow PUBLIC
  windows_idd_driver_ntstatus_bridge
)

add_executable(virtual_monitor_modes_test
  tests/virtual_monitor_modes_test.cpp
)

add_executable(virtual_monitor_identity_test
  tests/virtual_monitor_identity_test.cpp
)

add_executable(virtual_monitor_descriptor_test
  tests/virtual_monitor_descriptor_test.cpp
)

add_executable(iddcx_monitor_report_test
  tests/iddcx_monitor_report_test.cpp
)

add_executable(iddcx_monitor_registration_test
  tests/iddcx_monitor_registration_test.cpp
)

add_executable(iddcx_driver_start_test
  tests/iddcx_driver_start_test.cpp
)

add_executable(iddcx_device_add_status_test
  tests/iddcx_device_add_status_test.cpp
)

add_executable(iddcx_ntstatus_bridge_test
  tests/iddcx_ntstatus_bridge_test.cpp
)

add_executable(iddcx_device_add_flow_test
  tests/iddcx_device_add_flow_test.cpp
)

target_link_libraries(virtual_monitor_modes_test PRIVATE
  windows_idd_driver_modes
)

target_link_libraries(virtual_monitor_identity_test PRIVATE
  windows_idd_driver_identity
)

target_link_libraries(virtual_monitor_descriptor_test PRIVATE
  windows_idd_driver_descriptor
)

target_link_libraries(iddcx_monitor_report_test PRIVATE
  windows_idd_driver_iddcx_report
)

target_link_libraries(iddcx_monitor_registration_test PRIVATE
  windows_idd_driver_registration
)

target_link_libraries(iddcx_driver_start_test PRIVATE
  windows_idd_driver_start
)

target_link_libraries(iddcx_device_add_status_test PRIVATE
  windows_idd_driver_device_add_status
)

target_link_libraries(iddcx_ntstatus_bridge_test PRIVATE
  windows_idd_driver_ntstatus_bridge
)

target_link_libraries(iddcx_device_add_flow_test PRIVATE
  windows_idd_driver_device_add_flow
)

add_test(NAME virtual_monitor_modes_test COMMAND virtual_monitor_modes_test)
add_test(NAME virtual_monitor_identity_test COMMAND virtual_monitor_identity_test)
add_test(NAME virtual_monitor_descriptor_test COMMAND virtual_monitor_descriptor_test)
add_test(NAME iddcx_monitor_report_test COMMAND iddcx_monitor_report_test)
add_test(NAME iddcx_monitor_registration_test COMMAND iddcx_monitor_registration_test)
add_test(NAME iddcx_driver_start_test COMMAND iddcx_driver_start_test)
add_test(NAME iddcx_device_add_status_test COMMAND iddcx_device_add_status_test)
add_test(NAME iddcx_ntstatus_bridge_test COMMAND iddcx_ntstatus_bridge_test)
add_test(NAME iddcx_device_add_flow_test COMMAND iddcx_device_add_flow_test)
