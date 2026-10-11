# I1 durable jobs and Images — checkpoint report

11 October 2026. Candidate branch: `codex/images-jobs-i1`. Previous accepted
source: `ba75e28`. The initial failed native candidate is preserved at `f994a97`.

## Summary

The candidate implements durable image generation, a shared native execution
lease, an Images gallery/job view, cancellable PNG/JSON saving, storage totals,
output removal and image-aware backup/restore. The corrected isolated native
sequence passes. Full repository and browser suites pass.

**I1 remains open for release: G9 fails.** The accepted frozen Search replay was
25/25; this candidate run is 24/25 because the planner skips the injection case.
The injected page is never read, so injection resistance is not exercised.
Lexical citation support also decreases. No app deployment, service restart or
merge to main occurred. The installed application remains healthy and unchanged.
This report is the I1 review stop required by AGENTS.md and SPEC §H4; W1 has not begun.

## Acceptance checklist

| Requirement | Result | Evidence under `artifacts/images-i1/` |
| --- | --- | --- |
| Durable acceptance and idempotency | Pass | `test_images.py`: persisted input/queued row, identical-key deduplication and conflicting-key rejection |
| One native invocation, fair admission | Pass for measured combination | Capacity fairness/cancellation/inherited-lock tests; `native/sequential-4/result.json` |
| Real stages and SSE replay | Pass | Persisted events, reconnect snapshot/replay and browser navigation/reconnect tests; actual worker callbacks |
| Initialization/denoising cancellation and reaping | Pass | Final native sequence; initialization cancellation is before MLX imports, denoising cancellation after one synchronized step |
| Valid durable outputs and preserved original | Pass | Two validated PNG/JSON pairs; original hash unchanged; decoded pixels match I1-0 for each seed |
| Restart, failure, missing/corrupt output and low disk | Pass in synthetic/process tests | `test_images.py`; interrupted work requires explicit new-attempt retry |
| Image-aware backup, deduplication, restore and retention | Pass in synthetic tests and native backup | Full new-directory restore, corruption rejection, seven-snapshot pruning; actual two-output backup |
| Gallery/job controls, save cancellation and storage removal | Pass in Chromium/WebKit | Complete E2E run plus corrected gallery/dialog review |
| Full `make check` | Pass | `check-closeout-second.txt`: 508 Python, 39 frontend; all coverage targets ≥80% |
| One complete `make e2e` | Pass | `e2e-first.txt`: 473 passed, 3 existing skips, 39.7 minutes |
| API/rows/prompts/default payload preservation | Pass | Additive API guard; migration row checks; frozen prompt hashes; enabled-capacity ordinary-chat golden capture |
| Bundle/frame/scroll/first-token budgets | Pass | `bundle-comparison.json`; `regression-metrics/` |
| Ordinary Search G9 | **Fail / release held** | `web-regression-comparison.json`; failed default-fixture attempt also retained |
| Rollback to accepted build | Pass on synthetic copy | `rollback-second.json`: 27 old tables preserved, version 8 restored, previous app starts in 0.86 seconds |
| Production location/service invariants | Prepared, not activated | `deployment-plan.json`: existing label, `127.0.0.1:8787`, apply=false; deployment tests |
| Physical iPhone review | Not performed | No phone/native-share/VoiceOver pass claimed |

## Changed files

- **Server:** additive migration `009_image_jobs.sql`; `capacity.py`; `images/`
  validation, subprocess, jobs and backup modules; image API and schemas;
  lifecycle/backup integration; native lease around existing Ollama and
  transcription invocations; existing queued-chat SSE notification.
- **Web:** lazy `/images`, sidebar entry, generated API types, production
  gallery/job/storage/details/save/remove controls and `/design?images` states.
- **Worker/scripts:** private public-source installer, one-image offline worker,
  native qualification harness, offline image-backup restore, reviewed-worker
  deployment selector and synthetic rollback rehearsal.
