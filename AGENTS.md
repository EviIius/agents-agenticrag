# AGENTS.md — rules for coding agents in this repo

The plan is docs/SPEC.md. Read it before changing anything. Work phase by phase and stop for review
at the end of each phase with the report template in SPEC §H4.

Commands: `make setup` · `make dev` · `make check` (lint, types, unit tests, contrast, API types) ·
`make e2e` (Playwright vs fake runtime) · `make record-fixtures` (needs the real runtimes) · `make eval-web` (Phase 2+).

Hard rules:
- Stack and dependencies per SPEC §C1 only. Ask before adding any.
- Port 8787, bind 127.0.0.1, launchd label and Tailscale config never change.
- No extra modes/agents/model calls. Allowed model calls: answer, search planner, title,
  transcript clean-up (TRANSCRIPTION-SPEC §6).
- Transcription runs the external engine at WORKBENCH_TRANSCRIBE_HOME as a subprocess. No new packages.
- Never commit, log or screenshot a real recording, its filename or transcript text.
- No topic-specific prompt rules. Prompt edits require eval reports (SPEC §E12).
- Never send sampling params the user didn't set. Never infer capabilities from model names.
- Streaming = SSE events + rAF batching. Never poll. Never append notices to message content.
- UI: shadcn primitives + SPEC §G4 components + §G2 tokens only. Every state on /design.
- Never touch legacy data files except read-only import.
- "Done" requires evidence: tests, screenshots, reports.

User clarification (1 Oct 2026): exclude `llama3.3:70b-instruct-q4_K_M` from the new app's picker;
keep `llama3.3:70b-workbench-16k` and the other four local chat model variants. Apply this as a
stored user preference, never as a model-name capability heuristic.

User amendment (1 Oct 2026): use Ollama only, and continue Phase 1 and Phase 2 in
sequence without intermediate approval stops; retain checkpoint/phase evidence and
reports. LM Studio and generic OpenAI adapters are outside the current build scope.

User approval (1 Oct 2026): install Docker Desktop and run local SearXNG. Web search
must use free providers; no Brave API subscription or key is required. Verify real
parameter payloads and rename, pin/unpin, Markdown/JSON export and delete actions.

User amendment (1 Oct 2026): research and refine free web search integrations;
prefer Ollama Search if live evidence supports it, with free fallbacks. The user
saved its account key in the app. Continue to Phase 3 after Phase 2 is validated;
retain phase reports and evidence. Existing httpx adapters need no added SDK.

**User amendment — 3 October 2026 (deployment and storage):** Keep the engine’s public source under `transcribe/` in the Workbench repo and run it as a subprocess. Model weights, actual config, glossary and interpreter selection are ignored by Git; deployment copies them inside the installed app at `~/.local/share/workbench/app/transcribe` to avoid Documents access restrictions. Source recordings remain outside the repo. Uploaded audio is temporary by default: remove Workbench’s copy after durable transcription, preserving transcript text, raw text, timestamps and metadata. Failed/cancelled audio remains retryable until cleared. Settings offers opt-in audio retention and bulk clearing of inactive audio without deleting outputs or chats. This supersedes TRANSCRIPTION-SPEC decisions 1 and 3 and §12’s separate deployment folder. Jake authorized removal of existing uploaded audio copies.

Completed transcript outputs are kept even when unsent; seven-day housekeeping removes only unfinished unsent attachments.

**User amendment — 3 October 2026 (VoiceOver):** Jake reports VoiceOver did not work and asked to defer it for this build. Record the reported failure as an unresolved accessibility limitation; VoiceOver is no longer a release-blocking Phase 3 acceptance gate. Do not claim VoiceOver support passed. Other phase evidence and phone checks remain applicable.

**User authorization — 4 October 2026 (Phase 4):** Proceed with the reviewed roadmap corrections and Phase 4, stopping after 4B and 4D for review. Use Atelier, Chat controls and Web search as display labels at 4D; retain internal Workbench identifiers and compact numbered citations. CSS motion only, no new dependencies or model calls. Small motion is at most 200 ms; large surfaces at most 320 ms. Motion lives in `web/src/styles/motion.css`, checked by `scripts/check_motion.py`. C1's send timing and draft rollback are an explicit behavior change requiring rejection, chat-switch and new-draft tests. Future phases, `sqlite-vec`, embedding model installation and a second runtime are not authorized by this amendment.

**User authorization — 4 October 2026 (Phase 5):** Fix and verify the reported
Reduce motion › Always failure and missing app entrance using iPhone Mirroring,
then build `docs/next/PHASE-5-EVERYDAY-CHAT.md`. Presets, folders, document
attachments and automatic backups are in scope; this lifts the earlier non-goal
on folders. Stop for review after 5A, 5B and 5C. Document text and filenames follow
the recording privacy rule. No new packages or model calls. Later phases and
optional chat forking remain separately gated.

