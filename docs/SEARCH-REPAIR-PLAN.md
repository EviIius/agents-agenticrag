# Search repair proposal after the I1 diagnosis

11 October 2026. **Proposed, not executed.** Review this scope after
`IMAGES-SEARCH-DIAGNOSIS-REPORT.md`. The diagnosis authorization covers comparisons,
not production prompt changes or deployment. The Images release remains held.

## Repair the demonstrated boundaries first

The matched accepted and Images sources both fail external-page summarization
and the unknown-person question. Their Search modules and first-turn planner
requests are identical. Reverting Images will not fix these reproduced failures.
The accepted historical summary pass used the existing malformed-plan fallback;
it does not establish reliable classification. Other factual grounding failures
remain in their original reports.

Prepare **one generic prompt candidate**, using the existing planner and answer
calls. Preserve the old prompts and hashes. Do not introduce another verifier,
planner retry, model, tool, package, routing rule or topic-specific exception.

### Planner clarification

Append this exact proposed instruction to the existing planner prompt:

> A transformation requires content supplied in the latest message or the
> conversation. A title, URL or description of an external page identifies a
> resource; it does not supply that resource's content. Summarizing an external
> resource or factual subject whose content is absent is lookup, not transform.
> Transform supplied words, quotations, excerpts and an earlier conversation
> answer without searching unless the user also requests external facts.

This repairs the distinction between an operation and the input that operation
needs. It is not a guarantee that a model will obey the instruction. Tests must
cover short supplied text and history references as well as missing resources.

### Answer clarification

Append this exact proposed instruction to the existing web-answer prompt:

> Evidence must establish the requested subject, relationship and time period.
> First-person words such as "I" or "you" in a source refer to that source's
> participants; do not equate them with the requesting user without an explicit
> link in the conversation. Facts about unrelated subjects do not answer the
> requested fact. When that link or a requested detail is missing, state that it
> is not established by these sources. Do not substitute unrelated biographies
> or records, or state an unsupported value followed by a disclaimer.

This addresses relevance and explicit abstention. It does not restart the shelved
Research/evidence-selector experiments or change ordinary chat/Library prompts.

## Evidence before any promotion

1. Freeze the candidate prompt texts/hashes, evaluator, unchanged original 25
   cases/corpus, model, parameters, source and complete ordered invocation plan
   in Git before inference. Use a common explicit date within matched pairs.
   Keep ordinary answer sampling unset and existing utility parameters intact.
2. Add a **separate** 24-case synthetic boundary suite: six absent external
   resources, six supplied transformations, six history references, and six
   identity/time/missing-detail questions. Include ambiguous and mixed requests.
   Freeze eight as held-out cases before applying the candidate; never amend the
   original suite. Synthetic input/evidence only; no private user data.
3. Measure the unchanged and proposed prompts on those identical inputs. Require
   correct Search decisions, preserved transformation behavior, matching evidence
   identity/time, refusal of unsupported values and actual attack exposure with
   no injected instruction followed. Review support manually against the exact
   supplied passages, separately from token-overlap scores.
4. Run three full matched original-suite pairs with a frozen candidate, orders
   baseline/candidate, candidate/baseline, baseline/candidate. All three candidate
   runs must pass **25/25**, expose the attack and meet unchanged E12/G9 gates.
   Compare every aggregate and case with the matched baseline and retained
   accepted report. Record model/residency and runtime timing without asserting
   a cause from a single latency difference. Stop at a mandatory failure; retain
   the trial and report the remaining declared runs as not executed. Do not retry
   until a favorable result, lower a threshold or accept a new variance silently.
5. If these checks pass, run the unchanged fresh live Web evaluation and required
   repository/browser regression gates, preserve prompt hashes and H4 evidence,
   and present the Search/Images release decision. A fresh model result alone
   does not release Images. Keep the installed app healthy throughout.

If the candidate fails, stop with the failure and review a deterministic input/
reference validation design separately. Do not add that larger behavior change
mid-trial. Passing this bounded suite would establish measured behavior, not a
general claim that all factual answers are reliable.

## Sequence after the gate

1. Release and physically review the Images candidate when all release gates pass.
2. Review W1 ordered meeting-pack drafts using the existing durable execution and
   artifact lifecycle, explicit per-step model choices and human review of factual
   output. Workflow model calls remain separately authorized scope.
3. Reference editing, more image/chat residency combinations and broader automated
   agents remain later checkpoints. Storage/delete/backup controls already belong
   to the held Images candidate; model weights remain shared once.
