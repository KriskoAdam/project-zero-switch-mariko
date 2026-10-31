# Agent 3 — Horizon OS Security Researcher

- **Finding:** No known public HOS/kernel/service chain for Mariko + 23.0.1. CVE-2026-82079 is associated by Switchbrew with ldn/lp2p and fixed in 23.0.0, so 23.0.1 includes the fix.
- **Compatibility:** Switchbrew lists Mariko hardware-specific security fixes; HOS flaw table does not prove exploitability on Switch V2.
- **Evidence quality:** Nintendo advisory is primary but high-level; Switchbrew gives community reverse-engineered release details.
- **Unresolved:** Full public technical detail and independently reproduced impact of CVE-2026-82079; exact binary delta 23.0.0/23.0.1.
- **Sources:** [Nintendo advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [Switchbrew 23.0.0](https://switchbrew.org/wiki/23.0.0), [system flaws](https://switchbrew.org/wiki/Switch_System_Flaws), [fuse registers](https://switchbrew.org/wiki/Fuse_registers).