**User authorization — 4 October 2026 (4B review and 4C):** Jake asked Codex to verify the live Workbench and iPhone Mirroring, fix Markdown/JSON chat exports to use the cancellable format-selection/save/share flow already provided for recording outputs, then continue to 4C. Preparing a file may fetch the existing export endpoint; cancellation never starts a download or opens the native share sheet. Keep the chat export dialog available after save/share/download. Physical review observations by Codex must be labeled as such, not attributed to Jake. The 4D review stop remains in force.

**User clarification — 5 October 2026 (preset precedence):** Jake delegated the
conflict between exact preset-only sampling and the frozen model-default pipeline
to Codex ("Do what you think is best."). Preserve saved model defaults: a preset
overrides only the values it stores; unspecified values inherit the user's saved
model defaults, otherwise the runtime default. Empty presets add no sampling
values of their own. This refines P5-AC1; no provider/run pipeline change is needed.

**User acceptance and authorization — 5 October 2026 (5C and 6A):** Jake said
"5C is sufficient. Continue on." Record 5C as accepted without inventing individual
phone test results. Proceed to 6A transcript clean-up and glossary per
`docs/next/PHASE-6-TRANSCRIPTION-T2-AND-RUNTIMES.md`, stopping for review after 6A.
The optional second runtime, Library and Research remain separately gated. The
reported sidebar/other motion regression remains deferred at Jake's request.

**User clarification — 5 October 2026 (6A retry visibility):** Jake delegated the
conflict between hiding retry controls and the frozen T1 disabled-control behavior
to Codex ("Do what you think is best."). Preserve the visible disabled
"Transcribe again" entries after audio removal, with the re-upload explanation.
This refines the 6A plan's visibility note; unavailable audio still cannot retry.

**User acceptance — 5 October 2026 (6A):** Jake said “I confirmed it works.
Move on.” Close the 6A review stop, retaining source/evidence and the deferred
motion/accessibility limitations. The next phase's explicit gates remain: 6B
needs a named second runtime; 7-0 needs `sqlite-vec` approval and an embedding
model selection before installation or probe execution.

**User authorization — 5 October 2026 (7-0):** After Codex requested explicit
approval for `sqlite-vec` and the installed, runtime-reported embedding model
`qwen3-embedding:0.6b`, Jake said “go ahead.” Proceed with the Library probe
in `docs/next/PHASE-7-LIBRARY.md` §2 and stop for review after 7-0. Library
retrieval is in scope; this lifts the earlier RAG non-goal. Library text and
filenames follow the recording privacy rule. The future library answer prompt
in §5.3 requires frozen hashes and before/after evals for edits. Embedding calls
are distinct from chat model calls. Optional 6B is skipped; Ollama remains the
only runtime. Research is not authorized.

**User authorization — 5 October 2026 (7-0 interpreter remedy):** After the
extension-loading prerequisite failed, Jake said “go ahead” to preparing and
verifying an isolated uv-managed Python 3.14.7 environment while preserving
the current live runtime. Verify the approved extension and embedding probe
and existing app tests against the candidate. Keep the framework interpreter
and existing environments intact; do not alter the transcription interpreter.
An installed-app runtime switch is presented after candidate verification.

**7-0 environment closeout — 5 October 2026:** Both server environments now
use the verified uv-managed Python 3.14.7 build with extension-capable SQLite.
Their previous framework environments and installed manifests are preserved
under the private fallback path recorded in `artifacts/phase-7/candidate/promotion.json`.
The system/framework Python and transcription interpreter remain unchanged.
The full check/browser suites and actual installed/development probes passed.
Stop for 7-0 review before 7A. J7 eval targets remain unapproved until a later
explicit decision before 7B. Record the initial launchd activation failure and
successful recovery without claiming its cause was proven.

**User acceptance and authorization — 5 October 2026 (7-0 and 7A):** Jake said
“Not sure how to verify it, so I guess continue on”. Accept the technical 7-0
probe without inventing physical phone checks. Proceed to Phase 7A Library
storage, ingestion and Settings UI, stopping for review after 7A. Retrieval,
composer integration and the new answer prompt remain 7B work; J7 eval targets
still need approval before 7B. Ollama only; Research remains unauthorized.

**User acceptance and authorization — 6 October 2026 (7A and 7B):** Jake asked
to continue to 7B, reviewed the proposed J7 targets, then said “go ahead then”.
Proceed with retrieval, composer integration, cited answers and the synthetic
eval harness. J7 targets in Phase 7 §8 are approved as written. Stop for review
after 7B; missed targets keep the phase open. Ollama remains the only runtime,
and Research remains unauthorized. Do not use the user's real Library files
for logs, screenshots, fixtures or eval evidence.

**User authorization — 6 October 2026 (7B prompt refinement):** After the
version-one eval missed per-fact citation placement, Jake said “Go ahead and”
in response to the proposed generic refinement and before/after retest. Apply
the documented per-sentence/per-row citation and explicit-stated-facts
reinforcement, retain the original baseline and unchanged corpus/cases, and
rerun the full eval without lowering J7 targets. Finish 7B regression gates and
deployment if they pass, then stop for 7B review. Research remains unauthorized.

