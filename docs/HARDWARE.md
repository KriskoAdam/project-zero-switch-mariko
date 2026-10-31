# Hardware target

## Primary target

- Retail Nintendo Switch V2, owner-described model.
- Intended target platform: Mariko / NVIDIA Tegra X1+ T210B01 (also referenced as Tegra214 in this project).
- The physical USB identity 057e:201d identifies a Nintendo USB device in the observed MTP state; it does not identify the SoC revision.
- The model/revision has not been independently authenticated from a public hardware diagnostic or board-level observation. Treat Mariko as the intended target, not as a proven property of every recorded measurement.

## Platform distinctions

- **Erista:** original Tegra X1 variant associated with early Switch hardware. Do not assume its jailbreak methods work on Mariko.
- **Mariko:** later Tegra X1+ family used in revised Switch hardware. A “V1 Mariko” label is ambiguous and should not be used without exact revision evidence.
- **Switch 2:** a separate platform. A Switch 2 jailbreak does not establish a Switch V2 / Mariko jailbreak.

Every contribution should specify retail model/revision, SoC evidence, region if relevant, and whether the observation came from physical hardware, public source material, or an emulator.
