# PROJECT ZERO — Phase 12: Network & Web Runtime

Date: 2026-10-30. It was tested using the stock Nintendo Switch V2 via the system WifiWebAuthApplet. HOS 23.0.1 was previously manually confirmed by the user in system settings. The exact Mariko/T210B01 SoC has not been independently verified.

## Result

The test page successfully opened on the physical console and automatically saved the results to the Mac. The User-Agent from the console identifies the Nintendo Switch and the WifiWebAuthApplet. This is the real result of the web runtime; it is not proof of a vulnerability, a sandbox break, or a path to Homebrew.

Observed capabilities in this applet:

- Available: Promise, Fetch, URL, JSON, DOM element creation and events.
- Unavailable by test: WebAssembly was undefined.
- The DOM event was successfully invoked.
- Canvas 2D, video.canPlayType and semantic element main were available.
- Both Fetch and XMLHttpRequest POST to local server returned HTTP 200.
- WebSocket API was available and local echo test passed.
- The page was running over HTTP, so isSecureContext and crypto.subtle were false. HTTPS and certificate behavior were not tested; from this result it cannot be concluded that HTTPS is not supported by WebCrypto.

## Captured User-Agent

Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/613.0 (KHTML, like Gecko) NF/6.0.3.31.11 NintendoBrowser/5.1.0.55481

The public Switchbrew table contains an older entry for Switch with AppleWebKit 613.0, NF/6.0.3.27.11 and NintendoBrowser/5.1.0.35219; we did not find the exact string from our test in the available public search results. It is therefore a new local deduction of the User-Agent, not a publicly confirmed identifier of HOS 23.0.1. We associate the HOS version with this run based on a previous user read on the same console, not from the User-Agent.

The observation of the User-Agent is documented by the original Switch web applet. It does not prove T210B01/Mariko by itself; this chip has not been read or independently identified at this stage.

## Network path and proof

The user started a local DNS responder and temporarily set the Switch to allow the captive-portal web applet to reach the Mac. The DNS response from the Mac mapped ctest.cdn.nintendo.net to <PRIVATE_IP>. The HTTP server listened on the Mac's private address, TCP/80; the host test for this address returned an HTTP 200. A console log of the page with the User-Agent WifiWebAuthApplet and the saved test result confirms that the page was rendered and the scripts caught up.

The access log also contains HEAD requests for which the server returned a 501, and GET requests with a 200. HEAD requests did not prevent the page from loading successfully and completing the tests. Their origin or purpose is not determined from the log.

## Classification of evidence

| Assertion | Classification |
|---|---|
| Page rendered in WifiWebAuthApplet | Confirmed from physical console via its User-Agent and automatic result log |
| HOS 23.0.1 | Manually confirmed by user at an earlier stage; it is not encoded in User-Agent |
| Mariko/T210B01 | User-declared target, not verified in this experiment |
| JavaScript/DOM/Fetch/XHR/WebSocket results | Caught while running web applet on console |
| The exact User-Agent is specific to HOS 23.0.1 | Unverified; the searched public sources do not list the exact string |
| WebAssembly missing from every Switch web applet | Unverified; the test only applies to this page in WifiWebAuthApplet |
| Vulnerability or sandbox leak | Not found or tested |

## Security evaluation

The site used only harmless JavaScript. It didn't call Nintendo APIs, it didn't work with accounts or secrets, and it didn't run native code. The test confirms the presence of a usable system web runtime in the captive-portal context. It does not provide a generic browser, does not allow arbitrary native codes, and is not Homebrew entrypoint proof. No TLS warning was bypassed.

## Files and logs

- Test page: web/index.html
- HTTP server: server.py
- DNS responder: dns_redirect.py
- Results of automatic runs: `results/phase12_web_results.jsonl` — five runs: three host and two with Nintendo Switch User-Agent (the second is an extended PZ13 run)
- HTTP access log: results/phase12_access.log

Logs contain User-Agent and local client IP; leave them in the local project.

## Resources

