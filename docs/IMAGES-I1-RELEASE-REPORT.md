# Images I1 release report — 12 October 2026

## Summary

Jake approved product-delivery steps 1–4, including the specific retained G9
exception. The existing Images candidate is installed and healthy on the original
launchd service and Tailscale URL. One synthetic live generation completes with
measured SSE progress, durable output and idempotent duplicate submission.
Original Search failures remain failures; no grounding candidate is qualified.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Candidate resource/cancel/recovery/browser qualification | Pass | `IMAGES-I1-REPORT.md` and its retained native sequence; 508 Python, 39 frontend, 473 browser passes, three existing skips |
| Specific G9 hold resolved explicitly | Accepted exception | Product-delivery authorization in `AGENTS.md`; unchanged matched failures in `IMAGES-SEARCH-DIAGNOSIS-REPORT.md` |
| Private app/plist/SQLite fallback | Pass | `artifacts/product-delivery/i1-release/prepared.json` identifies the private snapshot; actual content stays outside Git |
| Existing database rows preserved | Pass | `verification.json`: 31 existing tables byte-equivalent, four added image tables |
| Ordinary Search source unchanged | Pass | All 14 module hashes match before/after installation |
| Existing service/route/runtime | Pass | Original label, 127.0.0.1:8787, local and normally verified HTTPS health 200; Ollama 0.35.0 |
| Actual live generation | Pass | `live-result.json`: 13.2637 seconds, nine measured SSE events, same job on duplicate submission |
| Output storage verified | Pass | PNG 1,033,972 bytes; metadata 726 bytes; output hashes and native file retained |
| Physical iPhone generation/save/cancel | Pending observation | Requested from Jake; automated mobile evidence is separate, no physical pass invented |

## Changed files

- Installed the already reviewed Images/jobs source, static build and existing
  approved worker selector using `scripts/deploy.py --apply`.
- Added public synthetic/hash-only release evidence under
  `artifacts/product-delivery/i1-release/`; no real recordings/documents captured.
- Product authorization and delivery plan record the approved exception and next
  two fixed workflows.

## Deviations from SPEC.md

The specific historical Search gate hold is accepted for I1. Its prior failures,
all original reports and targets remain unchanged. This does not qualify Search
quality or authorize another reliability experiment. Physical phone observation
remains pending while the explicitly approved delivery sequence continues.

## Runtime observations

The first hash-only snapshot helper could not read the Library virtual table
without loading the already approved SQLite extension. The initial source/log and
private snapshot are retained; the corrected helper enables that extension only
for its read-only hash connection. No interpreter/package/runtime change follows.

The live worker reports initialization, weight loading, denoising step progress,
decoding and saved output through SSE. No fake progress or polling is used.

## Test output

The same-source candidate's complete check/browser gates are retained in
`IMAGES-I1-REPORT.md`. Actual deployment and post-install verification logs,
including the native live result, are in `artifacts/product-delivery/i1-release/`.
The later combined workflow release runs a new complete regression suite.

## Screenshots

Synthetic responsive Images screenshots remain under `artifacts/images-i1/browser/`.
The actual synthetic live output is `artifacts/product-delivery/i1-release/live-output.png`.
No user's phone screen or private recording is included.

## Open questions for Jake

The previously requested iPhone generation/save/share/cancel observation remains
pending. This report records the technical release without attributing a device
test to Jake.
