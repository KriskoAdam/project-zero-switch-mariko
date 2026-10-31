# Agent 4 — Ghidra / REA Reverse Engineering Researcher

- **Finding:** Ghidra 12.2 documentation requires 64-bit JDK 25; macOS and Python 3.14 fit stated support. REA can statically inspect supplied supported binaries. Firmware inspection needs a separately configured Binwalk/Unblob provider; REA reports firmware tooling unsupported on this macOS host.
- **Compatibility:** This is tool support, not evidence about Mariko or HOS. No firmware image was supplied.
- **Evidence quality:** Official NSA Ghidra docs and REA project docs; no target artifact analysis.
- **Unresolved:** Validate Ghidra installation/provider version; REA's current live provider diagnostic expects a 12.1.x directory, which may not accept Homebrew's current 12.2. Firmware provider requires Linux and user-supplied tooling.
- **Sources:** [Ghidra setup](https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GettingStarted.md), [Ghidra release notes](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Configurations/Public_Release/src/global/docs/WhatsNew.md), [REA firmware docs](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md).

