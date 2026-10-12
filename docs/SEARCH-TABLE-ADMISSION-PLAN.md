# Proposed next correction: admit relevant table data

Status: **proposal only**, 12 October 2026. Start offline; no native inference or
deployment is authorized by this document. See the completed
`SEARCH-TASK-AND-EVIDENCE-AUDIT-REPORT.md` for the retained mechanical evidence.

## Concrete defect

An already-fetched, correctly chunked table has the complete header and 28 rows,
including 23 explicitly positive matching counts. Its 463-token cost fits the
524 tokens left in the actual 5,502-token source budget, but all three slots for
its page are occupied by introductions. Replacing one caption admits it at
5,333 tokens. More context, fetching, model calls or prompt wording are not
needed to correct this admission defect.

## One bounded correction

Refine existing ranking/selection of **original passages** so an eligible page's
relevant structured table can occupy one of its existing three slots instead of
a lower-value introductory passage. Require an original header and aligned rows,
literal requested column/role relevance, and budget fit. Preserve source URL,
ordinal, header, empty cells, dashes, units and every original row value. Use the
existing token estimate, source limit and passage cap; no new routing or model
call. Do not prefer arbitrary pipes, code, captions, link collections or ambiguous
header-like first data rows. Do not infer a missing condition, interpret a dash
as zero, filter named entities or assert complete coverage.

This first correction does **not** reconstruct lost HTML tables, combine multiple
different game tables, synthesize field values, rerender old answers, revive the
failed model-ID selector, or change prompts/schema. Those remain separate issues.

## Offline acceptance

1. Freeze one host candidate and hashes of the same original inputs before any
   model trial. Retain this audit, prior failures, scores and declared thresholds.
2. Replay the actual table omission with the calibrated estimator: admit the
   original data unit, preserve all seven columns and 28 rows, stay at most three
   passages/source and within 5,502 tokens. Verify complete original text bytes.
3. Add meaningful negatives: missing/ambiguous headers, uneven cells, escaped
   delimiters, empty cells, literal dashes, tables unrelated to the request,
   pseudo-tables/captions/code, over-budget data and many eligible sources.
4. Check that factual prose, source ordering, existing numeric/occurrence
   selection, citations and context admission remain intact. No topic-specific
   preference or fixture substitution. Run repository/browser gates once.
5. Stop with H4 before native inference. Report evidence-admission improvement
   separately from claim support or completeness; a host replay is not a new
   grounded answer.

## Native release remains gated

The audit also exposes contradictory task/query fields and a factual request
admitted by an unsafe creative label. Those need a separately reviewed generic
admissibility correction with actual pinned-runtime compatibility evidence.
The existing source extraction loses role tables, frozen discovery omits facets,
and the answer violates source-only rules. Do not knowingly repeat a full run
against those untreated failures or call a better lexical score reliable.

After mechanical repairs are reviewed, a new native order must begin with the
original known failures, preserve the complete benchmark and equal evidence for
both arms, and resolve evaluation coverage through a separately reviewed
coverage-checked comparison without overwriting original inputs/scores. A
required fact absent from the fixed replay cannot be qualified by a memory
answer or expected token. Stop on mandatory/support/protocol/G9 failure, retain all outcomes,
and pass semantic review plus repeated full gates. No target is lowered here.
Live app/default/runtime remain unchanged; no Research, image or workflow action.
