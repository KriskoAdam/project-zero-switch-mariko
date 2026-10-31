# Stage 4 — final verdict

**Decision: B — publicly announced Switch 1 userland exploit, compatibility with Mariko not confirmed.**

More specifically: there is a public claim by the author that his offline userland exploit supports both Switch 1 and Switch 2. However, there is no publicly available reproducible implementation, technical description, or independent confirmation of testing on the original Switch. Therefore, I understand Category B as a **publicly announced research path for Switch 1**, not a downloadable and verified exploit package.

## What is new and verifiable

The apparent "all firmware" vs. "20.0.0+" discrepancy has a likely platform explanation: 20.0.0+ is required on the Switch 2 to run a Switch 1 game in backwards compatibility, according to a later patch attributed to Gezine. This alone does not determine the extent of the firmware error on the original Switch. Since the original repair status was not directly accessible and the explanation was preserved through mirror/secondary reports, this conclusion has medium certainty.

## What is missing to confirm the target console

- proof of test on Nintendo Switch V2/Mariko (T210B01/Tegra214), not just "Switch 1/2" claim;
- specific test record on HOS 23.0.1;
- public PoC/source or detailed technical article with reproducible steps;
- exact determination of the process, sandbox and obtained authorizations;
- independent repetition of the result.

## Practical conclusion

On Mariko 23.0.1, according to public evidence, software input via Gezine cannot be confirmed today. The author's announcement is worth watching, but it doesn't in and of itself change the feasibility assessment for this particular console. Kernel exploit, system access, persistence or CFW are not documented.

## Decision sources

| Source | Date | Evidence Type | Credibility |
|---|---|---|---|
| [Gezine — Original Status](https://x.com/gezine_dev/status/2074894225460822503) | 07/08/2026 | Primary Public Assertion; text reproduced from contemporary articles, direct access when checking 403 | Medium for claim content; low for | functionality
| [Hackintendo — Contemporaneous Report](https://hackintendo.com/une-faille-userland-switch1-2/) | 07/08/2026 | Secondary report citing author | Medium for date and declared range |
| [Gezine — Subsequent Status](https://x.com/gezine_dev/status/2075682718155956275) and [mirror](https://w.twstalker.com/gezine_dev) | 07/10/2026 | Primary status unavailable; mirrored wording o Switch 2 20.0.0+ | Low to Medium |
| [Switch2Unlock — Timeline and Messages](https://switch2unlock.com/en/news/) | until 10/29/2026 | Secondary entry with links to original posts; states that the Gezine exploit remained unreleased | Medium for publication status; not technical verification |
| [Nintendo — security advisories](https://www.nintendo.com/security-advisories/en/index.html) | check 10/30/2026 | Official Notification Registry | High for registry content; an empty record does not prove the absence of the | error
