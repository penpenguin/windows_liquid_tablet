# Pen Packet

`PenPacketV1` is the first shared Apple Pencil input packet. The canonical layout is `pen_packet.h`.

The packet is packed, little-endian, and 38 bytes long. It starts with the `IPEN` magic marker, protocol version `1`, packet type, monotonic sequence, normalized coordinates, normalized pressure, signed tilt, button bits, and device timestamp in nanoseconds.

The Windows receiver must validate packets before input injection and must force UP on timeout, CANCEL, or disconnect when the pen is active.
