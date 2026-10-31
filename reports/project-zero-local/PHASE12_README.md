# PROJECT ZERO — Phase 12

Phase 12 includes both host and physical non-invasive tests of the system web applet on Switch and a follow-up probe of Phase 13. The test page is at web/index.html. The local HTTP server is server.py (handles both GET and HEAD) and the narrowly constrained DNS responder is dns_redirect.py. Results and access log are in results/.

## Confirmed result

The page was executed in the WifiWebAuthApplet on a physical Nintendo Switch. It caught Nintendo Switch User-Agent, successful DOM events, Fetch/XHR HTTP 200 and WebSocket echo. WebAssembly was undefined. HTTPS was not tested. Details and evidence limits are in REPORT.md and TEST_RESULTS.md.

HOS 23.0.1 was previously manually confirmed by the user on the same console. Mariko/T210B01 is not independently verified by this web test. This is not a vulnerability or a Homebrew entrypoint.

## Local logs

- results/phase12_web_results.jsonl — five runs: three host and two from WifiWebAuthApplet (one of them with PZ13 passive probe).
- results/phase12_access.log — HTTP requests; may contain the client's local IP.

## Cleaning up after the test

1. On the Switch, reset the DNS for the saved Wi-Fi network to Automatic.
2. Press Ctrl-C in Terminal window with sudo DNS responder.
3. Press Ctrl-C in the Terminal window with the HTTP server on port 80.

The router did not change. Never put your password, account or other secrets in the test page. Do not bypass it for TLS warning.

## Resources

- [Switchbrew — Internet Browser](https://switchbrew.org/wiki/Internet_Browser) — technical description of applets and known User-Agents.
- [Switchbrew — Network](https://switchbrew.org/wiki/Network) — network domains including ctest.cdn.nintendo.net.
- [Nintendo Support — temporary DNS change](https://support.nintendo.com/tw/switch/qna_sub/33977.html) — official instructions for manual DNS change and reset.

The latest passive bridge result and interpretation boundaries are in `../../reports/EVIDENCE_REGISTER.md` and `REPORT.md`. The local HEAD response was supplemented after detecting an HTTP 501 on the old server; the physical Switch test with the modified server has not yet been repeated.

Physical USB enumeration and read-only MTP/endpoint metadata are recorded in `../../reports/USB_LIVE_CAPTURE_20261031.md`. It is not proof of Mariko identification or Homebrew entrypoint.
