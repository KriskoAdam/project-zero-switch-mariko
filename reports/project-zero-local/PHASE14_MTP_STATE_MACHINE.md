# Phase 14 — MTP State-Machine Differential Test

**Conclusion:** Across nine successful MTP sessions, standard read-only operations behaved consistently. The Storage ID changed from `0x00040001` to `0x00050001` after the user disabled and re-enabled MTP mode; the new ID remained stable in all three sessions after transition C. Declared operations, events, responses, and root object count did not change. The observed ID change alone is not a security flaw. State D could not be measured: after the user unplugged and reconnected the cable, macOS did not enumerate the USB device in two passive checks, so no MTP requests were sent in state D.

## Physical measurements

| State | USB identity/interface | Sessions | Storage ID | Root objects | Result |
|---|---|---:|---|---:|---|
| A — MTP active at the start of measurement | `057e:201d`, interface `06/01/01`, 3 endpoints | 3 | `0x00040001` in all | 3 in all | All operations succeeded |
| B — repeated session without changing USB mode | `057e:201d`, `06/01/01`, 3 endpoints | 3 | `0x00040001` in all | 3 in all | Same DeviceInfo and capabilities as A |
| C — user exited and reactivated MTP | `057e:201d`, `06/01/01`, 3 endpoints | 3 | `0x00050001` in all | 3 in all | Same DeviceInfo and capabilities; all requests succeeded |
| D — user unplugged and reconnected the cable | After the action and during the follow-up check, ioreg showed no Nintendo USB device or MTP interface | 0 | — | — | Not measured; no requests sent |

State A means that MTP was active when this phase's measurements began; Phase 14 did not freshly activate it. State C is the first transition performed and confirmed during Phase 14. The earlier Phase 13 record noted a Storage ID change from `0x00030001` to `0x00040001` after a previous mode restart. This is consistent with a new ID following a session/mode change, but it does not explain how the ID is generated.

## Operations and responses

DeviceInfo declared operations `0x1001`–`0x100a`: GetDeviceInfo, OpenSession, CloseSession, GetStorageIDs, GetStorageInfo, GetNumObjects, GetObjectHandles, GetObjectInfo, GetObject, and GetThumb. Only the first six were actually exercised. Each executed data operation (`0x1001`, `0x1004`, `0x1005`, `0x1006`) returned `0x2001` (OK) in all nine sessions. OpenSession succeeded through libmtp. CloseSession was invoked by `LIBMTP_Release_Device`; the API does not return the raw CloseSession response code, so a successful wire-level response was not confirmed.

Declared event codes were `0x4002`, `0x4003`, `0x4004`, `0x4005`, `0x4007`, and `0x400c`; the Device Properties list was empty. GetStorageInfo returned sentinel values `0xffffffffffffffff` for capacity and free bytes, and `0xffffffff` for free image items. These are not measurements of SD-card capacity and must not be interpreted as actual free space.

The longest recorded data operation took 4 ms in A, 1 ms in B, and 2 ms in C. Timestamps and complete fields are in `reports/raw/phase14_mtp/session_matrix.json` and the original JSONL records.

## Differential interpretation

- DeviceInfo, declared operation codes, and event capabilities were stable across A, B, and C.
- The Storage ID was stable within each group and changed between B and C after the user changed MTP mode.
- The root object count was always 3.
- The A/B-to-C difference is temporally associated with disabling and reactivating MTP. This experiment cannot determine whether it reflects a session counter, mode change, recreation of the USB function, or another implementation choice.
- No protocol anomaly, rejection of a declared operation, inconsistent object count, or reproducible security flaw was found.

## Tool review and evidence limits

The tool `../../tools/phase14-mtp/mtp_state_probe.c` uses libmtp 1.1.23 and a versioned internal PTP ABI header retained from Phase 13. It checks the declared operation list before making requests; list sizes are limited to 256 items and Storage IDs to 32. It aborts the session on malformed or oversized lengths. Queries are limited to DeviceInfo, StorageIDs, StorageInfo, and GetNumObjects with format `0x0000` and root association handle `0xffffffff`. It does not enumerate names or contents and performs no writes. `LIBMTP_Release_Device` is used to close the session.

