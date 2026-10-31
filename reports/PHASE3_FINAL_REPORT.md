# Phase 3 — final technical report

**Date:** October 30, 2026
**Platform:** Nintendo Switch V2 Mariko / T210B01 / Switch V2 family
**OS:** Horizon OS 23.0.1
**Scope:** public research and non-invasive local tools. Console and proprietary firmware were not analyzed.

## 1. Conclusion

No reproducible software input for the exact T210B01/Mariko + HOS 23.0.1 combination without the modchip was found in the public sources reviewed. It is a time-bound result of public research, not proof of non-existence of a non-public error.

The NH Switch Guide describes the new Boot ROM for Mariko and its table lists Caffeine for patched/Mariko only at 4.1.0 and modchip from 5.0.0. HOS support in Atmosphère/Hekate applies after obtaining an entry path and does not prove an exploit. [NH Guide](https://switch.hacks.guide/user_guide/getting_started), [guide overview](https://switch.hacks.guide/)

## 2. Boot trust and hardware boundaries

- Fusée Gelée/CVE-2018-6242 concerns a vulnerable Tegra X1 Boot ROM RCM USB processing. Mariko uses the new Boot ROM. RCM remains a recovery mode, not an automatically exploitable input.
- Switchbrew introduces Mariko changes around DMA/GMMU, warmboot/Security Engine context and validation of Boot ROM inputs. These are community technical records for a hardware family, not a measurement of a specific Switch V2 unit.
- Production mustaches and anti-downgrade belong to the trust model; their status on a specific piece was not ascertained.

Sources: [Switchbrew fuses](https://switchbrew.org/wiki/Fuse_registers), [Switchbrew flaws](https://switchbrew.org/wiki/Switch_System_Flaws), [Atmosphère fusee](https://github.com/Atmosphere-NX/Atmosphere/blob/master/docs/components/fusee.md).

## 3. Errors and corrections

Structured records are in [VULNERABILITY_DATABASE.md](VULNERABILITY_DATABASE.md) and [vulnerabilities.json](vulnerabilities.json).

- Historical WebKit CVE-2016-4657, CVE-2017-7005, CVE-2016-4622, and CVE-2018-4441 have patches between 2.1.0 and 7.0.0 in Switchbrew. The records do not show that the given bugs on the Switch gave RCE; the exact compatibility of Mariko is not stated for several.
- Old kernel/service/NVIDIA bugs were fixed before 23.0.1. nvhax in nvservices is according to Switchbrew code execution in the context of the sysmodule when combining a primitive; it is not a stand-alone proven exploit for the target.
- CVE-2018-6242 is fixed by hardware in Mariko, not by HOS patch.
- CVE-2026-82079: Nintendo advisory states a possible information leak in a proximity attack; Switchbrew attributes the ldn fix to a change in 23.0.0. The public source does not demonstrate the full privilege escalation or CFW chain. HOS 23.0.1 follows this patch.
- Nintendo says 23.0.1 fixes a feature issue from 23.0.0. Switchbrew mentions update sdb, but leaves the security-flaws field blank. Without additional proof, we do not attribute 23.0.1 as a new security patch.

Sources: [Switchbrew flaws](https://switchbrew.org/wiki/Switch_System_Flaws), [23.0.0](https://switchbrew.org/wiki/23.0.0), [23.0.1](https://switchbrew.org/wiki/23.0.1), [Nintendo advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [Nintendo 23.0.1 notes](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html).

## 4. ns2jb and Switch 2

ns2jb author and repository describe Switch 2 HOS 23.0.1. The article describes a WebKit path that failed to execute the code in the sysmodule; the published successful procedure was a separate SmileBASIC/fs path. The author mentions a test on the original Switch, but does not list the model, firmware, or packaged reproducible steps for this branch. This does not confirm Switch V2/Mariko support. [ns2jb article](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/), [repository](https://gitlab.com/pepsipu/ns2jb).

## 5. Environment and measurable results

- CMake 4.4.5, Ninja 1.13.2, LLVM 23.1.4, pkg-config 3.0.10, OpenJDK 25.0.5.0.3.
- Preserved existing Homebrew, Git 2.54.0, Python 3.14.7, Node 24.22.2 LTS and Apple Clang.
- Ghidra 12.1.4 downloaded from NSA GitHub, SHA-256 verified; ARM64 native components built successfully.
- Python libraries isolated in .venv and pinned.
- REA 6.8.0 Codex registration aligned; Ghidra provider checks passed with CLI doctor with specified environment. The live Codex MCP process needs a restart to load the changed paths.
- REA firmware provider marks macOS as unsupported. The target firmware artifact was not delivered.
- Scripts smoke-tested on local synthetic Mach-O ARM64 and system Mach-O x86_64. Unit tests 6/6 passed.

Details: [ENVIRONMENT.md](ENVIRONMENT.md), [BINARY_ANALYSIS_READINESS.md](BINARY_ANALYSIS_READINESS.md), [INSTALLATION_LOG.md](INSTALLATION_LOG.md).

## 6. Independent Verification

Five agents examined boot, Horizon/kernel, WebKit/wireless, tooling and independent auditing. Each submitted a separate message to agents/phase3_*.md. Consensus: public proof for exact Mariko/HOS 23.0.1 target missing; claims for other hardware do not transfer to it.

## 7. What would change the conclusion

A publicly verifiable description with explicit T210B01/Mariko model, HOS 23.0.1 build identity, assumptions, permission boundaries, reproducible proof of entry and independent confirmation would be needed. Without it, we do not expect an exploit. Another safe work: track primary publications and analyze only legally provided static artifacts after REA format support is resolved.

