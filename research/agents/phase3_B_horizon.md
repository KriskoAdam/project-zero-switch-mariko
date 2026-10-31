# Agent B — Horizon OS, Kernel, and System Services

**Scope:** Public documentation for Nintendo Switch V2 / Mariko (T210B01), target HOS 23.0.1. No live device or firmware artifact was used.

## Findings

1. **A security issue is publicly documented as fixed in 23.0.0.** Nintendo's September 10, 2026 advisory describes a possible information disclosure through a nearby attack; the advisory intentionally omits exploit details. Switchbrew maps the fix to the `ldn` service and identifies CVE-2026-82079. Version 23.0.0 marks a security flaw as fixed and lists `ldn` among updated system modules. [Nintendo advisory index](https://www.nintendo.com/security-advisories/en/index.html), [Nintendo advisory PDF](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [Switchbrew 23.0.0](https://switchbrew.org/wiki/23.0.0)
2. **Target version 23.0.1 includes 23.0.0.** The public 23.0.1 page gives an October 1, 2026 release date and describes a fix for a long-start, pause, and software-closing issue introduced in 23.0.0; changed system modules include `sdb`. Its “Security flaws fixed” field is blank. The available record does not show that 23.0.1 added another security fix beyond 23.0.0, but no direct Nintendo advisory confirming this was found. [Switchbrew 23.0.1](https://switchbrew.org/wiki/23.0.1)
3. **23.0.0 changed more than `ldn`.** Switchbrew lists updates to numerous system modules (including `usb`, `bluetooth`, `wlan`, `nvservices`, and `ldn`), additional IPC response validation, and changes to NPDM/kernel capability metadata. A module update or metadata change alone does not establish a security fix for a specific vulnerability. [Switchbrew 23.0.0](https://switchbrew.org/wiki/23.0.0)
4. **Mariko has documented hardware fixes compared with Erista.** Switchbrew's technical table explicitly associates HAC-001-01/Tegra214/T210B01 with fixes for GMMU untranslated DMA access, saved Security Engine context protection, CVE-2018-6242 (Boot ROM USB stack; Fusée Gelée/ShofEL2), and Boot ROM SDRAM parameter validation. These entries concern a hardware revision, not an HOS patch range. [Switchbrew System Flaws](https://switchbrew.org/wiki/Switch_System_Flaws)
5. **Evidence is insufficient to establish exploitability on Mariko + 23.0.1.** The HOS 23.0.0 updated-module list and advisory are platform-family-level evidence; they do not say CVE-2026-82079 grants Mariko kernel execution, privilege escalation, or a homebrew chain. According to the record, the issue is already fixed in 23.0.1.
6. **No binary analysis was performed.** Without legally obtained and supplied 23.0.0/23.0.1 images, service code cannot be compared, Mariko-specific variants cannot be identified, and the patch diff cannot be independently confirmed. No keys or console data were used or obtained.

## Exact compatibility and evidence level

| Claim | Hardware/firmware scope | Evidence / confidence |
|---|---|---|
| Fusée Gelée/CVE-2018-6242 fixed in HAC-001-01 Mariko | Boot ROM hardware revision; not an HOS version | Switchbrew explicitly lists the model fix; high confidence in public revision documentation, not a test of this unit |
| GMMU DMA hardware fix | HAC-001-01 / T210B01 | Explicit Switchbrew entry; high documentary confidence |
| Security Engine warmboot context fix | HAC-001-01 / T210B01 | Explicit Switchbrew entry; high documentary confidence |
| Boot ROM SDRAM parameter validation fix | HAC-001-01 / T210B01 | Explicit Switchbrew entry; high documentary confidence |
| CVE-2026-82079 advisory | Nintendo Switch consoles, nearby attack; Switchbrew maps fix to 23.0.0 | Nintendo is primary evidence for the general impact; Switchbrew technically maps it to `ldn`. Exact exploit chain and hardware split are unproven |
| Additional security fixes in HOS 23.0.1 | Switch 1, 23.0.1 | Unknown: Switchbrew leaves the security-flaws field blank; release notes describe a functional fix from 23.0.0. Without a binary diff or advisory, documentation is incomplete |

## Open questions

- What exact bug and assumptions underlie CVE-2026-82079? Nintendo does not describe them publicly in the advisory.
- Which exact services/IPC paths and models were affected? Public sources do not prove a Mariko-specific exploitable chain.
- Does HOS 23.0.1 contain security changes beyond the published functional fix? Public records do not confirm this; a lawful binary diff could help, though interpretation would still be required without symbols.
- Are the 23.0.0 service updates identical on Mariko and Erista? Lawfully obtained, variant-specific artifacts would be needed.
- Is there a public PoC demonstrating privilege escalation or code execution on Mariko 23.0.1? None was found in the sources reviewed.

## Sources

- [Nintendo security advisory index](https://www.nintendo.com/security-advisories/en/index.html)
- [Nintendo September 10, 2026 advisory PDF](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf)
- [Switchbrew 23.0.0](https://switchbrew.org/wiki/23.0.0)
- [Switchbrew 23.0.1](https://switchbrew.org/wiki/23.0.1)
- [Switchbrew public system flaws](https://switchbrew.org/wiki/Switch_System_Flaws)
