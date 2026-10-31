# PROJECT ZERO Phase 21 — WebApplet HOS 23.0.1 Analysis

Date: 2026-10-31

## Outcome

No WebApplet NSO, matching NPDM, build manifest, or BrowserDll/SystemData artifact exists in the inspected workspace. No firmware binary was downloaded or extracted. The official Nintendo update page confirms that HOS 23.0.1 was released on 1 October 2026 and directs users to update through the console; it does not publish the WebApplet executable or a component hash. Therefore hash, format, binary identity, symbols/imports/exports, segment layout, exact permissions, and target-specific disassembly could not be verified.

This report records a focused public-source architecture review and the precise artifact gate. It is not static analysis of HOS 23.0.1 and does not establish a vulnerability or an entry point.

## Local artifact check

Read-only searches were run from the repository root:

```sh
find .. -type f \( -iname '*webapplet*' -o -iname '*.npdm' -o -iname '*.nso' -o -iname '*.nca' -o -iname '*.kip' \) -print
find . -maxdepth 4 -type f \( -iname '*web*' -o -iname '*npdm*' -o -iname '*nso*' \) -print
```

No HOS WebApplet, NPDM, NSO, NCA, or KIP was found. The only web-named project items were source documentation and prior Phase 12 HTML/runtime logs. Phase 18/19 app ELF/NRO are project-built homebrew samples and are not substitutes. No firmware contents, keys, private serials, or console secrets were accessed.

## Publicly documented architecture

The following details come from community reverse-engineering documentation. Unless a version is explicitly stated, do not treat these as a verified Switch 1 HOS 23.0.1 binary fact.

| Boundary / component | Publicly documented behavior | Evidence limits |
|---|---|---|
| Applet identity and invocation | Switchbrew labels the general WebApplet with program ID `010000000000100A` and applet ID `0x13`; it says the launching title supplies the initial URL. Offline WebApplet is ID `0x17`; captive portal is WifiWebAuthApplet ID `0x19`. | Community-maintained mapping; not checked against a 23.0.1 title database or NPDM in this project. |
| Navigation policy | General WebApplet is documented as whitelist-restricted; WifiWebAuthApplet is documented without that navigation whitelist. The source says this affects page navigation, while JavaScript network requests are a separate path. | Does not establish the exact 23.0.1 whitelist/configuration or imply arbitrary access or a security defect. |
| Shared browser runtime | The web-applet documentation places OSS/NetFront NROs in the shared BrowserDll SystemData, used by all web applets; much web content is also there. It describes core NRO paths and browser data. | This means the WebApplet main NSO and NPDM alone do not contain enough code/data to characterize the full web engine. The documentation is not an exact-build manifest. |
| Process services | Public NPDM notes list common web-applet service access and version transitions: `ns:am` replaced by `ns:web` from 3.0.0; `htcs:sys` added at 17.0.0 and removed at 18.1.0; `bsd:u` replaced by `bsd:a` from 19.0.0. WebApplet also has `ntc`; Offline and authentication applets differ. | Exact available service set must be read from the target NPDM. A versioned community table is not a substitute for the target artifact. |
| Filesystem permissions | The source documents SystemSaveData for web applets and ApplicationInfo for WebApplet/Offline, used for specified manual content and WebApplet's accessible-URL whitelist. It says known applets do not mount SD directly. | Not directly confirmed for this HOS build. These claims describe capabilities, not proof that page content can access those services directly. |
| Applet IPC / browser bridge | Public documentation describes applet argument/return storage, interactive WebSession messages for Web/Offline, and a JS `window.nx.sendMessage` path gated by the `JsExtensionEnabled` TLV. | Phase 12 did not establish that this flag is enabled for the target WebApplet configuration. Neither the bridge nor its native handlers were inspected in a binary here. |
| Firmware change record | Nintendo lists HOS 23.0.1 as released 1 October 2026 and describes a fix for software occasionally taking a long time to start, pause, or close in 23.0.0. | The changelog says nothing about WebApplet binaries, hashes, browser versions, or security patches. |

Sources:

