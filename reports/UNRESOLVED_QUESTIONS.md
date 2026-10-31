# Open questions, sorted by priority

## 1. Is there a public reproducible chain Mariko/T210B01 + HOS 23.0.1?

- **Status:** unanswered; it was not found in the reviewed public sources.
- **Missing proof:** exact revision/firmware, reproducible PoC and independent confirmation of input all the way to homebrew; this cannot be confirmed by safe purely static research without the relevant artifact.
- **Available counterindicator:** NH Guide lists for patched/Mariko Caffeine only at 4.1.0 and modchip from 5.0.0.
- **Certainty:** high that the reviewed sources do not prove such a path; it is not a proof of non-existence.

## 2. What exactly was tested on the original Switch with ns2jb?

Unknown. The author does not mention the model (Erista/Mariko), HOS, reproducible code or independent test. "Switch 1" alone cannot be applied to Switch V2/T210B01. [Article author](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/), [repository](https://gitlab.com/pepsipu/ns2jb).

## 3. What is the exact technical scope of CVE-2026-82079?

Nintendo advisory mentions possible information leak in proximity remote attack; Switchbrew bundles the patch with ldn in 23.0.0. A complete public description of the primitive, privileged context, Mariko reproduction and chain steps is missing. The certainty of the target impact beyond the advisor is low.

## 4. Did HOS 23.0.1 bring another security change compared to 23.0.0?

Public records do not list the security patch. Nintendo describes a functional fix for long start/pause/exit software; Switchbrew records the sdb update and leaves "security flaws fixed" blank. Legally obtained artifacts and documented binary comparison are missing.

## 5. How does the boot trust path differ on a specific Switch V2 unit?

General differences are documented, but the specific piece or fuse state has not been examined. A securely obtained, insensitive proof of a specific hardware revision is missing. Reading the secrets or manipulating the boot is not the next step.

## 6. Which old bugs have true Mariko build compatibility?

Switchbrew often lists the HOS patch without the SoC revision. The public build hash and test for Mariko are missing. The database therefore uses "unknown" where the evidence is insufficient.

## 7. Can REA analyze the HOS artifact on this Mac?

Not directly through the REA firmware parser in the current macOS server; diagnostics returns unsupported_host for firmware regions/extraction. Ghidra ARM64 is ready for a standalone supported binary. A legally provided artifact and a suitable importer are missing.

## Phase 13 — sorted experimental hypotheses (30/10/2026)

This is a priority for further safe work, not a bug claim. The degree of certainty is not expressed as a percentage. "Target evidence" distinguishes the physical observation of the applet from the confirmation of the Mariko chip; the exact SoC has still not been independently confirmed.

Legend: R = Mariko relevance, F = HOS 23.0.1 relevance, D = class of already available evidence according to `reports/EVIDENCE_REGISTER.md`, B = feasibility of secure verification, N = expected value of new knowledge, C = connection with the goal. H/M/L = high/medium/low; "block." = missing required artifact or access. Difficulty is listed separately as low/medium/high. Class E means a hypothesis without a target result.

| # | Hypothesis / testable question | R | F | D | B | Difficulty | N | C |
|---|---|---|---|---|---|---|---|---|
| 1 | Does WifiWebAuthApplet contain enumerable direct JS-native bridge globals from the tested list? | M* | H* | A | H | low | H | H |
| 2 | Are Worker, SharedArrayBuffer, Atomics and other runtime APIs available in the same WifiWebAuthApplet? | M* | H* | A | H | low | M | M |
| 3 | Does the JS API surface change between re-opening the same captive-portal page within a new applet session? | M* | H* | E | H | low | M | M |
| 4 | Are redirects and navigation in the applet limited to the original test domain? Without external targets, only the local co-origin path can be measured. | M* | H* | E | H | medium | M | M |
| 5 | Are Fetch/XHR/WebSocket callbacks only available for the same origin in this captive-portal context? | M* | H* | A | H | low | L | M |
| 6 | Does the detected User-Agent correspond specifically to the HOS 23.0.1 version and not just to the console/applet family? | M* | H* | A/C | H | low | M | M |
| 7 | Does the publicly documented configuration `JsExtensionEnabled` enable a native bridge in a specific WifiWebAuthApplet build? | M* | H* | C/E | H | high | H | H |
| 8 | What is the exact sandbox and service-permission profile of the WifiWebAuthApplet for HOS 23.0.1? | H* | H* | E | block. | high | H | H |
| 9 | Has the NetFront/WebKit patch level changed between the publicly documented User-Agent sample and this runtime? | M* | H* | A/C | H | medium | M | M |
| 10 | Is there another system web applet on stock Switch reachable by default without a special game/service? | M* | H* | C/E | H | medium | M | M |
| 11 | Is it possible to infer the availability of the system parser from the stock USB/MTP interface without sending data? | H* | H* | A | H | low | L | L |
| 12 | Is there a reproducible 23.0.1 specific applet-IPC contract in the public unencrypted SDK sources or documentation? | H* | H* | C/E | H | medium | M | H |

`*` The target device platform is declared; Mariko/T210B01 is not physically verified. HOS 23.0.1 was confirmed by a user on the same console at an earlier stage, it is not part of the current browser log.

### Evidence, safe test and informational value for individual hypotheses

1. **Bridge global:** it is supported by documented `JsExtensionEnabled`; against it, all 8 tested names on the console are absent. Physical descriptor test completed. Additional artifact needed to close configuration: exact applet TLV/metadata; without them we cannot rule out other names/accessories. High value for JS surface narrowing, low directly for HB.
2. **Web API:** physical log provides runtime results; against is that API accessibility does not show permissions. Test done; does not require a new artifact. Moderately informative when identifying runtime options.
3. **Session stability:** one physical run supports only one context; the second session is missing. The same page can be safely launched again, a new JSON log is required. Unknown variability; mean value.
4. **Navigation restrictions:** one local navigation supports applet accessibility, not redirect rules; redirect was not tested. It would require a local second endpoint, no external destinations. Exact policy unknown; mean value.
5. **Network API/origin:** successful Fetch/XHR/WS to same origin support functionality, nothing tests cross-origin. Another secure local origin would require a different port/host and CORS test. CORS unknown; low value for pre-HB.
6. **UA/build mapping:** the record gives the exact UA, but the absence of the HOS version in the UA stands against the mapping. Versioned public tables and user-reported System Version can be compared; without the HOS image, the exact build will not be verified. Medium value for context, not security impact.
7. **`JsExtensionEnabled`:** public documentation supports the existence of the TLV, the physical absence of `nx` is against its apparent activation. Without the configuration/metadata applet, the setting cannot be detected. Legal, unencrypted metadata artifact required; high value, currently blocked.
8. **Applet sandbox/service ACL:** the public service list for the applet family is indicative only, the exact 23.0.1 process profile is missing. Necessary executable + NPDM/metadata with trusted build identity. Very high target value but blocked by artifact.
9. **NetFront patch lineage:** UA and public table support version comparison, not patch status. Necessary versioned vendor changelog or binary build metadata; both are missing for exact correlation. Average value.
10. **Another stock web applet:** The public documentation names applets, but no other applet was run for this piece. Verification would require a manual standard UI action, no accounts/games; reachability identity on 23.0.1 unknown. Average value.
11. **USB/MTP parser:** VID/PID and UI document standard mode, but without sending files it says nothing about the parser. Safe passive descriptor reading is done; no further safe technical inference without a concrete artifact. Low value.
12. **Applet IPC contract in SDK/docs:** libnx/Switchbrew provide generic API and TLV hints; the exact binary contract 23.0.1 is missing. Comparing public source with public versioned docs is safe; it needs versioned metadata for the target. Medium to high value, depending on resource availability.

### Three best directions and selected experiments

1. **Passive bridge inventory on console (#1).** Already done and independently reviewed by Skeptic. Its narrow formulation ("selected named globals") was not observed; does not rule out a hidden/non-enumerable path.
2. **Exact applet config/ACL evidence (#7/#8).** Highest system flag, but stopped for missing legal unencrypted HOS executable/metadata.
3. **Exact correlation of runtime build/UA and public advisories (#6/#9).** Public review performed shows that CVE-2026-82079 is fixed in 23.0.0; The Nintendo 23.0.1 page lists a functional fix, not a full security changelog. Does not confirm target Mariko compatibility.

**First run experiment:** implement and run a passive probe descriptor in a real WifiWebAuthApplet; completed (PZ13-PHYS-01). **Most valuable next physical test:** repeat the captive-portal flow after fixing the `HEAD` handler on the local server and compare the HTTP log. The host preflight has already shown HEAD 200/no-body and GET 200. This test will only close our transport test track; it is not a security test.

The physical probe run is completed and recorded as `PZ13-PHYS-01` in `EVIDENCE_REGISTER.md`. Globals were not found in the checked list; this only disproves the narrow claim of enumerable names in this applet context. Mariko/T210B01 has not been independently verified.

An independent audit noted repeated `HEAD /` → HTTP 501 and subsequent `GET /` → 200. The cause was our own test service without `do_HEAD`; after completing the handler, the host test returned HEAD 200 with Content-Length 7996 and zero body, GET 200 with 7996 bytes. This trace is closed as a test server error, not a system anomaly.

### Public sources reviewed in consolidation

- Nintendo security advisory [CVE-2026-82079 (PDF)](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), 2026-09-10: according to the public notice, it concerns the original Switch before 23.0.0 and 23.0.0 is a fix; features "Send to Smartphone"/Mario Kart Live scenarios and QR code scanning. It does not specify Mariko/T210B01 or the exact boundary of authorizations. Therefore, it does not provide a route to 23.0.1.
- Nintendo [System Update Information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html), checked 2026-10-30: 23.0.1 release on 2026-10-01 and user-visible slow start/pause/close fix from 23.0.0. This page is not a complete security changelog.
- Switchbrew [Internet Browser](https://switchbrew.org/wiki/Internet_Browser), checked 2026-10-30: documents WifiWebAuthApplet, captive portal and `window.nx.sendMessage` only when TLV `JsExtensionEnabled` is on; it doesn't say TLV is enabled in WifiWebAuthApplet on 23.0.1. Our negative probe is consistent with this, but does not demonstrate a TLV setting or a complete absence of a bridge API.