**User authorization — 6 October 2026 (7B table citations and web variance):**
Jake said “Approve the recommendations”. Apply the proposed generic Citation
column refinement and continue in-scope citation wording refinements with retained
before/after reports, unchanged corpus/cases and the 100% J7 target. Accept the
documented G9 web replay variance for this checkpoint: all 25 cases pass with no
case regressions, lexical support 0.8823817 vs 0.8852879, median TTFT 4.467 vs
3.968 seconds and p90 5.987 vs 4.786 seconds. Preserve both reports and all release
thresholds; this is a specific accepted variance, not a general G9 exemption.
Finish the full regression gates before 7B deployment, then stop for review.
Research remains unauthorized.

**User acceptance — 6 October 2026 (7B):** Jake reported “The citation is correct
and information too.” Record Library answer/citation verification on his iPhone
and close the 7B review stop without inventing other phone checklist results.
Defer the recording attachment dropdown layout issue for later, as requested;
track it in `docs/DEFERRED-FIXES.md`. Keep private filenames/text and the supplied
phone screenshots out of repo evidence. Research remains unauthorized.

**User authorization — 6 October 2026 (8-0 evaluation only):** After Codex
recommended starting only the isolated Research evaluation early, Jake said
“Then go ahead and start”. Waive the two-week / 17 October calendar hold for
checkpoint 8-0 only. Prepare 15 multi-part cases and recorded public web fixtures,
measure the existing single-shot Search baseline and fresh live web release
eval, and run the 40-prompt native-tool probe on installed runtime-reported
tool-capable models. These isolated evaluation calls are authorized; production
model-call rules, code, data and deployment remain unchanged. Retain all failures
and stop with the gate report before 8A. Do not claim two weeks of daily use.
The Research product spec and proposed release targets still need Jake’s review
after the gate results; no agent loop, new dependency or product UI is authorized.

**User authorization — 6 October 2026 (8A isolated backend):** After reviewing
8-0 and Codex's recommendation, Jake said “Then do so”. Approve the Research
product specification and §9 targets with these qualifications: deterministically
regrade equivalent baseline wording using retained answers before freezing the
comparison; preserve genuine omissions and contradictions, original reports and
corpus. Keep ≥80% factual completeness, ≥15 percentage-point gain, native validity
≥95%, manual citation/claim review and all host budgets. Waive the remaining
calendar hold for isolated 8A development only; this does not assert two weeks of
daily use. Start with the tested daily 32K Qwen, qualifying by measured metadata
rather than model-name inference; GPT-OSS's failed probe is not qualified.
Research-only native steps (maximum eight) plus one answer are authorized in
the isolated backend. Tools are web_search, read_page and finish; no added
dependency, routing, supervisors, sub-agents or other tools. Freeze the v1
Research prompt; edits require before/after eval evidence. Keep the live app on
7B. Stop for 8A review before 8B UI or deployment.

**User authorization — 6 October 2026 (8A evidence refinement):** Jake asked to
continue the isolated prototype, fix evidence gathering and unsupported answers,
and determine whether it can exceed the required threshold for 8B. Refine the
generic Research planning/evidence behavior, with retained v1 before/after evals
and frozen prompt hashes. Preserve ordinary Search/Library prompts and payloads,
all original cases, corpus and grading, ≥13/15 complete cases, citation/support,
validity, injection and budget targets. No topic-specific rules, new packages,
extra calls, models or tools. Keep live 7B installed. Retain every trial; assess
semantic support separately from regex matches. Stop with the feasibility/8A
review before 8B UI or deployment; the request does not waive failed gates.

**User authorization — 6 October 2026 (8A consistency):** Jake asked to do what
is required to make 13/15 or 15/15 consistent. Continue isolated generic coverage
and support experiments, preserving all trials, the original benchmark, baseline
and thresholds. Predeclare repeated full runs of a frozen candidate and review
claim support separately; one favorable run does not qualify. Any additional
query-aware corpus must be separate and evaluate Search and Research on identical
evidence. No new dependencies, tools, models or calls; live 7B and the 8A review
stop remain unchanged.

**User clarification — 7 October 2026 (model research):** Jake requested more
model options and clearer picker categorization, then said to document Qwen 3.8
for now, research other candidates and continue the existing 8A scope. Model
research and a picker proposal are authorized; new model downloads, runtime
upgrades, default switches and picker deployment are not. Preserve the isolated
8A limits, accepted live 7B and the review stop before 8B.

**User authorization — 7 October 2026 (Research shelved; deferred polish):** Jake
asked to shelve Research, analyze and fix deferred issues, and provide next steps.
Stop isolated Research experiments; preserve source, failed trials and benchmark
history on their existing commits. No 8B or Research deployment. The production
polish branch starts from the accepted 7B build. Repair recording-menu safe-area
and scrolling behavior, diagnose mobile motion and refine model-picker clarity
using runtime-reported metadata only. No model downloads, runtime upgrades, new
packages, prompts, sampling changes or routing. Jake removed VoiceOver from the
current work list; preserve its historical reported failure without claiming a
pass, and keep ordinary keyboard/focus/label semantics.

