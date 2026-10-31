# Live USB observation — 2026-10-31

## Result

At 2026-10-31 00:10–00:12 +0100 macOS only enumerated host controller `AppleT8140USBXHCI`. `ioreg` did not return any nodes `IOUSBHostDevice` or `IOUSBHostInterface`; `system_profiler SPUSBDataType` ended with exit code 0 but no output. At this point, Switch via USB was not data-visible to macOS. No USB requests sent to Switch.

## Exact commands

```sh
/usr/sbin/system_profiler SPUSBDataType -detailLevel full
/usr/sbin/ioreg -p IOUSB -w0
/usr/sbin/ioreg -r -c IOUSBHostDevice -l -w0
/usr/sbin/ioreg -r -c IOUSBHostInterface -l -w0
```

## Raw outputs

The files under `raw/usb_20261031/` preserve the outputs. Relevant `ioreg` tree:

```text
+-o Root  <class IORegistryEntry, id 0x100000100, retain 35>
  +-o AppleT8140USBXHCI@00000000  <class AppleT8140USBXHCI, id 0x100000396, registered, matched, active, busy 0 (36657 ms), retain 32>
```

`system_profiler`, USB device nodes and USB interface nodes had zero bytes. All commands ended with exit code 0.

## Interpretation

- **Confirmed on macOS:** no USB peripheral device/interface is connected/enumerated in this capture. The record does not provide VID/PID, descriptors, endpoints or association with MTP/HID.
- **Not inferred:** physical absence of cable or bracket. The device may be off/sleep, the cable may only be running power, the connector may be loose, or the console may not be in standard USB data mode. These options are indistinguishable from the host tree.
- **Console ID:** Neither model nor Mariko/T210B01 nor HOS 23.0.1 can be confirmed from this USB capture.
- **Evidence class:** host observation. No interface has yet been protocol tested.

## Another necessary action

On the Switch, wake up the screen and in the official system menu, run **System settings → Data management → Manage screenshots and videos → Copy to computer via USB connection**. Leave the cable plugged in and let me know when the UI shows that the console is connected to the computer. I then recapture just the USB device/interface descriptors and compare them to this null baseline. Nothing will be written to microSD or system areas.

## Control subscription after "connected to PC" message

User confirmed that system UI shows PC connection. Control subscriptions on Mac at 00:11:43–00:11:52 +0100 remained unchanged:

- `ioreg -p IOUSB -w0`: Root and `AppleT8140USBXHCI@00000000` only.
- `ioreg -r -c IOUSBHostDevice -l -w0`: 0 bytes, no USB device node.
- `ioreg -r -c IOUSBHostInterface -l -w0`: 0 bytes, no USB interface node.
- `system_profiler SPUSBDataType -detailLevel full`: 0 bytes, the command ended successfully.

The raw second subscriptions are files with the extension `_after_ui.txt` in `raw/usb_20261031/`. This is a discrepancy between the user reported state of the UI and what the current Mac IOKit USB tree enumerates. It is not yet possible to decide whether the UI text indicates a different phase or a data connection is not available through this cable/port; Neither the VID/PID nor the MTP/HID protocol are confirmed. No communication has taken place with the USB device beyond passively reading the tree.

### Another necessary action

While leaving the Switch at the "Copy to PC via USB" screen, unplug and replug the same USB-C cable at both ends. I will let you know when the screen shows connection again. I will simultaneously repeat the same passive enumeration. If the device is still not in `IOUSBHostDevice`, it is not possible to proceed to the MTP/HID descriptors from an available Mac/USB connection; I will not try custom USB commands.

## Enumeration after reconnecting

The user left the Switch in "Copy to PC via USB" mode, unplugged and reconnected the same cable on both ends, and confirmed that the UI was reporting a connection again. A macOS passive read then found the device `Nintendo Switch` behind a USB 2.0 hub.

### Captured data

- VID `0x057e` (Nintendo), PID `0x201d`; macOS lists `bcdUSB=0x0200`, `bcdDevice=0x0100`, USB 2.0 high-speed (480 Mbit/s).
- One visible interface: `MTP`, class/subclass/protocol `06/01/01`, interface 0, configuration 1, three endpoints according to `bNumEndpoints`.
- Addresses, directions or endpoint types are not listed in these IOKit listings. That's why I don't list them as discovered.
- `system_profiler SPUSBDataType -detailLevel full` produced empty output even after enumeration; the crucial observation comes from `ioreg`.
- The serial number was redacted in the local text listings.

### Exact commands

```sh
/usr/sbin/ioreg -p IOUSB -w0
/usr/sbin/ioreg -r -c IOUSBHostDevice -l -w0
/usr/sbin/ioreg -r -c IOUSBHostInterface -l -w0
/usr/sbin/system_profiler SPUSBDataType -detailLevel full
```