libmtp makes an internal DeviceInfo request when opening the device; the tool then records an explicit DeviceInfo request as well. Successful internal opening confirms session creation, but libmtp diagnostics report Nintendo vendor extension ID `0xffffffff` and continue in PTP/MTP compatibility mode. The library calls CloseSession on release, but its public API hides the exact response code. Outputs are values parsed by libmtp, not raw USB/PTP packet bytes. Synthetic tests validate our JSONL validator, not libmtp's wire-level PTP parser.

Host-side validation tests: **6/6 passed**. They covered malformed JSON, oversized lists, execution of an unadvertised operation, invalid root-object-count arguments, and forbidden GetObjectHandles. Invalid requests were sent only to the synthetic validator on the Mac, never to the console.

## Reproduction

From `tools/phase14-mtp` (the device must be in the official MTP mode):

```sh
clang -Wall -Wextra -Werror \
  -I/opt/homebrew/Cellar/libmtp/1.1.23/include \
  -I/opt/homebrew/Cellar/libusb/1.0.30/include/libusb-1.0 \
  mtp_state_probe.c \
  /opt/homebrew/Cellar/libmtp/1.1.23/lib/libmtp.a \
  -L/opt/homebrew/Cellar/libusb/1.0.30/lib -lusb-1.0 -liconv -lobjc \
  -framework IOKit -framework CoreFoundation -framework Security \
  -o /tmp/mtp_state_probe

python3 capture_usb_state.py A ../../reports/project-zero-local/raw/phase14_mtp --json ../../reports/project-zero-local/raw/phase14_mtp/usb_A.json
/tmp/mtp_state_probe A 3 > ../../reports/project-zero-local/raw/phase14_mtp/state_A_records.jsonl 2> ../../reports/project-zero-local/raw/phase14_mtp/state_A_diagnostics.txt
/tmp/mtp_state_probe B 3 > ../../reports/project-zero-local/raw/phase14_mtp/state_B_records.jsonl 2> ../../reports/project-zero-local/raw/phase14_mtp/state_B_diagnostics.txt
# The user manually exits and reactivates “Copy to a Computer via USB.”
python3 capture_usb_state.py C ../../reports/project-zero-local/raw/phase14_mtp --json ../../reports/project-zero-local/raw/phase14_mtp/usb_C.json
/tmp/mtp_state_probe C 3 > ../../reports/project-zero-local/raw/phase14_mtp/state_C_records.jsonl 2> ../../reports/project-zero-local/raw/phase14_mtp/state_C_diagnostics.txt
python3 -m unittest -v test_validate_phase14.py
python3 validate_phase14.py \
  --input ../../reports/project-zero-local/raw/phase14_mtp/state_A_records.jsonl \
  --input ../../reports/project-zero-local/raw/phase14_mtp/state_B_records.jsonl \
  --input ../../reports/project-zero-local/raw/phase14_mtp/state_C_records.jsonl \
  --matrix ../../reports/project-zero-local/raw/phase14_mtp/session_matrix.json \
  --differential ../../reports/project-zero-local/raw/phase14_mtp/differential_results.json
```

Versions: libmtp 1.1.23, libusb 1.0.30. SHA-256: `mtp_state_probe.c` — `8e30393990cf1f3711459dcaf9cf9bd3af89a50f70d6b0a3a96930fb9a7cf56f`; `validate_phase14.py` — `0dc3b5de7de1b4f2f01df8d44fd04fecfe8890afaf41fcef410badf4566ed252`; `capture_usb_state.py` — `2a25b80101372bb149143d5c8dc8284280f5ba94b3aa30d9bb854d34e7cccdf5`.

## Decision

The MTP branch is closed for the current goal without a security finding. The Storage ID change after a user-controlled MTP restart is a reproducible but benign observed variation, with no evidence of exploitable impact. State D remains incomplete because macOS did not enumerate the USB device after reconnection; a repeat would first require restoring ordinary USB data connectivity. These results do not justify more MTP testing and do not establish a Homebrew entry point.
