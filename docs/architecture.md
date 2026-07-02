# Architecture

The system is split into replaceable modules so display transport, input injection, and driver work can evolve independently.

## Components

- Windows host: owns connection management, display capture, encoding, packet receive, mapping, diagnostics, and Windows input injection.
- iPad app: displays the Windows video stream, captures Apple Pencil events, separates finger touch from Pencil input, and sends normalized packets.
- Protocol: defines versioned little-endian packets in `protocol/`.
- Indirect display driver: eventually creates a Windows virtual monitor via IddCx. It does not perform networking.
- Optional HID pen driver: considered only if Synthetic Pointer cannot satisfy app compatibility.

## Data Flow

1. Windows host captures an existing or virtual display frame.
2. Host encodes and sends frames over a video channel.
3. iPad renders frames with a renderer abstraction.
4. iPad captures Pencil touches and converts them to normalized input events.
5. iPad sends input over a separate input channel.
6. Host maps normalized coordinates to Windows virtual screen coordinates.
7. Host injects pen input through the current input adapter.

## Initial Boundaries

- `windows/host/src/input/` will contain the Synthetic Pointer adapter and testable pen state machine.
- `windows/host/src/mapping/` will contain pure coordinate transforms.
- `windows/host/src/net/` will contain packet receive/send code.
- `windows/host/src/capture/` and `windows/host/src/codec/` remain swappable while latency work evolves.
- `ipad/iPadTablet/Sources/Pencil/` will contain UIKit Pencil capture.
- `ipad/iPadTablet/Sources/Mapping/` will contain pure coordinate and pressure mapping.

## Latency Design

Input and video are separate channels. Input is prioritized over video. Video queues must remain shallow and may drop stale frames. Latency metrics are collected per stage: capture, encode, network, decode, render, and input injection.
