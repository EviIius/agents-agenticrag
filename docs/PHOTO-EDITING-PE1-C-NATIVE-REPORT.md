# PE1-C native qualification report

20 October 2026 (local time). Source candidate `04394ca7`, isolated
`codex/photo-reference-prep`, draft PR #6.

## Summary

The approved matrix passed with exactly four native edit invocations and one
empty-message preload. HEIC editing works with no chat model loaded and with the
qualified daily Qwen at 32K; the oriented JPEG, cancellation and next-job recovery
also pass. Originals and reference bindings remain intact; exports are sanitized.
The requested green shirt appears in all three completed images, with visible
changes to other details. Quality acceptance and release preparation remain open;
no product guard, main, installed app or default was changed.

## Done-when checklist

| Item | Status | Evidence under `artifacts/photo-editing/pe1-c-native-20261020/` |
| --- | --- | --- |
| Exact bounded allowance and first-run journal | Pass: 4 images + 1 preload, no retry | `approval.json`, `launches.jsonl`, frozen `executed-source.json` |
| Empty-slot HEIC edit | Pass | `cases/empty-heic/`: retained raw HEIC, 2560→2048 reference, native/export PNGs |
| Qualified daily chat residency at 32K | Pass | `summary.json`: exact digest/context/size retained through remaining cases |
| JPEG EXIF orientation and metadata removal | Pass | `cases/resident-jpeg/`: orientation 6, 960×1280→1280×960 reference |
| Actual reference pixels, progress and output protocol | Pass | `results.json`: three 0–4 progress sequences, one 0–1 cancellation sequence |
| Cancel/reap under shared lease; no accepted output | Pass | `cases/cancel/`; four recorded reaps with process absent/lease held |
| Next-job recovery | Pass | `cases/recovery-heic/` complete, reference preserved |
| Raw originals, descriptors and sanitized export pixels | Pass | Controller byte/hash/critical-PNG-chunk assertions and retained receipts |
| Resource/health bounds | Pass for bounded matrix | 17.38 GiB completed-output MLX peak; unchanged observed swap; 102 health samples |
| Actual retained and observed storage | Measured | `results.json`, `storage.json`, per-upload/job reports |
| Output quality | Codex reviewed; Jake acceptance pending | `review.html`: green shirt succeeds; lighting/framing/facial rendering drift |
| Product empty-slot guard promotion | Not applied | Trial subclass only; application source remains B's 572-file tree |
| Installer/compatibility fallback release rehearsal | Pending | See prepared C plan; full old-server rollback remains prohibited |
| Main merge/publication/physical iPhone | Not performed | Draft PR remains isolated; existing phone acceptance is not attributed to PE1 |

## Changed files

No application server, web, image worker, prompt or provider source changed.
`AGENTS.md` records the explicit native allowance and closeout. This report and
synthetic native evidence/review page record the results. The supplementary
`LOCAL-AUTOMATION-NEXT-STEPS.md` answers Jake's roadmap question; it authorizes no
scheduler, watcher, agent or extra model call.

## Deviations from SPEC.md

The prepared subclass permits an empty slot alongside the existing strict 32K
measured combination, only for this qualification. Both arrangements passed;
this qualifies proposing the same narrow product change, not every resident
model/context combination. The live admission guard remains unchanged.

No dependency, weight, runtime, sampling, default, automatic unloading, extra
answer/helper call or Research/agent experiment was added. The one empty-message
preload is the exact separately approved body. Keep the 60-second generation/
decode, 24 GiB MLX, 1 GiB cache, 512 MiB swap-growth and ≤2-second health bounds.

## Runtime observations

| Case | Initializing | Generation/decode | Final state | MLX peak |
| --- | ---: | ---: | --- | ---: |
| Empty-slot HEIC | 2.53 s | 20.44 s | complete | 17.38 GiB |
| Resident Qwen JPEG | 3.79 s | 24.66 s | complete | 17.38 GiB |
| Cancel at real step 1 | No final metadata | Intentionally interrupted | cancelled | No final peak measurement |
| Resident Qwen HEIC recovery | 2.38 s | 24.68 s | complete | 17.38 GiB |

Initialization plus generation/decode is approximately 23–29 seconds for completed
cases; this excludes some HTTP/staging/persistence overhead. The cancelled
worker's resource checks ran through step 1, but there is no completed metadata
from which to report its final MLX peak. Do not impute the other cases' peak to it.

