# Search input contract: isolated execution declaration

11 October 2026. Jake authorized `SEARCH-INPUT-CONTRACT-PLAN.md` with “go ahead”.
Candidate source and all inputs/order are committed before real inference.

## One candidate

`artifacts/images-i1/search-input-contract/contract.py` installs only in the
temporary evaluator application, guarded by its `workbench-eval-*` data path.
Production files and the installed app remain unchanged. The candidate uses the
existing single planner and single answer; the answer prompt is the same generic
grounding refinement retained in the previous trial. No new answer refinement.
Utility temperature 0.2 / 256 tokens, answer sampling empty, native Ollama 0.35.0
and the installed runtime-reported 16K chat model remain fixed.

The host inventories explicit body/quote boundaries, unquoted literal translations,
previous responses and actual document/transcript attachment bodies. IDs bind
source, kind and original text; bounded previews total at most 2,800 serialized
characters, with 240 characters per input. The planner returns a nullable
`input_ref` (ID plus exact visible quote). Unknown/stale IDs, invented spans,
missing transform inputs and malformed combinations use the existing fallback
query. No second planner or validation model call is made.

Inventory follows the selected branch after the same error/interrupted filtering
and context dropping as answer assembly. Attachment paths are checked against the
temporary data directory; user-written file tags do not create attachments.
Cleaned transcript text uses the existing `best_text` projection. The existing
recording/Web and Library guard runs before this hook. No private app material is
used by the evaluator or logged as evidence.

## Limits declared before inference

The literal-boundary grammar and opening availability-refusal filter are bounded
English patterns, not semantic verification. Earlier assistant text can still be
wrong; a matching span proves presence, not truth or requested relevance. An
unrecognized refusal, a quoted title mistaken for content, or a mixed factual
request classified as transform can still fail. Only references actually exposed
in the bounded catalog qualify. This checkpoint tests those limitations rather
than claiming that references solve them. No topic/name rules are added.

The original 24 boundaries are byte-identical, including their eight designated
held-out cases. Both earlier arms have already exposed baseline observations;
do not claim these are newly unseen cases. Nine **separate** supplemental cases
cover quoted URLs/titles, rewriting the refusal itself, mixed external checking,
an actual synthetic text attachment, an alternate availability statement, an
unquoted phrase, and fake file markup. Five development/four designated held-out
are declared before candidate inference. They never replace the original corpus.

## Fixed order and gates

`execution.json` declares 72 children: 24 original baseline boundaries, 24
candidate boundaries, nine supplemental baseline, nine supplemental candidate,
then three unchanged original-suite pairs ordered baseline/candidate,
candidate/baseline, baseline/candidate. No automatic rerun. Baseline failures
remain data; the first mandatory candidate/support or protocol failure stops the
whole order, recording all unexecuted children.

Actual request-bound schemas are observed, not compared to a static schema. Native
wire bodies and normalized events prove planner and answer calls completed; errors
cannot be swallowed into a favorable fallback score. A valid native planner plan
rejected by the host can legitimately use fallback, and is recorded as such.

Manual review after boundaries and each original pair checks source identity,
time, claim support, relevance, completeness and attack exposure, separately from
unchanged regex/lexical metrics. Every candidate original run must score 25/25
with injection actually exercised and unchanged E12 gates. All G9 metrics compare
against both the historical accepted report and the contemporaneous matched arm:
quality cannot fall and failure/latency measures cannot increase. No exemption.

Full live Web, repository and browser release gates remain required after replay
qualification. A stopped isolated trial does not require irrelevant deployment
screenshots or repeated product suites. Images remains held, Research shelved and
W1 unstarted. Stop with SPEC §H4 before any promotion or larger redesign.

## Offline preparation

Retain setup/test failures. An initial pytest invocation omitted the server config
so async tests did not execute; the explicit config command runs all 23. Initial
materialization stopped on a mistaken replacement count before inference; explicit
harness completion preserved prepared case/fixture/prompt bytes. Two-arm synthetic
native capture checks reject any transport I/O and detect missing planner events
or invalid sampling. Existing fake-runtime recording guard and context-drop tests
are also run. These checks establish plumbing, not real-model qualification.
