# Feasibility of software homebrew

## Target and response

Target is Switch V2 Mariko/T210B01, serial prefix Switch V2, Horizon OS 23.0.1.

**Conclusion:** Public sources that have been reviewed do not document a reproducible homebrew software path for this exact HW/FW target without a modchip. In practice, the result should be marked as **unproven and, according to public evidence, currently unrealistic**, not as evidence that the vulnerability definitely does not exist.

## Why

1. Erista Boot ROM bug CVE-2018-6242/Fusée Gelée is fixed in Mariko. The presence of RCM mode does not mean a vulnerable Boot ROM.
2. Historical WebKit/Horizon exploits have old and narrow patch versions. Caffeine is listed in the public table for Mariko only at HOS 4.1.0; it is not HOS 23.0.1. No public chain found for 23.0.1 on Mariko.
3. CVE-2026-82079 is publicly associated with ldn/lp2p and fixed in 23.0.0; target 23.0.1 includes this patch. Available information does not document privilege escalation or CFW chain.
4. ns2jb shows a different Switch 2 platform to 23.0.1. The author's test on Switch 1 does not have a specific revision, firmware or public reproducible steps.
5. Atmosphère/Hekate compatibility with HOS once introduced does not provide an entry exploit.

## Resources and quality

- Nintendo update pages confirm that 23.0.1 exists for both the original Switch and Switch 2; the version number does not identify the SoC.
- The Nintendo advisory is primary, but describes CVE-2026-82079 in general.
- Switchbrew is a community reverse engineering documentation, valuable for historical bugs and update details.
- NH Switch Guide is a practical compatibility community; her tables are not an independent test of a particular piece.
- ns2jb author/repository are primarily for own Switch 2 implementation, not Mariko.

Sources: [Nintendo Switch updates](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html), [Switch 2 updates](https://www.nintendo.com/en-gb/Support/Nintendo-Switch-2/System-Update-Information-for-Nintendo-Switch-2-2843738.html), [NH Switch Guide](https://switch.hacks.guide/user_guide/getting_started), [Switchbrew System Flaws](https://switchbrew.org/wiki/Switch_System_Flaws), [CVE advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [ns2jb](https://gitlab.com/pepsipu/ns2jb).

## Next steps in safe range

- Complete local Ghidra/JDK/Python setup and archive exact versions/hashes.
- Use REA/Ghidra only on legally acquired, user-supplied artifacts; do not obtain proprietary firmware from the Internet and do not work with keys.
- Track new primary sources that explicitly mention Mariko T210B01 and HOS 23.0.1, reproducible procedure and independent confirmation.
- Until such evidence is discovered, do not present the exploit as existing and do not perform live console testing.


## Environment validation performed

REA 6.8.0 doctor with configured paths confirmed Ghidra 12.1.4, macOS arm64 native decompiler, headless analyzer and 64-bit JDK 25. Official buildNatives finished BUILD SUCCESSFUL. Running analyzeHeadless --help showed analyzer usage without loading the target file. Python venv import and pip check passed.

## Exact compatibility according to the current public guide

The NH Switch Guide distinguishes firmware support after obtaining the boot path from the availability of the input itself. His table for patched/Mariko systems lists Caffeine only for 4.1.0 and modchip from 5.0.0; general compatibility page 23.0.1 applies to V1 unpatched or modchip consoles. So HOS 23.0.1 support in Atmosphère/Hekate does not mean software Mariko path. Source: [Getting Started](https://switch.hacks.guide/user_guide/getting_started), [guide home](https://switch.hacks.guide/).
