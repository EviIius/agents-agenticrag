# Search input fallback: isolated execution declaration

11 October 2026. Jake said “continue going” after the stopped input-contract
trial and its proposed fallback correction. Freeze one candidate before inference.

## Candidate and unchanged controls

Only `artifacts/images-i1/search-input-fallback/` installs the candidate in a
temporary `workbench-eval-*` application. Product files, the installed app and
previous evidence remain unchanged. There is one existing planner and one
existing answer per turn; no repair call, title, embedding or image invocation.
Native Ollama 0.35.0, the runtime-reported 16K Qwen chat model, utility sampling
`temperature=0.2` / `max_tokens=256`, reasoning off, and empty answer sampling
are fixed. The previous candidate's global prompts and schema are byte-identical.

This candidate changes the host's response to planner mistakes. A complete,
unambiguous literal transformation binds to actual supplied material and stays
local even if native JSON omits its reference or wrongly requests lookup.
Invented native references/spans remain invalid. Missing external material uses
the existing lookup fallback. An ambiguous transformation with supplied material
asks for clarification through the existing answer, with one new, separately
hashed conditional system instruction in `instructions.json`. No extra call or
content notice is added. Force-search and mixed external checking retain lookup.

The catalog, selected-branch/context-drop handling, attachment path checks,
cleaned transcript projection, 240-character previews and 2,800-character catalog
budget remain as before. Host decision records contain modes/reasons/opaque IDs;
only synthetic/public fixtures are used by inference and evidence.

## Limits frozen before inference

Literal, formatting, external-check and opening availability patterns are bounded
English grammar, not semantic verification. A deictic request chooses the latest
supplied body or, absent one, the latest non-availability assistant response.
That can still select the wrong antecedent or preserve earlier false content.
Quoted commands are treated as data, but an unrecognized mixed instruction or
availability phrase can still fail. The planner may choose a valid but irrelevant
reference outside the grammar. Explicit named resources without bodies require
lookup; there are no topic/entity-specific rules.

## Corpus, order and gates

The original 25 full-suite cases, 24 boundary cases (eight designated held-out),
nine separate supplemental cases (four designated held-out), grading, fixtures,
historical reports and failures are retained unchanged. Earlier baseline and five
candidate observations are already known; these are not newly blind cases.

The byte-identical `execution.json` predeclares 72 children: 24 baseline
boundaries, 24 candidate boundaries, nine supplemental baseline, nine supplemental
candidate, then three original full-suite matched pairs ordered baseline/candidate,
candidate/baseline, baseline/candidate. There is no automatic retry. Stop on the
first mandatory candidate, semantic-support, protocol or G9 failure; record all
unexecuted children. Review semantic support separately after boundaries and each
full pair, and before advancing. Manual findings during execution can stop it.

Every candidate original-suite run must pass 25/25, actual injection exposure and
unchanged E12 gates. G9 compares with both the historical accepted report and its
matched baseline: quality cannot fall; failure and latency metrics cannot rise.
Native wire/events must prove one completed planner and answer; swallowed capture
or provider failures cannot receive a favorable fallback score. Actual per-request
schemas are checked. Native reference rejection is separately recorded from
transport validity and observed Search behavior.

Only after replay qualification can live Web, repository and browser release gates
run. Images stays held, Research shelved and W1 unstarted. Stop with SPEC §H4 before
promotion, another candidate or a larger redesign.

## Offline preparation

Tests replay the actual retained null-reference JSON without inference; cover
literal/quoted URL input, quoted commands, documents/transcripts, dropped/stale
and ambiguous material, force-search, mixed checks, availability replies,
clarification in the existing answer and independent task context. Retained
inventory tests and the existing fake recording/context guard tests protect the
hook. Actual capture/schema/protocol functions are tested with a rejecting
transport in baseline, candidate-valid-reference and candidate-null-reference
arms. Initial lint findings are retained; formatting repairs precede the freeze.
These checks prove plumbing, not model qualification.

An initial pre-inference freeze hashed its still-empty stdout log, which then
changed when the freeze completed. Verification correctly rejected that manifest.
Retain the initial manifest and verification error; exclude this output-only log
from the corrected freeze. No model call preceded this preparation repair.
