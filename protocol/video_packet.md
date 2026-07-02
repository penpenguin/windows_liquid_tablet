# Video Packet

`VideoPacketHeaderV1` is the first shared video frame header. The encoded payload bytes immediately follow the header.

The header is packed, little-endian, and 40 bytes long. It starts with the `IVID` magic marker, protocol version `1`, codec id, monotonic sequence, frame dimensions, capture and encode timestamps in nanoseconds, and `payload_size`.

Initial codec ids are `1 = H264AnnexB` and `2 = DebugJpeg`. Receivers must reject unsupported magic, version, codec, zero width or height, packets whose byte count does not match `40 + payload_size`, and payload sizes above the receiver safety limit. The current safety limit is 16 MiB.
