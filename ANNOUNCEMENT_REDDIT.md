# Reddit announcement draft (not posted)

**Title:** PROJECT ZERO: an open, AI-assisted investigation of a software-only Switch V2 Mariko entry point

I have opened PROJECT ZERO, a small independent research effort started with a Switch V2, a MacBook, and AI coding/research tools. The question is whether a reproducible software-only homebrew entry point exists for Mariko/T210B01 on HOS 23.0.1.

The honest result so far: we have not found or demonstrated one. We did safely observe the stock Wi-Fi web-auth applet loading a benign local page and performed read-only MTP measurements. The MTP storage identifier changed after a user-controlled mode restart, but no security issue was shown. The exact SoC on the test console is not independently verified.

The repository includes sanitized reports, host-side experiments, evidence labels, and an AI contribution guide. We are looking for independent source review, reproducible testing, and skeptical criticism—not exploit payloads, keys, firmware dumps, or console secrets. The local native Homebrew app is intentionally excluded.

[Repository link to be added after publication]
