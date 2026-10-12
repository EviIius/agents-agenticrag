# Proposed bounded answer comparison

12 October 2026. Prepared after the measurable offline table-admission result.
The table plan and AGENTS.md stop before native inference; this probe requires
explicit approval. No model call or deployment is authorized by this document.

## Concrete candidate

`artifacts/images-i1/search-table-admission/admission.py` replaces at most one
introductory passage with a relevant original table in an already eligible source.
33 tests pass. All 28 original-case turns are replayed; 22 actual source-bearing
turns reproduce baseline evidence exactly. The candidate changes only the known
comprehensive-list case, retaining seven columns / 28 rows / 23 explicitly positive
counts under the same context/source/passage limits. It changes no native schema,
prompt, model/default, sampling, dependency or production code.

## One question, at most three matched pairs

Use the original comprehensive-list question and recorded public evidence without
rewriting cases or corpus. Compare the current Search implementation with the
isolated table-admission hook; avoid combining earlier unqualified planner/answer
contracts. Same already-installed original Qwen profile, 16K eval context, Ollama
0.35.0 and user sampling payload `{}`. Existing utility exception remains
temperature 0.2 / maximum 256 tokens / reasoning off. Each turn uses the usual
one planner and one answer; no judge, retry, repair, title or Research call.

Predeclare order baseline/candidate, candidate/baseline, baseline/candidate. This
is at most **six planners and six answers**, plus at most six recorded empty-message
warm loads. Freeze source/schema/prompt/corpus/order before any inference. Verify
native wire, actually admitted evidence, settings and stream events. Do not run
while human inference/transcription is active. Required browser gates and native
timing measurements run sequentially to avoid host interference.

## Success and stopping

Review all 23 original required entries, requested inclusion/exclusion, correct
column roles, inline citation/claim support and every extra factual claim. A cited
but reversed or unsupported fact fails. Measure actual first-token/total latency
and source-budget overhead. Retain baseline failures as comparison evidence;
stop on the first candidate support/completeness/placement failure or any protocol
failure. No favorable retry or candidate change follows failure.

One success is not consistency. Three complete, supported candidate answers are
the bounded task result; neither that nor source coverage qualifies general Search,
the original full benchmark, Images release or unattended workflows. Known task
classification and corpus-coverage failures remain independently open. No deployment,
service restart, model switch/download, prompt change or Research restart follows.

If this candidate cannot improve the original answer with complete available
evidence, stop this approach and report that result; do not start another generic
prompt continuation. A further correction needs its own concrete review.
