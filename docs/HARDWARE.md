# Hardware scope

## Primary target

- Retail Nintendo Switch V2, owner-described model.
- Target hypothesis: Mariko / NVIDIA Tegra X1+ T210B01 (also referenced as Tegra214 in this project).
- The physical USB identity `057e:201d` identifies a Nintendo USB device in the observed MTP state; it does not identify the SoC revision.
- Model/revision was not independently authenticated from a public hardware diagnostic or a board-level observation. Treat Mariko as the intended target, not as a proven property of every recorded measurement.

## Distinctions

- **Erista:** original Tegra X1 variant associated with early Switch hardware. Do not transfer exploit results to Mariko without evidence.
- **Mariko:** later Tegra X1+ family used in revised Switch hardware. A “V1 Mariko” label is ambiguous and should not be used without exact revision evidence.
- **Switch 2:** a separate platform. Results and requirements for Switch 2 do not prove compatibility with Switch 1.

Every contribution should specify retail model/revision, SoC evidence, region if relevant, and whether the observation was made on physical hardware, source, or emulator.
