cmake_minimum_required(VERSION 3.20)

project(WindowsLiquidTablet LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

enable_testing()

add_subdirectory(windows/host)
add_subdirectory(windows/idd_driver)
add_subdirectory(windows/hid_driver_optional)
