#include "input/pen_session.h"

namespace wlt::host::input {

std::vector<PenEvent> PenSession::accept(PenAction action, const PenSample& sample) {
  std::vector<PenEvent> events;

  switch (action) {
  case PenAction::Down:
    if (active_ && last_sample_.has_value()) {
      events.push_back(make_event(PenAction::Up, *last_sample_, true));
    }
    active_ = true;
    last_sample_ = sample;
    events.push_back(make_event(PenAction::Down, sample, false));
    break;

  case PenAction::Move:
    if (active_) {
      last_sample_ = sample;
      events.push_back(make_event(action, sample, false));
    }
    break;

  case PenAction::Hover:
    if (active_) {
      last_sample_ = sample;
    }
    events.push_back(make_event(PenAction::Hover, sample, false));
    break;

  case PenAction::Up:
    if (active_) {
      active_ = false;
      last_sample_ = sample;
      events.push_back(make_event(PenAction::Up, sample, false));
    }
    break;

  case PenAction::Cancel:
    if (active_) {
      active_ = false;
      last_sample_ = sample;
      events.push_back(make_event(PenAction::Up, sample, true));
    }
    break;
  }

  return events;
}

std::vector<PenEvent> PenSession::force_up() {
  if (!active_ || !last_sample_.has_value()) {
    return {};
  }

  active_ = false;
  return {make_event(PenAction::Up, *last_sample_, true)};
}

std::vector<PenEvent> PenSession::force_up_if_idle(
    std::uint64_t now_ns,
    std::uint64_t idle_timeout_ns) {
  if (!active_ || !last_sample_.has_value()) {
    return {};
  }
  if (now_ns < last_sample_->timestamp_ns) {
    return {};
  }
  if ((now_ns - last_sample_->timestamp_ns) < idle_timeout_ns) {
    return {};
  }

  active_ = false;
  return {make_event(PenAction::Up, *last_sample_, true)};
}

bool PenSession::is_active() const {
  return active_;
}

PenEvent PenSession::make_event(PenAction action, const PenSample& sample, bool forced) const {
  return PenEvent{
      .action = action,
      .sample = sample,
      .forced = forced,
  };
}

} // namespace wlt::host::input
