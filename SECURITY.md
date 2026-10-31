# Security and responsible research policy

PROJECT ZERO is a public research record, not an exploit distribution project. Work must stay within owner-authorized, non-destructive observation and public-source analysis.

## In scope

- Public documentation, open-source code, and legally provided artifacts whose redistribution and analysis rights are clear.
- Host-only parser tests and synthetic models, labeled as such.
- Standard, documented, read-only interfaces used in an ordinary stock system state.
- Responsible discussion of vulnerability reachability and mitigations.

## Out of scope

- Firmware/bootloader modification, downgrade, partition writes, fuse changes, modchip installation, key extraction, secret access, or bypassing access controls.
- Unknown or malformed traffic sent to a console; exploit payloads; unauthorized native code execution; instructions intended to defeat protections.
- Copyrighted firmware/dumps, proprietary credentials, personal device identifiers, or private network information.
- Claims that a host-side test proves a vulnerability on Switch hardware.

## Reporting a suspected issue

Do not open a public issue containing secrets, private artifacts, or a working exploit. For a suspected Nintendo product vulnerability, use Nintendo's current official security reporting channel. For a project data/privacy issue, open a minimal issue without reproducing the sensitive value, or contact maintainers privately once a maintainer contact is established. Public issues are not a substitute for vendor disclosure.

## Evidence handling

Keep raw files only when lawful and necessary. Scrub serials, MAC addresses, account names, private IPs, local absolute paths, and tokens before submission. Record hashes for provenance, but hashes alone do not authenticate hardware or establish exploitability. Stop if an experiment could modify the target or disrupt service.
