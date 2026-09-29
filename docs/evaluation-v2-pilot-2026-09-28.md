# Local evaluation v2 pilot — 28 September 2026

The frozen `examples/evaluation-v2.jsonl` set has 24 questions against the four
sample documents in `.data/evaluation-corpus.db`. It covers simple and numeric
lookup, two-source answers, missing facts, access labels, and an imported
prompt-injection line. These are local diagnostic questions, not a general model
benchmark or a web-research evaluation.

| Model and workflow | Runs | Failed | Keyword answers | Abstention flag | Inline citation coverage | Mean time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3 30B A3B 32K, Fixed | 72 (3 repeats) | 0 | 57/57 | 15/15 | 100% | 1.28 s |
| Gemma4 12B MLX, Fixed | 24 (1 repeat) | 0 | 19/19 | 4/5 | 96% | 3.81 s |

The Direct baseline uses no sources and is deliberately tested on the same
source-specific questions; its keyword score is not a measure of general chat
quality. The reports and full answers are saved under `.data/evaluation-v2-*`
and are not published to the workbench's automatic router.

The first Qwen pass exposed two concrete defects. It guessed **600 calories**
although the Alfredo note has no calorie information. Fixed now rejects a
numeric claim absent from the cited passages, makes one correction attempt,
and returns an explicit abstention if the answer cannot be repaired. Several
two-source answers listed both citation IDs but showed only `[1]` inline. Fixed
now checks every listed citation for a marker, corrects distinct source-named
sentences conservatively, and collapses unused same-document citations.

The resulting 100% keyword and marker scores do **not** mean all claims are
supported. Manual inspection found “parchment prevents sticking” in a Qwen
answer even though the nachos note only says parchment makes cleanup easier.
Gemma's answer to the missing-year case correctly says the source does not give
a year, but it marked `abstained: false`; one abstaining answer retained an
unused citation. These are real gaps in claim review and output consistency.

Next evaluation work: annotate claim-level support by a person, add frozen web
search snapshots and timed cancellation cases, then repeat candidate models and
Agentic/Supervisor only where their extra work might help. Keep the current
Fixed-only automatic routing pilot provisional until that comparison exists.
