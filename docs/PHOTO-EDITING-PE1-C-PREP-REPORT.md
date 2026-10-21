# PE1-C preparation report — qualification and rollback

## Summary

CPU-only HEIC/JPEG preparation, compiled-app checks and synthetic schema-14
startup/retry rehearsals are complete. A real old-server rollback hazard was
found and a narrower compatibility fallback was verified. The bounded four-image
native qualification is prepared and fake-rehearsed, **not executed**. Main/live
and PE0/private-photo trial counts are unchanged. C is not release-qualified.

## Done-when checklist

| Item | Status | Evidence in `artifacts/photo-editing/pe1-c-prep-20261020/` |
| --- | --- | --- |
| Actual system HEIC + CPU codec; raw/preview/hash/metadata checks | Pass, CPU only | `cpu-heic.json`, `cpu_heic_check.py` |
| Larger HEIC edge limit and JPEG EXIF rotation | Pass, real CPU preparation | `fixture-manifest.json`, four-case `offline-controller.json` |
| Compiled candidate functional checks | 10/10, fake inference | `built-functional.txt` |
| Cold module/highlighter/active SSE checks | Pass, two browser observers | `built-browser.json` |
| Previous full-server schema-14 rollback | **Unsafe; blocked from release procedure** | `rollback.json`, previous manifest keys omit reference on retry |
| Candidate retries preserve pixels/reference | Pass, fake capture | `rollback-candidate-projection3.txt` |
| Original rows/files preserved in copied-data rehearsals | Pass | `rollback.json`: 42 table subsets, explicit chats/jobs immutable columns, 25 file hashes |
| Previous compiled UI + schema-aware candidate backend | Pass, Chromium + WebKit | `compatibility-browser.json`: reference-bound retry/output access |
| Native request budget/approval/failure/residency controls | 15 offline tests pass | `native-controls.txt` |
| Prepared four-case full controller | 4/4 fake jobs; actual CPU reference preparation | `offline-controller.json`; completion, cancellation, recovery |
| Native product-worker/resources/quality | **Pending separate approval** | `PHOTO-EDITING-PE1-C-PLAN.md`; no approval receipt supplied |
| Merge/publication/full old-backend rollback/actual iPhone | **Not performed or qualified** | Draft PR remains isolated |

## Changed files

- No product server/web/worker source is changed from B. `AGENTS.md` records
  authorization to prepare C without starting new native inference.
- This report and `PHOTO-EDITING-PE1-C-PLAN.md` define the qualification and safe
  fallback boundary.
- Synthetic offline scripts/results and a prospective trial-only admission
  subclass are in the C preparation artifact folder. No real photo/name/text is
  copied into Git. Generated large synthetic codec fixtures stay private, with
  public hashes/recipe only.

## Deviations from SPEC.md

The old server can start on schema 14, but lacks reference-aware retry. It must
not be used for rollback with current edit data. Previous UI + current backend
is a tested compatibility fallback, not complete backend rollback. A later
installer must enforce this boundary before publication. No limits, prompts,
packages, default, service identity or production files were changed.

The empty-model-slot admission is a **prospective trial-only policy**. The product
still requires the existing measured 32K profile. The new native plan asks to
qualify an empty slot and the same measured resident combination, plus at most
one explicit empty-message preload. No implicit allowance is inferred from
Jake's continuation or the earlier exhausted trial budgets.

## Runtime observations

Real `/usr/bin/sips` and the existing image interpreter/Pillow complete HEIC
conversion/normalization without importing MLX/MFLUX. A misleading `.png` upload
name still detects HEIF bytes. Malformed PNG decode is refused. The larger HEIC
normalizes from 2560 to 2048 square; the JPEG's orientation 6 swaps 960×1280 to
1280×960. Originals remain byte-identical and normalized previews strip metadata.

Compiled Chromium/WebKit cold pages load dynamic modules, render highlighted
code and open active SSE. Service workers were blocked: this is not a PWA update
or physical-phone pass. An earlier WebKit hard-navigation EventSource console
error is retained; its cause is not proven. Cold-page active-console checks do
not claim to fix every navigation teardown warning.

The old and new server rehearsals use extracted previous source/current source,
synthetic data copies and capture engines with network forbidden. Queued edits
are interrupted on startup. The old retry constructs only prompt/seed and invokes
ordinary generation; the candidate includes mode/reference and invokes edit.
No real worker is started in those rehearsals.

Read-only Ollama inspection reports no resident model, installed exact qualified
32K profile, and unchanged Ollama 0.35.0. No preload or inference was made.

## Test output

New focused evidence: real CPU codec cases and malformed refusal; **10/10**
compiled functional browser cases; **2/2** compiled cold-load observers;
**2/2** compatibility browser observers; old/candidate copied-data rehearsals;
**15** controller safety tests; **4/4** fake-controller cases with actual CPU
normalization. New native image/model calls: **zero**.

No broad suite is repeated with unchanged product code. B's exact source is
verified against its 572-file manifest; retain its full results honestly:
`make check` passes (745 Python, 132 frontend, 110 contrast pairs); the full
browser invocation has 737 passed / two older selector failures / three existing
skips, followed by a corrected complete image-upload file at 12/12. C does not
relabel that original invocation wholly green.

### Preserved preparation/harness failures

- Initial compiled-browser cleanup tried to signal an already exited process
  (ESRCH); cleanup now handles signalCode/ESRCH. One known owned fake-runtime PID
  was terminated. The next port-ownership guard correctly refused that occupied
  test port before cleanup. No live service process was touched.
- Initial rollback projection incorrectly treated FTS shadow storage as immutable
  rows. The corrected projection excludes search shadow families, preserves 42
  domain table subsets and separately checks immutable chats/jobs columns.
- A WebKit hard-navigation SSE console error is retained in its own attempt;
  later cold-load active-page checks are distinct evidence.
- The first preservation verifier used the wrong root for B’s repository-relative
  evidence paths; its assertion/log are retained. The corrected audit verifies
  the 922 unchanged files and the prior AGENTS text at its preserved commit.
- Initial compatibility helper consumed an HTTP body twice. Its source/log are
  retained; the corrected helper passes both browsers. No product patch was
  needed for these harness errors.

### Preservation audit

All 572 candidate source files, 429 candidate static files, 922 B evidence/source
files, 551 main files, 114 installed server files, 425 installed static files,
eleven PE0 source files and 73 PE0 evidence files verify unchanged. B’s original
AGENTS text is preserved at `a6163e17`; only the new C authorization/closeout is
appended. The four stopped-trial ledgers, six PE0 calls and one private photo
call are preserved. Local and normally verified Tailscale HTTPS health pass;
Ollama remains 0.35.0. See `preservation.json`.

## Screenshots

No supplied/private photo was captured. Existing B synthetic desktop/phone/theme
screenshots remain unchanged. C's compiled checks add response/console/protocol
records; no new UI layout is introduced that needs another screenshot matrix.

## Open questions for Jake

Approve or decline the concrete native qualification in the C plan: maximum
**four synthetic image-worker calls plus one empty-message preload** of the
already installed exact 32K profile, immediate stopping on failure. AGENTS.md and
the PE1 C gate require this separate bounded approval after A/B. No merge or
publication is part of that request. Native results and a concrete schema-aware
release/fallback procedure remain required before a release decision.
