# Next bounded 8A experiment proposal

Status: proposed; no inference run or qualification. Keep the daily qualified model,
original corpus/cases/grader/baseline/thresholds, host budgets and accepted live 7B.
New model downloads remain deferred. Trial 11 and all earlier failures are retained.

1. Simplify the existing final-call evidence-selection task. Avoid repeating the
   entire source body alongside its exact-unit catalog; measure token/context cost
   before inference. Keep document identity, headings, exact unit IDs and untrusted
   boundaries. Do not add a planning, repair, judge or answer call.
2. Treat literal label fragments as display choices only. They are not an answer
   coverage plan. Preserve a full user question and require causal explanations,
   comparisons, requested conditions and exceptions. Do not add benchmark nouns,
   question templates, expected answers or publisher-specific rules to prompts.
3. Preserve contiguous sentence context across soft line wraps. Avoid isolated
   fragments that drop causes or exceptions, while keeping hostile instructions
   separate. Every selected quotation must retain its immutable source provenance.
4. Keep value/date/ID rejection and separate semantic review. Visible-format
   normalization is a provenance remedy, not permission to infer an unstated day,
   assign a fact to another item, quote inaccurate background, or count a partial
   error response as completed. Retain before/after source and prompt hashes.
5. Add meaningful synthetic lifecycle/context/support-boundary tests. Freeze the
   candidate and predeclare three identical full 15-case runs before inference.
   Run confirmations only after every numerical, manual support/completeness,
   citation, injection and budget gate passes. Do not select favorable runs.

A further low score is not proof that the model can never qualify. A 13/15 regex
score is not proof of reliable Research. No proposed step authorizes 8B or changes
ordinary Search/Library prompts, runtime configuration, sampling or deployment.
