# PROJECT ZERO — Phase 13: live MTP measurement

Measurement date: 2026-10-31, Europe/Bratislava time zone (+0100). The scope was limited to standard, read-only MTP operations on the physical console. USB serial values have been removed from stored evidence.

## Device state before measurement — state A

`ioreg -r -c IOUSBHostDevice -l -w0` and `ioreg -r -c IOUSBHostInterface -l -w0` found a physical device `057e:201d`, product string `Nintendo Switch`, and one active MTP interface: class/subclass/protocol `06/01/01`, interface 0, three endpoints. The captured descriptors are in `../raw/phase13_mtp/state_b1_usb_devices.txt` and `state_b1_usb_interfaces.txt`.

The process list contained no process named `mtp`, `openmtp`, or `Android File Transfer`. However, IOKit listed ChatGPT and Brave Browser user clients at the USB device, so we cannot claim that our diagnostic tool was the only host-side observer. The `busy 0` measurement and successful MTP session show no observed collision during the test, but do not exclude other host observation. The sanitized process inventory is `raw/phase13_mtp/process_inventory.txt`.

The console was already in the standard “Copy to a Computer via USB” mode. No console setting needed to be changed. USB identity alone does not confirm V2/Mariko/T210B01. MTP DeviceInfo reported device version `23.0.1`; this is a value supplied by the device, not independent firmware attestation.

## Tool and integrity verification

Installed versions: libmtp 1.1.23 and libusb 1.0.30. The libmtp 1.1.23 source archive was downloaded from SourceForge; its SHA-256 matched the checksum in the local Homebrew metadata:

`74a2b6e8cb4a0304e95b995496ea3ac644c29371649b892b856e22f12a0bdeed`

The public `libmtp.h` header does not expose PTP response containers or the output count for `GetNumObjects`. To obtain exact response codes and counts, the local diagnostic program used internal PTP functions and data structures from that exact release's `src/ptp.h`. This is a version-specific internal ABI, not a stable public libmtp API. The program source is `../../tools/phase13-mtp/mtp_readonly_probe.c`, and its ABI declarations are in `../../tools/phase13-mtp/libmtp_ptp_abi.h`.

Compile from the repository root on the Mac:

```sh
clang -Wall -Wextra -Werror \
  -I/opt/homebrew/Cellar/libmtp/1.1.23/include \
  -I/opt/homebrew/Cellar/libusb/1.0.30/include/libusb-1.0 \
  tools/phase13-mtp/mtp_readonly_probe.c \
  /opt/homebrew/Cellar/libmtp/1.1.23/lib/libmtp.a \
  -L/opt/homebrew/Cellar/libusb/1.0.30/lib -lusb-1.0 -liconv -lobjc \
  -framework IOKit -framework CoreFoundation -framework Security \
  -o /tmp/mtp_readonly_probe
```

Run while the Switch is in MTP mode:

```sh
/tmp/mtp_readonly_probe \
  > reports/project-zero-local/raw/phase13_mtp/probe_records.jsonl \
  2> reports/project-zero-local/raw/phase13_mtp/probe_diagnostics.txt
```

The tool checks the device's declared operation list before GetStorageIDs, GetStorageInfo, and GetNumObjects. GetDeviceInfo also occurs when initializing the MTP session; the explicit query records the response code and fields. The program does not call GetObjectHandles, GetObjectInfo, GetObject, GetThumb, or any write operation.

## Device results

The device declared: `0x1001 GetDeviceInfo`, `0x1002 OpenSession`, `0x1003 CloseSession`, `0x1004 GetStorageIDs`, `0x1005 GetStorageInfo`, `0x1006 GetNumObjects`, `0x1007 GetObjectHandles`, `0x1008 GetObjectInfo`, `0x1009 GetObject`, and `0x100a GetThumb`.

Executed requests and actual responses:

| Operation | Code | Declared | Result | Time |
|---|---:|---|---|---|
| GetDeviceInfo | `0x1001` | yes | `0x2001 OK` | 00:21:50.827 |
| GetStorageIDs | `0x1004` | yes | `0x2001 OK`; storage `0x00030001` | 00:21:50.827–.828 |
| GetStorageInfo | `0x1005` | yes | `0x2001 OK` | 00:21:50.828–.829 |
| GetNumObjects — root, all formats | `0x1006` | yes | `0x2001 OK`; count `3` | 00:21:50.829 |

