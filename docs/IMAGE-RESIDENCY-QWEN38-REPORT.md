# Current Qwen3.8 image admission repair — H4 report

## Summary

Jake's physical iPhone check found that Brief to images and chat images both
reject the loaded Qwen3.8 profile. The shared guard still recognized only the
older profile measured in I1-0. Its new digest was rejected despite using less
resident memory. The approved one-image check passes with Qwen3.8 kept loaded.
The two-file fix is now installed on the unchanged production service/route.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Diagnose shared failure | Pass | `Engine.admit()` rejected current runtime digest; worker was installed/available; both paths share the engine |
| Narrow current-profile support | Pass | Shared exact-digest admission list, used by both image engine and fixed-workflow model selector |
| Preserve old safety limits | Pass | Single resident model, exact 32K context, <=21,827,095,100 resident bytes, <=512 MiB swap growth; same worker/cache/process/capacity guards |
| Offline regression | Pass | 61 targeted image/workflow tests; no old assertion modified; full `make check`: 664 Python / 104 frontend |
| One approved native image | Pass | `native-result.json`: one image, zero text calls, 15.09 s total / 10.55 s generation; validated PNG/metadata |
| Current Qwen3.8 remains resident | Pass | Before/during/after samples: exact expected digest, 32,768 context and 19,508,609,678 resident bytes; no load/unload/keep-alive request |
| Resource and health bounds | Pass | Zero positive swap growth; MLX peak 18,657,037,750 bytes; worst sampled app health 49.4 ms |
| Reaping and capacity release | Pass | Native worker exits, engine awaits/reaps it, lease ends with busy=false and fd=None |
| Conditional live publication | Pass | Current app/plist/database fallback; only engine and qualification files changed; restart to healthy 0.728 s; schema remains 13 |
| Actual installed admission and selector | Pass, zero further inference | Read-only `Engine.admit()` on installed source succeeds; current profile present in `/api/workflows/image-models`, local and verified HTTPS health 200 |
| Phone retry after fix | Pending | Asked Jake to retry failed workflow image step or chat image; no post-fix physical result invented |

Evidence: `artifacts/image-trial/qwen38-residency/`.

## Changed files

- `server/app/images/engine.py`: adds the exact measured current-profile digest
  alongside the existing digest; original context/size/count guards unchanged.
- `server/app/workflows/qualification.py`: consumes that same digest list rather
  than a separate one-profile check. Runtime metadata identifies models; names
  do not establish qualification or capabilities.
- `server/tests/test_image_residency_profiles.py`: admission, aliases, unknown/
  malformed digest, bad context/size, multiple loaded models and selector parity.
- `scripts/probe_image_residency.py`: the separately approved one-image resource
  check, with a private output directory, exact residency, host health/swap checks,
  shared cross-process lease, 120 s total bound and no retry/management calls.
- Plan, this report, `AGENTS.md`, frozen/executed source snapshots and new evidence.
  Original coverage report is restored; fresh coverage retained separately.

## Deviations from SPEC.md

Jake explicitly approved the one-image validation and conditional release.
This adds one measured resident configuration, not every installed model.
No new dependency, model, runtime, chat prompt/default/sampling rule, schema,
frontend or ordinary text request changes. The shared code fixes both entry points.
Neither factual grounding nor Research is qualified by this image check.

## Runtime observations

The installed FLUX.2 klein 4B worker, revision, MFLUX environment, 8-bit precision,
four steps, 1024-square settings, 1 GiB cache policy and seed 42 are unchanged.
The prompt is the original synthetic I1-0 red-mug/blue-notebook photograph case.
All native progress is emitted by the actual worker. The PNG is valid, 1,426,638
bytes (about 1.36 MiB), and Codex visually sees the requested mug/notebook scene.
No test output is inserted into the user's Gallery/chat or workflow history.

Qwen3.8's reported 19.51 GB residency stays below the unchanged 21.83 GB ceiling.
The test performs no chat decode, artificial warmup, explicit model load/unload,
expiry refresh, prompt transformation or retry. It is one resource sample; it
does not establish simultaneous decoding or arbitrary contexts/model combinations.

## Test output and preservation

- Targeted final invocation: **61 passed in 6.86 s**, including all existing image
  and fixed-workflow tests. No existing assertion or limit was weakened.
- Full `make check`: **664 passed in 304.06 s**, then **104 frontend tests**;
  lint, format, types, coverage, 110 contrast pairs, API types/additivity, motion
  and privacy checks pass. Web assets and frontend sources are unchanged; the
  previous complete 615-pass browser run remains applicable, not rerun here.
- One bounded native run: pass; all outputs/progress/samples retained privately,
  with public synthetic summaries and exact executed source. No extra inference
  follows the successful run or live publication.
- The new probe's remaining 102-character SQL literal triggered a style check;
  its exact executed source remains frozen. Splitting the adjacent string literal
  after the run fixes formatting without changing the parsed AST or query. AST
  equality and final lint/format pass; no native retry or evidence replacement.
- Native PNG/metadata remain private under
  `~/.local/share/workbench/qa/image-residency-qwen38-20261014/output`.
  No real user prompt, recording/document name, text or screenshot is captured.
- Current whole app/plist and consistent schema-13 database fallback are under
  `~/.local/share/workbench/qa/image-residency-qwen38-20261014/release`.
  The previous complete Studio app/data fallback remains intact. Publication
  rollback restores the two prior source files and exact plist; current data is
  preserved because this fix introduces no schema/data mutation.

## Screenshots

No live screenshot. Codex inspected the explicitly synthetic native test PNG.
The UI is unchanged; prior synthetic Studio/chat-image evidence remains intact.

## Open questions for Jake

Retry the failed image step or use Try again in chat. The current 32K Qwen3.8
configuration no longer requires Eject for this guard. Other unmeasured profiles,
different contexts and multiple loaded models remain subject to the existing
restriction. Report any error after retry; previous failed attempts stay visible.
