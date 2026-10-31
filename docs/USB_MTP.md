# USB and MTP observations

The standard user-facing “copy to computer over USB” feature exposed Nintendo VID/PID `057e:201d` and a USB MTP interface (`06/01/01`) in the recorded state. The captures in `reports/raw/` have been scrubbed of USB serial values.

Across nine standard read-only sessions, DeviceInfo, declared operation/event lists, StorageInfo response behavior, and root object count were stable. The Storage ID changed from `0x00040001` to `0x00050001` after the user ended and restarted MTP; each value was stable across three sessions in its measured group. Capacity fields were sentinel values and must not be read as SD-card capacity. DeviceInfo declared more operations than this project executed; object listing and file-reading operations were intentionally not sent.

The exact CloseSession wire response was hidden by libmtp's public API. The post-replug state could not be measured because macOS did not enumerate the device. The experiment found no reproducible security anomaly and does not offer a homebrew route. See `reports/project-zero-local/PHASE13_LIVE_MTP.md` and `PHASE14_MTP_STATE_MACHINE.md`.
