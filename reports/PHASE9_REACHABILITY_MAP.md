# PROJECT ZERO — Phase 9: reachability map

## Conclusion

There is **no HOS binary artifact, BootROM, or stock application for HOS 23.0.1** in this working tree. The public source libnx, its newlib dependency, the PROJECT_ZERO synthetic models, and the host analysis tools do not prove entry into a pre-Homebrew system. The available evidence therefore does not allow a new target experiment on Mariko 23.0.1. Known bugs in libnx require already running code.

Legend: "Stock availability" describes the normal path from the retail system or application, not exploitability. "Mariko/23.0.1" means direct evidence tied to that platform/build, not general architecture support.

## Components by execution phase

| Category / Component | When is | executed Does it require already running unsigned code? | Stock Availability / Public Interface | Proof Mariko + HOS 23.0.1 |
|---|---|---|---|---|
| **A — BootROM/IROM and First Boot Stages** | Before Horizon OS and before user titles. | No; it is a trusted boot stage. | Boot/recovery and RCM are hardware/boot interfaces. The public documentation describes the Tegra X1's legacy RCM behavior, but the presence of RCM mode alone does not prove a bug or code execution. | Public previous reports indicate that Fusée Gelée/CVE-2018-6242 does not apply to Mariko and Mariko has a newer BootROM. We don't have BootROM image, fuse status or target console measurement. There is no evidence for the Switch V2 unit. |
| **A — bootloader/warmboot/security environment** | After BootROM, before normal user environment and during privileged system transitions. | No; are part of the system. | A regular stock application does not have direct access to their internal interfaces. The public sources describe the architecture and historical paths, not an accessible stock API to run your own code. | Only community/historical chip family level claims. No HOS 23.0.1 boot artifact or evidence of a specific Mariko state. |
| **B — Horizon kernel and system services** | After starting HOS; services run in privileged system processes. | Not for system analysis; an attack from an application would need a reachable interface and a subsequent error. | IPC/services are available according to title identity, its permissions and service registration. Public SDK headers or community documentation show the API shape; they do not prove by themselves that any retail application will get a session to the given service. | Public Phase 3 registry links ldn/proximity info issue with patch before 23.0.1; it does not show the exploit chain or the exact Mariko build. We do not have HOS services and ACL 23.0.1 in binary form. |
| **C — stock user applications and parsers** | After HOS starts, in the user context and within the title's sandbox/identity. | No; the signed stock application executes normally. | Entries may come via application features, supported content, or network/IPC paths of a specific title. That's a generic boundary class, not an assertion about a specific Switch parser. The usability of the WebKit/web applet depends on the retail flow and its permissions. | We don't have HOS WebKit or stock title binaries, their build IDs, permissions or exact 23.0.1 configuration. Old WebKit CVEs from previous reports do not show Mariko 23.0.1 vulnerability. |
| **D — SDK/libnx and devkitPro newlib** | In the application process that uses them statically/linkily. | Yes for parsed libnx/newlib paths: require the application that contains this code to run. | Public APIs are intended for title authors; the source API does not mean that the same implementation is part of the system services. | We have pinned libnx source and AArch64 newlib object, not proof that a specific stock title/HOS 23.0.1 contains them, nor proof of exploitability on Mariko. Phase 7/8 anomalies are therefore not the first entry point. |
| **D — Atmosphère/Hekate and homebrew frameworks** | After successfully getting your own code to run or in a modified boot chain. | Yes, by definition they require a previous entry/boot path. | Publicly documented interfaces and firmware support after booting do not show how to get to first boot. | Post-entry compatibility is not proof for Mariko 23.0.1 software-only entry. Their target binaries are not parsed in this tree. |
| **Host lab: PROJECT_ZERO, Ghidra, REA, Capstone/LIEF** | On the macOS of the research computer. | Not against the console; they are not part of HOS. | Available locally. PROJECT_ZERO synthetic models deliberately introduce errors to test detectors. | No direct platform evidence. Ghidra/REA only analyzed AArch64 `libsysbase_dirent.o`, not HOS. |

## Reevaluation of traces from previous phases

- **Fusée Gelée/CVE-2018-6242:** category A, historical BootROM path on older Erista; previous local reports indicate a hardware fix in Mariko. RCM availability is not proof of vulnerability.
- **WebKit and older userland CVE:** category C. Previous reports indicate old patch boundaries; no local stock binary allows to confirm reachability or error on 23.0.1.
- **Horizon/sysmodule/local IPC:** category B. Public API and historical reports do not show stock caller → service → error → privileged impact for exact target.
- **Gezine/ns2jb:** public claims or research for a different/inaccurately specified target, not locally reproducible Mariko 23.0.1 track. The exact Switch 1 Mariko entrypoint does not follow from the previous phase.
- **libnx `fsdev_convertfromfspath`, `seekdir`, `fsdev_getfspath`:** category D, require a process with this library. Phase 7/8 results remain on file, but are out of pre-homebrew priority.
- **Synthetic PROJECT_ZERO findings:** host E1/E2 model results. They are not an implementation, fuzz result, or proof of HOS behavior.

## Decision test

None of the locally documented traces simultaneously satisfy: (1) reachability before Homebrew, (2) proof for Mariko, (3) proof for HOS 23.0.1, and (4) safely reproducible test. We have evidence for the source code of the libraries and host harnesses, not the target system. Therefore, a new technical conclusion about entry possibilities cannot be derived.
