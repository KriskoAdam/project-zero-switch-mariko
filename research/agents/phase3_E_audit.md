# Phase 3 Agent E — Independent Audit of Evidence and Database

**Scope:** Passive review of public documents and the `reports/vulnerabilities.json` design; no console, binaries, or payloads.

## Audit conclusion

The main report's conclusion is appropriately cautious: the cited public sources did not provide a reproducible software-only chain explicitly demonstrating Mariko/T210B01 + HOS 23.0.1. This is a bounded negative search result, not proof that an unknown or non-public vulnerability does not exist.

## Confirmed technical points

- Switchbrew says CVE-2018-6242 permits execution in Boot ROM/BPMP before privilege reduction and can lead to EL3 code. The same entry explicitly lists a fix on HAC-001-01/Mariko. This is strong public evidence that Fusée Gelée is not a Mariko entry point; it is not a test of a specific Switch V2 unit. [Switchbrew flaw matrix](https://switchbrew.org/wiki/Switch_System_Flaws#Hardware)
- Switchbrew's `nspwn` entry clearly describes arbitrary execution of an unverified ExeFS/NPDM with full system privileges and a fix in 5.0.0. The entry does not identify T210B01 as affected hardware. [nspwn](https://switchbrew.org/wiki/Switch_System_Flaws#nspwn)
- The `nvhax` entry says that, combined with an information leak/other ioctl primitives, a useful arbitrary write could be achieved; the table lists “Code execution under nvservices sysmodule,” fixed in 6.2.0. The database row should set `arbitrary_code_execution_documented=true`; `privilege_escalation_documented` may be `true` with a clear note that this is escalation from a service client into `nvservices` and requires additional primitives. The source alone does not establish Mariko applicability. [nvhax](https://switchbrew.org/wiki/Switch_System_Flaws#GPU)
- For CVE-2016-4657/7005/4622/4441, Switchbrew's browser table lists fixes in 2.1.0, 3.0.1, 6.1.0, and 7.0.0. The “Successful exploitation result” column is blank for these rows. It is therefore safer to use `arbitrary_code_execution_documented=null` for Switch specifically, even though the WebKit issues were exploited on other Apple platforms. Switchbrew only notes for 4657 that an adapted iOS exploit was later used on Switch. Without a direct Switch PoC in the source, do not set this to true. [browser rows](https://switchbrew.org/wiki/Switch_System_Flaws#Internet_Browser)
- HOS 23.0.0 is marked by Switchbrew as having “Security flaws fixed: yes,” links a Nintendo security notice, and includes an updated `ldn`; the `ldn`/`lp2p` row maps a stack overflow to a 23.0.0 fix. Nintendo's advisory broadly describes possible information disclosure from a nearby attack. No independent public source establishes a kernel/CFW chain or Mariko-specific exploitability. [23.0.0](https://switchbrew.org/wiki/23.0.0), [Nintendo notice](https://www.nintendo.com/security-advisories/en/index.html)
- Switchbrew's HOS 23.0.1 entry leaves “Security flaws fixed” blank and lists a functional fix for an issue in 23.0.0, an `sdb` update, and one unchanged unknown IPC interface. State that target 23.0.1 includes the CVE/`ldn` fix introduced in 23.0.0; do not claim 23.0.1 itself added a security fix unless another source confirms it. [23.0.1](https://switchbrew.org/wiki/23.0.1), [Nintendo 23.0.1 notes](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html)
- The ns2jb article directly calls the result a “software-only, tethered jailbreak” for Switch 2, 23.0.1. Its WebKit route achieved only native control-flow hijacking; the author says it was insufficient for system-module code execution due to XOM/PAC/CFI. The successful route was a separate SmileBASIC → filesystem chain. The author mentions testing on Switch 1 at the end, but gives no model/revision/firmware and no packaged procedure. This is not evidence of Switch V2/Mariko compatibility. [author's article](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/), [upstream](https://gitlab.com/pepsipu/ns2jb)

## Recommended corrections to the structured database

1. For WebKit CVE rows, set `arbitrary_code_execution_documented` to `null` where the Switchbrew table gives no Switch-specific successful exploitation result; note that iOS exploit history does not transfer to HOS.
2. For `nvhax`, mark documented code execution in the `nvservices` context as `true`; any privilege-escalation field should explicitly qualify this as “service client → system-module process; multiple bugs/primitives required.”
3. For `nspwn`, the current `privilege_escalation=true` is defensible; add that the source reports arbitrary code execution with full system privileges and `lr` access, not evidence about Mariko.
4. For CVE-2026-82079, `affected_firmware_versions: ["before 23.0.0"]` is inferred from the 23.0.0 fix, not an explicit advisory range. Mark it as inferred in the note and leave hardware/impact unknown.
5. For old OS issues whose firmware fix predates publicly documented Mariko guidance, do not let a general `null` imply an exploit claim. Explicitly distinguish “Mariko affected code unknown,” “target firmware fixed by version,” and “no evidence of Mariko testing.”
6. Label Nintendo's advisory as primary evidence for risk and recommended updates; Switchbrew is a community reverse-engineered secondary source for `ldn` internals and patch mapping. Do not describe all mixed sources as primary.

## Evidence matrix

| Claim | Evidence type | Confidence |
|---|---|---|
| Fusée Gelée fixed in hardware on Mariko | Switchbrew hardware entry, Atmosphère documentation | High for the model family; no exact-unit test |
| `nspwn` full-system code execution through HOS 4.1.0, fixed in 5.0.0 | Switchbrew technical entry | Medium/high as a public reverse-engineering report; Mariko scope unknown |
| `nvhax` code execution under `nvservices`, fixed in 6.2.0 | Switchbrew technical entry | Medium/high for the historical chain; exact T210B01 applicability unknown |
| Browser CVE fix levels | Switchbrew browser matrix | Medium; exploitation-result column is blank |
| `ldn` / CVE-2026-82079 fixed in 23.0.0 | Nintendo advisory + Switchbrew release mapping | High that 23.0.0 includes the fix; lower confidence on full technical impact |
| ns2jb for Switch V2 | No PoC specifying exact hardware/firmware | Unsubstantiated |

## Open questions

- No public exact Switch 1 model and system version are given for the ns2jb test.
- Nintendo's advisory does not provide the exact technical chain for the proximity attack; Switchbrew's mapping to `ldn` is community research.
- Without legally obtained, user-supplied 23.0.0/23.0.1 artifacts, a binary comparison cannot be performed in REA/Ghidra.
- Public exploit tables alone do not prove that every vulnerability was tested on Mariko/T210B01.
