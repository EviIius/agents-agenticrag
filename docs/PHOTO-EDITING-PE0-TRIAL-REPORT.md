# PE0 native photo-reference trial — 19 October 2026

**Review continuation:** After this report, Jake said “Continue.” Advance to
PE1 preparation with the documented generative-edit limitations; no individual
sample checks are attributed to Jake. See `PHOTO-EDITING-PE1-PLAN.md` and its
preparation report. The original technical results and measurement gaps below
remain unchanged; references to pending review describe the trial closeout.

## Summary

The frozen six-invocation sequence completed: one synthetic portrait, three
reference edits, cancellation and the scheduled recovery edit. All six pass
their applicable protocol, residency, resource and control checks. Edits visibly
follow the request, but portrait lighting, texture and framing also change.
**Technical feasibility passes; human quality acceptance and PE1 remain open.**

Review the actual unmodified images side by side:
[`review.html`](../artifacts/photo-editing/native-20261019/review.html).
The budget is exhausted; no retry or additional inference follows this report.
Main remains `c0d65ee02747f2834944fd6f60539b67b7d2f442`; the live app is healthy.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Six authorized invocations, fixed order/settings | Pass | `worker-launches.jsonl`, six ordered private reservations, `summary.json` |
| Frozen sources/private copies/selectors | Pass | All eleven executed files, four private source copies and both selectors match `execution-manifest.json` / `preservation-final.json` |
| Pixel references and original integrity | Pass | Request/metadata original and working SHA-256 bindings; every recorded case file rehashed at closeout |
| Non-square/oriented input | Pass for decode/orientation; framing limitation | JPEG 1024×768, EXIF 6 → upright 768×1024 working PNG; output 1024×1024 reconstructs framing |
| Real progress and completed output protocol | Pass | Five completed streams: denoising 0,1,2,3,4 → decoding → finished; durable PNG/metadata hashes |
| Daily chat coexistence | Pass for this sequence | Exactly the qualified digest remained resident at 32768 context in all observed samples; no refresh/load/unload call |
| Generation/decode, peak and cache limits | Pass for five completed jobs | 9.42–20.41 s; ≤17.378 GiB reported MLX peak; 1 GiB unused-allocation cache policy |
| Swap/app health | Pass | Zero measured host-swap growth in all six cases; recurring/final health guard enforces ≤2 s |
| Cancellation/reaping/recovery | Pass | Cancel after real denoising step 1, exit -15, no completed/partial output; all six worker PIDs absent before lease release; scheduled next edit finishes |
| Actual edit quality | Partial, human acceptance pending | Requested changes visible; foreground lighting/detail drift and square reconstruction recorded in per-case Codex visual reviews |
| Logical storage/input/output bytes | Measured | 20,304,489 bytes across six private case directories; breakdown below |
| Temporary disk high-water | Not directly measured | Instrumentation records final retained file sizes; no claim of sampled peak disk allocation |
| Product/main/live preservation | Pass | 551 production source hashes, 114 installed server files, 425 installed static files, four stopped experiment ledgers and local/verified HTTPS health |

All evidence paths in this report are under
`artifacts/photo-editing/native-20261019/` unless stated otherwise.
The earlier prerequisite-wait report, empty-residency observations and zero-call
manifests remain in Git at `0e4a73a7`; initial files are retained, not regraded as
native failures. Jake then confirmed **“Loaded at 32K”**, and actual runtime
metadata passed before each invocation.

## Changed files

- **Isolated execution/evidence:** six retained sessions, exact requests,
  events, actual launch journal, hashes, output PNGs and metadata; hash-bound
  Codex visual reviews before advancing; read-only closeout/galleries.
- **Docs:** this H4 report, native status/manifest and AGENTS.md closeout.
- **Server/web/dependencies:** no changes. The production worker, schema,
  prompts, default model, runtime, service identity, port and route are intact.
  The isolated worker/controller/contracts and eleven frozen execution files
  were not changed during or after the trial.

## Deviations from SPEC.md

The named PE0 user amendment authorizes this isolated six-image-worker-call
trial. No text-model, embedding, agent or Research call was added.

The measurement harness did **not** sample temporary disk usage during the
worker calls. Post-attempt logical sizes are actual measurements, reverified
at closeout; they are not filesystem allocation or a measured disk high-water.
Complete that instrumentation before claiming the plan's peak-storage measure.
Do not spend a seventh invocation to repair this omission.

Non-target portrait changes are quality limitations, not hidden full passes.
Codex continued the frozen feasibility sequence because the target edit was
visible and there was no clear identity/geometry breakdown; exact preservation
was never promised by PE0. Jake may reject the quality at this review boundary.

## Runtime observations

### Frozen engine and residency

Installed MFLUX **0.22.0**, FLUX.2 klein 4B revision
`e7b7dc27f91deacad38e78976d1f2b499d76a294`, 8-bit components,
1024×1024 output, four denoising steps, guidance 1.0, seed 42 and the existing
1 GiB unused-allocation cache limit. No sampling, seed or prompt was adjusted.
Actual `Flux2KleinEdit` requests supplied hash-verified reference pixels.

The qualified daily chat digest
`09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`
remained resident at 32768 context, reporting 19,508,609,678 resident bytes.
Ollama remains **0.35.0**. Coexistence was measured while chat was idle; this
does not qualify simultaneous active chat/image generation or other models.
Pre-existing host swap was about 3.8 GiB; **growth was zero**, not absolute swap.

### Actual cases

