# Search conversation guard: isolated execution declaration

11 October 2026. Jake said “continue then” after the current improvement list and
the recommendation to repair factual requests being classified as small talk.
Freeze one candidate, input set and order before native inference.

## One candidate

Only `artifacts/images-i1/search-conversation-guard/contract.py` installs the guard,
inside the temporary `workbench-eval-*` application. Product files and the live
application are unchanged. The existing material-binding/reference/clarification
policy is retained. Global planner/answer prompts, schema and conditional
clarification instruction are byte-identical to the previous candidate.

For `task=conversation`, the complete latest turn must match the host's bounded
English grammar of greetings, thanks, brief social exchanges, acknowledgements
and questions about the assistant itself. At most four social acts and 240
characters are admitted. Matching only a greeting substring cannot suppress a
factual tail. Failure raises the internal `ConversationNotAdmitted` condition,
which uses the existing lookup fallback. Existing supplied-input binding still
has priority; force-search and ambiguous-transform clarification retain their
previous behavior. There is no new prompt, topic/entity rule or model call.

There is one existing planner and one answer per turn. Native Ollama 0.35.0,
runtime-reported 16K Qwen, utility temperature 0.2 / 256 output tokens, reasoning
off, and empty answer sampling remain fixed. No image/title/embedding/Research
or workflow invocation, added package, model, runtime upgrade or deployment.

## Declared limits

This is a bounded English admission grammar, not semantic intent verification.
Unfamiliar or multilingual social wording can fall back to unnecessary lookup.
A context-dependent acknowledgement may still refer to earlier factual work.
Assistant-identity replies are not independently truth-verified. Native creative
and calculate labels retain their previous handling, and can still be mistaken.
This guard qualifies only conversation admissibility, not every possible no-search
decision. Earlier material/reference/coverage/support limitations remain open.

The eight ordinary-task cases cover complete greetings, thanks, two factual tails,
poetry, pure Python, arithmetic and editing a quoted greeting. Four development
and four designated held-out are fixed before inference. They do not replace
original cases or constitute a blind independent benchmark. Their synthetic
wildcard web fixtures are identical for both arms and are not live web evidence.

## Preserved corpus and fixed order

The original 25-case full benchmark, 24 boundaries/eight designated held-out,
nine supplemental cases/four designated held-out, all grading, fixtures, historical
reports, failed trials and release targets remain unchanged. Known earlier
observations are not newly unseen cases.

`execution.json` declares 88 children: the same 24 baseline boundaries, 24
candidate boundaries, nine supplemental baseline, nine supplemental candidate,
then eight ordinary baseline and eight ordinary candidate cases. Last are the
same three original full-suite pairs ordered baseline/candidate,
candidate/baseline, baseline/candidate. Original 72-child relative order is
preserved. The boundary phase ends after 82 children; no automatic rerun.

Stop at the first mandatory candidate, semantic-support, protocol or G9 failure.
Record all unexecuted children. Manual source/subject/date/support/relevance and
completeness review remains separate from regex/lexical metrics and is required
before the original full pairs and between pairs. Observed semantic failure can
stop the boundary phase early. Do not regrade the prior correct decline or waive
its search/wording failure.

Every candidate original full run must pass 25/25, actually expose/resist injection
and meet unchanged E12 gates. G9 compares with both historical accepted and matched
baseline reports: quality cannot decrease; failures/latencies cannot increase.
No favorable-seed retry, new corpus replacement or accepted-variance exemption.

Actual request-bound schema, native wire bodies and normalized events must prove
one completed planner/answer. Transport/instrumentation failures cannot acquire a
favorable score through fallback. Host decisions retain the internal rejection
reason separately. Live Web, full repository/browser release checks and physical
phone review remain required later. Images stays held; Research shelved; W1 waits.
Stop with SPEC §H4 before another candidate or promotion.

## Offline preparation

85 policy/inventory/conversation and existing recording/context checks pass;
eight copied old-policy expectations remain deselected with their original files
preserved. Tests replay the exact retained native conversation JSON, exercise
complete/social-plus-factual turns, genuine local tasks, force-search, supplied
quote precedence, clarification and unchanged instruction hashes. Four rejecting-
transport arms exercise actual capture/schema/protocol code, including rejected
native conversation. Fixture extraction/order and runtime metadata are verified
without inference. Initial lint output is retained before formatting.

Two initial combined source patches aborted validation before writing because
their closeout hunks were out of order. Correctly ordered patches applied before
tests; this is preparation, not a native runtime failure. No candidate inference
preceded successful tests and the Git freeze.
