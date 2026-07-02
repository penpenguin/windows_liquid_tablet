# Host Discovery

Local host discovery uses a versioned service advertisement that can be carried by Bonjour/mDNS, UDP broadcast, or another local-network discovery adapter. The initial Bonjour service type is `_wlt._tcp`.

## DNS-SD TXT record contract

The DNS-SD TXT record contract is the canonical key/value payload emitted by the host mDNS response and consumed by the iPad Bonjour browser:

| Key | Meaning |
| --- | --- |
| `version` | Discovery payload version. Initial value is `1`. |
| `hostId` | Stable host identifier for upsert/deduplication. |
| `name` | User-visible host display name. |
| `address` | IPv4 address or hostname used by the iPad app. |
| `inputPort` | TCP port for the Apple Pencil input channel. |
| `videoPort` | TCP port for the encoded video channel. |
| `pairingCode` | Six ASCII digit pairing code shown by the host. |

The input and video channels remain separate. Receivers reject records with missing identifiers, missing addresses, unsupported versions, zero ports, the same input/video port, or invalid pairing codes.
