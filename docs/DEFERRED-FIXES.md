# Deferred fixes — resolved polish, 8 October 2026

## Current status — 19 October 2026

This section supersedes the historical pending/proposal entries below.

- Live source is PR #5's merge `b41ec355`: the manual-title and workflow wording
  repairs are released alongside Aether, attachments, workflow/chat images and
  idle embedding handoff. Jake confirmed the earlier image paths and phone
  checks. On 19 October he confirmed the title stays, Workflows opens in Canvas
  and Outline, and a workflow run works; the new phone check is closed.
- The isolated native agent C1 candidate failed and stopped after one call; N1,
  Hermes and PydanticAI trials remain preserved. No agent implementation is
  integrated. No further prompt/framework campaign or Research restart is active.
  Evidence: `codex/native-agent-loop` at `376205a3`,
  `docs/AGENT-C1-RETEST-REPORT.md` on that branch.
- The narrow follow-up passes 726 Python / 126 frontend / 721 browser tests,
  with three existing skips. Installed hashes, copied-data fallback and actual
  HTTPS synthetic UI checks pass. See `PRODUCTION-FOLLOWUPS-REPORT.md` and
  `PRODUCTION-FOLLOWUPS-RELEASE-REPORT.md`; no native agent code is included.
- Remaining product work: photo-reference editing and the disabled workflow
  blocks. Their reviewed implementation/native-validation scopes are still
  separate. Existing Search/Library remain available; factual reliability is
  not newly qualified. Further quality repair needs a concrete failing example.
- VoiceOver remains removed from the current work list. Its historical reported
  failure is retained; no pass or new physical-phone timing is claimed.

## Current QA repair checkpoint — 17 October 2026

**Release follow-up:** PR #3 is merged and the tested repairs/Aether display name
are live. See `QA-ROADMAP-RELEASE-REPORT.md`; phone acceptance is pending. The
paragraphs below retain the original branch-review status. Hermes assessment is
now the next priority, ahead of a custom agent loop; reference-photo editing is
tracked in `HERMES-AND-PHOTO-EDITING-PLAN.md`.

The older sections below retain their checkpoint history. Current implementation
is on `codex/qa-roadmap-repairs` in draft PR #3 and is not deployed. The source
draft rollback, unsupported thinking fallback, Document Start input and disabled
embedding Eject defects are repaired. Auto is labeled Model default; long
thinking has truthful guidance and Stop, and Aether is the display name.
The frozen candidate passes 686 Python, 126 frontend and 711 browser tests,
with three unchanged browser skips. The installed app remains unchanged;
publication is the next review checkpoint.

Full QA results and remaining limits are in
[`QA-ROADMAP-REPAIRS-REPORT.md`](QA-ROADMAP-REPAIRS-REPORT.md). Preserve current image
memory limits: the embedding recovery is explicit manual Eject, not automatic
unloading. No hard thinking deadline, Answer now continuation, factual grounding
qualification, agent/tool loop, new workflow block or routing is claimed.

| Issue | Current action | Verification |
|---|---|---|
| iPhone recording menu clips its first action and reaches the home indicator. | Implemented safe-area collision padding and a scrollable visible-viewport height limit. Preserve unavailable retry entries and their explanation. | Synthetic portrait, landscape and keyboard-sized viewport checks; first/last action access, dismissal and focus return. See deferred polish report for results. |
| Sidebar/other motion appears absent on the phone. | The installed preference is Always, which intentionally suppresses animations. Implemented effective status and guidance to follow the device preference in Appearance. On 15 October the static-chat report again had Always saved; restored Follow system and verified repeated drawing/thinking movement plus actual send entrance in the installed build. Preserve the intentional desktop width snap because its WebKit candidate exceeded the frame budget. | No physical iPhone pass is invented. See `docs/CHAT-MOTION-AUDIT-REPORT.md` for temporal Chromium/WebKit checks and retained synthetic videos, plus the earlier polish report for sidebar checks. |
| Model picker is difficult to scan. | Implemented All, Loaded, Images, Reasoning and Tools filters using reported capabilities; mark Selected separately from Loaded. | Synthetic filter, search, selection, loading/context and keyboard tests. |

VoiceOver was removed from the current work list at Jake’s request. Historical
reports retain the reported failure; this is not a successful VoiceOver test.
Ordinary labels, keyboard access and focus handling remain in place.

