# Mariko Software-Only Jailbreak Feasibility

## Target and current assessment

Target under investigation: Nintendo Switch V2 / intended Mariko platform (T210B01), Horizon OS 23.0.1. The physical console's SoC identity has not been independently authenticated.

**Current assessment:** the public sources reviewed do not establish a reproducible software-only homebrew path for this exact hardware/firmware target without a modchip. The jailbreak objective remains unachieved and, based on currently available public evidence, technically difficult. This is a statement about the evidence reviewed—not proof that no undisclosed or future entry point exists.

## What the existing research tells us

1. Erista Boot ROM bug CVE-2018-6242/Fusée Gelée is fixed in Mariko. RCM mode alone is not an entry point.
2. Historical WebKit/Horizon exploits have narrow firmware ranges. Caffeine is listed for Mariko only at HOS 4.1.0, not 23.0.1. No public chain for Mariko 23.0.1 was found in the reviewed sources.
3. CVE-2026-82079 is publicly associated with ldn/lp2p and fixed in 23.0.0; target 23.0.1 includes this patch. Available information does not document a privilege transition or homebrew chain.
4. ns2jb demonstrates a different Switch 2 platform on 23.0.1. The author's Switch 1 test lacks a specific revision, firmware, and public reproducible steps.
5. Atmosphère/Hekate compatibility with a firmware version does not itself provide the initial software entry point needed for a stock Mariko jailbreak.

## Research references

- Nintendo update pages confirm that 23.0.1 exists for both the original Switch and Switch 2; version number alone does not identify the SoC.
- The Nintendo advisory is a primary source but describes CVE-2026-82079 at a high level.
- Switchbrew is community reverse-engineering documentation useful for historical issues and update details.
- NH Switch Guide provides practical compatibility information, not an independent test of this specific console.
- ns2jb's public implementation is primarily scoped to Switch 2, not Mariko.

Sources: [Nintendo Switch updates](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html), [Switch 2 updates](https://www.nintendo.com/en-gb/Support/Nintendo-Switch-2/System-Update-Information-for-Nintendo-Switch-2-2843738.html), [NH Switch Guide](https://switch.hacks.guide/user_guide/getting_started), [Switchbrew System Flaws](https://switchbrew.org/wiki/Switch_System_Flaws), [CVE advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [ns2jb](https://gitlab.com/pepsipu/ns2jb).

## Work that could improve feasibility

- Complete local Ghidra/JDK/Python setup and record exact versions/hashes.
- Analyze only legally obtained, user-supplied artifacts; do not obtain proprietary firmware through circumvention or work with console keys.
- Track primary sources that explicitly identify Mariko T210B01 and HOS 23.0.1, with reproducible procedures and independent confirmation.
- Prioritize research that could identify a stock-software entry point and explain how it might lead to homebrew execution.

## Environment validation performed

REA 6.8.0 doctor with configured paths confirmed Ghidra 12.1.4, macOS arm64 native decompiler, headless analyzer and 64-bit JDK 25. Official buildNatives finished BUILD SUCCESSFUL. Running analyzeHeadless --help showed analyzer usage without loading the target file. Python venv import and pip check passed.

## Compatibility note

The NH Switch Guide distinguishes firmware support after obtaining the boot path from the availability of the initial entry point. Its table for patched/Mariko systems lists Caffeine only for 4.1.0 and modchip from 5.0.0; general 23.0.1 support applies to unpatched V1 or modchip consoles. Therefore, Atmosphère/Hekate support for HOS 23.0.1 does not imply a software-only Mariko jailbreak. Sources: [Getting Started](https://switch.hacks.guide/user_guide/getting_started), [guide home](https://switch.hacks.guide/).