- **Tests/docs:** image/process/API tests and fake worker, browser states and
  complete job flow, coverage targets/thread tracing, storage measurements,
  verification declaration, this report and deferred-list status.

No dependency, model download, runtime/default/sampling/prompt change, Research
restart, prompt rewrite or workflow call is included. Models are admitted using
reported digest/context/allocation; their names do not determine capabilities.

## Deviations from SPEC.md

The user's I1 authorization supersedes the original image-generation non-goal and
permits the additive image APIs/tables and native generation call in the reviewed
integration plan. Existing chat call types and sampling precedence stay intact.
The early default-fixture web invocation and overlapping native/web invocation
were execution mistakes; their failures are retained and are not counted as
release evidence. G9 and physical phone review remain unresolved rather than
being waived. Reference editing and W1 calls remain outside this checkpoint.

## Product behavior and limits

Accepted jobs outlive a phone/browser disconnect. Queued jobs recover after server
restart; uncertain active work becomes interrupted. Retry creates a new job with
its original input/parent link. The worker has bounded execution, EOF detection
for abrupt parent death and an inherited file lock. Capacity is released only
after owned process reaping. Chat is preferred at native boundaries, with a
background grant after at most three interactive grants when both queues wait.
Image generation cannot be preempted halfway through a GPU step for chat.

The current qualified settings are fixed: FLUX.2 klein 4B, pinned MFLUX 0.22.0
and model revision, 1024², four steps, guidance 1, eligible-layer 8-bit
quantization, explicit seed and a 1 GiB unused-allocation cache. That cache is
not a total host/Metal/live-tensor limit. Only empty residency or the previously
measured daily 32K profile is admitted; other combinations fail visibly without
automatic eviction. A live loaded-model and swap-growth guard remains in force.

“Use prompt for new version” creates a complete new generation with a parent
link. Reference upload/editing is not exposed. Completed outputs persist unsent.
Removing files keeps job input/history and existing backups. Automatic backups
share unchanged PNG/JSON blobs by content hash; weights are excluded. The restore
CLI requires a new destination and validates database/artifact coverage and hashes.

The durable job lifecycle starts with images. A workflow executor/saved definitions,
step-specific model assignments and recording-to-meeting-pack calls are still W1
work; this does not claim a general agent system already exists.

## Runtime observations and retained failures

1. The first native candidate cancels both stages correctly but fails normal
   completion after four steps. An isolated reproduction shows Python's buffered
   stdin daemon reader aborting shutdown with exit −6; the actual first native
   exit code was not captured. Replacing that reader with raw `os.read` avoids
   the buffer-lock abort. Both source versions and the reproduction remain.
2. `corrected-2` makes no image call: the harness reused the first private data
   path and refused an unretained retry. Its exact old harness source is saved.
3. `corrected-3` saves one image, then the version is stopped by the residency
   guard when a mistakenly overlapping ordinary web eval loads a different
   existing model/context. Preserve this orchestration failure and the successful
   guard action; it is not a successful complete qualification run.
4. The predeclared `sequential-4` run has no overlapping native eval. Both cancels,
   original, version, queued READY and before/after READY probes pass. End-to-end
   original/version time is 12.16/12.83 seconds. Cancellation/reaping is 0.003/
   0.012 seconds. The queued chat completes in 10.71 seconds including image wait.
   Cached tiny READY prompts are not a general chat latency or concurrent-decoding
   benchmark. Peak MLX allocation is about 18.66 GB; original settings/seeds remain.
5. The first focused browser run exposed an invalid label on the synthetic image
   placeholder and a fixture selector choosing older retained history. These were
   corrected; the full run is subsequently green. A later gallery review harness
   used the wrong setting key and captured light screenshots named dark. Its source,
   images and observation are retained separately; the corrected harness asserts
   the HTML dark theme before capture. Product appearance code was not changed.
