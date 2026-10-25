# Part A release — 25 October 2026

## Summary

Jake said **“approved”** after reviewing the completed Part A checkpoint.
[PR #12](https://github.com/EviIius/agents-agenticrag/pull/12) merged as
`958891bec226d7bc22c9635b370c021598b77686`. The qualified static blur repair is
published at [Aether](https://jakes-mac-mini.tailc4d343.ts.net/).

The service was not restarted. The backend, image worker, runtimes and selectors
are unchanged. No user chat or preference was changed by release verification,
no model was loaded/unloaded, and no inference or download was invoked.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Approved exact main merge | Pass | PR #12, expected head `7c94406d`, merge `958891be` |
| Qualified source/evidence preserved | Pass | 456 source hashes and 166 prior evidence hashes; `verification.json` |
| Current server/worker compatibility | Pass | 126 backend/shared/lock files and four worker files match; runtime/configuration hashes preserved |
| Fresh rollback preparation | Pass | Previous static tree and online DB backup; backup schema 14, integrity ok, no FK violations |
| Web-only publication | Pass | All 476 candidate files exact; 44 old hashed assets retained; 47 files changed |
| Service invariants | Pass | Same PID 77443; plist/bind/port/label/Tailscale unchanged; no restart |
| Local and HTTPS delivery | Pass | Health 200 and nine exact HTML/SW/JS/CSS/theme-init asset hashes on each origin |
| Actual installed UI | Pass | Four Chromium/WebKit light/dark cases with synthetic intercepted APIs; computed blur and overlay alpha checked |
| User data safety | Pass | No write/restore to live data by controller; current schema/integrity/FKs valid; no row-equality claim during ongoing user activity |
| Physical iPhone/Safari application | Pending | No acceptance invented; earlier “I’ll check later” remains pending |

## What changed

- The runtime product remains the single CSS repair qualified in
  [the technical report](AERO-BLUR-FIX-REPORT.md).
- Publication uses `artifacts/aero-blur-fix-release-20261025/publish_static.py`,
  pinned source/static manifests and the established atomic-copy pattern.
- The generic deployer and obsolete older static-publisher backend baseline were
  not used. The current schema-aware backend and worker remain installed.
- Every new asset was installed before index switched; service worker was last.
  Old hashed assets remain available to already-open pages.
- Release authorization, this report and synthetic installed-UI evidence were
  added. The original workspace and all 15 supplied critique inputs are preserved.

## QA and runtime observations

The existing qualified **785 Python /151 frontend /969 contrast-pair /900 browser**
gates and four existing browser skips remain the release baseline. Product bytes
are unchanged, so the complete suite was not needlessly rerun for release docs.
Initial JS remains **252,228 /256,000 gzip bytes**.

Release dry-run and actual publication pass. All **476 candidate static files**
match their pinned hashes; the installation contains **520 static files** after
retaining **44** old assets. The current and backup databases report schema 14,
integrity `ok` and no foreign-key violations. The running service PID remains
**77443** before and after publication.

The installed observer loads actual normally verified HTTPS assets in Chromium
at 1440px and WebKit at 390px, in both themes. Every API response is intercepted
with invented data; no request is forwarded to a live mutation/model endpoint.
It verifies:

- composer/header/sidebar or mobile sheet blur and at least 92% overlay alpha;
- Tools and Settings, with a decoded 1024px synthetic busy image in the gallery;
- ordinary typing and enabled Send without sending;
- new-chat motion and the reduced-motion trigger;
- Workflows opening, no horizontal overflow and zero page/asset errors.

These are four installed-UI checks, not a second complete browser regression or
a real iPhone, installed Safari, real keyboard/share or real generation pass.
Earlier rendered contrast qualification remains **584 text runs**, minimum
**5.64:1** with or without blur. Codex inspected the installed phone-width dark
Settings capture; that observation is not attributed to Jake.

## Evidence

All new public evidence is in `artifacts/aero-blur-fix-release-20261025/`:

- `dry-run.json`, `release-manifest.json`, `publish_static.py`;
- `publication.json` and `publication.log`;
- `installed-ui.mjs`, `installed-ui.json`, `installed-ui.log`;
- eight `*-fake.png` screenshots, `verification.json`, privacy and hash manifests.

Earlier failed fixture attempts and all prior QA records remain unchanged.
No existing test, assertion, timeout, skip or threshold changed for this release.
No new dependency, schema, prompt, sampling, provider or model call was introduced.

## Rollback

Fresh private recovery files are at
`~/.local/share/workbench/releases/aero-blur-fix-20261025/`:
the previous static tree, its manifest, a consistent online DB backup and the
publication controller/result. The DB is private recovery evidence, not a UI
rollback selection and never a replacement for newer user work.

For a UI delivery failure, restore only the previous static bytes, with index
and service worker last. Keep any newly added hashed assets available for open
clients, and preserve the **current backend, worker and current data**. The
publication controller has this rollback path; no rollback was needed.

## Next checkpoint

Part A is live. Part B is next on its separate branch: make source photos and
Create/Edit modes visible, use the approved image-follow-up behavior, and expose
stopped/empty replies before the controls and starter cleanup. J22–J25 are already
approved; their broader changes are not part of this release. The archive schema
and rule remain a later presentation-before-migration gate.

The real iPhone check and historical VoiceOver limitation remain pending/unresolved.