| Invocation | Case | Init s | Generation/decode s | Total case s | PNG bytes | Quality/control observation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Portrait | 2.71 | 9.42 | 12.42 | 1,489,546 | Coherent fictional adult, brown bob, blue shirt, grey background |
| 2 | Garden background | 2.14 | 20.41 | 22.76 | 1,669,143 | Target succeeds; warmer face/hair highlights and regenerated fabric |
| 3 | Red clothing | 1.84 | 16.87 | 18.88 | 1,304,518 | Red shirt/upright decoding succeed; framing, skin, contrast and texture change |
| 4 | Green mug | 1.83 | 20.38 | 22.39 | 1,378,113 | Target succeeds; notebook/view/light closely align, fine texture/highlights differ |
| 5 | Cancel | — | Cancel at step 1 | 7.17 | 0 | Worker reaped with lease held; no image or metadata, no MLX peak claimed |
| 6 | Recovery garden | 1.63 | 19.62 | 21.44 | 1,669,139 | Successful recovery; same decoded pixels as case 2, recurring quality limits |

The four completed edits took **16.87–20.41 seconds** for generation/decode
(18.88–22.76 seconds total case time). Reported completed-worker MLX peak is
18,657,035,702–18,659,198,390 bytes (**17.376–17.378 GiB**), below 24 GiB.
The 0.5-second process-RSS samples are retained but are neither true process
peak nor GPU/MLX peak. Cancellation emitted no completed native metadata, so
its native MLX peak was not captured.

Recovery and the first background output have different PNG file hashes but
**identical decoded RGB pixels** in a separate CPU-only comparison. Both native
files and metadata remain intact. This is one repeat, not a determinism study.
Native PNGs contain engine metadata; working inputs are normalized and stripped
of original EXIF. PE1 must sanitize exports rather than treating native engine
metadata as an approved export contract.

### Measured storage

| Case | Original + working input bytes | Whole output PNG bytes | All retained case files bytes |
| --- | ---: | ---: | ---: |
| Portrait | 0 | 1,489,546 | 1,490,754 |
| Background | 2,975,335 | 1,669,143 | 4,646,888 |
| Clothing | 1,005,895 | 1,304,518 | 2,313,001 |
| Mug | 2,849,981 | 1,378,113 | 4,230,497 |
| Cancel | 2,975,335 | 0 | 2,976,465 |
| Recovery | 2,975,335 | 1,669,139 | 4,646,884 |
| **Total** | **12,781,881** | **7,510,459** | **20,304,489** |

Sizes are logical bytes, excluding weights, filesystem allocation/compression,
screenshots and public diagnostic copies. All six private case directories use
**20.30 MB (19.36 MiB)**. Five finished PNGs use **7.51 MB**; each is
**1.30–1.67 MB**. Four actual edited revisions total 6.02 MB.
Every revision is a full PNG, not a Photoshop-style delta. At the observed size,
100 retained outputs would be roughly 130–167 MB, excluding originals/working
copies. Actual future photos can differ.

The trial deliberately retains separate per-case input copies, including the
cancelled attempt. Deduplicating all identical original/working/output payloads
by SHA-256 would represent **12,852,124 unique bytes** for these samples;
this is a host-only calculation, not implemented production retention.
PE1 should pin owned references and reuse them across revisions with explicit
ownership/reference counts, and count them in cleanup and backup/restore.

## Test output

- **Native:** six of six applicable protocol/resource/control checks pass;
  exactly six actual worker launches, no retry, no extra text-model calls.
- **Visual:** Codex inspected all five completed images and original comparisons;
  all requested edits visible, with documented non-target drift. Jake's quality
  acceptance is pending. No real person or private user file was tested.
- **Closeout:** `summarize.py` rechecks every recorded private case-file hash,
  exact ordered budget, completed step streams, cancellation emptiness, reaping,
  residency, swap and eleven executed source hashes; records storage and live
  preservation. Local and normally verified Tailscale HTTPS health pass.
- **Gallery only:** eight actual images load with no horizontal overflow at
  1240×1100 and 430×1100 in Chromium. Screenshots inspected by Codex; this is
  not a physical iPhone or app acceptance claim.
- **Offline reuse:** 84 preparation checks passed (47 new, 37 existing image/
  residency), as recorded in the frozen preparation report. Prior full suites
  (726 Python / 126 frontend / 721 browser, three existing skips) are reused
  solely through exact unchanged-source parity. No new full suite/build run.
- **Privacy/diff:** final privacy audit and `git diff --check` pass; all retained
  media is synthetic. Failed first system-Python metadata preflight (missing
  httpx, before any invocation) remains recorded; no package was added.

## Screenshots

- `review-desktop-synthetic.png` — actual gallery at 1240×1100.
- `review-phone-synthetic.png` — actual gallery at 430×1100.
- `cases/{portrait,background,clothing,mug,recovery}/image.png` — unmodified
  native PNGs; these are trial outputs, not screenshots of private application data.
- `cases/clothing/reference.png` — actual upright non-square working reference.
- `review.html` — all four original/edit pairs, exact prompts and measured limits.

## Open questions for Jake

PE0 requires your quality review before PE1. Inspect the garden, red-shirt and
green-mug comparisons, especially the portrait lighting/fine-detail changes and
square reconstruction. Are these acceptable for an explicitly labelled
**generative photo edit** with original comparison? No exact-preservation,
mask/brush editing or guaranteed-likeness claim is supported.

If accepted, review PE1's concrete composer/job/reference-storage/backup scope
before implementing it. The temporary disk high-water measurement remains open.
PR #6 stays draft on `codex/photo-reference-prep`; this checkpoint performs no
main merge or deployment. Failed agent trials and Research remain closed.