Research is shelved; see [RESEARCH-SHELVED.md](RESEARCH-SHELVED.md).

## Findings from the approved model comparison

The comparison is complete. These observed failures are the proposed next
repair scope; no production prompt or grader change was made during measurement.

| Finding | Proposed next action | Evidence |
|---|---|---|
| Current ordinary-chat model obeyed commands embedded in two invented records. | Design a generic untrusted-record treatment, retain the original prompts and run before/after everyday and release evaluations before a prompt change. No topic rules or extra model calls. | `artifacts/model-comparison/pair-1-baseline-everyday-review.json`, E17/E18. |
| Both models can add unsupported facts or omit local citation binding despite favorable automatic scores. | Strengthen claim review and test generic source-only/citation behavior with retained baselines. Do not lower required gates or use lexical overlap as proof. | Per-run Web and Library manual review JSON under `artifacts/model-comparison/`. |
| Library grader can attach a citation after a sentence period to the following sentence. | Add a focused positive/negative citation-binding fixture and repair the grader separately; preserve all original scores and avoid granting unsupported neighboring claims a citation. | Candidate pair 1 Library `resume`; raw report and manual review retain the 96.4% automatic result. |

No new production fix, model switch or Research restart is part of this comparison.

## Reliability follow-up — 10 October 2026

The comparison table above records its original proposed scope. The citation
grader's post-period/table binding has since been repaired with positive and
negative fixtures and separately labelled regrades; original answers and scores
are retained. This corrects measurement, not semantic support or model quality.

| Remaining item | Current state | Next action |
| --- | --- | --- |
| Grounded answer contract | v14 original-case native smoke rejected and stopped. Named references/identity keys are valid, but identity-only rows and an over-budget prose selection still fail the host guards. No candidate qualified. | Align native schema with host admissibility before another bounded original-case trial; preserve source context and all failures. |
| Retrieval, completeness and relevance | Full latest Web/Library trial remains gated; previous omissions and extra/irrelevant claims remain unresolved. | Evaluate unchanged cases and manual claim support only after the protocol smoke passes. |
| Ordinary-chat untrusted records | No production fix; retained unchanged-pipeline evaluation remains 16/20. | Separately evaluate generic untrusted-record treatment against original everyday and release checks. |
| Attachment context warning | Published the corrected input/output allowance, saved-default precedence and readable warning. Six focused checks and one complete 463-pass browser rerun passed; three existing skips retained. | Reopen/reload Atelier to receive the frontend update. Stable server preserved; private static/database fallback saved. No physical iPhone acceptance claimed. |
| Image generation | Documented Mac options only; nothing installed or downloaded. | Separately approve and benchmark a named Draw Things / FLUX.2 klein 4B trial before integration. |

See `EVIDENCE-OBJECT-REPORT.md` for this checkpoint's actual results. Research
remains shelved and VoiceOver stays off the current work list.

## Approved sequence, checkpoint R — 10 October 2026

The earlier table remains the v14 history. The approved bounded v15 repair now
passes the original first smoke, selecting complete Team/Wins fields with the
original context and citations. Its gated Web remainder then stops when six
individually admitted excerpts violate a source's combined quotation allowance.
No failed factual output, retry, full Web result, Library or consistency run
followed. This candidate is not qualified.

End this selector design at the declared checkpoint. Review a simpler presentation
through existing source cards/“What the model saw” and explicit missing-evidence
status. This proposed fallback is not implemented and does not resolve remaining
relevance, completeness or ordinary-chat injection failures. No release targets
are waived; factual automated outputs remain drafts for review.

The next independent checkpoint is the concrete MFLUX/FLUX.2 klein 4B worker
trial proposed in `IMAGE-TRIAL-PLAN.md`, followed by durable jobs and image UI,
then ordered workflows. No image dependency or weights were installed. See
`EVIDENCE-BUNDLES-REPORT.md` for actual results and the checkpoint review stop.


## Image trial I0 — 10 October 2026

The earlier image rows describe the pre-installation proposals. Jake subsequently
approved the named isolated MFLUX/FLUX.2 klein 4B trial. Its twelve generations
and one reference edit are complete; the live application is not integrated.
All original grounding failures remain unqualified and Research remains shelved.

