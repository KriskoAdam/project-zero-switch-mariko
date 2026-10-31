# PROJECT ZERO — Phase 11: physical device research

## Conclusion

On a stock Switch, the user read HOS **23.0.1**. The system shows an inserted microSD and states **119GB available space**. The user also confirmed the internet connection.

At first, the MacBook only saw power. After manually running the Switch's official "Copy to PC via USB" feature, the console announced a PC connection and macOS listed the USB MTP interface. After the official disconnect, the MTP interface disappeared, but the USB device remained enumerated with a different PID and HID interface. No files were read or transferred.

This confirms standard stock USB functionality on a physical device, **not a vulnerability or a Homebrew entrypoint**. The Mariko/T210B01 model has not been independently confirmed; The USB descriptor does not specify it.

## Phase A — macOS baseline before connection

| Area | Observation | Classification |
|---|---|---|
| OS/Architecture | macOS 27.0.1, build 26A434, `arm64` | Confirmed on macOS only |
| USB before connecting | Apple "USB2.0 Hub", VID `0x05AC`, PID `0x8015`, device class `0x09`, subclass `0`, protocol `1`, link 480 Mbit/s; Switch did not appear | Confirmed only on macOS |
| USB diagnostics | Available: `/usr/sbin/system_profiler`, `/usr/sbin/ioreg`, `/usr/sbin/diskutil`. `lsusb` and `usbprober` were not found in PATH. `system_profiler SPUSBDataType` did not return a usable dump; I/O Registry was used. | Confirmed only on macOS |
| | `lo0`, `gif0`, `stf0`, `ap1`, `en0`, `awdl0`, `llw0`, `utun0`, `nan0`, `utun1`–`utun5`; `en0` active. IP and MAC addresses were not recorded. | Confirmed only on macOS |
| `networksetup` | Installed but listing hardware ports failed with `AuthorizationCreate() failed: -60008`. | Not verified by this tool |
| External disks/SD | `diskutil list external` failed: DiskManagement framework was not available in the session. I/O Registry showed internal non-removable media; `/Volumes` contained system volumes. An external SD reader/card was not connected on the Mac. | Confirmed with | diagnostics limitation
| SD file system | SD card remained in Switch; Mac didn't see her. | Unverified on Mac |

`sudo` was not used; disks would not mount, unmount, or write. SD content was not read.

## Phase B — USB observation

| Status | MacOS Observation | Classification |
|---|---|---|
| Cable connected, before starting official USB function | User confirmed charging. In the given snapshot, the macOS Switch USB device was not enumerated. | Charging: confirmed by user on physical device. USB: Confirmed on macOS only. |
| Switch in official screen "Copy to PC via USB" | User reported "connected to PC". I/O Registry showed Nintendo Switch, VID `0x057e`, PID `0x201d`, link 480 Mbit/s. Device descriptors indicated class/subclass/protocol `0/0/0`. | UI: Confirmed by user on physical device. USB descriptors: only confirmed on macOS. |
| USB interface in this mode | I/O Registry created `IOUSBHostInterface` named `MTP@0`, with `bInterfaceClass=6`, `bInterfaceSubClass=1`, `bInterfaceProtocol=1`. | Confirmed only on macOS |
| After official disconnection in Switch UI | User reported disconnection. Mac still saw Nintendo Switch, VID `0x057e`, PID `0x2000`, link 480 Mbit/s. MTP interface disappeared; left interface `IOUSBHostInterface` with class/subclass/protocol `3/0/0`. | UI: Confirmed by user on physical device. USB: Confirmed on macOS only. |
| Content data | MTP client or Album did not open, nothing was copied, read or changed. | Confirmed by the scope of work performed |

The exchange of standard USB enumeration requests and the acquisition of descriptors is data communication. No screenshots/videos or other user files were transferred. The USB signature/serial fields were not copied to the report.

Nintendo says the feature is for copying screenshots/videos; macOS may require MTP-compatible software and does not guarantee compatibility. No MTP program was installed. [Official Nintendo Support](https://support.nintendo.com/jp/switch/data_management/screenshot_movie/index.html), checked 2026-10-30.

## Phase C — official system interfaces

| Interface | Observation | Classification |
|---|---|---|
| System Version | User from System Settings → System read `23.0.1`. | Confirmed by user on physical device |
| Data management | The user confirmed that the stock system shows the microSD card. | Confirmed by user on physical device |
| Available location | UI states `119 GB available`. It's free space, not total capacity. | Confirmed by user on physical device |
| Internet | The user reported that the console is connected. The Wi‑Fi name, IP, and password were not recorded. | Confirmed by user on physical device |
| USB media-copy | Stock function on the console showed the connection to the PC and the MTP descriptor on the Mac. | UI: physical device; descriptors: macOS |

## Phase D — evaluation

- **Confirmed on physical device by user:** HOS 23.0.1, microSD recognition, 119GB free space, internet connection, charging and USB UI status messages.
- **Confirmed only on macOS:** USB VID/PID, link speed, MTP interface during official media-copy function and interface class `3/0/0` after disconnection.
- **Derived:** exchange of USB descriptors means standard USB data enumeration; by itself it does not demonstrate access to files or other system interfaces.
- **Unverified:** exact SoC/Mariko SKU, microSD full capacity and filesystem, content MTP transfers and any vulnerable or privileged interface.

Homebrew/payloads, exploit attempts, recovery/bootloader modes or firmware operations were not launched. No custom USB commands were used, keys extracted or firmware read. The results do not prove a vulnerability or a path to Homebrew without a modchip.
