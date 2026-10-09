# Proposed next reliability checkpoint

This is a reviewable proposal after the 9 October isolated repair, not permission
to deploy a different answer contract. Read `RELIABILITY-REPORT.md` first.
Research remains shelved; the production tree and current default remain stable.

## Decision

Do not promote any of v1–v7 or switch the default to Qwen 3.8. The controlled
pilot improved everyday behavior, but both profiles still fail factual Web
review. Repeating failed free-form prompts is not a release strategy. Separate
retrieval coverage, source provenance, relevance and answer completeness.

## Build and evaluate one bounded evidence contract

1. **Recover requested fields before generation.** Test generic table selection
   in the full isolated pipeline, preserving scores, source IDs, column labels,
   blank cells and the existing numeric predicate. The offline 14/23 to 23/23
   coverage result is a hypothesis, not a passing answer. Any ambiguous table
   binding must abstain. Preserve all original cases, including missing currency.
   If a required field is absent from the recorded corpus, retain that original
   coverage failure. Record a separate query-aware public corpus for matched
   current/candidate evaluations; do not silently replace saved pages or give
   credit for a fact supplied from memory. Test useful queries as well as the
   binary search decision, within the existing query/fetch/call budgets.
2. **Keep source context with every selectable unit.** Current sentence/row
   splitting can lose subjects, dates, qualifications or a column's meaning.
   Preserve those in host-owned unit metadata and render them together. Test
   infoboxes, repeated headers, captions, signs/decimals, negations, time limits,
   absent fields and earlier-turn ambiguity using novel synthetic documents.
3. **Constrain the existing answer call.** Let it select IDs for supported
   evidence, without writing new factual prose. Validate IDs and their source
   membership before rendering. Support multiple units where required; the
   current one-unit-per-source prototype intentionally cannot complete complex
   tables. Retain source-specific quotation limits and safe text rendering.
   Tables may render original fact cells with their original column meanings;
   do not infer a new property/value relationship from matching numbers.
4. **Show unsupported coverage honestly.** Never label a valid ID or literal
   quote as a verified answer. A rejected output yields an explicit inability
   to substantiate the request, with existing sources available for inspection.
   Empty evidence must be distinguishable from a successful complete answer.
   There is no automatic retry, second answer call, judge or Research loop.
5. **Evaluate before UI or promotion.** Predeclare manual checks for identity,
   property/value binding, dates, negation and relevance for every answer,
   including earlier turns. Run the unchanged 20 everyday, 25 Web and 34 Library
   cases; keep original scoring and explicitly record any answer-format
   compatibility failures. Keep the personal-breakfast, absent-currency and
   complete-table failures in the suite. Add held-out checks, then repeat a
   frozen candidate three times only after the first full pilot passes.
6. **Review the product tradeoff.** Evidence-first answers will be less fluent
   and may decline more requests. Review sample outputs and the existing SSE
   rendering/notice/export contract before changing product behavior. Require
   the existing regression, performance and live free-provider checks before
   deployment. Ordinary chat, prompts and user sampling remain unchanged until
   specifically included in that reviewed checkpoint.

## Stop conditions

Fail on invented text, wrong source, wrong relation, lost qualification,
unsubstantiated identity, ignored injection, incomplete requested coverage or
regression. Schema success is not semantic success. If the evidence contract
cannot meet the unchanged gates, retain it as evaluation tooling and report
that limit. No model download, runtime upgrade, package, extra model call,
routing or Research restart is part of this proposal.
