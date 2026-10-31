# PROJECT ZERO Phase 25 — BrowserDll Target Research

Date: 2026-10-31  
Target: original Nintendo Switch V2 / Mariko (T210B01), HOS 23.0.1  
Scope: Correct the browser-applet target mapping, trace the public version metadata and dependencies, and search local user backup locations. No console interaction, firmware acquisition, key access, or synthetic firmware construction.

## Result

No HOS binary or backup was found. We therefore did not calculate target-file hashes or run NSTool, the PROJECT ZERO parser, Ghidra, or REA on Nintendo code. The new technical result is a **target-identification correction**: for WifiWebAuth on HOS 22.0.0 and later, Switchbrew's Applet Manager service table maps applet ID `0x19` to program ID `0100000000001043`, while the older program ID `0100000000001011` is the pre-22.0.0 mapping. The title list labels `0100000000001043` as `openWeb`; `0100000000001011` is marked stubbed from 22.0.0+. Thus the relevant 23.x executable to request is the 22+ `openWeb` title and its matching NPDM, not an assumed standalone `010...1011` binary. This is a community-source mapping, not local executable verification.

## Corrected target map

| Role | Switch 1 title / identifier | Publicly listed version information | Interpretation and confidence |
|---|---|---|---|
| WebApplet / LibAppletWeb | Program ID `010000000000100A`; applet ID `0x13` | Title list says updated through 22.0.0 and stubbed at 22.0.0+ | Not the right single target for the stock captive-portal path on 23.x. This phase did not inspect its stub binary. Medium confidence in the public catalog claim. |
| WifiWebAuth applet type | LibraryApplet ID `0x19` | AM service mapping: `0100000000001011` on 1.0.0–21.2.0; `0100000000001043` on 22.0.0+ | Exact redirect shown in the community service table. High confidence that the source documents this ID mapping; no local runtime call trace. |
| `openWeb` applet program | Program ID `0100000000001043` | 22.0.0 `v1476396108`; 22.5.0 `v1481638368`; 23.0.0 `v1543505072` / `23.0.0.1200` | Current public candidate executable/NPDM for the 23.x WifiWebAuth applet path. It is a shared applet program; the applet type selected by AM is what makes a launch WifiWebAuth. Do not conflate applet ID with program ID. |
| `systemWeb` applet program | Program ID `0100000000001042` | 22.0.0, 22.5.0, and 23.0.0 title versions appear in the public title list | Separate system web applet; not a substitute for WifiWebAuth. Both systemWeb and openWeb are listed as having all files updated in 23.0.0. |
| BrowserDll shared SystemData | Title ID `0100000000000803` | 23.0.0 title version `v1543505072` / `23.0.0.1200` | Shared browser data for web applets, including OSS NROs. The public 23.0.0 changelog lists changes to buildinfo, UI/browser data, and `/nro/netfront/`. |
| HOS 23.0.1 delta | System version 23.0.1 | Switchbrew's 23.0.1 page lists `sdb` and `SystemVersion:/file` changes | Public metadata suggests BrowserDll and openWeb remain at their 23.0.0 title version in 23.0.1. This is an inference from title/update catalogs, not a hash comparison or a Nintendo-signed manifest. |

The title version `23.0.0.1200` is a component/title revision, not the overall HOS version `23.0.0` or `23.0.1`. The `23.0.1` public changelog says it fixes a launch/pause/close delay introduced in 23.0.0; it does not expose component bytes or an authenticated file manifest.

## Version and dependency history

- **HOS 22.0.0:** Switchbrew's current title list marks legacy WebApplet `010000000000100A` and legacy WifiWebAuth program `0100000000001011` as stubbed from 22.0.0+. Its AM-services table maps the `LibraryAppletWifiWebAuth` applet type to `0100000000001043` from 22.0.0 onward. The title list identifies `0100000000001043` as `openWeb`.
- **HOS 23.0.0:** the 23.0.0 change page lists BrowserDll among updated SystemData. It specifically lists `/buildinfo/buildinfo.dat` and `/nro/netfront/` contents as changed. It lists both `systemWeb` and `openWeb` applet files as updated. The title list gives BrowserDll, openWeb, and systemWeb title version `23.0.0.1200`.
- **HOS 23.0.1:** the public change page lists only `sdb` and `SystemVersion:/file` changes. Combined with the title list, the strongest public candidate set for the user's 23.0.1 runtime is therefore the Switch 1 BrowserDll and `openWeb` artifacts at component version `23.0.0.1200`. Exact reuse on a particular Mariko unit remains unverified until hashes or the actual installed content are available.

Switchbrew's Internet Browser page states that browser OSS NROs are stored under BrowserDll SystemData and shared by web applets. It also documents `shareddata:/buildinfo/buildinfo.dat` and NetFront runtime version strings. Public history mentions modules such as `oss_wkc.nro` and NetFront NRO paths, but it does not provide the 23.0.0.1200 NRO files or hashes. The browser engine code is therefore still unavailable for inspection.

## Security boundary and previously measured runtime