StorageInfo reported storage type `0x0001` (fixed ROM), filesystem `0x0002` (generic hierarchical), access `0x0001` (read-only), and description `Album`. Capacity and free bytes were `18446744073709551615`; free objects were `4294967295`. These are maximum unsigned/sentinel values, not usable capacity measurements. `GetNumObjects` used `format_code=0x0000` and root association handle `0xffffffff`; it returned only an aggregate count, without names or handles.

In both live runs, libmtp warned that `VendorExtensionID=0xffffffff` and therefore the device might “typically” be PTP, although VendorExtensionDesc reported `nintendo.com: 1.0`. This warning comes from the host library's heuristics; the standard MTP requests in the measurement still succeeded. It is not a console error.

The JSONL records retain time, request code, declared support, response code, and raw response fields. The requested `raw/phase13_mtp/device_info.json`, `storage_info.json`, and `operations.json` are derived from them. The `mtp-detect` baseline is in `mtp_detect_baseline.txt`; warnings are in `probe_diagnostics.txt`.

“Raw fields” here means the exact decoded PTP response fields and response codes returned by internal functions in libmtp 1.1.23; no USB packet trace was captured and no data-object content was saved.

## Unsuccessful GetNumObjects variant

The first read-only attempt through `LIBMTP_Custom_Operation` used storage `0x00030001`, format `0`, and association `0`. The device returned `0x2009 InvalidObjectHandle` (the libmtp wrapper reported `-1`). The only repeat was the standard root query with association `0xffffffff`, whose root meaning is documented in Microsoft's MTP implementation guide; it succeeded with a count of 3. The rejection of association handle zero is recorded as a parameter-dependent response, not a vulnerability. Raw outputs are `probe_stdout.jsonl` and `probe_ptp_debug.txt`; the structured record is in `operations.json`.

## Device properties

DeviceInfo returned an empty `DevicePropertiesSupported` list and did not include `GetDevicePropDesc` (`0x1014`) or `GetDevicePropValue` (`0x1015`) in the supported operations. These requests were therefore not sent. The device declared six event codes (ObjectAdded/Removed, StoreAdded/Removed, ObjectInfoChanged, StorageInfoChanged); no event was forced or changed.

## What this adds beyond `mtp-detect`

`mtp-detect` had already shown the declared operation codes and sentinel StorageInfo values. This measurement added:

1. Response codes `0x2001` for successful DeviceInfo, StorageIDs, StorageInfo, and GetNumObjects.
2. An executed root GetNumObjects request returning `3`, without enumerating objects.
3. Exact timestamps and response fields in JSON files.
4. Confirmation that the device declares no device properties, so property-description/value requests were correctly omitted.
5. A repeatable response difference between association `0` and the root marker `0xffffffff`.
6. A physical MTP → HID → MTP transition after standard UI actions and reactivation.
7. A Storage ID change between the first MTP mode and the reactivated mode (`0x00030001` → `0x00040001`), while an immediate repeat in the same mode did not change the ID.

No security flaw was found. A count of three MTP objects does not identify them and provides no evidence of system-data access or a Homebrew entry point.

## State comparison: A, B0, and B1

After the user exited MTP mode through the standard UI, the USB function changed from MTP (`057e:201d`, `06/01/01`, three endpoints) to HID (`057e:2000`, `03/00/00`, one endpoint). macOS assigned the interface to the system `AppleUserUSBHostHIDDevice`. No HID data was read or sent.

After the user reopened the official copy screen, MTP returned with its original VID/PID and interface class. The B1 read-only probe succeeded with `0x2001 OK` responses. DeviceInfo declared the same operations and empty device-property capabilities. The Storage ID changed from `0x00030001` in A to `0x00040001` in B1. A further probe 12 seconds later, without a mode change, again returned `0x00040001` and object count 3. This shows a change between modes and stability during repeated measurements in an active mode; the cause is undetermined.

B1 times: GetDeviceInfo `00:24:33.312`, GetStorageIDs `00:24:33.312–.313`, GetStorageInfo `00:24:33.313–.314`, GetNumObjects `00:24:33.314`. Repeat: GetDeviceInfo `00:24:45.034–.038`, GetStorageIDs `00:24:45.038–.039`, GetStorageInfo `00:24:45.039`, GetNumObjects `00:24:45.039–.040`.

