# Proposed Library prompt revision — approval pending

Version 1 remains active and frozen. The first full real-model baseline is
`server/evals/library/reports/2026-10-06-114229-full.json`. Its answers are unchanged
in the punctuation-corrected regrade. No proposed text has been sent to a model.

Recommendation: keep the existing source-only, abstention, numbering and injection
rules and strengthen the generic citation instruction with these sentences:

> Every factual sentence, bullet and table row needs its own inline citation.
> Place table citations inside the row they support. A lone citation below a
> table or at the end of a paragraph does not cover earlier statements.

Also reinforce the existing restriction to stated facts:

> Do not infer attributes or fill in details that the passages do not state.

These instructions apply to every topic. They add no model calls, dependencies,
query rewriting or runtime changes. After approval, freeze the revised prompt
hash, run a full before/after comparison on the unchanged corpus and cases, and
review all answers. Keep the 100% citation gate. Then finish the full regression
suite and web replay before deployment or 7B closure.