1. [Nintendo Switch Brew — Internet Browser](https://switchbrew.org/wiki/Internet_Browser), checked 2026-10-30. Public reverse-engineering documentation. Describes NetFront NX/WebKit, captive-portal applet, custom DNS and known User-Agent samples. Medium credibility for documented historical observations; not a primary Nintendo source.
2. [Nintendo Switch Brew — Network](https://switchbrew.org/wiki/Network), checked 2026-10-30. Public reverse-engineering documentation lists ctest.cdn.nintendo.net as a replacement for the older connection-test name. It does not confirm the exact flow on our version.
3. [Nintendo Support — temporary DNS change on Switch](https://support.nintendo.com/tw/switch/qna_sub/33977.html), checked 2026-10-30. Official instructions for temporary DNS change and reset; high trustworthiness for normal setup procedure, not for captive-portal internals.

## Continued research — Phase 13 passive bridge API inventory

**Question:** Does the WifiWebAuthApplet from JavaScript expose visible globals that may represent a JS-native bridge? The test only detects them via property descriptors. Accessor values ​​are not read; Neither `nx.sendMessage` nor `webkit.messageHandlers` are called. The test does not generate an error, does not try to escape from the sandbox, and does not send any data outside the local server.

**Implementation:** `web/index.html` adds identifier `p0-wifiweb-passive-bridge-v1`, inventory `nx`, `webkit`, `external`, `chrome`, `require`, `process`, `Deno`, `Components`, safe check of descriptors `sendMessage`/`messageHandlers` only for directly accessible data properties and additional runtime feature checks (BigInt, Atomics, SharedArrayBuffer, Worker, MessageChannel). The result goes to the existing local JSONL log.

**Host Verification:** On 10/30/2026 the page was loaded in the Codex in-app browser from the local server at `<PRIVATE_IP>:8765`. `py_compile` server preflight passed. The page completed the tests and saved the JSON result; Fetch/XHR returned 200 and WebSocket local echo succeeded. In this browser, `nx`/`webkit` was absent, `external` accessor (value not read), `chrome` data property; other selected globals absent. Host behavior does not carry over to Switch.

**Physical result on first write-in:** None yet for new probe. A later physical replay is in a separate section below; the original log without `probe_id` is not retroactively considered a probe result.

**Reproduction on Switch:** After starting the local DNS responder and HTTP server on port 80, temporarily set a manual DNS server on the saved Wi‑Fi network to the Mac's private IP, run the standard connection test again and open the page in the system WifiWebAuthApplet. When you see "Done" reset DNS to "Automatic" and stop both local servers. Do not continue at TLS/authentication warning; the test is HTTP local diagnostics. Proof needed: new JSONL line with `probe_id=p0-wifiweb-passive-bridge-v1` and Switch User-Agent.

**Conclusion limits:** Even a negative descriptor result does not rule out a hidden/unenumerable bridge, an API accessible only through an accessor, another applet configuration, or a system IPC path. The positive presence of a global would not by itself prove that it is callable, privileged, vulnerable, or usable on Homebrew. The list of twelve qualitatively ranked hypotheses and the top three directions are in `../reports/UNRESOLVED_QUESTIONS.md`.

### Physical repetition of the probe — 10/30/2026

The user reported the completion of the procedure. The new entry in `results/phase12_web_results.jsonl` has `probe_id=p0-wifiweb-passive-bridge-v1`, client User-Agent `Nintendo Switch; WifiWebAuthApplet`, server time `2026-10-30T23:47:17+0100`, and the HTTP log confirms page loading, test requests and result POST. This is **class A according to user report and correlated logs**, not a cryptographically authenticated device identity; HOS 23.0.1 is confirmed by the user from the previous download. Mariko/T210B01 has not been independently identified.

Probe results on this console:

- `nx`, `webkit`, `external`, `chrome`, `require`, `process`, `Deno` and `Components`: `present:false`.
- `nxSendMessage` and `webkitMessageHandlers`: not inspected because parent globals were not available as direct data properties.
- `invokedAnyNativeBridge:false`.
- `WebAssembly`, `Atomics` and `SharedArrayBuffer`: `undefined`; `Worker` and `MessageChannel`: `function`.
- DOM event succeeded; Fetch and XHR received an HTTP 200; local WebSocket echo succeeded.

**Evaluation:** The hypothesis of a directly visible bridge in the controlled list was not confirmed in this captive-portal run. This does not exclude a bridge available via a different name, accessor, specific session/context, uncovered API or IPC available only to native code. The result does not demonstrate a vulnerability and does not provide evidence of a software-only Homebrew entry.

After recording the result, the temporary DNS responder and HTTP server processes were terminated; the socket check no longer found a listener for UDP/53, TCP/80 or TCP/8765. The DNS state stored in the Switch cannot be verified from a Mac; it should be left on "Automatic".

### Follow-up check of the HTTP HEAD trace

An independent Skeptic found in the access log repeated `HEAD /` → 501 before the successful `GET /` → 200. The cause was local and directly verifiable: the own `BaseHTTPRequestHandler` did not have a `do_HEAD` method, so the standard handler returned 501. I added a secure HEAD response without a body. Host test on 10/30/2026 returned `HEAD 200`, `Content-Length: 7996`, body 0 bytes and `GET 200` with 7996 bytes. This closes the clue as a limitation in our test server; it's not console behavior or a bug. The current hashes of the server and the access log are in the registry records.

**Artifact Integrity:** SHA-256 `web/index.html`: `5ced501e8aaa3b64b37d9600985be86c07804d5b5171e1a89de4bf937b8ece1b`; `server.py` after adding HEAD support: `87dbe24529169097fdeb70aad447fda47ddd6d741200f955cb1ff5fe046e7808`; `results/phase12_web_results.jsonl`: `d4f6ace2247e874cd99df88e5cf73c169c13cd507780c390e4bdc12623e3615e`; `results/phase12_access.log` after subsequent host HEAD testing: `2fa7023dd8eb3c27a1d5322c390fe99e8e488d31fa2fa9a7ae7067cc664dd35c`. Classification and independent review is recorded by `../../reports/EVIDENCE_REGISTER.md`.


**Publication translation note:** the physical test used the original Slovak-labeled page. This repository contains its English translation, prepared after the test. Current translated page SHA-256: fdd9b044956bcb48fb6e11be230b549f0865bb95f2519dce554764ebb60757d2. Historical hashes identify the original tested page and are not hashes of the translated file.