**Source closeout — 8 October 2026:** While continuing Jake's next steps, main
was consolidated to the tested production application/tooling tree from
`codex/deferred-polish`; the unreleased Research runtime, schema additions and
wiring are absent from that tree. Research source remains on `7737046` /
`codex/phase-8a-research`, with failed reports and frozen inputs preserved. No
Research deployment or new experiment is authorized. The ordinary model
comparison proposal is `docs/MODEL-COMPARISON-PLAN.md`; named download and
evaluation approval remains separate.

**User authorization — 8 October 2026 (everyday model comparison):** Jake
answered "Approved" to the named Qwen3.8 comparison question. Download
`qwen3.8:27b-q4_K_M`, prepare an isolated 32K profile and execute
`docs/MODEL-COMPARISON-PLAN.md`, including the proposed everyday 18/20 gate and
unchanged E12/E13/J7 targets. Stop on smoke protocol/context/format/support/
injection failure and preserve all outcomes. No Research restart, other models,
runtime upgrade, new dependency, prompt/sampling change, default switch or
deployment is authorized. The existing runtime and production data remain.

**Comparison closeout — 8 October 2026:** The named candidate and isolated 32K
profile are installed; four ordered smokes and all three matched full pairs are
complete. The candidate fails qualification: mandatory Web lookup/citation
checks fail in every run, and source-only everyday grounding remains incomplete.
Original Library citation failures include a documented post-period parser
limitation; do not misrepresent those as fabricated required facts or silently
regrade them. Baseline weaknesses, all setup failures, answers and manual reviews
are retained in `artifacts/model-comparison/` and the H4 report at
`docs/MODEL-COMPARISON-REPORT.md`. Production equals the stable `f87db46` tree,
Ollama remains 0.35.0, and no default switch, deployment or Research restart took
place. Repository checks passed. Stop for comparison review; further prompt,
grader, profile, download or runtime experiments require their own reviewed scope.

**User authorization — 9 October 2026 (reliability repair):** After reviewing
the model comparison failures, Jake asked Codex to make it reliable and figure
out the failures. Proceed with `docs/RELIABILITY-PLAN.md`: separate citation
grader repair and generic planner/source-only/untrusted-record prompt repairs,
using retained before/after evaluations on the already-installed profiles.
Preserve original reports, frozen cases/corpus and release targets. No topic
rules, new models, runtime/dependency/sampling/default changes, routing, extra
production calls or Research restart. Keep the stable installed app during
experiments and stop with H4 results; failed gates prevent promotion/deployment.

**Reliability checkpoint — 9 October 2026:** Seven isolated generic framing/
prompt trials and two exact-provenance contracts are retained under
`artifacts/reliability/`. Local post-period Library grading is repaired with
negative placement tests and separate original-answer regrades; candidate's
three original required-fact citation scores become 100%, without altering
raw answers or excusing genuine baseline omissions. The latest full pilot
improves everyday scores to current-model 19/20 and candidate 20/20, but both
fail manual Web grounding and extra-claim review. Host-owned IDs achieve 8/8
structural validity on each profile while failing identity/context/coverage.
No candidate is qualified. Original cases, thresholds, reports and frozen
inputs remain intact; production source and installed affected modules remain
the stable f87db46 tree. Research remains shelved. H4 evidence is
`docs/RELIABILITY-REPORT.md`; the bounded answer-contract proposal is
`docs/RELIABILITY-NEXT-CHECKPOINT.md`. Stop for review before product integration
or further experiments; no default switch or deployment occurred.


**User authorization — 9 October 2026 (evidence contract continuation):** Jake
asked to continue the proposed next reliability checkpoint: preserve source fields
and context, validate references, and explicitly decline unsupported information.
Build and evaluate the bounded evidence contract in isolation, preserving earlier
trials, corpus and targets. Research stays shelved; no new model, dependency,
runtime, default or deployment is authorized. Review the output/streaming tradeoff
before product integration. Also correct the reported misleading attachment
context warning and honor user-set output limits in its estimate; keep the
existing reserve rule and provider sampling unchanged.

**Evidence contract checkpoint — 9 October 2026:** The isolated source/context
catalogue and single-call ID-selection contract are implemented, but the first
full baseline pilot fails: Web 5/25 full cases, Library 22/28 required-fact/citation
final turns and excessive validated-answer latency. Ordinary unchanged-pipeline
checks score 16/20 by their declared rubrics. Do not qualify or deploy it. All
v4-v10 sources, failures and original inputs are retained; v6-v10 are host-only
replays with no new inference. The latest renderer preserves literal values and
neutralizes source markup/links in actual Chromium/WebKit chat checks. Relevance,
completeness, table citation parsing and the quotation cap remain unresolved.
The context-warning correction honors user output overrides/defaults in its
estimate, with no sampling or provider change; it is tested but not deployed.
The full browser run retains one WebKit auto-scroll test failure; visible center
scrolling fixes that check in the focused rerun, without changing product copy
behavior. H4 evidence is `docs/EVIDENCE-CONTRACT-REPORT.md`. Stop for review before
another inference experiment or product integration; Research remains shelved.

