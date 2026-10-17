# QA repair release — 17 October 2026

## Summary

Jake accepted the repair checkpoint and authorized release. PR #3 is merged as
`dc427dc3e5cc5db49944f844e3a1d90bcfed0522`; its exact tested application and the
Aether display rename are live at the existing Tailscale URL. The service returned
healthy in 2.017 seconds. The private full app/data/plist fallback is verified.
Physical iPhone acceptance is requested and pending.

## Done-when checklist

| Item | Result | Evidence |
| --- | --- | --- |
| Merge reviewed source | Pass | PR #3 merged; all 560 frozen source/test/config hashes match the tested candidate |
| Reproduce tested build | Pass | All 425 rebuilt hashes match; initial JS 254,975 gzip bytes, budget 256,000 |
| Full regression evidence | Pass, exact-source reuse | 686 Python / 126 frontend / 110 contrast pairs; one complete browser invocation with 711 passed and three unchanged skips |
| Full fallback and rehearsal | Pass | Private app/data/plist copies; consistent SQLite backup; candidate and previous application start on copied schema-13 data with network forbidden |
| Data preservation | Pass | All 55 pre-existing table projections match on copied startup and while live data is quiescent before bootstrap; no schema migration or data rewrite |
| Installed source/static | Pass | 114 server files and 425 current-build static files verified; previous hashed assets retained |
| Service and runtime identity | Pass | Exact original plist, one worker, 127.0.0.1:8787, Tailscale output unchanged; Ollama 0.35.0; existing venv, transcription and image-worker controls preserved |
| Live local/HTTPS checks | Pass | Health, workflow definitions/templates and image status; exact index/service-worker hashes; production /design remains 404 |
| Installed UI | Pass, synthetic API fixtures | Actual HTTPS Chromium and iPhone-profile WebKit: Aether title, Model default/reported levels, Tools/chip, paste undo, photo upload/viewer/removal, no overflow or page errors |
| Physical iPhone | Pending | Requested after publication; no physical result or VoiceOver pass invented |

Evidence: `artifacts/qa-roadmap/release-20261017/`. The repair report and all failed
baseline/harness/qualification attempts remain in `QA-ROADMAP-REPAIRS-REPORT.md`
and `artifacts/qa-roadmap/repair-1/`.

## Changed files

- **Installed server/web/shared display config:** exact reviewed application;
  no further product code changes during release. The same plist and installed
  interpreter are reused. Neither package synchronization nor worker/weight
  installation is performed.
- **Release controls:** a frozen private adaptation of the earlier reviewed
  one-off rollout, with its source/hash and public copy retained. It verifies the
  current manifests, rehearses schema 13 on both copies, disables child network,
  and removes the old migration-only all-messages-are-text assertion. This release
  performs no explicit migration. Ordinary rollback keeps live data because the
  schema is unchanged.
- **Docs:** release authorization/closeout, this report, and the reprioritized
  `HERMES-AND-PHOTO-EDITING-PLAN.md`. The original repair report remains a historical
  checkpoint with a release follow-up link.

## Deviations from SPEC.md

Preserve the exact working plist and existing frozen environment rather than
re-rendering the service or reinstalling packages. Use the reviewed full-fallback
rollout pattern rather than the generic deploy script, which would synchronize
packages and touch the transcription installation unnecessarily. Preserve old
hashed assets for open clients.

Full suites are reused through exact parity of all 560 frozen source/test/config
files, as authorized; no new broad test invocation is claimed. The production
build is reproduced and installation/startup/live UI are checked separately.
No new grounding exception, accuracy qualification or native experiment is implied.

## Runtime observations

The previous PID was 97687; the restarted service has PID 60537. Service identity,
arguments, environment, private worker selectors and the Tailscale route are
unchanged. The local and normally certificate-verified HTTPS endpoints are healthy.

The release controller and UI observer make zero native inference/load/unload
requests. UI API traffic is intercepted with synthetic fixtures; production static
assets are fetched from the real HTTPS origin. No real chat, filename, document,
photo or recording is captured in evidence.

## Test output

- Exact merged-source verification: **560/560** hashes.
- Fresh build parity: **425/425** hashes; **254,975** initial gzip bytes.
- Applicable completed source suites: **686 Python**, **126 frontend**, **110
  contrast pairs**, **711 browser passes / three unchanged skips / zero failures**.
- Candidate and prior copied-data lifecycle checks pass at schema **13** with
  sockets disabled. All **55** existing table projections are preserved.
- Actual installed server/static hashes and local/HTTPS status/hash checks pass.
- Actual HTTPS UI observer passes Chromium at 1440 and WebKit/iPhone 13 at 390;
  zero page errors, overflow or native inference requests.

These verify the repairs and release mechanics. They do not independently verify
Claude's original model accuracy/timing claims, promise faster reasoning, or
qualify factual grounding. The new thinking warning uses the existing Stop action;
there is no guaranteed Answer now response or hard reasoning deadline.

## Screenshots

The repair checkpoint retains synthetic screenshots. The live release observer
takes no screenshot/video and reads no real API data. It verifies actual installed
assets with synthetic responses; source and result JSON are retained.

## Rollback

- Source tag, pushed to GitHub: `checkpoint/pre-qa-roadmap-2026-10-17`.
- Private fallback:
  `/Users/evilius/.local/share/workbench/qa/qa-roadmap-release-20261017T212135Z`.
- Contains the complete prior app, complete private data snapshot with consistent
  SQLite backup, exact plist, manifests, rehearsal logs and frozen controller.
- The controller's `rollback` action restores the prior app/plist, keeps current
  live data on the unchanged schema, and checks health. Whole-data restoration is
  reserved for a separately assessed recovery so accepted messages/files are not
  silently replaced by an earlier snapshot. No rollback is executed on this
  successful release.

Existing Home Screen bookmarks may retain their manually assigned name; the
page/PWA display metadata is Aether. No new icon or internal service rename occurs.

## Next checkpoint and open questions for Jake

Await the requested phone result and repair any release regression. Hermes
integration assessment now takes priority over a custom agent loop; the concrete
proposal and photo-editing scope are in `HERMES-AND-PHOTO-EDITING-PLAN.md`.
Installation and native trials still require their named scoped approval under
AGENTS.md. Nothing in this release installs Hermes or enables reference edits.