The project has a physical-console observation from Phase 12, preserved in `../PROJECT_ZERO/PHASE_12/results/phase12_web_results.jsonl`: the console's captive-portal session reported user agent `Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/613.0 ... NF/6.0.3.31.11 NintendoBrowser/5.1.0.55481`; it completed ordinary DOM/event, Fetch, XHR, and WebSocket tests. The passive JS surface check found `WebAssembly`, `Atomics`, and `SharedArrayBuffer` undefined; `Worker` and `MessageChannel` existed. The bridge probe did not invoke native bridge functions. This is a prior physical runtime result, not fresh analysis of the Phase 25 title mapping or proof of an exploit boundary. The Switch's Mariko identity was not authenticated by that probe.

Switchbrew documents a service-access list for web applet NPDMs and describes applet IPC/launch behavior. Its Internet Browser page's explicitly `[S2] OpenWeb` service expansion is Switch 2 material and was **not** projected onto Switch 1. Without the 23.0.0.1200 `openWeb` NPDM, its actual service access-control descriptors and kernel capabilities remain unverified. Without the matching executable, JS-native bridge implementation, IPC handlers, imports/exports and reachable parsing code remain unverified. Public titles, SDK headers, and a browser User-Agent cannot substitute for those files.

## Local artifact and backup search

Inspected the project and searched file names in:

- the repository and sibling `PROJECT_ZERO` tree for NSO, NPDM, NCA, KIP, NRO, NSP, XCI, CNMT, PFS0, and BrowserDll/NetFront/WebApplet names;
- `/Users/adamkrisko/Downloads`, `/Users/adamkrisko/Desktop`, and `/Users/adamkrisko/Documents` for matching executable/container extensions and target component names.

The only NRO files found were PROJECT ZERO's own homebrew application and its release copy. The only browser-related filename match outside those was the earlier Phase 21 report. No candidate backup, HOS container, BrowserDll, NetFront NRO, `openWeb` NSO, or NPDM was found. No file contents outside those candidates were read; no secrets or console keys were searched.

## Sources and evidence quality

| Source | Date / type | Evidence used | Confidence and limits |
|---|---|---|---|
| [Switchbrew Applet Manager services](https://switchbrew.org/wiki/AM_services) | Accessed 2026-10-31; community service/title mapping | Applet ID `0x19` maps to old `010...1011` through 21.2.0 and `010...1043` at 22.0.0+. | Medium/high for what the catalog records; no local IPC trace or binary verification. |
| [Switchbrew title list](https://switchbrew.org/wiki/Title_list) | Accessed 2026-10-31; community title catalog | Maps `010...1043` to openWeb and lists title revisions through 23.0.0.1200; marks legacy WebApplet and old WifiWebAuth title stubbed at 22.0.0+. BrowserDll is `010...0803`. | Medium for title/version metadata; not official binary hashes. |
| [Switchbrew 22.0.0 page](https://switchbrew.org/wiki/22.0.0) | Accessed 2026-10-31; community changelog | Provides the version transition context; read together with title list and AM services page. | Medium; not an official binary manifest. |
| [Switchbrew 23.0.0 page](https://switchbrew.org/wiki/23.0.0) | Accessed 2026-10-31; community changelog | BrowserDll changes include buildinfo and NetFront NRO data; openWeb and systemWeb applet files updated. | Medium for component change records, no hashes or payload. |
| [Switchbrew 23.0.1 page](https://switchbrew.org/wiki/23.0.1) and [Nintendo's official update notice](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html) | Accessed 2026-10-31; community delta and official release note | Community report says `sdb` and SystemVersion file; Nintendo confirms release date and user-facing functional fix. | High for Nintendo's release note; medium for community title delta; neither publishes component hashes. |
| [Switchbrew Internet Browser](https://switchbrew.org/wiki/Internet_Browser) | Accessed 2026-10-31; community reverse-engineering documentation | BrowserDll stores shared OSS NROs and browser data; documented web-applet behavior and service caveats. | Medium for architecture summary; its Switch 2-specific service list is excluded from Switch 1 conclusions. |
| Phase 12 console log | 2026-10-30; local test log and user-operated physical console | Reports WifiWebAuthApplet UA and observed web APIs for the test page. | A for the recorded applet session only; no authenticated Mariko hardware identity, no bridge invocation, and no binary identity. |

## Conclusion and next gate

The target should now be named **Switch 1 `openWeb` program `0100000000001043` at title revision `23.0.0.1200`, launched as LibraryAppletWifiWebAuth (`0x19`), together with its paired `main.npdm` and BrowserDll SystemData `0100000000000803` at the same component revision**. This is the best public metadata-based target set for HOS 23.0.1; it is not a claim that the bytes have been acquired or independently matched to the user's console.

No actual artifact passed the identity gate. The next step remains waiting for a legitimately provided, unencrypted, provenance-backed candidate set or a clearly redistributable research dataset containing the openWeb executable + matching NPDM + BrowserDll `buildinfo` + relevant NetFront/OSS NROs. Only after SHA-256 and title/build pairing are verified should NSTool and PROJECT ZERO parsers run. The exact IPC and JavaScript bridge audit is blocked on those executable and NPDM bytes.