**User continuation — 9 October 2026 (isolated evidence fields):** Jake said
“continue going forward” after the evidence contract report and proposed next
scope. Proceed with the bounded checkpoint in docs/EVIDENCE-FIELDS-PLAN.md:
repair table citation evaluation with separate regrades, select original table
columns with retained subject/property/context, separate Web prose/data and
Library excerpt limits, compact duplicated evidence input and measure original
retrieval coverage. Freeze inputs before a baseline pilot; retain all failures
and stop for review. No Research restart, product integration/deployment, default
switch, new models/packages/runtime, sampling changes or extra model calls.

**Evidence fields closeout — 9 October 2026:** Table-row citation evaluation is
repaired with separate regrades; original reports/cases remain unchanged. v11
separates Web prose/data and Library excerpt limits and offers original column
selection with compact input. Its native baseline trial fails protocol: 15
rejected, one unsupported, one interrupted grounded stream; no full Web report,
Library trial, candidate or repeat. Host-only old Library selections score 27/28
required facts/citations, not a new model or semantic pass. v12's stricter schema
and ordinal/subject guard are prepared and tested but unexecuted. Native grammar
compatibility, immediate protocol stopping, authenticated host-context costs,
retrieval coverage, relevance/completeness, ordinary grounding and latency remain.
Full make check passes (434 Python / 39 frontend); production is unchanged, no
deployment or Research. H4: docs/EVIDENCE-FIELDS-REPORT.md. Stop for review before
another inference trial or product integration.


**User continuation — 10 October 2026 (native evidence and image research):** Jake
asked to continue the refinement and research image generation models for the Mac
mini. Proceed with the isolated checkpoint in docs/EVIDENCE-NATIVE-PLAN.md: fix
authenticated host-context accounting, validate the prospective strict schema
with an original-case smoke, and stop immediately on protocol or semantic failure.
Preserve all prior outcomes, original inputs and thresholds. Research image
models and Mac implementations only; no image weights, application/runtime
installation, package addition or image integration is authorized. Research stays
shelved; no production prompt/default change or deployment. Stop with an H4 report.


**Native evidence closeout — 10 October 2026:** v13 fixes authenticated host-note
quotation accounting; unchanged saved selections recover the 23-row budget
rejection, a host-only diagnostic. The single original-case native smoke fails
and stops automatically: missing identity columns and repeated IDs, no factual
output, full report, remainder, Library, candidate or retry. Ollama 0.35.0's
pinned llama.cpp schema builder gives items precedence over prefixItems; the
positional schema was incompatible. A named-object v14 remedy is prepared and
host-tested but unexecuted natively. 452 Python / 39 frontend checks pass; all
7,296 original inputs and frozen executed source remain intact. Installed source
matches stable f87db46 and remains healthy; no deployment or Research. Image
model options are researched in docs/IMAGE-MODEL-OPTIONS.md, recommending a named
Draw Things / FLUX.2 klein 4B trial separately; no image download/install or
integration occurred. H4: docs/EVIDENCE-NATIVE-REPORT.md. Stop for review before
further inference, runtime/model installation or product integration.

**User continuation — 10 October 2026 (named evidence fields):** After the
remaining-work review, Jake said “Go ahead with what you think is best.” Proceed
with `docs/EVIDENCE-OBJECT-PLAN.md`: validate the prepared v14 named-object schema
in isolation, using one original-case smoke and immediate protocol/semantic
stopping before gated original Web/Library stages. Preserve all failures, original
inputs and targets. Assess the independently tested frontend context-warning
correction for a separate release. Research stays shelved; no image installation,
new models/packages/runtime, default switch or unqualified production answer
change. Stop with an H4 checkpoint report before further inference experiments.

**Named evidence closeout — 10 October 2026:** One original-case v14 native smoke
ran and failed; no remainder, Library, candidate or retry followed. Named IDs and
identity keys satisfy the supplied schema, but its identity-only rows violate
the host's minimum-field guard; a separate long prose selection exceeds its
quotation allowance. This is an under-constrained contract, not proof that the
runtime ignored its named-object grammar. No factual output or answer integration
occurred. The next proposed repair is native/host admissibility parity, unexecuted.
All 7,296 original inputs, 194 prior source files, six prospective files and 204
executed files are unchanged. Full checks pass (458 Python / 39 frontend); the
WebKit scrolling failure is retained, fixed with stronger visibility/settling
preconditions, and passed ten repeated checks plus one complete browser rerun
(463 passed, three existing skips). The independently approved context-warning
frontend was published with private static/database fallback, healthy local/HTTPS
checks and unchanged 81-file stable server, service identity and Tailscale route.
No runtime restart, prompt/sampling/default change, image installation or Research.
No physical phone pass is invented. H4: `docs/EVIDENCE-OBJECT-REPORT.md`. Stop for
review before another inference experiment or unqualified answer integration.