| Item | Measured state | Proposed next action |
| --- | --- | --- |
| Native image execution | All 13 outputs validate; real initialization/denoising cancellation and next-job recovery work. The first wrapper inspection bug and exact source are retained. | Review the full gallery and I0 H4 report before selecting the engine for integration. |
| Image quality | Nine clean generation matches; three flagged samples, including a second lamp, fox anatomy and ambiguous pear shape. | Human quality review; no favorable-seed selection, prompt rewrite or automated repair loop. |
| Image/chat resource coexistence | First image increases host swap. Chat is loaded in the fresh-worker stages, then expires before the resident batch ends. | Separately qualify bounded unused-allocation caching with intended chat residency verified for each sample; do not claim a global memory cap. |
| Queue and image product | Proposed only, with durable state/artifacts, real cancellation, SSE recovery and explicit resource handling. | Use the existing stack for I1 jobs and Images together after the memory gate; see `IMAGE-INTEGRATION-PLAN.md`. |
| Ordered workflows | Proposed after I1; no workflow model calls or autonomous agents implemented. | Recording-to-meeting-pack drafts first, then image drafts/variants with human selection. Factual reliability targets still apply. |

See `IMAGE-TRIAL-REPORT.md` for measurements, failures and regression closeout.
This is a separate image trial; neither factual-answer qualification nor a
physical phone pass follows from these results. VoiceOver remains off the list.

## I1 candidate — 11 October 2026

The authorized jobs/Images candidate now implements durable acceptance, native
admission, real cancellation/reaping, SSE replay, restart reconciliation, gallery
and job visibility, storage/removal and image-aware backup/restore. The corrected
native sequence, 508 Python / 39 frontend checks and one complete 473-pass browser
run pass. It is **not deployed**: the frozen Search replay is 24/25 against the
accepted 25/25, skips the injection fixture and lowers lexical citation support.
See `IMAGES-I1-REPORT.md`; preserve the failed trials and this review stop.

Next: review I1 and diagnose G9 with a separately frozen baseline/candidate
comparison before release. Physical phone review follows release. W1 ordered
meeting-pack drafts, reference editing, other loaded image/chat combinations and
the previously observed preference-write question remain later work. VoiceOver
remains outside the work list. Storage measurements are in `IMAGES-STORAGE.md`.

## I1 matched Search diagnosis — 11 October 2026

The frozen eight-run comparison is complete. Accepted source and Images source
both fail the same external-summary/unknown-subject cases, scoring 23/25. Six
focused planner requests match exactly and all select transformation without
supplied page text. The historical summary pass used fallback; its original
error is unknown. All failures, source captures and earlier evidence are retained.

**G9 remains failed; Images is not released.** Candidate lexical support is lower,
and semantic inspection also finds identity/relevance and unsupported-value
weaknesses. No prompt edit, production restart or W1 work occurred. See
`IMAGES-SEARCH-DIAGNOSIS-REPORT.md` and the bounded proposed before/after scope
in `SEARCH-REPAIR-PLAN.md`. Review that repair before further native experiments;
do not weaken the original cases/targets or deploy around the gate.

## Bounded Search trial — 11 October 2026

The first bounded prompt trial is **invalid for planner qualification**. A harness
assertion compared the bound request schema with the static schema and blocked
every planner request. Twenty-nine real answers ran via forced fallback; four
executed candidate external-resource answers are supported, but the translation
cites an unrelated page. All reports and the original stop record are preserved.
No candidate held-out/negative cases or original full runs qualified.

The harness correction passes offline reproduction and protocol-failure checks;
it is retained as a patch, with the frozen first harness unchanged. The next
checkpoint is a separately frozen retest of the same candidate/inputs/grading
with actual planner wire/trace verification. See `SEARCH-REPAIR-REPORT.md`.
**Images remains unreleased; prior G9 failures remain open.** No production
prompt change, deployment, service restart, W1 or Research call occurred.

## Corrected Search retest — 11 October 2026

The corrected native trial genuinely fails the first candidate case: an absent
page is classified as a transformation, Search is skipped and required facts are
missed. All 25 children have real planner/answer traces; baseline is 19/24 on the
separate boundary suite, executed candidate 0/1. Twenty-nine later children remain
unexecuted. These are not original 25-case benchmark scores. See
`SEARCH-REPAIR-RETEST-REPORT.md`, including its correction to the first report's
abstention-grading prose.

