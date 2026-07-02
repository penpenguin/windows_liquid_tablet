#include "net/pen_packet_fuzz_corpus.h"
#include "net/pen_packet_parser.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::invalid_pen_packet_corpus;
  using wlt::host::net::parse_pen_packet_v1;

  const auto corpus = invalid_pen_packet_corpus();
  if (int code = expect(corpus.size() >= 8, 1); code != 0) {
    return code;
  }

  for (const auto& sample : corpus) {
    const auto parsed = parse_pen_packet_v1(sample.bytes);
    if (int code = expect(!parsed.ok(), 2); code != 0) {
      return code;
    }
    if (int code = expect(parsed.error == sample.expected_error, 3); code != 0) {
      return code;
    }
  }

  return 0;
}
