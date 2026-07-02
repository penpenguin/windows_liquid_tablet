add_library(windows_hid_optional_core
  src/hid_device_state.cpp
  src/hid_request_handler.cpp
  src/hid_report_descriptor.cpp
)

target_include_directories(windows_hid_optional_core PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

add_executable(hid_report_descriptor_test
  tests/hid_report_descriptor_test.cpp
)

add_executable(hid_device_state_test
  tests/hid_device_state_test.cpp
)

add_executable(hid_request_handler_test
  tests/hid_request_handler_test.cpp
)

target_link_libraries(hid_report_descriptor_test PRIVATE
  windows_hid_optional_core
)

target_link_libraries(hid_device_state_test PRIVATE
  windows_hid_optional_core
)

target_link_libraries(hid_request_handler_test PRIVATE
  windows_hid_optional_core
)

add_test(NAME hid_report_descriptor_test COMMAND hid_report_descriptor_test)
add_test(NAME hid_device_state_test COMMAND hid_device_state_test)
add_test(NAME hid_request_handler_test COMMAND hid_request_handler_test)
