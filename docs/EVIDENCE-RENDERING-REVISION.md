# Evidence contract v7: literal rendering replay

This revision changes only the isolated host renderer. It makes no model calls,
changes no selection prompt, and does not qualify a model or a production pipeline.

## Reason

Version 5 escaped decimal points and hyphens in raw Markdown. The existing Library
grader consequently missed `0.5` and `ORCHID-42` even though their visible values
were preserved. Keep those original failed reports intact; a separate replay can
measure the formatting correction without rerunning inference or retrieval.

## Changes

- Put source text in literal inline code spans so decimal points, negative signs
  and identifiers survive unchanged and source HTML/links stay inactive.
- Reject selected evidence containing backticks. The existing citation scanners
  do not reliably recognize arbitrary code-span delimiters; this conservative
  restriction is a new limitation, not a claimed compatibility fix.
- When the user requests a table, render selected prose in an Evidence/Citation
  table. Structured source rows retain their original headers, cells and context.
- Retain v6's unidentified-speaker check and explicit unsupported-information
  wording. Keep source fields, source membership, context, quotation limits and
  the selection prompt unchanged.

## Verification

Freeze source, tests and input trace hashes before replaying all 62 v5 selection
streams. Assert that reconstructed evidence units exactly match the original
catalogues. Save both original and revised outcomes, with no inference, retrieval
or original-report mutation. Evaluate any grading differences as host-rendering
diagnostics only. Missing facts, irrelevant selections, poor response time and
the original failed release gate remain unresolved.
