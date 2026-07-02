#pragma once

#include "input/pen_session.h"

#include <vector>

namespace wlt::host::app {

struct DebugStrokeRect {
  float left;
  float top;
  float right;
  float bottom;
};

struct DebugPenCommand {
  input::PenAction action;
  input::PenSample sample;
};

std::vector<DebugPenCommand> make_rectangle_stroke(DebugStrokeRect rect);
std::vector<DebugPenCommand> make_fixed_rectangle_stroke();

} // namespace wlt::host::app
