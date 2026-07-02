# Shortcut Packet

`ShortcutPacketV1` is the shared input-channel packet for iPad shortcut panel actions. The canonical layout is `shortcut_packet.h`.

The packet is packed, little-endian, and 20 bytes long. It starts with the `ISHT` magic marker, protocol version `1`, shortcut action, monotonic sequence, and device timestamp in nanoseconds.

The Windows receiver must validate shortcut packets before dispatching them to the host shortcut action boundary.
