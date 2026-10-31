# PROJECT ZERO — Phase 10: requirements for target artifacts

## Inventory conclusion

There is no stock application HOS/BootROM file in the project. Local inventory found **0** files `.nso`, `.nro`, `.kip`, `.nca`, `.xci`, `.romfs`, `.nsp`, `.kip1`, `.kip2` or `.cnmt`; the only non-Ghidra target looking binary is devkitPro newlib `libsysbase_dirent.o`, ELF64 AArch64. It's not a Nintendo code.

## Missing inputs

| Missing Artifact | Required Format and Architecture | Required Metadata | Integrity / Purpose |
|---|---|---|---|
| **Identity of exact HOS 23.0.1 build** | Versioned manifest or trusted release metadata; format can be text/JSON/XML signed by the publisher. | Exact version and build ID, region/release type, component/title ID, date or release identifier. | Verify the issuer's signature and certificate chain, if available; compare the SHA-256 artifact with the trusted manifest. Without a build identity, compatibility with 23.0.1 cannot be claimed. |
| **HOS kernel / privileged boot and system modules** | Unencrypted and unpacked executable in original format, ideally ELF64 little-endian AArch64 or a format that has a verified loader. The NSO/KIP/Nintendo container needs to be labeled with the actual format, not renamed to ELF. | Original name/title ID, build ID, segments and their addresses/rights, relocations, imports, symbols (if any), link to HOS build. In addition, authorizations and service ACL/capability metadata for modules. | Hash of each original file and trusted source. The associated descriptor/manifest metadata is also needed for IPC analysis. Without it, only isolated instructions can be analyzed, not stock reachability. |
| **Stock applet or application with input parser** | Unencrypted executable/rodata for AArch64, ideally native NSO/ELF with segment map; associated resources separately. | Title ID, version, HOS build, process identity, service permissions/capabilities, input types and applet launch context. | Verify original hash and metadata; maintain the link between the executable and the manifest. Needed to assess stock reachability from normal UI/content/network.
| **Related permissions and IPC contract** | Permission descriptor/manifest or public versioned specification; no need for a binary if it authoritatively covers a particular build. | Process → service name/IPC interface → granted permissions → version ID. | Trusted signature/source and link to HOS 23.0.1. The SDK header alone is not enough to confirm that a stock title will receive the service.
| **BootROM/IROM only if pre-HOS trust is to be investigated** | Officially published or researcher-provided binary/forensic artifact of exact T210B01, with architecture/segments documented. | SoC/BootROM revision, model family, hash and origin. | Signed vendor manifest or trusted source. In the current scope, no console dump, fuse data, keys or physical measurement are requested. This artifact is not required for purely HOS userland auditing, but is required for direct binary boot ROM assertions.

### The difference between the three kinds of "source"

1. **Public SDK/library source code** (eg libnx) describes the given library. It does not automatically include the Nintendo HOS implementation or the stock build.
2. **Encrypted firmware container** (eg a file from a distribution package) is only a container for this purpose. Without legally available decrypted content and trusted metadata, the internal executable cannot be analyzed. No decryption or key retrieval is performed in this work.
3. **Unencrypted executable** allows static analysis if the format is supported or the correct loader and segment/relocation metadata are available. The executable itself without proof of origin/build ID still does not deliver HOS 23.0.1.

## Minimum acceptable package

For the first offline experiment, one well-chosen stock applet or system module is sufficient, if the package contains: (a) an unencrypted executable, (b) a hash verifiable against a trusted source, (c) a HOS build/title/module identity, and (d) permissions/IPC metadata that will allow the stock caller to be determined. Without these four items, the experiment does not meet the Phase 9/10 objective.
