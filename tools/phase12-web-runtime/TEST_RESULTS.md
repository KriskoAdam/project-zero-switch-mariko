# PROJECT ZERO — Phase 12 test results

## Continuation: physical USB/MTP observation (2026-10-31)

After reconnecting, macOS enumerated a Nintendo Switch (`057e:201d`) over USB 2.0 high-speed. Interface 0 was MTP (`06/01/01`) with three endpoints. Using `mtp-detect`, libmtp 1.1.23 reported device version `23.0.1` and one read-only `Album` storage. The device string does not distinguish V2/Mariko and is not independent firmware attestation. No objects were read and no writes were performed.

The passive libusb reader `usb_descriptors.c` then recorded the active configuration's endpoints: `0x81` IN bulk, 512 bytes; `0x01` OUT bulk, 512 bytes; `0x82` IN interrupt, 24 bytes, interval 4. The reader used `libusb_get_device_list`, `libusb_get_device_descriptor`, and `libusb_get_active_config_descriptor`; it did not open or claim the device and sent no MTP/bulk/interrupt data. Standard descriptor requests may be used to obtain USB descriptors. Reproduction steps and evidence classification are in `../../reports/USB_LIVE_CAPTURE_20261031.md`; raw output is in `../../reports/raw/usb_20261031/usb_endpoint_descriptors.txt`.

## Physical console

The page loaded in the applet, as shown by the saved result with this User-Agent:

```text
Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/613.0 (KHTML, like Gecko) NF/6.0.3.31.11 NintendoBrowser/5.1.0.55481
```

| Test | Result |
|---|---|
| JavaScript | Promise, Fetch, URL, and JSON available; WebAssembly was `undefined` |
| DOM / events | `createElement` and `addEventListener` available; synthetic DOM event succeeded |
| HTML5 | Canvas 2D true; `video.canPlayType` is a function; semantic `main` element true |
| Fetch | POST to local server returned HTTP 200 |
| XMLHttpRequest | POST to local server returned HTTP 200 |
| WebSocket | API available; local echo succeeded |
| HTTP / secure context | HTTP; `isSecureContext` false and `crypto.subtle` false. HTTPS was not tested |
| Automatic logging | Console result saved in `results/phase12_web_results.jsonl` |

### Repeat with passive probe — physical console

A new record with `probe_id=p0-wifiweb-passive-bridge-v1` was captured at 2026-10-30 23:47:17 +0100. The User-Agent again identified WifiWebAuthApplet. All selected globals (`nx`, `webkit`, `external`, `chrome`, `require`, `process`, `Deno`, `Components`) had `present:false`. No native bridge was invoked. `Worker` and `MessageChannel` were available; `Atomics`, `SharedArrayBuffer`, and `WebAssembly` were `undefined`. The DOM event, Fetch/XHR HTTP 200, and WebSocket echo succeeded again.

This result only refutes the presence of these specifically enumerated globals in this run. It does not rule out other APIs, an indirectly accessible bridge, or system IPC. The log does not identify Mariko/T210B01.

## Follow-up fix to the test server

An independent review found that repeated `HEAD /` responses with status 501 came from the local `BaseHTTPRequestHandler`, which did not implement `do_HEAD`. After adding a standard bodyless response, the host-side test returned HEAD 200, Content-Length 7996, empty body; GET returned 200 with 7996 bytes. The cause was in our test server, not the Switch. The corrected server was not retested on the physical console because that was unnecessary to identify the source of the 501 responses.

This result concerns WifiWebAuthApplet, not every Switch web applet. The user had previously confirmed HOS 23.0.1 in system settings on the same console. Mariko/T210B01 was not independently verified.

## Host-side test on Mac

Earlier runs in the Codex in-app browser verified that the page and server worked. On 2026-10-30, the extended `p0-wifiweb-passive-bridge-v1` probe was also preflighted in the same type of host browser (Chrome 156 User-Agent, not Nintendo Switch). The page completed, saved JSONL locally, Fetch/XHR returned 200, and the WebSocket echo succeeded. Descriptor inventory reported `nx`/`webkit` absent, `external` as an accessor whose value was not read, `chrome` as a data property, and the other selected globals absent. This host result only confirms that the page and logging work; it does not establish applet behavior.

## Network verification on Mac

- The DNS response for `ctest.cdn.nintendo.net` pointed to the Mac's private address (redacted in the public records).
- The HTTP server on TCP/80 returned 200 for a local request using that Host value.
- The access log recorded a page GET returning 200 and a results POST.
- Some HEAD requests returned 501; GET and subsequent tests succeeded.

## Interpretation

The experiment verified a web runtime and passively inspected selected globals on the physical Switch. The new observation is that the controlled list of bridge-like globals was not enumerable in this WifiWebAuthApplet session, while `Worker`/`MessageChannel` were available and `WebAssembly`/`Atomics`/`SharedArrayBuffer` were not. This is not a security flaw or evidence of a software Homebrew entry point.

After testing, restore the Switch's DNS setting to Automatic and stop the HTTP and DNS processes with Ctrl-C in their Terminal windows. Do not enter credentials.