Ollama reported the exact approved digest, context 32,768 and resident size
19,508,609,678 bytes through the three resident cases. No keep-alive refresh or
unload was sent. Observed host swap stayed at **3,709 MiB**; that is no observed
growth, not zero pre-existing swap. Maximum of 102 measured health requests was
0.01675 seconds. All four owned workers were reaped and absent while the shared
lease was still held; capacity is released afterward. No output is accepted from
the cancelled job, and its inputs remain available for explicit retry.

### Storage (decimal MB unless stated)

| Retained item | Measured size |
| --- | ---: |
| One native edited PNG | 1.35–1.41 MB |
| Its separate sanitized export | 1.35–1.41 MB |
| Output + export per completed edit/revision | 2.70–2.82 MB, plus metadata |
| One HEIC original + normalized reference | 0.35 + 2.85 = 3.20 MB |
| One JPEG original + normalized reference | 0.22 + 1.11 = 1.33 MB |
| Three completed output/export pairs combined | 8.26 MB |
| Four cases' retained originals/working inputs combined | 9.06 MB |
| Final complete QA data tree, unique-inode logical bytes | 18.54 MB |
| Peak observed whole-tree logical / unique-inode / allocated | 28.94 / 19.87 / 20.29 MB |

The matrix intentionally uses separate chats, so even identical HEIC inputs have
separate owners. Within a chat the product's existing dedup/pins share a retained
reference across revisions; the native job bindings are hard links. Logical
pathname totals therefore count some input bytes twice. The final whole-tree
pathname total is 27.61 MB, compared with 18.54 MB after deduplicating inodes.
Cancelled edits retain inputs and metadata but no output PNG/export.

There are 384 whole-tree samples, maximum observed gap 0.266 seconds, plus upload
and per-job barrier/timer observations. These are observed high-water values,
not an absolute physical APFS peak. Kernel `st_blocks` accounting does not dedup
shared clone extents. No storage result is inferred from just final PNG sizes.

### Visual review by Codex

All three completed outputs show the requested green shirt. The sideways JPEG
reference remains sideways in its output; normalization follows its EXIF flag.
HEIC input hashes and original bytes are unchanged. The edits also re-render
facial features/skin texture, alter lighting and adjust framing. The result is
usable as a generative variation, without exact-face/pixel-preservation claims.
This observation is by Codex; Jake has not accepted this sample set. His real
photo is not used, shown or copied into this report/evidence.

## Test output

New native matrix: **4/4** expected outcomes; exactly four worker reservations,
one preload, zero plain-generation dispatches or other model calls. The frozen
577-file executed source, fixtures/selectors and per-case output/reference
assertions verify. No retries or extra native tests follow this exhausted budget.

No broad suite rerun is needed for unchanged product source. Retain preparation's
15 safety tests, four fake-controller cases, ten compiled functional browser cases
and two each compiled/fallback browser observers. B's full `make check` passes
(745 Python, 132 frontend, 110 contrast pairs). Preserve B's full browser result
as 737 passed / two older selector failures / three skips, followed by the corrected
complete image-upload file at 12/12; do not relabel the original invocation green.

Preservation audit passes: 572 B product/test source files, 429 candidate static,
922 B evidence/source files, 52 frozen C preparation files, 577 executed C files,
551 main, 114 installed server, 425 installed static, eleven PE0 source and 73 PE0
evidence files. PE0 remains six calls; the separate private hat test remains one.
Stopped Hermes/PydanticAI/N1/C1 ledgers are unchanged. Local and normally verified
Tailscale HTTPS health pass; Ollama remains 0.35.0. No production file, service,
port, plist or route was changed.

## Screenshots

`review.html` presents the three retained synthetic reference/export pairs.
Images under `cases/empty-heic/`, `cases/resident-jpeg/` and
`cases/recovery-heic/` are actual local worker outputs, not browser illustrations
or cloud-generated substitutes. Cancel has its retained input and no output.
No private user imagery or real recording/document content appears in evidence.

## Open questions for Jake / next boundary

Review the sample pairs' generative-edit quality before integration approval.
Next work would promote the qualified empty-or-exact-32K guard with regression
checks, extend the worker installer for the edit/CPU contracts and prepare the
concrete schema-aware deployment/fallback rehearsal. Full old-server rollback on
schema 14 is unsafe; retain the previous-UI/current-backend fallback boundary.
Only after those gates should merge/publication be proposed; the physical phone
check comes after an approved release. Automated workflows remain a separate
next scope; this trial grants no scheduler/watcher/model-agent implementation.