**Images remains unreleased.** Next proposed checkpoint is the supplied-input
reference check in `SEARCH-INPUT-CONTRACT-PLAN.md`, with unchanged original
benchmarks/gates and explicit preservation of transformations and attachments.
No product change, extra experiment, deployment, W1 or Research call followed
the mandatory stop.

## Isolated Search input contract — 11 October 2026

Frozen at `4ac3100`. Four candidate missing-resource summaries now perform native
lookup and give supported citations, but the next literal translation fails: its
supplied `bonjour` reference is omitted, and generic host fallback searches and
cites an unrelated record. The declared mandatory stop is preserved. Baseline is
20/24; candidate is 4/5 executed, with 43 later children unexecuted. These are
separate boundary scores, not qualification of the original Web benchmark.

See `SEARCH-INPUT-CONTRACT-REPORT.md` for native/host evidence and the proposed
next fallback-policy correction: locally resolve unambiguous literal input,
retain lookup for absent external content, and clarify ambiguous targets. No
further experiment is run after the stop. **Images remains unreleased; G9 stays
open.** The live app remains healthy and unchanged. Research is shelved; W1 waits.

## Isolated Search fallback policy — 11 October 2026

The frozen host fallback candidate repairs the supplied-literal failure in native
execution: seven transformations stay local, six despite missing native references.
It supports four external summaries and the explicit-identity lookup. Candidate
then stops at an unknown-personal-fact case: native conversation classification
skips required Search. The answer correctly declines to guess; do not describe
this as an invented meal or silently regrade the failed lookup/wording checks.

Fresh boundary baseline is 20/24; candidate is 12/13 executed. Thirty-five later
children, including every candidate held-out and supplemental case and the six
original full runs, remain unexecuted. See `SEARCH-INPUT-FALLBACK-REPORT.md`.
All prior failures and original targets remain; **Images is still unreleased**.

Next proposed reviewed repair: generic admissibility checks for non-lookup /
conversation decisions, preserving real small talk, supplied transformations,
creative work and pure math/code. No topic exception, extra call or broader
native retry follows this stop. Live app/runtime are healthy and unchanged.
Research remains shelved and W1 waits for reliability and image release.

## Image memory checkpoint I1-0 — 10 October 2026

Jake accepted proceeding from I0. The frozen 1 GiB unused-allocation cache policy
now passes both native cancellations, four-image recovery and unchanged before/
after READY probes. Daily chat residency remains present around every image;
45 health/swap/activity samples show no stage-relative swap growth. All four
decoded outputs match their I0 counterparts exactly. Live allocation still peaks
at 18.66 GB; this qualifies a small sequential combination, not a hard host cap
or concurrent full-context chat. See `IMAGE-MEMORY-REPORT.md` and retained results.

| Remaining item | Current state | Next action |
| --- | --- | --- |
| Image resource admission | Tested daily profile plus fixed image settings passes; other loaded models/context sizes are unqualified. | Admit only measured combinations initially; report resource waiting explicitly, without silently unloading models. |
| Durable queue and Images | Concrete I1-A/B proposal exists; no production code, schema or image UI deployed. | Implement durable acceptance/artifacts, idempotency, real cancellation/reaping, SSE replay, restart reconciliation and Images/Jobs together after this review. |
| Startup preference write | An isolated read-only Chromium probe attempts `PATCH /api/settings` during startup; the route is blocked and its body is not captured. WebKit attempts no write in the same measurement. | Check appearance hydration/preference synchronization separately; no redundant-write cause or phone failure is established. Original failed measurement and corrected after-batch result remain separate. |
| Image quality and factual reliability | Four resource samples match I0 pixels; I0's other defects and prior grounding failures remain open. | Keep human selection and reviewed factual drafts; do not infer broad quality or answer reliability from the memory pass. |

The original Research failures remain preserved and shelved. Ordered workflows
follow durable execution and have a separate reviewed call/evaluation scope.

## Isolated Search conversation guard — 11 October 2026

Frozen at `00d36fd1`. All 24 existing boundary cases and nine supplemental cases
pass with reviewed source support. The new guard actually catches native small-
talk classification on both unknown-personal-fact requests, performs lookup and
declines unsupported identities. These are synthetic boundary scores, not the
original 25-case benchmark or a claim of repeated live-web reliability.