Outputs are in `raw/usb_20261031/*_reseat.txt`. Nothing was sent to the console; it was a passive reading of the macOS system registry.

### What the result proves

- **Confirmed on physical device via macOS:** after plugging in again, USB enumeration of device identified by manufacturer/product strings as Nintendo Switch is present and MTP interface is exposed.
- **Does not prove:** that MTP contains or makes available specific files; that microSD or internal storage can be read; model V2, Mariko/T210B01 or HOS 23.0.1. VID/PID and product strings alone do not confirm these hardware/firmware features. HOS 23.0.1 remains user-specified data from a previous interaction, not the result of USB enumeration.
- **Protocol in this passive measure:** MTP transactions and USB endpoints have not yet been tried. No custom commands or data were sent.

This branch met the goal of passive device recognition. Further investigation of the MTP would require a separate, strictly read-only standard read, and its result would have to be distinguished from the enumeration itself.

## Read-only MTP discovery

MTP client was missing on Mac after passive enumeration. Installed `libmtp` 1.1.23 (dependency of `libusb` 1.0.30) via Homebrew and ran:

```sh
/opt/homebrew/bin/mtp-detect
```

The command ended with a code of 0 and recognized `057e:201d` as "Nintendo Switch / Switch Lite". It listed an MTP interface, a maximum packet size of 512 bytes for IN/OUT, a device version of `23.0.1`, and a single storage entry of `Album` with permission `read only`. Capacity and free space were reported as units alone, which are sentinel values ​​and do not determine the actual storage size. The tool listed supported standard MTP operations, including reading objects, but did not request a list of objects or their contents. The raw output is in `raw/usb_20261031/mtp_detect.txt`; the serial number is redacted.

This is observing the physical console via standard MTP discovery of device information and storage metadata. The contents of the files were not read, and no write, delete, send, or format operations were performed. The device version string corresponds to the user-specified HOS 23.0.1, but itself is only metadata reported by the device, not an independent confirmation of the firmware. The product identification still doesn't distinguish the V2/Mariko from the other variants of the original Switch. The SoC identifier did not appear.

Versions of the Homebrew package and its dependencies were checked 2026-10-31 against [Homebrew Formulae page for libmtp](https://formulae.brew.sh/formula/libmtp). It's the actual package entry, not Nintendo's documentation. `mtp-detect` pointed out that the device does not have a standard MTP vendor-extension ID, although it reports `nintendo.com: 1.0`; however, it successfully completed the metadata discovery. By itself, this warning does not prove a vulnerability or code execution.

### Current conclusion to USB

The standard "Copy to PC via USB" mode exposes the limited MTP interface. macOS with libmtp can identify the product and get the basic read-only album storage metadata. Switch won't mount as a drive in macOS. Apart from MTP, no other diagnostic interface or path to system files was shown; the experiment did not provide evidence of software input for Homebrew.

## Exact USB endpoints from the active configuration

In order to supplement the addresses that IOKit did not write directly, a small reader `PROJECT_ZERO/PHASE_12/usb_descriptors.c` using libusb was created. Reads standard USB descriptors via API `libusb_get_device_list`, `libusb_get_device_descriptor` and `libusb_get_active_config_descriptor`; the device does not open or claim and does not send MTP, bulk or interrupt data transfers. USB enumeration and descriptor retrieval itself may use standard descriptor requests.

Mac reproduction with Homebrew libusb 1.0.30:

```sh
clang -Wall -Wextra -Werror \
  -I/opt/homebrew/opt/libusb/include/libusb-1.0 \
  switch-research/PROJECT_ZERO/PHASE_12/usb_descriptors.c \
  -L/opt/homebrew/opt/libusb/lib -lusb-1.0 \
  -o /tmp/pz12-usb-descriptors
/tmp/pz12-usb-descriptors
```

Result (exit 0):

```text
Nintendo Switch VID:PID 057e:201d
USB 2.00, device release 1.00, configurations 1
Active configuration value 1, interfaces 1
Interface 0 alt 0 class/subclass/protocol 06/01/01, endpoints 3
  endpoint 0x81 IN bulk max-packet 512 interval 0
  endpoint 0x01 OUT bulk max-packet 512 interval 0
  endpoint 0x82 IN interrupt max-packet 24 interval 4
```

Source SHA-256: `7e0d07e5a862f61f07111c4a800617584e73f3b195a6177e5e90941a99d50553`. Raw output: `raw/usb_20261031/usb_endpoint_descriptors.txt`, SHA-256 `db739b305ec0debeb459b2218eaa5e839fdcf768d277598c9e11fed71c8359be`.

This confirms the layout of the USB active configuration, not the availability of any data operation or storage content. IN/OUT addresses describe the direction of the endpoint from the host's point of view. The research stops here: standard read-only discovery has already confirmed the available MTP interface and its endpoints; another MTP read would touch user album objects and not add proof of reachability before Homebrew.
