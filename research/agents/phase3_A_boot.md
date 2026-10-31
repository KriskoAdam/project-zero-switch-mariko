# Agent A — Mariko Hardware and Boot Architecture

## Finding

No public, reproducible software entry point through the boot chain was identified for Switch V2 with Mariko/T210B01 on HOS 23.0.1. Erista Fusée Gelée (CVE-2018-6242) is a vulnerability in the Tegra X1 USB recovery Boot ROM. NVIDIA says affected older Tegra processors allow an attacker with physical access to bypass secure boot, while later SoCs are not affected. Atmosphère describes Fusée as a payload launched in RCM by exploiting CVE-2018-6242. These sources do not support transferring the Erista PoC to Mariko. [NVIDIA advisory](https://nvidia.custhelp.com/app/answers/detail/a_id/4660/~/security-notice%3A-nvidia-tegra-rcm-vulnerability), [Atmosphère Fusée](https://github.com/Atmosphere-NX/Atmosphere/blob/master/docs/components/fusee.md)

## Architecture observations

Switchbrew's reverse-engineered documentation lists Mariko IROM fuse patches: initializing unused IRAM, changing Security Engine context behavior, clearing RAM after a failed bootloader verification, an RCM stack-cookie check, and clearing crypto context and TZRAM. It also notes that Mariko uses XUSB for RCM independently of fuse state. That is a transport property, not evidence of a vulnerability. [Switchbrew Fuse registers](https://switchbrew.org/wiki/Fuse_registers)

The same page identifies Mariko FT revision 3.0 / CP revision 2.0 and a separate fuse-register map. These are family-level, reverse-engineered findings, not an audit of a specific Switch V2 unit. A Switch V2 serial prefix alone is insufficient to determine its exact fuse state or manufacturing configuration.

The Atmosphère changelog explicitly distinguishes the bootloader context for Mariko support: Fusée can start Mariko only if it has already been loaded by a bootloader with the required SE keys. The project itself does not provide a way to reach that state. [Atmosphère 0.17.0 changelog](https://github.com/Atmosphere-NX/Atmosphere/blob/master/docs/changelog.md)

NH Switch Guide currently distinguishes unpatched Erista from patched/Mariko. For patched/Mariko it lists Caffeine at 4.1.0 and a modchip at 5.0.0 or later. HOS 23.0.1 support on its landing page concerns unpatched V1 or modchipped units, not a software entry point for Mariko. This is community compatibility guidance, not an inspection of a particular unit. [Getting started](https://switch.hacks.guide/user_guide/getting_started), [RCM guide](https://switch.hacks.guide/user_guide/rcm/)

## Compatibility

| Claim | Hardware | Firmware | Assessment |
|---|---|---|---|
| CVE-2018-6242 / Fusée Gelée | Vulnerable early Tegra X1/Erista; Mariko's newer Boot ROM is outside the documented vulnerable class | Boot ROM exploit, not an HOS 23.0.1 bug | No compatible evidence for T210B01 |
| Atmosphère/Fusée loader | Mariko is supported when loaded from an already obtained bootloader context | Release compatibility can include newer HOS | Support after boot, not a way to obtain that context |
| RCM on Mariko | Mariko supports the intended RCM mode and uses XUSB | Independent of HOS | A mode is not an exploit |
| Caffeine | Community table lists patched/Mariko at 4.1.0 | Not 23.0.1 | Not applicable to the target |
| Switch V2-specific exploit | None identified | HOS 23.0.1 | No reproducible public demonstration found |

## Evidence quality

- **High for the cited implementation/documentation claims:** NVIDIA advisory for CVE-2018-6242; Atmosphère source project for its loader behavior.
- **Medium for Mariko IROM patch details:** Switchbrew is public reverse-engineered documentation with specific patch pseudocode, but not an official NVIDIA/Nintendo specification.
- **Medium for practical compatibility:** NH Switch Guide summarizes a community-tested model/firmware matrix, but does not prove the state of a particular unit.
- **Low or none for a specific Switch V2 unit:** it was not connected or examined; fuses were not read.

## Open questions

1. Is there a public, independently reproducible demonstration of Mariko T210B01 boot-chain code execution on exact HOS 23.0.1?
2. What exact Switch 1 revision and firmware did the ns2jb author test? These are unknown and cannot be treated as Mariko evidence.
3. Is there a new public Mariko exploit chain absent from the guide, Switchbrew, and Atmosphère sources? This search is not a complete view of private research.
4. Determining the exact fuse state of a particular Switch V2 would require reading it from the console, which was out of scope and not performed.

## Agent conclusion

**Exact compatibility:** no software entry point without a modchip was substantiated for Switch V2/Mariko + HOS 23.0.1. RCM availability, Atmosphère firmware support, and the Erista Boot ROM exploit are not evidence of such a path. This is a bounded negative public-research result, not proof of impossibility.