The separately declared ordinary-task cases catch an inherited failure: new
Python code is labeled transform, and the candidate demands supplied material
that does not exist. It searches instead and gives no useful function. Baseline
handles the same native label locally. Candidate ordinary checks are 5/6 executed;
the mandatory stop leaves two ordinary cases and six original full-suite children
unexecuted. Preserve the failure and all prior evidence; no favorable retry or
grader change. See `SEARCH-CONVERSATION-GUARD-REPORT.md`.

Next proposed checkpoint: distinguish creating a self-contained artifact from
editing supplied material in the generic task contract. Cover new code, edits to
actual code and code requests requiring external facts. Retain missing-resource
lookup, small talk, input-reference integrity, source checks, original targets
and existing call limits. Review and freeze a separate candidate before inference.
**Images remains unreleased; G9 is open.** Live app/runtime are healthy and
unchanged. Research stays shelved; W1 waits for reliability and image release.

## Isolated Search creation contract — 11 October 2026

Frozen at `a7ea2d9b`. The exact prior code-failure replay and 111 offline checks
pass, but the native sequence stops before new-code tests. Baseline boundaries
are 20/24; candidate 12/13 executed. The stopped answer correctly searches and
declines the unknown user's personal fact with source-scoped attribution. The
frozen regex rejects “does not establish”; search/citation checks pass. Preserve
the original failure score and semantic observation separately. This is a grading
false negative, not a hallucinated meal or native proof of the code repair.

Sixty-seven later children remain unexecuted; full release qualification is open.
Review `SEARCH-ABSTENTION-GRADING-PLAN.md` for a grading-only correction with
retained audits and unsafe-answer negatives before re-freezing the same candidate
and an explicit retest order. No prompt wording workaround or favorable retry.
See `SEARCH-CREATION-CONTRACT-REPORT.md`. **Images stays unreleased; G9 remains
open.** Live app/runtime are healthy and unchanged; Research shelved, W1 unstarted.

## Equivalent-decline retest — 11 October 2026

Frozen at `0e456fdc`. The grading-only correction passes 176 offline checks and
a separate 183-answer audit; two lexical false negatives are corrected separately,
all 25 historical benchmark lexical scores unchanged, original scores/reports and
genuine failures retained. Both native code smokes pass and the candidate actually
uses `create_local` for transform/null-ref to return a working addition function.
Fresh personal-fact declines now pass with lookup/source-scoped attribution.

The broader run stops at an actual binding/completeness defect: “only that provided
comparison” is not recognized despite the visible complete comparison. Host
takes `clarify`; the model ignores its transmitted instruction and drops both
required weights. Do not classify this as a wording false negative or waive the
numeric requirements. Baseline boundaries are 19/24; candidate 21/22 executed;
58 later children, including six full suites, remain unexecuted.

Review `SEARCH-SCOPED-INPUT-PLAN.md` for bounded leading scope-modifier binding
with real supplied material, missing-source/ambiguity negatives and an early
comparison smoke. No prompt expansion, retry or release follows the stop.
H4: `SEARCH-ABSTENTION-RETEST-REPORT.md`. **Images remains held; G9 open**.
Live app/runtime remain healthy/unchanged; Research shelved and W1 unstarted.

## Scoped supplied-input checkpoint — 11 October 2026

Frozen at `b6326124`. The bounded leading only/just correction passes 200 offline
checks and all 49 synthetic candidate cases. The repeated actual native
transform/null-reference comparison now binds its real supplied material and
preserves both weights and their relation. New-code smokes remain useful and
local. These targeted successes do not qualify the full Search pipeline.

The first original matched full pair stops at baseline 24/25 and candidate
22/25. Two creative native plans include stray queries; the host rejects them
and wrongly falls back to lookup. A comprehensive answer reverses cited
champion/runner-up roles and omits required entries. Targeted review also finds
an unsupported currency supplied from memory and wrong time/granularity in
automatically passing answers. Higher lexical citation support and valid IDs
miss these semantic errors. Both mandatory and matched G9 gates fail; no
original scores, outputs or stop index are edited. Four later full children
remain unexecuted. See `SEARCH-SCOPED-INPUT-REPORT.md`.

Next proposed checkpoint: offline task/query consistency and evidence coverage
audit in `SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md`. Trace extraction, table roles,
requested properties and chronology using retained inputs before choosing one
bounded correction and another reviewed native trial. **Images remains held;
G9 is open.** Product/live app and runtime are healthy and unchanged. Research
remains shelved; W1 follows reliability and image release.

