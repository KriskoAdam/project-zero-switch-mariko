# Current research findings

## No demonstrated entry point

No reproducible, publicly evidenced software-only homebrew entry point for Switch V2 Mariko on HOS 23.0.1 has been demonstrated by this project. This is not proof that no undisclosed vulnerability exists.

## Narrow observations

1. **Web auth applet:** a benign local test page ran ordinary DOM and network API checks in a stock Wi-Fi authentication applet session. This establishes limited JavaScript runtime behavior for that session, not an exploit, native execution, or a Mariko-specific bug.
2. **USB/MTP:** the standard USB MTP interface was available when the user activated “copy to computer over USB”. Read-only operations succeeded. A storage identifier changed after a standard MTP mode restart; the observed behavior was consistent within each group and no security impact was shown.
3. **libnx ABI:** the Phase 7 host test resolved a callback buffer capacity issue in a public SDK/library call chain. It is not HOS code and requires already-running Homebrew, so it is not a first entry point.
4. **Artifacts:** no target HOS executable/NPDM was available in the local archive. Ghidra/Capstone results from generic or SDK artifacts must not be represented as analysis of stock HOS.
5. **Public exploit claims:** ns2jb/other public materials must be evaluated against exact platform, SoC, firmware and chain boundaries. A Switch 2 claim or author statement of limited Switch 1 testing is not evidence of Mariko 23.0.1 compatibility.

Full source-specific detail and uncertainties are preserved in `reports/`.