- [Nintendo Switch System Update Information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html), official support page, retrieved 2026-10-31. Supports version/date and user-facing update notes only.
- [Switchbrew Internet Browser](https://switchbrew.org/wiki/Internet_Browser), community reverse-engineering documentation, retrieved 2026-10-31. Supports the applet/whitelist/BrowserDll/WebSession descriptions above, but is not an exact 23.0.1 primary artifact.
- [Switchbrew NPDM](https://switchbrew.org/wiki/NPDM), community format/capability documentation, retrieved 2026-10-31. Supports NPDM structure and documented capability interpretations; target permissions remain unverified.
- Existing local observation: `docs/WEB_RUNTIME.md` and `tools/phase12-web-runtime/`. The stock WifiWebAuthApplet displayed the benign local page and the recorded DOM/network APIs worked in that single session. That does not identify or exercise the separate general WebApplet executable and does not prove a vulnerability.

## What the existing tools could establish if the gate were met

- `scripts/inspect_switch_artifact.py` can hash and validate a documented subset of NSO/NPDM headers and metadata. It does not authenticate provenance/signatures, implement full capability semantics, or decompress NSO payloads.
- `scripts/inspect_arm64_binary.py` can analyze ELF/AArch64 symbol ranges and a bounded entrypoint CFG. It cannot currently load a Switch NSO directly.
- Ghidra was verified for a host-built ELF, not for a Switch NSO/WebApplet binary. A Switch-specific Ghidra loader was not verified.
- Capstone/pyelftools/LIEF were tested on host-built ELF. REA was not demonstrated on an HOS artifact in the reviewed evidence.

Thus a compressed NSO, even if obtained lawfully, would not yet be directly disassemblable by the current path. The target executable must be provided in an authorized inspectable representation, or a separate compliant decompression/loader implementation must first be validated against a trusted independent implementation. Do not claim the current parser performs this step.

## Required artifacts and acquisition result

For a meaningful, build-specific WebApplet investigation, the minimum artifact set is:

1. The Switch 1 HOS 23.0.1 main executable for program ID `010000000000100A` (preferably unencrypted and uncompressed ELF/AArch64 or NSO, with a documented legitimate source).
2. Its matching `main.npdm` (or equivalent process metadata), retaining the program ID and build association.
3. A trustworthy identity record: official/public component manifest or legally supplied provenance, target model family, HOS version/build, file lengths and SHA-256 values. A filename or user-agent string is not enough.
4. BrowserDll/SystemData for that same build: NetFront/OSS core NROs and associated browser data/whitelist. These are needed to inspect engine code and configuration because the applet shares its engine from SystemData.
5. If examining applet-to-native messages, the applet configuration/argument schema and the exact observed `JsExtensionEnabled`/related TLV settings. Do not infer the flag from the JavaScript surface alone.

Acquisition attempt/result: the official Nintendo update reference located in this phase describes installation via the console and contains no downloadable executable/NPDM or public file hashes. No official public WebApplet binary source was found in this bounded search. We did not download proprietary firmware, extract from the console, decrypt a container, obtain keys, or use unofficial firmware mirrors. Consequently the requested target artifacts could not be obtained through a verified legitimate public channel in this phase.

## Security-relevant interface map

```text
Launching title
  └─ applet launch + argument storage / initial URL
       └─ WebApplet main process (process permissions from matching NPDM)
            ├─ URL/whitelist policy and applet configuration
            ├─ applet IPC / WebSession message boundary (where enabled)
            ├─ Horizon services allowed by process SAC/capability metadata
            └─ shared BrowserDll SystemData
                 └─ NetFront/OSS NROs + browser data/resources
                      └─ remote/local page parsing and JavaScript execution
```

This is a public-documentation-derived map, not a recovered HOS 23.0.1 call graph. Important unresolved relationships include which exact service calls the WebApplet binary makes for page/IPC operations; whether and where JS extension messages are enabled; exact memory/process flags, service ACL, filesystem control and kernel capabilities in its NPDM; and the version/hash/configuration of the shared BrowserDll on Switch 1 HOS 23.0.1.

## Determination

The static WebApplet investigation is **blocked on artifacts**. No binary analysis was performed, and no exploitability conclusion can be drawn. The architecture review improves the artifact request: obtain not only the WebApplet NSO/NPDM, but also the matching BrowserDll SystemData and build identity. Reconsider analysis only when an authorized, integrity-verifiable set is available in a format the tools can inspect. Until then, the most accurate result is an evidence-backed public architecture map plus an explicit unknown list—not a synthetic firmware substitute.