## Offline task/evidence audit — 11–12 October 2026

The three retained source selections reproduce exactly with their actual
calibrated token estimates. A complete 28-row table is fetched/chunked, but its
page's three slots are introductions. The data costs 463 tokens and fits the 524
remaining; replacing one caption keeps the current limits. Raw role tables also
lose structure during extraction or headers during chunking. These mechanics
do not excuse the actual reversed/unsupported claims.

Fresh query wording cannot repair discovery in the fixed replay, whose provider
batches ignore new queries. Comparison evidence is missing a requested property;
an unfetched name in a menu is not a supplied country/property assertion. Recent
results mix time/granularity; later fetched game chunks are omitted. The creative
task/query contradiction is reproduced offline, and blindly accepting a creative
label exposes another factual-intent gap. Original automatic scores remain
unchanged; there are no new native model results.

H4: `SEARCH-TASK-AND-EVIDENCE-AUDIT-REPORT.md`. Next proposed correction is
offline **relevant table admission within current limits** in
`SEARCH-TABLE-ADMISSION-PLAN.md`. Native reruns remain held until known mechanical
failures have concrete reviewed repairs. **Images remains held; G9 open**.
Live app/default/runtime remain unchanged; Research shelved and W1 unstarted.

Closeout: 29 diagnostic / 508 Python / 39 frontend / 473 browser tests pass, with
three existing browser skips. Preserve the initial corpus-absence hypothesis and
archival guard failures; 400 fresh generated test files are retained separately,
all prior 16,675 frozen and 17,369 committed evidence/eval files restored/verified.
Local and normally verified HTTPS health pass; no native inference or deployment.

Forty newly generated fake settings captures are archived too, for 440 fresh test
outputs retained in total; no tracked original is removed.

## Bounded table admission — 12 October 2026

The isolated selector repairs the retained omission offline: all original seven
columns / 28 rows / 23 positive entries now fit 5,337 of 5,502 tokens. All 22
source-bearing original turns replay exactly; only the failing list case changes.
33 admission and 16 native guard tests pass. No production selector is changed.

Jake approved up to three native pairs on the original question. The first pair
returns 23/23 entries in both arms because both planners choose the correct
qualifying event; the existing pipeline already supplies the full table, so the
new hook is a no-op. The candidate adds an unsupported “later won” relationship
to aggregate counts. Its automatic score passes, but manual claim review fails
and stops four later children. No native answer improvement or consistency is
demonstrated. Two planners / two answers / two warm loads; no retry or new prompt.

**Stop broad prompt continuation.** The concrete next proposal is host-only
structured extraction/chunking and missing-facet diagnostics, preserving original
roles/values, reproducing the actual omission branch and retaining all old scores.
See `SEARCH-TABLE-ADMISSION-REPORT.md` and `SEARCH-STRUCTURED-EVIDENCE-NEXT.md`.
No further inference or release is authorized by these proposals. 508 Python /
39 frontend / 473 browser tests pass; three existing browser skips remain.
Live app unchanged and healthy; Images held, G9 open, Research shelved, W1
unstarted and VoiceOver off the current list.

## Product delivery 1–4 — 12 October 2026

The earlier held/unstarted entries are historical. Jake approved the explicit
Images release exception and two fixed workflows. Images and Workflows are now
live, with additive migration, rollback, durable retry/cancel/reconnect and source
exports verified. Research remains shelved; broad reliability experiments end.

| Remaining item | Measured state | Next action |
| --- | --- | --- |
| Ordinary Search/grounding | Existing failures retained; no qualified repair | Keep source review and specific failure evidence; do not restart broad prompt trials |
| Meeting-pack quote context | Native adversarial case recasts a quoted instruction as an attendee assertion | Human source review required; preserve failure before any separately reviewed refinement |
| Model timestamp placement / task taxonomy | Budget action lacks its timestamp; a commitment also appears under Decisions | Original source timeline/speakers now displayed/exported directly; model formatting remains imperfect |
| Physical iPhone Images/workflows | Automated responsive/WebKit and live HTTPS inspection pass; requested device observation pending | Check generation/save/share/cancel on the actual phone without attributing an unperformed pass |
| Future workflow builder | Two fixed templates only | Use them and collect concrete failures; arbitrary steps, agents, external writes and scheduling need a reviewed scope |