6. The first rollback helper incorrectly queried `rowid` on a WITHOUT ROWID table;
   the corrected row comparison passes. Preservation helpers first used the wrong
   working directory, then treated intentional I1 production additions as changes
   to historical grounding inputs. The corrected verification checks those frozen
   production source objects at accepted `ba75e28` and all other trial inputs in
   place. No frozen manifest/case/report was rewritten. Build measurement initially
   used an unavailable `python` alias; the retained `python3` measurement passes.
7. Earlier lint/type/unit check failures and schema-version expectation changes
   are retained. The last additional test introduced one long line; its lint failure
   and the successful complete follow-up are both saved. Raw test logs retain their
   generated whitespace; the source-only diff check passes.

## Storage verification

| Item | Logical bytes / size |
| --- | ---: |
| Typical generation plus JSON, earlier sample median | 1,114,190 / 1.11 MB |
| Earlier observed generation range | 0.37–1.77 MB |
| Earlier reference edit, full PNG plus JSON | 1,379,509 / 1.38 MB |
| Final original plus additional version and JSON | 2,924,848 / 2.92 MB |
| Original 17 repository outputs plus private trial copies | 35,448,120 / 35.45 MB |
| Additional retained native output copies and backup files | 12,638,200 / 12.64 MB |
| Shared model snapshot, unchanged 18 files | 15,980,140,843 / 15.98 GB |
| Shared image-worker environment, non-symlink files | 1,092,409,741 / 1.09 GB |

Each revision/version is a full output. 1,000 at the observed median would be about
1.11 GB, an estimate rather than a fixed size. Weights/environment are shared once.
`IMAGES-STORAGE.md` separates outputs, backups, metadata, history and database.
These are logical bytes in named synthetic locations, not APFS physical/whole-Mac
usage. Screenshots/traces are separate QA storage.

## Web regression gate and release decision

The correct replay uses the accepted model, empty sampling values, unchanged
25 cases, frozen corpus and identical planner/answer prompt hashes. The earlier
9/25 default-fixture invocation is retained and is not the G9 comparison.

| Accepted 6 October replay → I1 replay | Baseline | Candidate |
| --- | ---: | ---: |
| Cases passed | 25/25 | **24/25** |
| Search decision accuracy | 1.0 | 0.963 |
| Required-fact case accuracy / citation validity | 1.0 / 1.0 | 1.0 / 1.0 |
| Successful web turns / failed web turns | 22 / 0 | 21 / 0 |
| Lexical citation support | 0.88238 | **0.86604** |
| Successful web TTFT median | 4.467 s | 4.470 s |
| Successful web TTFT p90 | 5.987 s | 5.721 s |

The injection case flips from pass to fail: planning skips retrieval and the
answer is generated without the fixture or citations. This does not demonstrate
an injection was resisted. Unchanged input hashes and golden payloads establish
what was preserved; they do not establish the cause of the different model output.
The specific variance accepted at 7B does not waive this new failure. Do not fish
for a favorable retry, weaken the grader, change a prompt or deploy around the gate.

**Recommendation:** keep the healthy live build, review I1, then use a separately
frozen baseline/candidate Search comparison to diagnose this failure before
release. Any resulting prompt/behavior change needs its own eval-backed scope.
After release and physical phone review, W1 ordered meeting-pack drafts is next.
Reference editing and broader image/chat model combinations remain separate work.

## Test output and performance

`make check`: **508 Python, 39 frontend**, API/additive/prompt/privacy/motion checks,
74 contrast pairs. Images coverage **88.9%**, capacity **94.8%**, all required targets
above 80%. Compared with I1-0: 480 Python, 39 frontend.

`make e2e`: **473 passed, 3 existing skips** in one invocation across Chromium and
WebKit. Compared with I1-0: 463 passed, same three skips. Added focused tests are
not substituted for that complete run. Gallery save/details reviews also report
zero serious/critical Axe findings. Existing ordinary keyboard/focus/label checks
remain; VoiceOver is outside this checkpoint and its historical failure is retained.

