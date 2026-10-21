# PE1-C — bounded product-worker qualification

20 October 2026. **Prepared; native execution is not authorized or performed.**
The branch remains `codex/photo-reference-prep`, draft PR #6. Main and the
installed app remain at the accepted production build. PE0 remains six calls;
the separately requested private hat edit remains one. Neither allowance is reused.

## Offline results and assessment

See `PHOTO-EDITING-PE1-C-PREP-REPORT.md` and
`artifacts/photo-editing/pe1-c-prep-20261020/`.

- Real system HEIC conversion and real CPU reference normalization pass; retained
  raw originals, orientation, edge limits and metadata stripping are checked.
- Ten functional cases pass against the actual compiled candidate, with fake
  inference, across Chromium and iPhone-sized WebKit. Both cold-load observers
  load highlighted code and open active SSE without asset failures/page errors.
  An earlier hard-navigation WebKit SSE console error is retained separately;
  these checks do not establish its cause or a physical PWA update pass.
- The previous server **is unsafe on schema 14**: it starts, but retrying an edit
  drops the reference and dispatches plain generation. The current server keeps
  the reference. Original immutable rows/input/output files remain preserved in
  both synthetic rehearsals, including a queued edit interrupted on startup.
- Previous compiled UI + current schema-aware backend preserves reference-bound
  retry and output access in both browsers. That is a **compatibility fallback**,
  not permission to use the complete old server against new data.

## Concrete native proposal (requires Jake's approval)

Use the already installed MFLUX **0.22.0**, FLUX.2 klein 4B pinned revision
`e7b7dc27f91deacad38e78976d1f2b499d76a294`, existing interpreter/weights,
8-bit components, four real denoising steps, guidance 1.0, one 1024-square image
per invocation. No download, new dependency or runtime change.

Maximum **four image-worker invocations**, in this order; no replacement seeds,
retries, speculative extra case, answer/helper call or real user photo:

| Case | Actual residency | Frozen synthetic input | Seed | Required result |
| --- | --- | --- | --- | --- |
| empty-heic | No loaded model | 2560-square HEIC, normalized to 2048 square | 420101 | Complete edit; original bytes retained; sanitized output |
| resident-jpeg | Exact qualified Qwen digest at 32K | 960×1280 JPEG, EXIF orientation 6 → 1280×960 | 420102 | Complete edit; orientation correct; chat remains resident |
| cancel | Same qualified residency | Same oriented JPEG | 420103 | Cancel on real denoising step 1; child reaped while lease held; no accepted output |
| recovery-heic | Same qualified residency | Same HEIC | 420104 | Next complete edit; original/reference/export checks pass |

All four use exactly this synthetic edit instruction:

> Change the shirt to vivid green. Preserve the person, pose and background as closely as possible.

The source is the retained **synthetic** PE0 portrait, never Jake's private photo.
Fixture bytes/hashes/expected normalization are frozen in `fixture-manifest.json`.
Quality must still be reviewed; generative edits can alter faces, framing and
unrelated details. Completing the matrix does not prove exact likeness.

### One explicitly bounded residency setup request

The read-only 20 October check reports no loaded model and the installed exact
32K profile. To avoid another manual load interruption, request permission for
**at most one empty-message preload**, after the empty-slot case succeeds:

```json
{"model":"qwen3.8:27b-atelier-eval-32k","messages":[],"stream":false,"keep_alive":"15m","options":{"num_ctx":32768}}
```

This selects only the already installed approved profile for the trial; it does
not change the app default or add sampling settings. Require installed digest
`09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`,
32K context, integer resident bytes within the existing 21,827,095,100-byte bound.
Do not infer capabilities from its display name. No later keep-alive refresh,
automatic chat eviction or second preload. If residency changes unexpectedly,
stop. If the initial slot is occupied, wait for natural expiry or a human choice;
do not unload it.

### Prospective admission policy

The prepared `native_candidate.py` subclass changes only the edit admission
predicate to **empty slot OR the existing strict measured resident combination**.
It is used only by this isolated qualification controller. The application guard
is unchanged and still requires the measured 32K resident profile. Only a passed
empty-slot native case permits proposing the same narrow product change plus its
regression tests. Unknown/multiple/64K/oversized/bool-sized reports remain refused.

### Execution and stop controls

`native_trial.py` defaults to CPU normalization and fake inference. `--native`
requires a separately written approval receipt matching the frozen execution
manifest. No receipt is supplied in this checkpoint. The controller:

- preserves a private first-run folder; reserves each image/preload request to an
  fsynced journal **before** dispatch, maximum four plus one;
- verifies frozen source/fixtures/selectors and uses the actual product API,
  reference pinning, jobs, worker, output validation and metadata stripping;
- allows only the declared runtime metadata/health reads and exact preload HTTP
  body; rejects ordinary generation dispatch and other controller HTTP requests;
- shares `~/.local/share/workbench/data/native.lock` with the installed app;
  requests no active human chat, and never opens live app data for writing;
- checks actual 0–4 synchronized denoising events, reference descriptor/hash,
  worker hash, retained raw bytes and sanitized export's unchanged pixel chunks;
- retains the unchanged 60-second generation/decode bound, 24 GiB MLX peak,
  1 GiB cache, 512 MiB swap-growth margin, ≤2-second app health and 300-second
  process supervision; records health/residency/swap/reaping under the lease;
- stops the matrix on the first failure, writes HALTED and refuses continuation;
  a worker failure before the cancel checkpoint is a failure, not a reason to wait
  for or start another case;
- times out execution at 12 minutes (then finishes mandatory reaping/cleanup) and samples storage every 0.25 seconds
  plus durable-operation barriers, including job/reference measurements and final
  retained bytes. Report logical, unique-inode and kernel allocation separately:
  these are observed high-water values, not a proven absolute APFS peak.

Actual/native outputs and detailed records go to a separate private QA folder.
Only synthetic evidence may later be copied into Git. Preserve every failed
attempt and leave PE0/private-user/stopped-trial ledgers untouched. The CPU/fake
controller rehearsal is not native memory, latency or quality qualification.

## After qualification: release remains separately gated

1. Review native output quality, cancellation/recovery, reference and export
   integrity, measured resources and storage. Failure leaves C open.
2. If the empty slot qualifies, apply the exact tested admission predicate and
   update the existing strict admission regressions; run required focused checks
   and source/preservation gates. Keep all unrelated policy unchanged.
3. Before publication approval, prepare a concrete installer/fallback bundle
   containing app, image-worker selectors/source, consistent DB **and reference
   companion** snapshot, static files and original plist. The existing worker installer copies only the
   generation worker: extend its reviewed whitelist for the edit worker and CPU
   contracts before release. Rehearse on copies.
   Quiesce/reap jobs before a binary switch. Preserve current user messages/inputs.
4. **Prohibit full old-server rollback on schema 14.** The accepted fallback is
   previous UI with the schema-aware backend, verified here for output/retry.
   Pre-release schema-13 backups remain disaster-recovery evidence, not a silent
   rollback that discards newer data. A server regression needs a reviewed
   schema-aware repair or recovery procedure; there is no proven full backend
   rollback today. Do not use generic old-directory restore automation for PE1.
5. Request merge/publication approval after passed gates and concrete fallback
   review. Keep port 8787, bind 127.0.0.1, label, service and Tailscale unchanged.
6. After an approved release, request the actual iPhone upload/edit/reference/
   save/share/cancel check. Browser emulation is not physical acceptance.

No new agent, Research, workflow edit block, vision helper, mask/brush UI,
additional model, chat prompt or sampling/default change is in this checkpoint.
