# Agent 1 — Mariko Boot Chain Researcher

- **Finding:** No public reproducible software-only entry for V2 Mariko/T210B01 on 23.0.1 found. Fusée Gelée affects vulnerable Erista Boot ROM; Mariko has hardware Boot ROM fixes. RCM is a recovery mode, not proof of exploitable ROM.
- **Compatibility:** Erista exploit excluded. Mariko boot protections apply by hardware family; no exact Switch V2 unit evidence. HOS 23.0.1 not validated by a PoC.
- **Evidence quality:** Switchbrew and Atmosphère primary project docs are technically useful; they are not a live Switch V2 test.
- **Unresolved:** Public exact-revision PoC; exact fuse state is unknown and was not queried.
- **Sources:** [Switchbrew fuse registers](https://switchbrew.org/wiki/Fuse_registers), [Atmosphère fusee](https://github.com/Atmosphere-NX/Atmosphere/blob/master/docs/components/fusee.md), [NH Switch Guide](https://switch.hacks.guide/).