**User authorization — 10 October 2026 (proposed sequence, checkpoint R):** Jake
approved `docs/APP-DIRECTION-AND-WORKFLOWS.md` and prioritized its recommended
sequence. Begin with the bounded generic native/host admissibility repair in
`docs/EVIDENCE-BUNDLES-PLAN.md`: synthetic tests, one original-case daily-profile
smoke, immediate protocol/semantic stopping, then conditional original Web/Library
and predeclared consistency checks. Preserve earlier trials, inputs and targets.
One candidate only in this checkpoint; failure ends inference and prompts a
simpler-design recommendation. Stop with H4 evidence before product integration
or image installation. Future image-engine/dependency selection and workflows
need their concrete reviewed scopes; no new model/package/runtime/sampling/default
change or Research restart is part of checkpoint R.

**Checkpoint R closeout — 10 October 2026:** The bounded v15 candidate passes
the first original-case smoke (5.37-second validated-answer TTFT), then stops
automatically when individually legal excerpts exceed their combined source
quotation allowance. It is not qualified. No retry, full Web score, Library,
consistency run or new native contract follows. End this selector design; a
simpler existing-source presentation is proposed, not implemented. Checks pass:
480 Python, 39 frontend and 463 browser tests, three existing browser skips.
All 7,296 original inputs, 204 prior frozen files and 214 current frozen files
remain intact; original tracked evidence is restored with new results retained
separately. Installed 81-file server and 422-file static tree are unchanged;
local and normally verified Tailscale HTTPS health checks pass, Ollama remains
0.35.0, and no deployment or Research restart occurred. H4 report:
`docs/EVIDENCE-BUNDLES-REPORT.md`. Stop for review. The concrete next image-worker
scope, MFLUX/FLUX.2 klein 4B in `docs/IMAGE-TRIAL-PLAN.md`, is prepared but no
image dependencies/weights are installed; named-dependency approval remains
required before that installation.

**User authorization — 10 October 2026 (image trial I0):** Jake said “go mahead”
after the checkpoint R report and concrete MFLUX/FLUX.2 klein 4B recommendation.
Accept R's closeout without qualifying the failed grounding candidate. Proceed
with `docs/IMAGE-TRIAL-PLAN.md`: the named MFLUX dependency set and one model are
approved in an isolated image-worker environment. Pin the published package,
dependency lock and model revision; preserve the application/transcription
interpreters, Ollama, service, ports and production data. Use the declared
synthetic prompts/settings, retain all outputs/failures, measure actual resource
use/progress/cancellation/recovery, and stop with the I0 H4 report for quality
and latency review before I1 integration. No Research restart, production image
UI, additional model, chat prompt/default change or workflow agents are approved.


**Image trial I0 closeout — 10 October 2026:** The approved isolated
MFLUX 0.22.0 / FLUX.2 klein 4B trial completes twelve 1024-square generations
and one reference edit. Actual synchronized progress, initialization/generation
cancellation with process reaping and next-job recovery pass. Preserve the first
wrapper quantization-inspection failure and exact nine-file source snapshot;
its generic Module-leaf correction changes no model, precision, prompt or seed.
All outputs remain native and retained. Codex flags three generation samples;
Jake's quality/latency review is pending. Median generation is 9.77 seconds;
comfortable mixed-model memory is not qualified because first-image swap grows
and the chat model expires before the resident batch ends. Proposed bounded-cache
qualification and I1 jobs/Images are in `docs/IMAGE-INTEGRATION-PLAN.md`, not run.
Checks pass: 480 Python, 39 frontend, 12 isolated controls and 463 browser tests,
three existing browser skips. All 505 installed app files, 7,296 original inputs,
204/214 earlier frozen files, both nine-file image attempts and 5,260 earlier
tracked artifacts verify preserved. Local/normally verified HTTPS health pass;
Ollama remains 0.35.0 and no deployment/service restart occurred. H4 report:
`docs/IMAGE-TRIAL-REPORT.md`. Stop for I0 review before memory-policy inference
or I1 product integration. Research remains shelved; workflows/agents remain
later reviewed scope and no factual-answer candidate is qualified by this trial.


**User acceptance and authorization — 10 October 2026 (I0 and I1-0):** Jake said
“Go ahead” after the committed I0 results, sample gallery, quality/memory caveats
and recommended sequence. Accept I0 for proceeding without inventing per-image
observations or a physical phone result. Execute the separately frozen bounded
cache qualification in `docs/IMAGE-MEMORY-PLAN.md`, using the existing pinned
engine/environment/weights, original photograph/text prompts and seeds, intended
daily chat residency checks, native cancellation/recovery and before/after chat.
Keep I0 and all earlier evidence intact. Stop on declared resource/residency/
latency/failure guards; no fallback, explicit model unload, keep-alive override,
new package/model, runtime/default/sampling/prompt change or Research restart.
Retain H4 evidence and stop after I1-0 review before I1 production jobs/Images.
Ordered workflows/agents remain later reviewed scope.

