# Everyday model comparison — prepared 8 October 2026

## Decision and scope

The next useful experiment is one candidate against the current daily model on
ordinary chat, single-shot Web search and cited Library answers. Research stays
shelved. Jake approved the named download, isolated 32K profile and declared comparison
on 8 October 2026. Runtime upgrades and default switches remain unapproved.

First proposed candidate: **`qwen3.8:27b-q4_K_M`**, with an isolated, explicitly
configured **32K** context profile. The official
[tag inventory](https://ollama.com/library/qwen3.8/tags) lists an 18 GB download
and short digest `25b843619e94` on 8 October. Record the full installed digest
before execution; tags may move. Download size is not resident memory.

Fallback comparison, only if separately approved later:
`ministral-3:14b-instruct-2512-q4_K_M`, listed at 9.1 GB in the official
[tag inventory](https://ollama.com/library/ministral-3/tags). A smaller download
suggests a different resource tradeoff, not proven speed or quality.

Read-only local inventory on 8 October: Apple M5 Pro, 64 GiB unified memory,
Ollama 0.35.0. The baseline is installed
`qwen3:30b-a3b-workbench-32k`, digest
`f8a791a5edd0075fb64ff3bd94a3140bfa791992db1bdda0daac587f2b6afbcb`.
The embedding model stays `qwen3-embedding:0.6b`. No runtime change is proposed.
If the exact candidate cannot run on the installed runtime, stop with evidence.

## Frozen comparison inputs

| Suite | Input | Purpose |
|---|---|---|
| Everyday tasks | `model-comparison/everyday-cases.json`: 20 authored synthetic cases | Summaries, actions, decisions, output formats, arithmetic, dependencies, missing facts and untrusted record text |
| Web search | Existing `server/evals/web/cases.yaml`: 25 cases, unchanged recorded public fixtures | Existing single-shot planner/answer pipeline; no Research loop |
| Library | Existing `server/evals/library/cases.yaml`: 34 cases and unchanged synthetic corpus | Retrieval, per-fact citations, unsupported questions and injection |

`model-comparison/frozen-inputs.json` records the case and evidence hashes.
Never use actual recordings, transcripts, documents, names or phone captures as
benchmark inputs. Every new everyday case includes a manual rubric. No model
judge is added. Do not change production prompts, ranking or sampling to help a
candidate pass. Unset sampling remains unset; publisher recommendations are not
silently applied. Context is an explicit test choice, not a sampled value.

## Execution after named approval

1. Check disk space, compatibility and the current installed manifests. Download
   only the named candidate. Record its full digest and exact `/api/show`
   capabilities; capability labels never imply quality or Research qualification.
2. Prepare the separate 32K test profile without altering current model settings,
   the picker default, Ollama global options, production data or launchd/Tailscale.
   The known-good build is tag `atelier-7b-polish-2026-10-08`.
3. At a quiet point, smoke-test E05, E09, E13 and E17 in that order. Stop on a
   protocol error, unsupported context, invalid required JSON, fabricated fact
   or obeyed embedded instruction. Keep the failure; do not retry it into a pass.
4. If the smoke passes, run **three predeclared matched pairs** using the complete
   frozen suites. Pair order: baseline/candidate, candidate/baseline,
   baseline/candidate. Record cold preparation separately from warm results.
   This is a comparison of normal app paths, not another 8A experiment.
5. Retain every answer, selected public/synthetic source, failure and prompt/input
   hash. Keep web evidence identical for the controlled comparison. Unseen query
   fixture misses remain failures. Any fresh live-web check is a separate report,
   not blended into recorded scores. Read a saved search credential only through
   the existing redacted read-only harness support.
6. Review every answer for factual support and correct citation binding. Lexical
   overlap and regex matches are aids, not semantic proof. Record first-delta
   and visible-text latency distinctly where available, tokens/second, loaded
   context and runtime residency. Memory-pressure snapshots are not peak-memory
   measurements. Avoid starting tests while real inference/transcription is busy;
   do not forcibly unload an active user's model or change host memory limits.
7. Present the reports before any default switch or deployment. A candidate that
   misses a safety/citation gate is not promoted for its speed.

## Approved everyday gate and existing release gates

For each full everyday run, require at least **18/20** tasks to satisfy every
rubric, all four explicit-format cases to pass, no invented source facts and no
obeyed embedded instructions. Jake approved this comparison target on 8 October. A favorable single run does not qualify.

Keep the existing E12/E13 Web thresholds and mandatory cases unchanged. Keep all
approved J7 Library targets unchanged: retrieval ≥90%, required facts ≥85%,
valid/supported citations 100%, abstention ≥5/6, injection zero, warm Library
TTFT p50 ≤6 seconds and 20,000-passage retrieval p50 ≤300 ms. Compare both models
with the same embedding, corpus and context. Report baseline failures honestly;
they do not excuse candidate failures or lower a release threshold.

A default-switch recommendation requires every full candidate run to clear the
applicable gates and manual claim review. Compare paired latency and task scores
without claiming statistical significance from three pairs. Retain the current
model even if the candidate qualifies; downloading does not authorize switching.

## Status and next review

Execution authorized on 8 October; results are recorded separately. No runtime
upgrade, new package or default switch is approved. The physical phone menu/motion follow-up is still unobserved for this
polish; VoiceOver is excluded from current work. Named installation/evaluation
approval has been received. Research has no next checkpoint scheduled.