B1 raw records: `raw/phase13_mtp/state_b1_ioreg_tree.txt`, `state_b1_usb_devices.txt`, `state_b1_usb_interfaces.txt`, `state_b1_probe_records.jsonl`, and `state_b1_probe_diagnostics.txt`. Repeat probe: `state_b1_repeat_records.jsonl` and `state_b1_repeat_diagnostics.txt`. Machine-readable comparison: `raw/phase13_mtp/state_comparison.json`.

Both requested MTP measurements are complete. If further protocol characterization is needed, the next safe test would repeat only the read-only MTP probe after another standard mode restart and record whether the Storage ID changes again. There is currently no reason to enumerate objects or inspect their contents.

## Sources and credibility

1. [libmtp 1.1.23 SourceForge release](https://sourceforge.net/projects/libmtp/files/libmtp/1.1.23/) — primary upstream source archive; its SHA-256 was checked against the local Homebrew formula checksum. A separate GPG signature was not checked. High confidence for the implementation and internal ABI of this exact version.
2. [MTP Responder Development Guide, Microsoft](https://download.microsoft.com/download/3/D/A/3DA4C937-ABCA-43F1-A5D7-8FF4C8584FAF/MTP%20Responder%20Development%20Guide.pdf) — official documentation for protocol operations and the root parent value; medium-high confidence for general MTP behavior, not Nintendo's implementation.
3. [Homebrew Formulae: libmtp](https://formulae.brew.sh/formula/libmtp) — package/dependency source and checksum for the archive; high confidence for distribution metadata, not the console's protocol behavior.

All links were checked on 2026-10-31. The console was not modified, Album contents were not read, and no unknown or write operations were performed.

## SHA-256 checksums for local outputs

- `../../tools/phase13-mtp/mtp_readonly_probe.c`: `42740c5c4518f1ec518238e48ff257c3e7d77f80fb5ffbef0c6d3614f6e319f9`
- `../../tools/phase13-mtp/libmtp_ptp_abi.h`: `33f1c0f5b5f17c1a2beb8fc8af496512525838737dd2a045b82eff3a47df23d5`
- `raw/phase13_mtp/device_info.json`: `c15b9e9c2cddb5da59e5014f9d60f2fbd6f627d8562e365d869f7868375bf4b4`
- `raw/phase13_mtp/storage_info.json`: `8cb399cb1696cbbff7f126133ad57f00763b05193ddcccef817fabe2ffc8d210`
- `raw/phase13_mtp/operations.json`: `f3834d925dea5f458c898f2882045b217f9b406275e88adb256e9ae577e0ef5c`
- `raw/phase13_mtp/probe_records.jsonl`: `16e8fda9da0cb260039855c0ce82756b50a43f2c3a7de267c601815d209fca0c`
- `raw/phase13_mtp/state_b1_probe_records.jsonl`: `2af61127b95df51125a0165ba5eacbbf4d0348ef8f109fd87e9a17424e3feb64`
- `raw/phase13_mtp/state_b1_repeat_records.jsonl`: `e3a00045bc879195a358b56b3a06c85666b29082ae76ad3a5f6b3bb6b4dfcd8e`
- `raw/phase13_mtp/state_comparison.json`: `2cb8c036f8f10c0d4528626ffa975f5f14b80d4e3076c95f18122dc9ff542b94`

## State B0 — after standard MTP exit

After the user pressed B on the copy screen, macOS still enumerated the device, but its configuration changed:

- PID changed from `0x201d` to `0x2000` (VID remained `0x057e`).
- MTP interface `06/01/01` disappeared.
- One HID interface appeared: `03/00/00`, interface 0, one endpoint; macOS assigned it to system `AppleUserUSBHostHIDDevice`.
- IOKit recorded HID usage page `0x06`, usage `0x20`, and an input-report counter. HID report contents were neither read nor sent; this fact alone does not establish their meaning.
- The USB 2.0 high-speed connection and product string `Nintendo Switch` remained active.

Raw IOKit outputs after exiting MTP are `raw/phase13_mtp/state_b_ioreg_tree.txt`, `state_b_usb_devices.txt`, and `state_b_usb_interfaces.txt`. This is physical evidence of a USB function-mode change after a standard UI action. It does not mean the HID interface provides command or diagnostic access; its protocol was not tested.

The user then reopened the standard copy screen. MTP returned with VID/PID `057e:201d` and interface `06/01/01`. The B1 read-only probe succeeded with `0x2001 OK` responses; details are in “State comparison: A, B0, and B1” and the raw JSONL outputs.
