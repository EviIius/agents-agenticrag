# Reliability repair — 9 October 2026

Jake asked Codex to make ordinary chat and Web search reliable after reviewing
the failed model comparison. This authorizes generic prompt and grader repairs
with retained before/after evaluations on the two already-installed profiles.
Research stays shelved. No downloads, runtime upgrades, packages, routing,
sampling changes, additional production model calls or default switch.

## Checkpoint scope

1. Repair the Library checker's post-period citation binding separately. Test
   positive placement and negative neighboring-sentence/row/paragraph cases.
   Write separate regrades of retained answers; never overwrite original scores.
2. Fix the planner's distinction between supplied text and a referenced page
   which has not been read. Test novel requests, supplied-text transformations,
   follow-ups and adversarial content as well as the unchanged Web benchmark.
3. Strengthen generic source-only and local citation behavior. Protect quoted
   records and attachments as data, preserve extraction values and make missing
   information explicit. No subject-specific rules or model-specific prompts.
4. Freeze each trial before inference. Retain every trial, prompt, answer,
   selected passage and failure. Original comparison runs are the before
   baseline. Use identical frozen case/corpus hashes and runtime profiles.

## Evaluation and release decision

Run a full everyday/Web/Library pilot on the current model. Run the candidate's
planner/citation regressions and a full pilot if those permit useful comparison.
An improving frozen trial needs three complete runs on each profile before a
qualification recommendation. A failed pilot is not retried into a pass; further
trials must have a documented generic change and new version. New held-out
synthetic checks supplement, never replace, the original suites.

Keep all existing E12/E13/J7 thresholds and the 18/20 everyday threshold, including
zero obeyed embedded overrides and source-only grounding. Review unsupported
extra claims, exact value/source relationships and every earlier answer in a
follow-up case. Automatic lexical or fact-presence scores are not semantic proof.
Grader corrections cannot manufacture missing facts or excuse unsupported claims.

The installed app and its data stay on the stable build during experiments.
Run regression checks on a candidate only after its inference measurements.
Stop with SPEC H4 evidence and an honest recommendation. A failed gate prevents
deployment or promotion; report the remaining limitation rather than weakening
the threshold. No universal factual-accuracy guarantee is implied by a benchmark.

## Diagnostic refinements and stricter feasibility test

Trials v1–v7 preserve their effective module hashes and all outcomes. v7 also
tests a generic fixed 1,500-token Web evidence ceiling on both profiles. This
reduces measured prefill cost; lost coverage and unsupported answers count as
failures. It is not a deployed budget change.

Free-form answers in v6/v7 still misbind values or invent absent game scores.
Predeclare a separate extractive feasibility probe: one answer call selects
literal excerpts with source IDs in a JSON schema. A deterministic checker
accepts only exact text from that cited source, with bounded excerpt sizes and
no arbitrary prose. Invalid output is rejected, never repaired or retried.
No planner, judge, Research loop or additional model call is added to a request.

Run the same eight retained difficult Web/Library inputs on both installed
profiles, sequentially after the v7 pilot. Freeze prompt, schema and input hashes
before inference. Test rejection of altered numbers, wrong sources, partial
invalid output, extra fields, Markdown/HTML and malformed JSON without inference.
This is an isolated answer-contract experiment, not a replacement for the
unchanged release benchmark. Report relevance, coverage and exact provenance
separately; an exact quotation does not prove the source is true or answers the
question. A product change would require a reviewed streaming/format contract
and full gates before deployment.

The candidate v7 comprehensive-list replay also omits an available full table:
the smaller budget selects introductory paragraphs instead. Test a separate
offline table-priority hypothesis on those identical saved page bytes and novel
synthetic item/state tables. Prefer intact tables only when at least two literal
requested header terms match and the user asks for a list/table/comparison.
Retain all scores, rows and values; do not infer a condition, create facts or
alter production ranking. Measure coverage at the same budget and label it an
offline selection experiment, not an answer/release pass.

v2 literal-copy results: current model 4/8 accepted, candidate 7/8 accepted.
Invalid copied excerpts are rejected in full, never silently fixed. Predeclare
v3 on the identical eight inputs: each source has host-owned short evidence
units; the single answer call chooses at most one unit ID per source or null.
The host supplies text and any original table header. No generated prose/quote
is accepted. Retain the word cap and every rejected/missing-information outcome.
Measure relevance and coverage manually. Schema validity and exact text by
construction do not prove factual truth, completeness or correct selection.
