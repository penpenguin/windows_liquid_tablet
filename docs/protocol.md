# Protocol

The first protocols are versioned little-endian binary packets for Apple Pencil input and encoded video frames. Canonical C++ layouts live in `protocol/`.

## PenPacketV1

All numeric fields are little-endian. Coordinates and pressure are normalized before transport.

| Field | Type | Meaning |
| --- | --- | --- |
| `magic` | `uint32` | Packet marker. Bytes are `IPEN`; the little-endian integer value is `0x4E455049`. |
| `version` | `uint16` | Protocol version. Initial value is `1`. |
| `type` | `uint16` | `0=down`, `1=move`, `2=up`, `3=hover`, `4=cancel`. |
| `sequence` | `uint32` | Monotonic packet sequence used for drop logging. |
| `x` | `float32` | Normalized x coordinate, `0.0..1.0`. |
| `y` | `float32` | Normalized y coordinate, `0.0..1.0`. |
| `pressure` | `float32` | Normalized pressure, `0.0..1.0`. |
| `tiltX` | `int16` | Pen tilt in degrees, clamped to `-90..90`. |
| `tiltY` | `int16` | Pen tilt in degrees, clamped to `-90..90`. |
| `buttons` | `uint16` | Bit flags for future side-button or shortcut state. |
| `timestamp` | `uint64` | Device timestamp in nanoseconds. |

The packed V1 size is 38 bytes.

## ShortcutPacketV1

Shortcut panel actions use the same input channel as Pencil packets, but carry a distinct magic marker so the receiver can frame mixed packet types.

| Field | Type | Meaning |
| --- | --- | --- |
| `magic` | `uint32` | Packet marker. Bytes are `ISHT`; the little-endian integer value is `0x54485349`. |
| `version` | `uint16` | Protocol version. Initial value is `1`. |
| `action` | `uint16` | `1=undo`, `2=redo`, `3=eraser`, `4=modifierShift`, `5=modifierAlt`. |
| `sequence` | `uint32` | Monotonic shortcut sequence used for drop logging. |
| `timestamp` | `uint64` | Device timestamp in nanoseconds. |

The packed V1 size is 20 bytes.

## VideoPacketHeaderV1

Encoded video frames use a fixed-size header followed by codec payload bytes. The canonical layout is `protocol/video_packet.h`.

| Field | Type | Meaning |
| --- | --- | --- |
| `magic` | `uint32` | Packet marker. Bytes are `IVID`; the little-endian integer value is `0x44495649`. |
| `version` | `uint16` | Protocol version. Initial value is `1`. |
| `codec` | `uint16` | `1=H264AnnexB`, `2=DebugJpeg`. |
| `sequence` | `uint32` | Monotonic video frame sequence. |
| `width` | `uint32` | Encoded frame width in pixels. |
| `height` | `uint32` | Encoded frame height in pixels. |
| `capture_timestamp_ns` | `uint64` | Host capture timestamp in nanoseconds. |
| `encode_timestamp_ns` | `uint64` | Host encode completion timestamp in nanoseconds. |
| `payload_size` | `uint32` | Encoded payload byte count immediately following the header. |

The packed V1 header size is 40 bytes. Receivers reject unsupported magic, version, codec, zero dimensions, packets whose byte count does not match `40 + payload_size`, and payload sizes above the receiver safety limit. The current safety limit is 16 MiB.

## Reliability Rules

- The Windows receiver logs sequence gaps.
- DOWN/MOVE/UP ordering is enforced by the host-side state machine.
- Missing UP is handled by timeout and disconnect fail-safe.
- CANCEL forces an UP if a pen is currently active.
- Invalid magic, unsupported version, out-of-range type, NaN coordinates, or out-of-range pressure are rejected before injection.

## Mapping Rules

- iPad sends normalized coordinates relative to the rendered content area.
- Windows maps normalized coordinates to the target virtual screen rectangle.
- Pressure maps from `0.0..1.0` to Windows pen pressure `0..1024`.
- `tiltX` and `tiltY` remain signed degrees and are clamped before injection.
