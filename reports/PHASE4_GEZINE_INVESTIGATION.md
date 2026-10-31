# Phase 4 — Gezine investigation

**As of 10/30/2026** This is a narrowly focused verification of public claims, not a technical analysis of the exploit. No firmware image or console artifact was used.

## Conclusion in a nutshell

On July 8, 2026, Gezine publicly **announced** the userland exploit for "Switch 1/2" and claimed that it was not a WebKit or save exploit and "works at all fw". This is proof of the author's public claim, not proof of an independently verified or publicly usable exploit. As of the date of review, I could not find a public source code, PoC, technical article, or reproduction manual. News of the demo describes a video featuring the Nintendo Switch 2; I couldn't find evidence of a demo on the original Switch, and certainly not on the Mariko/T210B01.

The published permission boundary is only "userland". The announcement does not imply an application sandbox leak, system service compromise, kernel, persistence, or CFW. The name "userland" alone does not tell in which process or in which specific sandbox the code is running.

## Checking of individual claims

| Question | Finding | Certainty |
|---|---|---|
| Original announcement | X status dated 08/07/2026 by Gezine: "I created switch 1/2 userland exploit that is not webkit or save exploit" and claim about all firmwares. The direct status could not be retrieved during the check (HTTP 403); date and text are reproduced in contemporary articles. | Medium for precise wording; high that the author made such a claim publicly |
| Original Switch 1 | The author explicitly writes Switch 1/2. That is a direct claim of support, not an independent test. Later reviews refer to the video as a demonstration on the Switch 2. | Medium for claimed support; low for real functionality on Switch 1 |
| Mariko/T210B01 | No test found for Mariko, Model V2, T210B01/Tegra214 or Switch V2. Erista also cannot be confirmed as a tested device. | High confidence that such evidence is lacking in the public sources reviewed; not proof that the test never ran |
| | firmware range "All fw" is the author's broad claim with no version matrix, builds, bug IDs or reproduction steps. Secondary articles mention 20.0.0+, but a later patch attributed to Gezine says that 20.0.0+ on Switch 2 is required to enable Switch 1 game compatibility. This is a different host platform condition; it does not show the lower limit of vulnerability of Switch 1. | Medium for this resolution; the patch itself is only available via mirrored post |
| Availability | I could not find a public exploit repository, PoC or package. October's scene reviews still list the Gezine exploit as unreleased. | Mid-Alto |
| Technical Mechanisms | No primary technical analysis of the code, errors or ROP chain was found. Claims of ARM64 ROP in secondary reports are insufficient to establish the mechanism. | High |
| Permissions | The author calls it userland. Elevation of privileges to service/kernel or access to the system is not documented. | High |

## Important technical interpretation 20.0.0+

The most concrete new insight from the review is that "20.0.0+" cannot safely be listed as the minimum vulnerable firmware of the original Switch. Tarnkappe's secondary article filed this ambiguously as an exploit requirement. Gezine's mirrored profile later gives a more precise explanation: the Switch 2 needs 20.0.0+ to enable compatibility with the Switch 1, and a physical card with the appropriate minimum firmware for a manual update. This explains the requirement to run a Switch 1 game on Switch 2, not the extent of the bug on Switch 1. Since the original patch status is unavailable to the tool, I rate this interpretation as **moderately credible**, not confirmed fact.

## Resources

Each entry lists the source date, type of evidence, and credibility for the claim in question.

1. [Gezine, X status 2074894225460822503](https://x.com/gezine_dev/status/2074894225460822503) — **8. 7. 2026; primary public notice; medium credibility**. Direct content was not available in this collection (403); the text of the announcement is reproduced by independent articles, including Hackintendo.
2. [Hackintendo — Une faille userland Switch 1 & 2](https://hackintendo.com/une-faille-userland-switch1-2/) — **8. 7. 2026; secondary article with embedded/quoted status; medium credibility** for what the author reported, low for unexplained technical details.
3. [Gezine, X status 2075682718155956275](https://x.com/gezine_dev/status/2075682718155956275) — **10. 7. 2026; primary follow-up status; unavailable while loading (403)**. Patch cited by [TwStalker profile mirror](https://w.twstalker.com/gezine_dev) — **capture dated July 2026; secondary mirror; low to medium credibility**.
4. [Tarnkappe — Gezine entdeckt Userland-Exploit](https://tarnkappe.info/artikel/jailbreaks/gezine-entdeckt-userland-exploit-fuer-nintendo-switch-1-2-331326.html) — **11. 7. 2026; secondary article; low to medium confidence** for the 20.0.0+ boundary claim because it does not distinguish platform assumption from error extent.
5. [Switch2Unlock — News](https://switch2unlock.com/en/news/) — **continuously updated until 10/29/2026; secondary overview with links to original statuses; medium confidence** for date, unissued status, and source records; is not an independent technical confirmation.
6. [Nintendo — Security advisories](https://www.nintendo.com/security-advisories/en/index.html) — **page checked 10/30/2026; official register; high credibility** for published advisories. No record was found identifying Gezine or this error. The absence of a record is not proof of the absence of error.

## What is needed for verification

To elevate a claim to confirmed compatibility would require, as a minimum: a public reproducible PoC or full technical analysis; the exact game/app and entry point; result on specific Mariko/T210B01 console and HOS 23.0.1; process/authorization boundary record; and independent reproduction. None of these points are publicly documented in the sources reviewed.
