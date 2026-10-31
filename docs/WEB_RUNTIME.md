# Stock web runtime observations

The Phase 12 experiment used the standard Wi-Fi connection test/captive portal path and a local benign HTML page. The page logged a user agent and exercised basic DOM/events, Fetch, XMLHttpRequest, and WebSocket. Results are tied to one applet session and one test page. Some modern APIs were absent in the observed environment; consult the detailed report and raw sanitized logs for the exact checks.

This was not a general browser or WebKit audit. HTTPS behavior was not established; the local test used HTTP. No native-code bridge, arbitrary service access, sandbox escape, or vulnerability was demonstrated. A captive portal does not by itself bypass the applet's trust boundary. See `tools/phase12-web-runtime/` and `reports/project-zero-local/`.