See `PRODUCT-DELIVERY-REPORT.md` for exact calls, retained failures, test layers,
source preservation, migration verification and image storage measurements.
VoiceOver remains off the work list; its historical reported failure is retained.
# Image creation in chat — 12 October 2026

Requested by Jake during the WS-B continuation. Pending:

- Start image creation from the ordinary message composer, with a model-like image choice.
- Show generation progress, cancellation and generated images as turns in that same conversation.
- Keep save/share, retry identity and automatic seeds; repeat controls belong in optional advanced settings.
- Keep the gallery as a secondary place to browse saved images.

This replaces the current embedded Images workspace as the desired creation flow.
Review the durable chat-artifact/message schema and restoration behavior as a
separate implementation scope after the Workflow Studio engine checkpoint.
WS-B remains isolated; this entry does not claim the chat integration is built.

13 October: Jake authorized Claude's supplied `docs/next/chat-images/` plan after
WS-D, with its recommended defaults. The references and prototype are preserved;
`docs/CHAT-IMAGES-IMPLEMENTATION-REVIEW.md` records the implementation corrections.
Next checkpoints are CI-A (waiting/reasoning indicator), CI-B (saved image turns
in the composer), and CI-C (viewer, iteration and exports), each with review.
The chat integration remains pending; no merge or live publication is authorized.


## Studio and chat images — 14 October 2026

The earlier CI-A/B/C pending rows are historical. CI-C is implemented on the
isolated `codex/workflow-studio` branch with one full green 615-pass browser run,
three existing skips; main/live are unchanged. Viewer, lineage/refinement,
vision-gated upload, phone snap/dots and image exports pass automated checks.
Physical iPhone acceptance of this new chat-image flow remains pending.

The native workflow repair passes source binding, two complete factual drafts,
review reload, approval, edited saving and immutable raw outputs. It stops after
six calls when the cancellation timing probe misses its running window. A third
finished draft also broadens the materials claim, so fidelity remains inconsistent.
Streaming/RSS/driver cleanup capture defects are repaired. Event-triggered UI
cancellation passes offline against fake runtime, not native. Native cancellation
and recovery remain unverified; no seventh call or retry ran.

See `WORKFLOW-STUDIO-NATIVE-REPAIR-REPORT.md`. No broader Search/grounding pass,
Research restart, VoiceOver result, template/default change or main publication
is implied. Remaining knowledge/logic blocks and reference-pixel editing are
future scope; final main merge needs Jake's explicit okay.


## Native cancellation/recovery closeout — 14 October 2026

The missing native control pair now passes on the isolated Studio branch. Actual
first-text SSE clicks a visible enabled UI Cancel control; incomplete stream
closure, partial output, zero downstream execution and capacity release are
verified. One identical single-block run then completes, survives reload and
stays outside normal history. Two native calls only; no retry. One recovered
answer passes manual fact review, without excusing earlier unsupported claims.

The prior DOM-window failure remains preserved. An offline editing-precondition
failure is also retained; closing the prior Run view fixes it. See
`WORKFLOW-STUDIO-NATIVE-CONTROLS-REPORT.md`. UI/control verification is complete
for this checkpoint. Main/live are unchanged and merge/publication need Jake's
explicit okay. New-flow physical iPhone acceptance, general factual grounding,
future WS-E blocks and reference-pixel editing remain separate; VoiceOver stays
outside the current list and Research is shelved.

## Idle embedding handoff for images — 17 October 2026

Jake's physical phone check found the qualified chat plus idle Library embedding
model rejected by the image guard. He approved automatic release of configured
local embedding-only models at image preparation under the shared scheduler.
The verified patch covers chat and workflow images, preserves the qualified chat
and every existing image resource limit, and leaves Library data/config intact.
The next Library embedding request uses its normal adapter to load as needed.

Technical evidence passes: 721 Python / 126 frontend, 45 focused admission/handoff
tests and 14 targeted Chromium/WebKit browser checks. Publication and physical
phone acceptance are recorded in `IMAGE-MEMORY-HANDOFF-REPORT.md`. Other chat or
unknown models and unqualified contexts still require an explicit choice. Hermes
preparation remains preserved, with native execution awaiting the phone check.
