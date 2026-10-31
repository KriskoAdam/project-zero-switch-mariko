# Agent C — WebKit and Network Attack Surface (Independent Findings)

**Target:** Original Nintendo Switch V2, Mariko/T210B01, HOS 23.0.1.
**Method:** Passive review of public primary sources; no console, firmware image, or exploit was used.

## Findings

### 1. Publicly known WebKit vulnerabilities are historical

Switchbrew lists the following browser issues:

| Identifier | Public description | Fixed |
|---|---|---:|
| CVE-2016-4657 | Historical WebKit vulnerability | HOS 2.1.0 |
| CVE-2017-7005 | WebKit type confusion | HOS 3.0.1 |
| CVE-2016-4622 | WebKit memory corruption; reappeared in 4.0.0 | HOS 6.1.0 |
| CVE-2018-4441 | WebKit/browser vulnerability | HOS 7.0.0 |

Source: [Switchbrew — System Flaws](https://switchbrew.org/wiki/Switch_System_Flaws). This is a community historical compatibility map; it does not establish a complete exploit chain or the state of every hardware revision. No publicly reproducible WebKit chain for Mariko + HOS 23.0.1 was found in these sources.

The Switch has no ordinary user-facing browser application, but it has system browser applets, including captive-portal `WifiWebAuthApplet`. This means browser attack surface exists; it does not mean a current vulnerability is known. [Switchbrew — Internet Browser](https://switchbrew.org/wiki/Internet_Browser)

### 2. ns2jb: evidence for Switch 2 and limited signal for the original Switch

The author's article describes ns2jb as a software-only, tethered jailbreak for **Switch 2 on HOS 23.0.1**, with native code execution in an ordinary system module and the built-in filesystem system module. The upstream repository describes itself as a jailbreak for Switch 2. [Author's article](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/), [repository](https://gitlab.com/pepsipu/ns2jb)

Important distinctions in the write-up:

- The WebKit attack through a custom Wi-Fi captive portal reportedly achieved native control-flow hijacking, but the author says it did not achieve arbitrary IPC/system-module execution. The author cites XOM, PAC, and CFI in the target Switch 2 environment as obstacles.
- The described successful route was a separate SmileBASIC 4 (original Switch game) → memory corruption/ROP → filesystem bug → system-module privilege and code execution chain. The author says further work would be needed to port the filesystem exploit to WebKit; therefore the browser route was not a complete chain.
- The article's conclusion says the exploit was also tested on “Switch 1,” but was not packaged/released for it. This is firsthand evidence of some test on an original Switch and should not be omitted. However, the public article gives no model/revision (Erista vs. Mariko), exact HOS version, conditions, separate artifacts, or reproduction steps for that test. It therefore **does not confirm** Switch V2/Mariko 23.0.1 compatibility, while also precluding the categorical claim that the author tested no Switch 1 at all.
- The author separately says Switch 1 does not support PAC; that does not establish compatibility with Switch V2 or its Boot ROM/Mariko security changes.

Evidence quality: the firsthand write-up and repository are strong evidence for the author's claims about the published Switch 2 result. The unpublished Switch 1 test is an author claim without public reproducibility or exact hardware/firmware identification. Neither source establishes Mariko 23.0.1 compatibility.

### 3. Wireless interface and the HOS 23.0.0 CVE

Nintendo's September 10, 2026 advisory describes possible console information disclosure through a nearby attack. Nintendo notes that details may intentionally be generalized. [Nintendo Security Advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf)

For HOS 23.0.0, Switchbrew records a security fix in `ldn` and associates it with CVE-2026-82079; HOS 23.0.0 was released on September 10, 2026. [Switchbrew — 23.0.0](https://switchbrew.org/wiki/23.0.0) Nintendo's official update history says the original Switch has had HOS 23.0.1 since October 1, 2026, and describes a fix for software startup, pause, and closing issues. [Nintendo Switch update history](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html)

Consequence: the CVE-2026-82079 fix introduced in HOS 23.0.0 is present in 23.0.1. Nintendo's public description does not establish code execution, privilege escalation, or a Mariko-specific chain. Switchbrew's technical mapping is community reverse-engineering, not independent confirmation of an end-to-end exploit. The reviewed web sources did not show that the issue provides a homebrew entry point on the target version.

## Compatibility

| Finding/research | Platform with direct public evidence | Mariko + HOS 23.0.1? |
|---|---|---|
| Historical browser CVEs | Original Switch browser on older HOS versions per Switchbrew | Not established; patch levels predate 23.x by years |
| ns2jb WebKit stage | Switch 2, custom captive portal; author describes only control-flow hijack, not a system-module chain | No |
| ns2jb SmileBASIC/filesystem chain | Published target and detailed result: Switch 2, HOS 23.0.1 | Not established |
| ns2jb author's Switch 1 test | Author says original Switch was also tested; no package or details published | Cannot determine; exact model/firmware missing |
| CVE-2026-82079 / `ldn` | Nintendo advisory is platform-level; Switchbrew maps the fix to HOS 23.0.0 | Already fixed in HOS 23.0.1; no exploit chain established |

## Conclusion

Public sources do not confirm a software entry point for the original Switch V2, Mariko/T210B01, on HOS 23.0.1. The strongest specific recent lead, ns2jb, has its primary reproducible documentation for Switch 2. The author's note about Switch 1 suggests an unpublished test, but without exact hardware and firmware it cannot establish compatibility with the target. This is a bounded negative result, not proof that no private or future exploit exists.

## Open questions

1. What exact Switch 1 model, Boot ROM revision, and HOS version were used in the author's unpublished ns2jb test?
2. Which components of the SmileBASIC/filesystem route were tested on Switch 1, and did the result include privilege/code-execution stages rather than only game memory corruption?
3. Is there public, reproducible confirmation of a test specifying Mariko/T210B01 and HOS 23.0.1?
4. What is the full technical scope of CVE-2026-82079 beyond Nintendo's high-level advisory, and did it differ between Switch 1 and Switch 2? Even if answered, target 23.0.1 includes the 23.0.0 fix.
5. What is the exact WebKit build and n-day identifier discussed in the ns2jb article? The cited passage does not state them publicly; moreover, the described route did not reach system-module execution.
