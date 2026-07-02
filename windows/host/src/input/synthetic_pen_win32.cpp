#include "input/synthetic_pen.h"

#ifndef _WIN32
#error synthetic_pen_win32.cpp must only be built on Windows.
#endif

#include <windows.h>

#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>

namespace wlt::host::input {

namespace {

class Win32SyntheticPenSink final : public SyntheticPenSink {
public:
  Win32SyntheticPenSink()
      : device_(CreateSyntheticPointerDevice(PT_PEN, 1, POINTER_FEEDBACK_NONE)) {
    if (device_ == nullptr) {
      const auto error = GetLastError();
      std::ostringstream message;
      message << "CreateSyntheticPointerDevice failed for PT_PEN GetLastError=" << error;
      throw std::runtime_error(message.str());
    }
  }

  ~Win32SyntheticPenSink() override {
    if (device_ != nullptr) {
      DestroySyntheticPointerDevice(device_);
    }
  }

  Win32SyntheticPenSink(const Win32SyntheticPenSink&) = delete;
  Win32SyntheticPenSink& operator=(const Win32SyntheticPenSink&) = delete;

  bool inject(const SyntheticPenFrame& frame) override {
    POINTER_TYPE_INFO pointer{};
    pointer.type = PT_PEN;
    pointer.penInfo.pointerInfo.pointerType = PT_PEN;
    pointer.penInfo.pointerInfo.pointerId = 1;
    pointer.penInfo.pointerInfo.ptPixelLocation.x = frame.x;
    pointer.penInfo.pointerInfo.ptPixelLocation.y = frame.y;
    pointer.penInfo.pointerInfo.pointerFlags = flags_for(frame.action);
    pointer.penInfo.penFlags = PEN_FLAG_NONE;
    pointer.penInfo.penMask = PEN_MASK_PRESSURE | PEN_MASK_TILT_X | PEN_MASK_TILT_Y;
    pointer.penInfo.pressure = frame.pressure;
    pointer.penInfo.tiltX = frame.tilt_x;
    pointer.penInfo.tiltY = frame.tilt_y;

    if (InjectSyntheticPointerInput(device_, &pointer, 1) != FALSE) {
      return true;
    }

    std::cerr << "InjectSyntheticPointerInput failed GetLastError="
              << GetLastError() << "\n";
    return false;
  }

private:
  static POINTER_FLAGS flags_for(PenAction action) {
    switch (action) {
    case PenAction::Down:
      return POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT | POINTER_FLAG_DOWN;
    case PenAction::Move:
      return POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT | POINTER_FLAG_UPDATE;
    case PenAction::Up:
      return POINTER_FLAG_UP;
    case PenAction::Hover:
      return POINTER_FLAG_INRANGE | POINTER_FLAG_UPDATE;
    case PenAction::Cancel:
      return POINTER_FLAG_UP;
    }

    return POINTER_FLAG_UPDATE;
  }

  HSYNTHETICPOINTERDEVICE device_ = nullptr;
};

} // namespace

std::unique_ptr<SyntheticPenSink> make_win32_synthetic_pen_sink() {
  return std::make_unique<Win32SyntheticPenSink>();
}

} // namespace wlt::host::input
