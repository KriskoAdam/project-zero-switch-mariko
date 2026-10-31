# Project history

PROJECT ZERO grew from local research into a staged, evidence-labeled investigation. This summary records what is present in the sanitized archive; it does not recreate missing files.

- **Initial setup and early research:** project structure, toolchain work, and initial research are described in the root workspace README and later reports. No standalone Phase 1 or Phase 2 report files were present in the local archive at publication-copy time.
- **Phases 3–5:** broad public-source research, Gezine claims, vulnerability delta, and a Mariko compatibility verdict. The reports do not establish a software-only Mariko 23.0.1 entry point.
- **Phase 6:** source-grounded analysis of public libnx code with host-side tests; no target firmware binary was analyzed.
- **Phase 7:** resolved the fsdev filename callback buffer-capacity question against the documented callback contract. The reported 256-byte capacity makes the write at index 255 safe for that call path. This is a library/SDK result, not a stock Horizon entry point.
- **Phase 8:** automated host-side experiments and synthetic models; these do not establish a Nintendo-system vulnerability.
- **Phases 9–10:** reachability and artifact audits found no suitable HOS executable/NPDM for target binary analysis in the local project. Proprietary firmware was not acquired.
- **Phase 11:** owner-operated, standard USB and console UI observations. USB connection state and MTP mode were observed; no console modifications occurred.
- **Phase 12:** a benign local page was loaded through the stock Wi-Fi web-auth applet. Basic web APIs were observed; no native bridge or vulnerability was established.
- **Phase 13:** standard read-only MTP requests were executed. The libmtp interface did not expose all wire-level response details.
- **Phase 14:** nine MTP sessions were compared across user-controlled states. The Storage ID changed after MTP mode restart; other measured capabilities and responses were stable. USB state D was not measured successfully. No security anomaly was found.
- **Phase 15/16:** a native Homebrew application was developed locally, but it is explicitly excluded from this public repository in full, including source and build outputs.

See each phase report for dates, methods, source links, and the limits of its claims.