**Image memory I1-0 closeout — 10 October 2026:** The single frozen 1 GiB
unused-allocation cache policy passes unchanged before/after READY probes,
initialization/denoising cancellation with reaping and four-image recovery.
Daily chat residency remains reported before/after every image; 45 health/swap/
activity samples show no positive stage-relative swap growth. Median generation
is 9.47 seconds; all four decoded outputs match I0 exactly. Live allocation still
peaks at 18.66 GB; neither a global memory cap nor concurrent full-context chat
is qualified. Preserve the failed first read-only browser assertion and its
separately frozen after-batch correction; no physical iPhone pass or normal
Chromium startup during generation is claimed. Checks pass: 480 Python, 39
frontend, 26 isolated controls/guards and 463 browser tests, three existing skips.
All 505 installed app files, 5,458 earlier tracked artifacts, 7,296 original inputs,
204/214 grounding files, both nine-file I0 attempts, 17 current frozen files and
18 model files verify preserved; the image interpreter and 56 package versions
are unchanged. Local and normally verified HTTPS health pass; Ollama stays 0.35.0.
No deployment/service restart occurs. H4 report: `docs/IMAGE-MEMORY-REPORT.md`.
Stop for I1-0 review before the proposed I1-A/B durable jobs and Images integration.

**User acceptance and authorization — 10 October 2026 (I1 jobs and Images):**
Jake asked to continue and verify storage used by generated images and revisions.
Accept the committed I1-0 resource checkpoint for proceeding, without inventing
phone or general image-quality acceptance. Implement I1-A/B from
`docs/IMAGE-INTEGRATION-PLAN.md` using the existing pinned worker environment and
weights: durable jobs, native admission, SSE, Images, storage/deletion and output
backup/restore. No new dependency/model download, prompt rewriting, hidden model
eviction, Research or workflow calls. Keep prior frozen trials intact. Generation
versions are complete outputs; reference editing remains gated by its file rules.
Retain native cancellation/recovery and full regression evidence, then stop for
I1 review before W1.
Research remains shelved; workflow/agent calls remain separately reviewed scope.

**I1 candidate review stop — 11 October 2026:** Durable image jobs, shared native
admission, Images/job visibility, storage removal and image-aware backup/restore
are implemented on `codex/images-jobs-i1`. The corrected isolated native sequence
passes; initial shutdown, harness and overlapping-eval failures remain retained.
Checks pass: 508 Python, 39 frontend and one complete Chromium/WebKit run with
473 passed / three existing skips. All prior artifact bytes, installed source,
image environment and weights are preserved. G9 remains failed: the accepted
frozen Search replay is 25/25; the current 24/25 run skips the injection fixture
and lowers lexical citation support. No application deployment, service restart
or merge to main occurred. Stop with `docs/IMAGES-I1-REPORT.md` for I1 review;
do not begin W1, reference editing or release around the failed gate. Any further
Search comparison/refinement must retain this failure, original corpus/thresholds
and frozen prompts. Research remains shelved.

**I1 matched Search diagnosis closeout — 11 October 2026:** Jake asked to
“continue going” after the I1 report recommended an isolated matched comparison.
The declaration/harness/manifest was frozen at `897056f` before inference. All six
focused planner tests and both full real-runtime replay runs are retained. Accepted
`ba75e28` and Images `7383347` both score 23/25 and fail the same summary/unknown-
subject cases. All six focused requests are identical; Search source is unchanged.
The historical summary pass used plan fallback, whose original error is unknown.
This diagnoses an existing failure, not a G9 waiver: injection is unexercised and
candidate lexical support is lower. No prompt/product edit, deployment, service
restart, W1 call or Research restart occurred. Preserve all 6,134 earlier evidence
files. Stop with `docs/IMAGES-SEARCH-DIAGNOSIS-REPORT.md`; the concrete bounded
prompt/eval proposal in `docs/SEARCH-REPAIR-PLAN.md` remains separately reviewed.

**User authorization — 11 October 2026 (bounded Search repair):** Jake said
“continue going” after the matched diagnosis and concrete repair proposal.
Execute the single generic prompt candidate and frozen before/after scope in
`docs/SEARCH-REPAIR-PLAN.md` / `docs/SEARCH-REPAIR-EXECUTION.md`. Keep production
prompts unchanged until qualification. Preserve the original 25 cases/corpus/
grading, all failed trials, thresholds, empty answer sampling and existing utility
parameters. Freeze the separate 24 synthetic cases, eight held out, before any
candidate inference. Stop at a mandatory candidate/support/G9 failure and retain
unexecuted calls explicitly. No new dependency/model/runtime/default, added call,
automatic retry, topic rule, Research restart, image invocation or W1 work.
Stop with the H4 result before release or a larger deterministic repair design.