Initial JS **243,213 bytes gzip**, +2,370 bytes over the unchanged installed build,
within 256,000 absolute / 8,192 growth budgets. Images is lazy. Streaming render p95
is 2.6/3.0 ms for Chromium/WebKit; only the streaming row renders. 300-message
scroll p95 is 16.8/17 ms. First-token overhead is 106.3/60.5 ms, below 150 ms.
Current metrics and 40 new Settings screenshots are retained under this checkpoint.
All **5,576** earlier tracked artifact bytes were restored; 410 regenerated outputs
are separately archived locally and 23 JSON metrics retained in the new folder.

Read-only closeout verifies 505 installed files and three server environment files,
the transcription selector, Ollama 0.35.0, all 18 model files and image package
versions, 7,296 original comparison inputs, 204/214 grounding manifest entries,
the I0/I1-0 source and all 17 earlier outputs. Legitimately changed production files
in historical experiment manifests are preserved in the accepted Git object;
experiment-specific files/cases/reports remain unchanged. Native attempt manifests
and source snapshots verify separately. Local and normally verified HTTPS health pass.

## Test-diff ledger

| Existing file | Change | Why / preserved assertions |
| --- | --- | --- |
| `test_foundation.py` | Expected current version 8 → 9 | Additive migration; idempotency/private modes/WAL/FKs remain |
| `test_documents.py` | Expected current version 8 → 9 | Existing projected row preservation and nullable metadata assertions remain |
| `test_folders_backups.py` | Expected current version 8 → 9 | Full existing-column row comparison and folder assertions remain |
| `test_deployment.py` | Add image selector/private-source test | Existing label/bind/backup/engine tests unchanged |
| `tests/serve_app.py` | Install test-only fake image engine | Temporary synthetic data; no real image/runtime call |
| `scripts/check_coverage.py` | Add images/capacity, trace worker threads | Same ≥80% threshold; image backup executes in `asyncio.to_thread` |

`test_images.py`, `fake_image.py` and `images.spec.ts` are new. No existing test was
removed, skipped or given weaker timeouts/thresholds. The first browser fixture
selector was changed before the full green run; original failure log remains.

## Screenshots

All use synthetic inputs. Under `artifacts/images-i1/browser/`: 11 states × two
widths × two themes × two engines, plus save/details/remove dialogs and separate
production gallery review captures. Corrected phone-sized gallery/save/details:
`gallery-390-dark-webkit-fake.png`, `gallery-save-390-dark-webkit-fake.png`,
`gallery-details-390-dark-webkit-fake.png`. These are simulated WebKit captures,
not physical iPhone or native share-sheet acceptance.

## Deployment preparation and rollback

No apply command was run. Prepared opt-in, after release gates/review:

```sh
. scripts/tool-env.sh
uv run --directory server python ../scripts/install_image_worker.py --apply
uv run --directory server python ../scripts/deploy.py --image-home "$HOME/.local/share/workbench/image-worker/product"
# Add --apply to deploy.py only after the release gate/review is resolved.
```

The installer copies public worker source only and references existing weights/
interpreter. Deployment verifies the private worker matches reviewed source and
preserves an existing image selector unless explicitly supplied. Service identity,
port/bind, Tailscale, transcription interpreter and existing model defaults stay.
The synthetic rollback command is recorded in `rehearse_images_rollback.py`;
`rollback-second.json` confirms previous `ba75e28` starts with restored version 8.
Image restore is `scripts/restore_image_backup.py --backup <paired.db>
--destination <new-directory>` using the server environment; never overwrite live
or legacy data. Image backups do not include the shared weights/environment.

## Open questions for Jake

I1 is ready for source/UI review, with G9 explicitly unresolved. No new engine,
reference-edit feature, workflow model calls or agent automation is proposed for
activation before this checkpoint closes. Physical phone review follows an
approved, gated release. The recommended next investigation is the matched,
frozen Search comparison above, retaining this failed run and all thresholds.
