# Phase 4 — new public research for Switch 1

**Scope of review:** Public sources released in 2025–2026, with emphasis on Mariko/T210B01, HOS 20.x–23.0.1, userland, services, and kernel. The list only lists things relevant to the Switch 1/2 difference; does not repeat the general overview from phase 3.

## Search result

I have not found a new, technically documented exploit for the original Switch on Mariko/HOS 20.x–23.0.1 in the public sources reviewed. The most relevant new clue is Gezina's July 2026 announcement: it directly claims a Switch 1/2 userland exploit outside of the WebKit/save path, but without public code, technical analysis, or verification on the original Switch. Only the unverified option remains for the Mariko 23.0.1 target.

The later public project **ns2jb** is not proof for Mariko: its primary repository and author description are explicitly for Switch 2. This is the most important platform difference in the new results, and the reason why the recent Switch 2 reports cannot be flipped to Switch V2.

## Relevant records

| Research | Date and Type of Evidence | What | Proves Relation to Mariko 23.0.1 | Credibility |
|---|---|---|---|---|
| Gezine — new offline userland exploit | 7/8/2026; author's public claim on X, reproduced in | articles Author claims "Switch 1/2", outside of WebKit and save exploit, "all fw". Later articles describe the video as a Switch 2 demo; no public implementation. | Switch 1 is declared, Mariko and HOS 23.0.1 are not proven. | Medium for the existence of a public assertion; low for functionality on the target device. See [primary status](https://x.com/gezine_dev/status/2074894225460822503), [periodic report](https://hackintendo.com/une-faille-userland-switch1-2/). |
| Gezine — follow-up explanation 20.0.0+ | 7/10/2026; author's status which was not directly loadable and its mirror | 20.0.0+ is listed for Switch 2 backwards compatibility of Switch 1 games; it is not a reliable threshold of the Switch firmware vulnerability 1. | Does not apply as proof of HOS 23.0.1 exploitatibility on Mariko. | Low to medium; [primary status](https://x.com/gezine_dev/status/2075682718155956275), [mirror](https://w.twstalker.com/gezine_dev), [secondary explanation](https://modda.se/en/news/underland-exploit-foer-switch-2). |
| ns2jb | 18.–22. 10. 2026; primary [author entry](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/) and [GitLab source repository](https://gitlab.com/pepsipu/ns2jb) | Publicly published research path for Switch 2, HOS 23.0.1. It is proof positive only for Switch 2. | Not transferable proof for Switch 1, Mariko or T210B01. Calling it a "Switch exploit" without a model is misleading. | High for published code and declared target; tests on a physical device are the author's claim, test independence is limited. |
| Nintendo Security Advisories | Register checked 10/30/2026; official primary source | Contains published security notices, but not found Gezine/Mariko 23.0.1 advisory. | This does not confirm independent exploit disclosure or patch mapping. | High for register content; the absence of a record is not proof of the absence of a vulnerability. [Official Registry](https://www.nintendo.com/security-advisories/en/index.html). |

## Which remains without proof

- Public ARM64 userland, service or kernel PoC for the original Switch V2/Mariko on HOS 20.x–23.0.1.
- New offline entry point for original Switch, independent of browser, transferred save file, modchip or existing unlock.
- A public conference transcript or technical article that would discuss Gezina's claim and map it to Erista/Mariko.
- Independent reproduction of Gezine on Switch 1 or Mariko.

A search will not prove that private research does not exist. It just means that no new reproducible evidence for the target has been found in the public sources searched.
