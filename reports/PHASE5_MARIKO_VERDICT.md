# Phase 5 — verdict for Mariko / HOS 23.0.1

## Classification: B remains, with the same caveat

There is a publicly reported Gezine claim of a userland exploit for both Switch 1 and Switch 2; compatibility with Mariko/T210B01 is not confirmed. "B" classifies the public announcement of Switch 1, not the availability of a public executable package.

No reproducible PoC, source code, exact Mariko identifier, HOS 23.0.1 build or independent test was added to today's delta-check. X original statuses return a 403 on load, leaving them unauthenticated over this channel; 403 does not disprove content. Secondary reports describe Gez's later Switch 2 demonstrations and claims, but do not bridge the missing evidence for the original Switch Mariko.

Ns2jb remains explicitly a Switch 2 project with HOS 23.0.1. Nintendo's official update for the original Switch still lists 23.0.1 as the latest version and describes a functional fix. Switchbrew does not release a new security patch with 23.0.1; The CVE-2026-82079/ldn fix is ​​bundled with 23.0.0 and is therefore already included in 23.0.1.

## What can be claimed

- **Author's Claim (E0/E1 Publication Evidence):** Gezine announced userland exploit for Switch 1/2; firmware range "all fw" is the author's claim. There is no public implementation detail or version test.
- **Secondary note:** Switch2Unlock still lists the exploit as unreleased in October; other secondary records describe an unpublished physical-cartridge direction and a Switch 2 HDMI dump.
- **Primary state of ns2jb:** upstream GitLab marks it as Switch 2 jailbreak; it's not a confirmation Mariko.
- **Official HOS delta:** Nintendo lists 23.0.1 as the current version, with a functional issue fixed. A newer original Switch version is not announced.
- **Phase 5 synthetic results (E1/E2 model):** only test the local Python model, not the Nintendo implementation.
- **Physical Test/Static HOS Analysis for Switch V2:** none.

## Practical conclusion

For Nintendo Switch V2 Switch V2 / Mariko T210B01 / HOS 23.0.1, software-only homebrew path without modchip is not confirmed according to publicly verifiable evidence. The classification does not change and it is not a proof of the absence of an error.

Only reproducible proof tied to a specific Mariko SKU/SoC and HOS 23.0.1 build, along with a public description/artifact, a precise privilege boundary, and independent confirmation would change the verdict. No such evidence has been found at this stage.