**Bounded Search trial closeout — 11 October 2026:** The single candidate inputs
were frozen at `0bd3349`. The first harness incorrectly compared the production
request-specific planner schema with the static schema, preventing all planner
native calls and forcing fallback. Preserve all 29 child reports, 29 real answer
calls, wire bodies and the original automatic stop record. Raw scores 12/24
baseline and 4/5 executed candidate do not qualify planner behavior. Candidate
translation cites an unrelated source; four external-resource answers are
supported under forced fallback. Nineteen candidate cases (including all eight
held out) and six original full runs remain unexecuted. No original grader/input
or failed report was changed. A retained harness-only patch passes offline
schema/failure-detection checks without further inference; the original harness
stays frozen. All 7,471 frozen inputs and 6,285 prior evidence files are preserved;
production is healthy, Ollama remains 0.35.0 and Images is not released. No
production prompt edit, deployment/restart, W1 or Research call occurred. Stop
with `docs/SEARCH-REPAIR-REPORT.md`; next review is a fresh frozen retest of the
same candidate with the corrected harness, not a product redesign inferred from
invalid planner measurements.

**User authorization — 11 October 2026 (corrected Search retest):** Jake said
“continue going” after the invalid-trial H4 report and concrete corrected-harness
proposal. Execute `docs/SEARCH-REPAIR-RETEST-EXECUTION.md` in a new retained output
directory. Apply only the reviewed harness schema-observation/error-recording/
protocol correction, validate it offline, and freeze it before inference. Keep
the same candidate, 24 cases/eight designated held out, fixtures, original 25-case
benchmark/grading, 54-child order, runtime/context/sampling and release targets.
Preserve the first invalid trial and all prior bytes. Stop at protocol/host,
mandatory candidate/support or G9 failure; do not retry, broaden prompts or
silently regrade. Production stays unchanged, Images unreleased, Research shelved
and W1 unstarted. Stop with H4 before a release or larger repair design.

**Corrected Search retest closeout — 11 October 2026:** Frozen at `3507d1d` before
inference; all 25 children have verified native planner and answer requests with
unchanged schema/sampling. Baseline is 19/24 on the separate boundary suite; the
first candidate case fails (0/1 executed), returning transform/empty queries for
an absent page, skipping retrieval and missing the required facts. No fallback
or harness failure causes that candidate outcome. Stop preserved immediately;
23 candidate cases and six original full runs remain unexecuted. First invalid
trial, all 13,947 frozen inputs and 6,564 prior evidence files remain intact.
Production is healthy and unchanged, Ollama remains 0.35.0; no release/restart,
extra experiment, W1 or Research call occurred. H4 is
`docs/SEARCH-REPAIR-RETEST-REPORT.md`. Its explicit erratum corrects the earlier
report's abstention-grading prose without modifying original reports or scores.
Stop for review before implementing or evaluating the proposed supplied-input
contract in `docs/SEARCH-INPUT-CONTRACT-PLAN.md`; no further prompt-only trials
or Images deployment are authorized by this closeout.

**User authorization — 11 October 2026 (isolated Search input contract):** Jake
said “go ahead” after the corrected retest report and the proposal in
`docs/SEARCH-INPUT-CONTRACT-PLAN.md`. Implement and test that supplied-material
inventory/reference/schema contract in isolation, retaining ordinary production
source and deployment. Use the existing one planner and one answer, existing
runtime/context/sampling, original 25-case benchmark and 24 boundaries. Freeze
one candidate, any separate supplemental ambiguity corpus and the complete order
before inference. Keep all earlier failed trials and thresholds; stop on protocol,
mandatory candidate/support or G9 failure, with H4 and unexecuted calls recorded.
No new package/model/runtime/default, repair call, retry, topic rule, Research,
Images invocation/release or W1 work is authorized. Reference validation is not
a general semantic guarantee; explicitly test missing material, prior refusals,
literal transformations, context dropping and attachment/recording protection.

**Search input-contract closeout — 11 October 2026:** The isolated candidate and
72-child declaration were frozen at `4ac3100`. All 29 executed children have
verified native planner/answer wire/events. Fresh baseline is 20/24 on the separate
boundaries; candidate is 4/5 executed. Four absent-resource summaries now perform
native lookup with supported facts/citations; these successes do not exercise
host rejection of an invalid transformation. The literal translation then emits
transform/input_ref=null despite an actual supplied literal catalog/schema ID.
Host rejection falls back to Search and the answer cites unrelated evidence;
search decision/manual support fail. Mandatory stop preserved; 43 later children
(including all supplemental and original full runs) remain unexecuted. Twenty-five
offline tests and two-arm rejecting-transport capture checks passed before freeze.
All 14,237 frozen files and 6,853 prior committed evidence files remain intact.
Production is healthy/unchanged and Ollama stays 0.35.0. No release/restart, extra
call, Research, image invocation or W1 action occurred. Stop with H4 at
`docs/SEARCH-INPUT-CONTRACT-REPORT.md`. Review its proposed host fallback-policy
correction before another candidate; do not waive original targets or promote
this four-case improvement as qualification.
