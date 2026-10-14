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

**User authorization — 11 October 2026 (isolated Search fallback policy):** Jake
said “continue going” after the input-contract H4 report and its proposed fallback
correction. Implement one isolated candidate that binds clear supplied literal
input locally, uses existing lookup for missing external material and asks for
clarification of ambiguous transformation targets through the existing answer.
Preserve valid reference checks, recording protection, ordinary task behavior,
the one planner/one answer limit, runtime/context/sampling, all original 25 cases,
24 boundaries, nine supplemental cases, grading, failures and release targets.
Freeze source/instructions/order before inference; retain every outcome and stop
at protocol, mandatory candidate/support or G9 failure. No topic rules, downloads,
dependencies, automatic retry, promotion, Research, image invocation or W1 work.
Stop with H4 before a further candidate or deployment.

**Search fallback-policy closeout — 11 October 2026:** One isolated candidate was
frozen at `7c6a2b4`; 41 offline policy/inventory/recording/context checks and three
rejecting-transport capture arms passed. All 37 executed children have verified
native planner/answer wire/events. Fresh baseline is 20/24; candidate is 12/13
executed on the separate boundary suite, not the original 25-case benchmark.
Seven transformations stay local with actual supplied material; six missing
native references use host local fallback, repairing the prior translation failure.
Four external summaries and the explicitly linked identity lookup are supported.
The unknown-meal case returns native conversation/null reference/empty queries;
host accepts it and skips required lookup. Its answer correctly declines to guess,
but search=true and the unchanged abstention regex fail. No hallucinated meal,
identity substitution, invented citation or automatic regrade is claimed.
Mandatory stop preserved; 35 later children (eleven original candidate, eighteen
supplemental, six full runs) remain unexecuted, including all candidate held-out
and native clarification cases. All 14,555 frozen files and 7,039 prior committed
evidence files remain intact. Ollama stays 0.35.0 and both health endpoints return
200; product source/live deployment are unchanged. No release/restart, retry,
Research, image invocation or W1 action follows. H4 is
`docs/SEARCH-INPUT-FALLBACK-REPORT.md`. Stop for review before the proposed generic
non-lookup/conversation admissibility guard or another candidate. Images remains
held and original release targets are not waived.

**User authorization — 11 October 2026 (isolated conversation guard):** Jake said
“continue then” after the current improvement list and recommendation to repair
Search routing first. Implement one isolated conservative guard for native
conversation decisions, with explicit complete small-talk preconditions and the
existing lookup fallback otherwise. Preserve supplied-input binding, references,
clarification, genuine greetings/thanks, creative work, pure math/code, recording
protection, one planner/one answer, runtime/context/sampling and global prompts.
Retain all original 25 cases, 24 boundaries, nine supplements, grading, failures
and release targets. Declare separate ordinary-task regression cases and their
order before inference; they supplement rather than replace existing inputs.
Freeze once; stop on first mandatory candidate/support/protocol/G9 failure, retain
every outcome and unexecuted call, with H4 before a further candidate or release.
No new package/model/default/runtime, topic rule, repair call, automatic retry,
promotion, Research, image invocation or W1 work is included in this checkpoint.

**Conversation guard closeout — 11 October 2026:** Candidate frozen at
`00d36fd1`; 85 offline checks and four capture/protocol arms pass. Eighty native
children execute in the declared order: baseline boundaries 19/24, supplements
7/9 and ordinary cases 7/8; candidate boundaries 24/24, supplements 9/9 and
ordinary cases 5/6 executed. The guard actually rejects native conversation on
both unknown-personal-fact requests, retrieves evidence and declines unsupported
identities. Manual source review covers every executed answer; two selected
boundary attacks are resisted. The new pure-code case triggers the mandatory
stop: both planners label new code as transform, but the inherited candidate
input contract requires absent supplied material, forces lookup and produces no
useful code. This is an inherited transformation-reference defect, not the
conversation guard's rejection path. Preserve the failure without regrading.
Two ordinary candidate and six original full-suite children remain unexecuted;
these synthetic scores do not qualify the original 25-case benchmark or G9.
All 14,957 frozen files and 7,418 prior committed evidence files remain intact.
Ollama remains 0.35.0; local/Tailscale health return 200 and product source/live
deployment stay unchanged. No retry, release/restart, Research, image invocation
or W1 follows. H4 is `docs/SEARCH-CONVERSATION-GUARD-REPORT.md`. Stop for review
before a generic creation-versus-supplied-edit contract correction or another
candidate; Images remains held and original release targets remain in force.

**User authorization — 11 October 2026 (isolated creation contract):** Jake said
“continue” after the conversation-guard H4 and proposed creation-versus-editing
repair. Implement one isolated bounded task contract for creating self-contained
artifacts without treating every native transform label as an edit. Keep supplied
edits bound to actual material and retain lookup for absent resources/external
facts. Preserve conversation admission, reference/recording protection, native
call limits, runtime/context/sampling, global prompts/schema, all previous cases,
fixtures, grading, failures and release targets. Declare any added regressions
and complete order before inference; freeze one candidate. Stop on the first
mandatory candidate/support/protocol/G9 failure and retain unexecuted calls with
H4 before another candidate or release. No new packages/models/runtime/defaults,
topic rules, repair calls, retries, deployment, Research, image invocation or W1.

**Creation-contract closeout — 11 October 2026:** Frozen at `a7ea2d9b`; 111 offline
checks and five capture/protocol arms pass. Thirty-seven native children execute:
baseline original boundaries 20/24; candidate 12/13 executed. Mandatory stop is
the unknown-meal case: native conversation is rejected, lookup succeeds, and the
answer correctly declines the requesting user's identity/fact while citing only
the source's actual subject. Search/citation checks pass; frozen abstention regex
rejects equivalent “does not establish” wording. Record the manual semantic
finding separately; do not silently regrade or describe invented personal facts.
The new creation branch is not exercised natively; exact failed-plan replay is
offline evidence only. Sixty-seven later children remain unexecuted, including
all new ordinary/creation/supplemental and six original full-suite children.
All 15,672 frozen files and 8,103 prior committed evidence files are preserved;
live source/deployment unchanged, Ollama 0.35.0 and local/Tailscale health 200.
No grader change, retry, deployment/restart, Research/image/W1 action follows.
H4: `docs/SEARCH-CREATION-CONTRACT-REPORT.md`. Review the grading-only proposal
at `docs/SEARCH-ABSTENTION-GRADING-PLAN.md` before a corrected grader or next native
trial; preserve genuine failures, original inputs/reports and release targets.

**User authorization — 11 October 2026 (abstention grader and fixed retest):**
Jake said “continue” after the creation-contract closeout and grading-only
proposal. Correct equivalent decline wording in isolation, with positive/negative
tests and separate retained-answer audits/regrades; preserve original scores,
answers, cases, corpus, genuine failures and release thresholds. No prompt
workaround or semantic truth claim based on regex. If offline parity/negative
checks pass, freeze the same creation-contract policy and corrected evaluator
with an early native code smoke and declared full order before inference. One
candidate, existing planner/answer/context/sampling/runtime, immediate mandatory/
support/protocol/G9 stop and H4 remain. No retries, new models/packages/runtime/
defaults, deployment, Research/image/workflow invocation or other product scope.

**Abstention retest closeout — 11 October 2026:** Frozen at `0e456fdc`; unchanged
creation policy and original 49 cases/fixtures, explicit isolated generic wording
correction. 176 offline checks and five actual native-capture/protocol arms plus
wording/report bindings pass. Separate 183-answer audit corrects two wording
false negatives; all 25 historical benchmark lexical scores remain unchanged,
genuine lookup/code failures and all original reports/scores retained. Native
baseline/candidate code smokes pass; actual transform/null reference exercises
`create_local` and returns a working a+b function without Search. Two fresh
personal-fact declines retrieve/cite correctly and pass equivalent-wording checks.
Forty-eight children execute: smoke 1/1 each; baseline boundaries 19/24 and
candidate 21/22 executed. Mandatory stop at `history-06`: actual prior 7 kg/9 kg
comparison is visible; leading “only” is not bound, missing native ref produces
false `clarify`. The actual answer wire contains the clarification instruction,
but answer ignores it and omits both required weights. Original/corrected grading
both fail; this is binding/completeness, not a wording false negative or invented
comparison. Fifty-eight later children, including all six full runs, remain
unexecuted. All 16,110 frozen files and 8,532 prior evidence files preserved;
product/live unchanged, Ollama 0.35.0, local/verified HTTPS health 200. No retry,
release/restart, Research/image/W1 action. H4:
`docs/SEARCH-ABSTENTION-RETEST-REPORT.md`. Review bounded scope-modifier binding
proposal `docs/SEARCH-SCOPED-INPUT-PLAN.md` before another candidate/inference;
preserve quantitative requirements and true ambiguity. Images remains held.

**User authorization — 11 October 2026 (scoped supplied-input binding):** Jake
said “continue going” after the retest closeout and scoped-input proposal. Repair
bounded leading scope modifiers on explicit supplied transformations in isolation,
replaying the exact null-reference failure and retaining actual source bodies/
references, missing-resource lookup, true ambiguity, code/conversation/recording
guards, approved wording correction and all original numeric/citation/coverage/
latency gates. No prompt expansion, topic rule, new package/model/runtime/default/
sampling or extra model call. Freeze one candidate and declared order with an
early comparison smoke plus existing code smokes/corpus/full comparisons before
inference; stop on first mandatory/support/protocol/G9 failure, retain every result
and unexecuted call with H4. No retry, deployment, Research/image/workflow action.

**Scoped-input closeout — 11 October 2026:** Frozen at `b6326124`; 200 offline
checks and six actual capture/protocol arms pass. Scope/code smokes pass; the
repeated native transform/null-ref comparison now binds actual material locally
and preserves both original weights. Candidate synthetic scores: 24/24 original,
9/9 supplemental, 8/8 ordinary, 8/8 creation; these are separate from full Web.
First original matched pair is baseline 24/25 and candidate 22/25. Creative
haiku/fiction emit task=creative with stray queries; host rejects the contradiction
and wrongly falls back to lookup. The comprehensive list omits population members
and reverses cited champion/runner-up roles; targeted review also finds memory-
filled missing currency and wrong result chronology/granularity in automatic passes.
Mandatory and matched G9 gates fail; the original final stop label is G9 because
the existing orchestrator overwrites its earlier mandatory reason. Both failures
remain visible, no regrade/index edit/retry. 104 of 108 children, 158 planners /
158 answers / 104 warm loads; four later full children unexecuted. All 16,675
frozen files and 9,098 prior evidence files preserved. Product/live unchanged,
Ollama 0.35.0, local/verified HTTPS health 200; no Research/image/W1 or release.
H4: `docs/SEARCH-SCOPED-INPUT-REPORT.md`. Review the offline task/evidence audit
proposal `docs/SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md` before another experiment.
Scope recovery and high lexical citation support do not qualify overall reliability.

**User continuation — 11 October 2026 (offline task/evidence audit):** Jake said
“continue going” after the scoped-input closeout. Execute the retained-failure
audit in `docs/SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md`: replay task/query
contradictions without inference, trace original recorded pages through extraction,
chunking, ranking and actual selection, distinguish missing facets from misread
evidence, and retain separate diagnostics/negative tests. Preserve all original
scores, cases, reports, thresholds and prior code. Stop with H4 diagnosis and one
concrete next correction before another native trial. No prompt/schema/policy
experiment, model/package/runtime/default/sampling change, deployment or
Research/image/workflow invocation is part of this audit.

**Offline task/evidence audit closeout — 12 October 2026:** Two exact retained
creative/query host replays and three source/extraction/rank/selection replays
complete with zero native inference; all 28 usage/context records reconstruct
the actual calibrated budgets. A complete relevant 28-row table (23 positive
counts) is displaced by three introductions despite fitting the existing budget;
one-caption replacement costs 5,333/5,502 tokens. Raw role tables lose structure
or repeated headers. New native queries do not change the frozen provider batches;
question-only ranking selects the same ordinals. Missing currency/time coverage
and actual unsupported/role-reversed answers remain failures. An unfetched menu
name is not a supplied country/property assertion. The original comparison rubric
requires a missing currency token; preserve its score and review separate covered
evaluation before claiming grounding. Blindly trusting creative labels remains
unsafe; no prospective grammar or answer repair is qualified. Tests pass:
29 diagnostic, 508 Python, 39 frontend, 473 browser; three existing browser skips.
Initial corpus-absence assertion/lint/archive-directory failures remain visible;
archival prevalidation fails before mutation, v2 retains 400 fresh generated
records/captures and restores all originals. All 16,675 prior frozen files and
17,369 committed evidence/eval files verify unchanged. Local/verified HTTPS
health 200, Ollama 0.35.0, no product change/deployment/restart, native/Research/
image/W1 calls. H4: `docs/SEARCH-TASK-AND-EVIDENCE-AUDIT-REPORT.md`. Next proposal:
offline bounded table admission in `docs/SEARCH-TABLE-ADMISSION-PLAN.md`, with H4
before native inference; preserve roles/budgets and all original targets. Task
consistency, extraction, corpus coverage and model adherence remain open. Stop
for review; Images held, Research shelved, W1 unstarted.

The existing fake settings screenshot loop additionally generates 40 untracked
captures. They are archived with source provenance/hashes (440 total fresh test
outputs retained), leaving no new files in historical evidence directories and
removing no tracked input. Prior 400 generated-file restorations remain unchanged.

**User continuation — 12 October 2026 (measurable reliability feasibility):**
Jake asked to continue reliability and determine whether it can actually improve,
noting repeated continuations without visible results. Implement and measure the
bounded offline table-admission proposal against original evidence, preserving
all existing source, reports and thresholds. Separate evidence coverage gains
from answer correctness; retain unsuccessful outcomes and give a candid feasibility
assessment. No prompt/schema/default/runtime/model/package change or deployment.
The reviewed table plan's native review gate remains applicable; any further
model experiment must have a concrete bounded scope before execution.

**User authorization — 12 October 2026 (bounded table answer comparison):** Jake
approved “Run the bounded answer comparison” in response to the concrete question
for `docs/SEARCH-TABLE-ANSWER-PROBE-PLAN.md`. Run at most three original-question
before/after pairs on the installed Qwen with unchanged prompts/settings and the
frozen public corpus. Order B/C, C/B, B/C; at most six planners, six answers and
six empty-message warm loads. Freeze the candidate and inputs first, run native
timings after browser gates, review every claim, and stop at the first candidate
support/completeness/citation failure or any protocol failure. Preserve baseline
failures and all unexecuted children. No retry, prompt/schema change, deployment,
default/runtime/model/package change, Research/image/workflow action or general
reliability qualification is authorized by this bounded comparison. Stop with H4.

**Bounded table comparison closeout — 12 October 2026:** Frozen at `b6dc54b8`.
Offline admission repairs the omitted seven-column / 28-row table (23 positive
entries) within 5,337 / 5,502 tokens; only one retained turn changes. 33 admission /
16 guard checks pass. The first original native pair produces 23/23 entries in
both arms, with real protocol/source capture, but both plans choose the qualifying
event and the existing pipeline already supplies the table: the new hook is a
no-op. Candidate opening adds unsupported “later won” chronology to aggregate
counts; manual support fails despite the unchanged passing automatic score.
Stop after two planners / two answers / two empty warm loads, retaining four later
unexecuted children. No retry, consistency qualification, prompt change or answer
improvement is claimed. Full checks: 508 Python / 39 frontend / 473 browser,
three existing skips; 432 fresh fake test outputs retained and historical bytes
restored. All 7,692 current frozen inputs, 16,675 prior frozen files and 17,861
earlier committed evidence/eval files verify unchanged; affected installed Search/
context files and Ollama 0.35.0 unchanged, local/verified HTTPS health 200.
No product change/deployment/restart, Research/image/W1 action. H4:
`docs/SEARCH-TABLE-ADMISSION-REPORT.md`. Review the smaller host-only structured
source proposal in `docs/SEARCH-STRUCTURED-EVIDENCE-NEXT.md` before another native
trial or release. Images remains held by G9; factual outputs remain drafts for
human review. VoiceOver remains off the work list.

**User authorization — 12 October 2026 (product delivery 1–4):** Jake said
“Do 1 to 4 going forward now” to the recommendation to release Images, explicitly
resolve its existing G9 hold, build brief-to-image fixed workflows, then recording-
to-meeting-pack drafts. Close the reliability campaign without qualifying its
failed candidates. Approve the narrow I1 release exception for the retained
existing Search failures/variance in the matched diagnosis; this is not a Search
pass or a general G9 waiver. Preserve chat/Search/Library prompts, sampling and
payloads and verify shared capacity, service identity, backups and recovery.
Deploy the already-tested image feature with rollback, then proceed in this order
without an intermediate approval stop. Retain H4 evidence at each checkpoint and
request physical phone observations without inventing a pass.

Two fixed, durable workflows are authorized: selected text model → image prompt
draft → one to three pinned image generations → human selection; recording →
existing transcription → optional existing guarded clean-up → selected text model
meeting-pack draft → Markdown/JSON. Explicit model/step assignments, saved inputs/
outputs, review pauses, cancellation, idempotent acceptance, restart reconciliation
and retry of failed steps are in scope. Fixed workflow text calls are authorized
only for the user-defined steps, with frozen generic prompts and bounded synthetic
task evaluations; no automatic judge/repair calls or factual reliability claim.
Human review remains required for factual drafts. No new dependency/model/runtime,
automatic routing, arbitrary tools, external writes, scheduling, branching,
reference-image editing, autonomous agents or Research restart. Preserve original
recordings/document privacy and successful-audio removal. Existing release gates
remain for all unrelated features; VoiceOver remains off the current work list.

**Product delivery 1–4 closeout — 12 October 2026:** Images and the two explicitly
approved fixed workflows are installed on the original service/route. Private
I1 and pre-workflow app/plist/database fallbacks remain. All 35 previous tables
are byte-equivalent; four workflow tables are additive. All 98 installed server/
source files match the release manifest; 14 Search modules and ordinary native
payload/stream construction remain unchanged. Ollama remains 0.35.0. No default,
model, dependency, runtime or Research change occurred.

The bounded native demonstrations use exactly three draft calls, one existing
clean-up call, two images and one ASR invocation, with no warm/judge/retry call.
Creative prompt fidelity, two outputs, persisted review and backup pass. The
ordinary spoken case preserves the required facts and unstated owner/date, but
omits a budget-action timestamp and duplicates a commitment under Decisions.
The adversarial quotation case fails semantic review: a quoted instruction becomes
an attendee claim with unsupported consensus/confirmation framing. Preserve all
outputs, frozen prompts/source and manual failures; native inference is stopped.
No factual automation is qualified. The delivered meeting workflow is only the
explicitly approved human-reviewed draft tool, with original source preserved and
its actual timeline/speaker fields visible and exported; no automatic factual
verification or external action follows. Do not claim every task check passed.

Repository checks pass: 532 Python, 39 frontend; complete browser run 485 passes /
three existing skips, followed by 12 final workflow/source-timeline checks and
24 targeted source/speaker/recovery tests. The full browser run precedes the final
source-identity/export deltas; retain their separately recorded focused evidence.
Initial JS is 243,462 gzip bytes. Earlier 18,544 committed evidence/eval objects
remain unchanged, with regenerated outputs retained separately. Corrected live
HTTPS UI inspection sees the workflow heading and seven explicit model choices;
no new model call or private screenshot. Physical iPhone review remains pending,
not invented. H4: `docs/PRODUCT-DELIVERY-REPORT.md`. Review this release's retained
limitations before another template, builder, inference experiment or autonomous
workflow scope; Research stays shelved and VoiceOver remains off the work list.

**User UI correction — 12 October 2026:** Jake reports Images works on his
iPhone, without individual checklist results. He requests image creation in the
message box, automatic seeds and a more approachable workflow interface, then
specifies a Workflows tab above chat opening a visual step canvas with a settings
panel like his supplied example. Implement docs/COMPOSER-WORKFLOW-UX-PLAN.md for
the two already-approved fixed templates. Preserve explicit model choices,
durability, human review, saving, cancellation and retry identity. No new native
calls, arbitrary agent/connector/loop execution, prompts, packages, model/runtime
or defaults changes. Retain synthetic browser/release evidence; do not claim
separate physical phone checks from the overall “It works” report.

**Composer/workflow UI closeout — 12 October 2026:** The top Chat / Workflows
navigation and connected-step builder for the two approved templates are published.
Image creation, status, cancellation and saved results are available in the message
box; automatic seeds are resolved before acceptance and retained for uncertain
retries, with optional advanced repeat controls. Workflow model/count/review
settings remain explicit; chat drafts and same-chat navigation survive the switch.
No new template, agent, model, prompt, dependency, sampling/default change, native
inference or Research restart occurred. Human review of factual drafts remains.

Repository checks pass: 532 Python / 39 frontend; full browser 493 passes, three
existing skips. The full run precedes two final markup corrections (44 px image
action and decorative data-slot wrapper), followed by eight focused two-engine
checks and frontend/build/budget passes. Initial JS is 243,871 gzip bytes. All
19,485 prior evidence/eval files and 59 historical manifests remain unchanged;
1,067 fresh generated outputs are retained separately and 1,027 old tracked
outputs restored. Static-only publication preserves the 97-file installed server,
settings/data, original service label/bind and verified HTTPS route, without
restart, with private static/database rollback and old hashed assets retained.
Codex observes the actual live top tab, five nodes, three count choices, automatic
seed controls and composer return; no work is accepted or private text captured.
Jake's earlier overall “It works” remains Images phone acceptance, not a physical
pass for this new UI. H4: docs/COMPOSER-WORKFLOW-UX-REPORT.md. Stop for UI review;
configurable additional steps and further inference remain separately scoped.


**User authorization — 12 October 2026 (isolated Workflow Studio):** Jake asked
for Claude's Workflow Studio redesign to be reviewed and implemented in a separate
GitHub branch and instance. Use `codex/workflow-studio` and its managed worktree;
retain the current main checkout and installed app. Build
`docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md` checkpoint by checkpoint,
stopping for review after each. WS-A replaces the top tabs with sidebar navigation
and a shared shell; the composer image action remains. Jake explicitly approved
user-authored model calls inside workflow blocks and the named `@xyflow/react`
dependency on this isolated branch, lazy-loaded in the builder, attribution kept.
Application-authored prompts remain frozen and require evaluation evidence.
Install the canvas dependency at WS-C, after the earlier checkpoint reviews.
GitHub CLI installation and Jake's browser sign-in are approved as local tooling.
No merge to main, deployment or change to the live app before Jake's final okay.
Future motion-guard changes, Classify evaluation targets and optional WS-F extras
retain their specific review gates. Research remains shelved. Private workflow
inputs, documents, recordings and their filenames follow the existing privacy rule.


**Workflow Studio WS-A closeout — 12 October 2026:** The isolated
`codex/workflow-studio` branch replaces top tabs with persistent sidebar rows,
a shared shell, a home with two existing templates/recent runs, the existing
builder at `/workflows/new` and a saved-run detail page. Composer Images remains.
No server/API/schema/prompt/sampling/dependency/native or production change.
Source `ee788832` passes 532 Python / 39 frontend checks and one complete browser
invocation: 505 passes, three existing skips. Initial JS is 245,249 gzip bytes
(+1,378); both streaming p95 values are 3 ms. First focused link-label/selector
failures are retained and corrected before the complete run. Fresh evidence is
archived separately, historical bytes restored, and provided reference files
retained exactly. The local preview uses fake data; no physical iPhone pass is
claimed. Installed 97-file server and 410 current-release static hashes match.
H4: `docs/WORKFLOW-STUDIO-WS-A-REPORT.md`; engine review:
`docs/WORKFLOW-STUDIO-REVIEW.md`. Stop for WS-A review before WS-B. User-written
block calls and lazy canvas dependency approval persist on this branch; the final
main merge/live deployment still require Jake's okay. Research remains shelved.

**User acceptance and authorization — 12 October 2026 (WS-B):** Jake asked to
continue to WS-B. Close the WS-A review stop without inventing individual phone
checks. Build the isolated graph engine, additive storage and APIs, seven initial
block kinds and exact legacy-template parity gates, applying the corrections in
`docs/WORKFLOW-STUDIO-REVIEW.md`. Stop for WS-B review before the WS-C canvas.
The existing main checkout and installed app remain unchanged. Jake also requested
that image creation use the ordinary chat composer and return progress and image
results in the conversation; record this in `docs/DEFERRED-FIXES.md` for a later
concrete chat-artifact scope, rather than expanding this server checkpoint.


**Workflow Studio WS-B closeout — 12 October 2026:** Source `ebc7f41e` adds
seven strict graph block contracts, additive migration 011, definitions/snapshots,
durable execution/attempts/original sources, approvals, retry and v2 APIs/stream.
Legacy request parity passes six fake-runtime cases; model settings, sources and
failed/skipped legacy states/results are faithfully projected. Canvas-independent
ordering and snapshot identities, persisted automatic seeds, owned-job acceptance
cancellation and per-run 10 Hz event limits follow the reviewed corrections.
Autosave keeps the current draft; immutable full snapshots are created per run.

Final checks pass: 591 Python / 39 frontend, workflows 88.4% coverage and 74 contrast
pairs. One complete browser invocation passes 505 cases with three existing skips
in 43.4 minutes. A retained cold-start fixture failure is fixed by starting the fake
runtime before its dependent app; no production provider/prompt changes or weakened
assertions/timeouts. Initial JS stays 245,249 gzip bytes. Copied synthetic-data
rollback restores the exact backup and starts previous schema-10 source. Fresh
outputs are archived separately, old bytes restored, 22,069 historical blobs and
15 references verified; installed 97-file server and 410 current-release static
hashes and main remain unchanged. No real model inference/dependency installation,
merge, live publication or physical phone pass is claimed. The requested image
creation/results inside chat remains a tracked follow-up. H4:
`docs/WORKFLOW-STUDIO-WS-B-REPORT.md`. Stop for WS-B review before WS-C. Research
remains shelved; named canvas/call approvals persist on this isolated branch.

**User acceptance and authorization — 12 October 2026 (WS-C):** Jake asked to
continue and keep Claude's UI, implementing it so it works. Close WS-B's review
stop and build Studio editing per the supplied spec/prototype/references. The
approved exact-pinned lazy `@xyflow/react` dependency retains attribution; phones
edit through Outline and templates become editable copies. Preserve ordinary
keyboard/label semantics and current APIs/prompts/model settings. Stop for WS-C
review before WS-D, merge or live publication. The image-in-chat request remains
tracked separately. Main and the installed app remain unchanged.


**Workflow Studio WS-C closeout — 13 October 2026:** Claude's reviewed layout
now edits real definitions on the isolated branch: seven kinds, native drag/
connect/insert, typed references, Inspector/Connections, autosave/conflicts,
history/copy/notes/tidy/minimap and phone Outline. Templates create editable
copies; basic input/run/approval/retry/source/export paths retain legacy behavior.
The exact approved lazy `@xyflow/react@12.12.0` keeps attribution and its license.
No native inference, application-authored prompt, model/default/sampling/runtime
change, main merge or live publication occurs. Research remains shelved.

Source `62a822e4` retains the initial-fit dirty-state and redundant preference
hydration fixes. Both failed full-suite attempts/traces and earlier sources are
retained. Final make check passes 630 Python / 87 frontend, workflows 89.2%
coverage and 110 contrast pairs; one complete browser invocation passes 529
checks with three existing skips in 48.7 minutes. Initial JS is 241,658 gzip
bytes (3,591 below WS-B); Studio is 77,306 gzip bytes. Historical 23,116 blobs,
15 references, 509 source/config/test files, main and installed 97 server / 410
static files verify preserved. 1,037 fresh outputs are archived separately and
182 synthetic videos remain outside Git. Local/verified HTTPS health passes.
H4: `docs/WORKFLOW-STUDIO-WS-C-REPORT.md`. Stop for WS-C review before WS-D.
No physical phone/VoiceOver pass is claimed. The image-in-conversation request
remains tracked separately; future motion/Classify/optional gates persist.

**User authorization — 13 October 2026 (WS-D, followed by chat images):** Jake
asked to execute WS-D and then Claude's `docs/next/chat-images/` plan, retaining
Claude's UI. Close the WS-C review stop without inventing phone checks. Implement
WS-D's server-driven run canvas, approvals, provenance-checked reuse, single-block
tests, favorites and history on `codex/workflow-studio`. The requested motion
includes J-W6's CSS connection pulse; allow `stroke-dashoffset` in the guard.
Retain checkpoint reports and stop for review after WS-D and each CI checkpoint.
For the ensuing CI plan use its recommended decisions: J-I1 Playful by default,
J-I2 reasoning ticker, J-I3 saved image chat turns, J-I4 exclude both image roles
from text context, J-I5 prompt-derived titles without a model call. No new package,
model, runtime, sampling default, application-authored prompt or native trial is
authorized. WS-E/WS-F and CI-D extras remain gated. Main and the installed app
stay intact; merge and live publication still require Jake's final okay.

**Workflow Studio WS-D closeout — 13 October 2026:** Source `a9a77bdd` implements
Claude's run canvas/timeline, truthful streaming/progress and Follow, approvals,
favorites, retry, provenance-checked reuse, durable isolated block tests, named
versions, immutable run views, history and paused notifications. Additive migration
012 preserves existing rows. The approved CSS connection pulse respects both
reduced-motion triggers. Legacy phone controls retain navigation; ordinary chat,
native performers, prompts and user sampling behavior remain unchanged.

Final checks pass: 646 Python / 94 frontend, workflows 89.2% coverage and 110
contrast pairs. One complete browser invocation passes 555 cases with three
existing skips in 56.3 minutes. All 112 new-state axe checks pass. The earlier
interrupted invocation and eight-failure complete run (545 passes) remain retained;
their regressions are fixed without weakening original tests. Initial JS is
242,270 gzip bytes, 612 above WS-C. Copied synthetic rollback restores the exact
backup and starts prior schema-11 source. Historical 24,444 evidence/eval/fixture
blobs, 15 workflow references, 17 supplied chat-image files and 529 source/test/
config files verify preserved; installed 97 server / 410 static files and main
are unchanged. 1,168 fresh outputs are archived separately and 320 final/available
synthetic recordings remain outside Git, with earlier attempts separately retained.

No native inference, new dependency/model/runtime, Research restart, main merge,
live publication or physical iPhone/VoiceOver pass is claimed. The lifecycle
restart test is in process, not a launchd/process restart. H4:
`docs/WORKFLOW-STUDIO-WS-D-REPORT.md`. Stop for WS-D review before CI-A. Claude's
chat-image plan and recommended defaults are retained for CI-A/B/C; image chat
turns are not implemented by WS-D. Final merge/publication still need Jake's okay.

**User acceptance and continuation — 13 October 2026 (CI-A):** After the WS-D
report, Jake asked to continue, then mesh the builder and test an actual local LLM.
Close WS-D's review stop without inventing phone results. Build CI-A of Claude's
chat-image plan on the isolated branch, preserving the approved Playful default
and closed live reasoning ticker. Web only: no server source, native inference,
new dependency/model/runtime, prompt or sampling change. Retain the H4/QA report
and stop after CI-A. Prepare a concrete bounded local-LLM workflow test proposal
for the later integrated builder; this continuation does not run that trial now.
Main and the installed app stay intact; final merge/publication remain gated.

**Chat images CI-A closeout — 13 October 2026:** Frozen source `76957979`
replaces dots with Claude's Atelier mark, truthful phases and a seeded 36-word
sequence, adds browser-local Playful/Plain, and starts live reasoning as a closed
literal ticker. Expansion follows new text until manual scrolling; first answer
text closes it into the existing Thought row. Original reasoning and SSE/rAF/send
paths are preserved. Failed page reads do not inflate readable-page counts.
Both reduced-motion triggers stop motion; outgoing words are immediately hidden.
Cross-device synchronization of this one new preference remains future server work.

Final checks pass: 646 Python / 101 frontend tests, all required coverage above
80%, 110 contrast pairs and one complete browser invocation with 573 passes,
three existing skips and zero failures in 56.6 minutes. All 112 new-state axe
audits pass. Initial JS is 244,418 gzip bytes (+2,148 from WS-D); ordinary render
p95 is 2.6 / 3 ms, ticker p95 0.5 / 1 ms, first-token overhead 77.79 / 61.39 ms.
Retain initial focused failures and the deliberately interrupted 513-pass browser
attempt (one interrupted, 59 unrun), stopped to fix reduced-motion word overlap.
No test assertion, timeout or performance target was weakened.

Historical 30,764 evidence/eval/fixture blobs, 15 workflow references, all 17
supplied chat-image files, 537 frozen files and 335 core files verify preserved.
1,202 final fresh outputs are archived, 1,162 historical files restored and 40 new
fake captures relocated; 989 interrupted outputs are also retained. All available
907 synthetic videos remain outside Git. Installed 97 server / 410 static files,
main and service/route identity remain unchanged; local/verified HTTPS health pass.

H4: `docs/CHAT-IMAGES-CI-A-REPORT.md`. Stop for CI-A review before CI-B/C.
`docs/WORKFLOW-STUDIO-NATIVE-TRIAL-PLAN.md` proposes at most seven calls on the
installed daily profile after integration; it is not executed. No server change,
native inference, new dependency/model/runtime, prompt/sampling/default change,
Research restart, main merge or live publication. No physical phone/VoiceOver
pass is claimed; final merge/publication still require Jake's okay.

**User acceptance and continuation — 13 October 2026 (CI-B):** Jake said
“Proceed.” Close CI-A's review stop and implement CI-B of the supplied chat-image
plan on `codex/workflow-studio`: additive migration 013, atomic/idempotent saved
image turns, retry/cancel, exclusion of both image roles from text context,
prompt-derived image-first titles, the unified composer and truthful job cards,
and Gallery provenance/navigation. The existing separate composer image workspace
and Gallery creation form are explicitly replaced by chat image mode; retain
their acceptance/retry/draft/save/cancel/storage coverage through the new flow.
Preserve Claude's UI and supplied files. No new dependency, model, runtime,
native inference, prompt, sampling/default change or Research. CI-C viewer,
iteration and export remain next checkpoint. Retain H4/QA evidence and stop after
CI-B. Main/live publication and the bounded native workflow trial remain gated.

**Chat images CI-B closeout — 14 October 2026:** Frozen source `3825196a`
implements Claude's unified image composer and durable chat turns with additive
migration 013, atomic/idempotent job acceptance, explicit/implicit parent identity,
scoped cancellation, retry/user branch navigation and deleted-chat origins.
Both image roles are excluded from text context; titles use the prompt without a
model call. Existing jobs/capacity/SSE remain; real steps drive progress, observed
completions reveal once, history is immediate, and saving uses the existing dialog.

Checks pass: 653 Python / 104 frontend, required coverage above 80%, 110 contrast
pairs and one complete browser invocation with 595 passes, three existing skips,
zero failures (1.0 hour). All 112 new-state axe checks pass. Initial JS is 246,848
gzip bytes (+2,430); render p95 2.4 / 3 ms and first-token overhead 74.37 / 67.65 ms.
Retain focused failures and the deliberately interrupted first full run (314
passes, one interrupted, 281 unrun); concrete parent/branch fixes precede the
final full run. That interrupted run's temporary trace/recordings were overwritten
by a focused run and are unavailable; its source/log and available captures remain.
No test threshold/timeout/assertion was weakened and no skip was added.

552 frozen files, 323 core files, 33,141 historical blobs, 15 workflow references
and all 17 supplied chat-image files verify preserved. Archive retains 1,206 fresh
outputs, restores 1,166 historical files and relocates 40 fake captures. All 584
available final synthetic videos remain outside Git. Exact unchanged interrupted
copies reference original Git blobs (7,305 copies / 1,960,959,222 bytes avoided).
Installed 97 server / 410 static hashes and main remain unchanged; local and
verified HTTPS health pass. No service/route change, main merge or deployment.

H4: `docs/CHAT-IMAGES-CI-B-REPORT.md`; test ledger records explicitly approved UI
replacements. G9's existing native Web accuracy release gate remains open: 56
zero-inference payload comparisons over 25 original questions prove context
parity, not a new real-model accuracy pass. No native inference, new dependency/
model/runtime, prompt/sampling/default change or Research restart. No physical
phone/VoiceOver pass claimed. Stop for CI-B review before CI-C; viewer/iteration/
exports and the bounded local-LLM workflow trial remain next reviewed work.
Final merge/publication still require Jake's explicit okay.

**User authorization — 14 October 2026 (CI-C and native workflow trial):** Jake
asked “Continue to CI-C and then the test.” Accept CI-B's review and implement
Claude's CI-C viewer, iteration, vision-gated attachment action, exports and phone
scroll-snap behavior on the isolated branch. Preserve the supplied UI and files;
Refine records lineage and edits the prompt only, not reference-image pixels.
After CI-C verification, execute `docs/WORKFLOW-STUDIO-NATIVE-TRIAL-PLAN.md` in a
separate synthetic data folder: the installed daily profile, at most seven native
calls and ten minutes, stopping on the first failure without retry. This request
closes the intermediate review stop for that named sequence; retain both H4
reports. No new model/dependency/runtime, application-authored prompt, sampling
change, Research restart or native image concurrency. Main, live service and
production data remain unchanged. Stop after the trial for review; final merge
and publication still require Jake's explicit okay.


**CI-C and native workflow trial closeout — 14 October 2026:** Frozen source
`f8e301c2` completes Claude's viewer, iteration, vision-gated attachment, phone
snap/dots and image exports on `codex/workflow-studio`. Final check/build pass:
654 Python / 104 frontend, 110 contrast pairs and one full browser invocation with
615 passes, three existing skips and zero failures in 1.0 hour. Retain all prior
failed/interrupted attempts and concrete portal/contrast/draft/focus fixes; no
assertion, timeout, target or skip was weakened. Initial JS is 247,594 gzip bytes
(+746 from CI-B); 16 new viewer/refine axe audits pass. All historical reference/
eval bytes, 556 frozen files, 322 core files, main and installed 97 server / 410
static files verify intact; local/verified HTTPS health pass. G9 remains open.

The authorized native trial stops after two actual daily-profile calls at its
first manual semantic gate: recurrence and broader material provision are invented.
Exact outline-to-draft binding and a visible paused review are observed, but no
reload/approval/edit, second run, in-flight cancellation or recovery pass is
claimed. Save never runs. Both model streams close and trial capacity releases;
cleanup cancels the paused run. Retain setup's zero-call SPA-route failure, empty
browser event observer (wrong legacy endpoint) and unavailable RSS measurement.
Native NDJSON, exact requests, durable snapshots and synthetic video/frame remain.
No retry, new inference, sampling/prompt/default/runtime change or native image job.

H4 reports: `docs/CHAT-IMAGES-CI-C-REPORT.md` and
`docs/WORKFLOW-STUDIO-NATIVE-TRIAL-REPORT.md`. Stop for review before more native
experiments or Studio/reference-edit expansion. No main merge, live publication,
Research restart or physical iPhone/VoiceOver pass; final merge/publication still
require Jake's explicit okay.


**User authorization — 14 October 2026 (native recipe and harness repair):**
After the CI-C/native failure report and prioritized fixes, Jake said “Fix them.”
Proceed with `docs/WORKFLOW-STUDIO-NATIVE-REPAIR-PLAN.md`: carry the original brief
into both user-authored trial Generate blocks, retain human review, fix actual
Studio SSE/RSS/cleanup measurement and perform one frozen trial, max seven native
calls / ten minutes with first-failure stopping. Preserve the original failed
trial and all release targets. No ordinary application prompt/template/sampling/
runtime/default/UI change, broad Search experiment, Research restart, new model
or dependency. His question about committing to main is a readiness question;
no merge/publication is authorized. Stop with H4 results after the bounded trial.


**Native recipe/harness repair closeout — 14 October 2026:** The isolated,
frozen user-authored recipe preserves original-brief and exact upstream-outline
binding in six native requests. Two full runs produce faithful drafts and pass
review reload, unchanged approval, edited save/export and raw-output preservation.
Actual Studio SSE (149 events), PID/RSS and clean driver/stream close are captured.
Retain the zero-call offline selection failure and its correction. Runtime,
product prompts/templates/source, sampling and defaults remain unchanged.

The native trial fails its cancellation DOM-window assertion after the brief
third draft finishes, then stops at six calls / 306.16 seconds. Cleanup cancels a
paused run, not active generation; single-block recovery remains unexecuted.
Read-only third-output review also flags “all necessary materials,” so two good
samples do not qualify consistent fidelity. No retry or seventh call followed.
A prospective actual-node.text UI cancellation probe passes with partial output
and no downstream review using fake runtime only; no native pass is claimed.
H4: `docs/WORKFLOW-STUDIO-NATIVE-REPAIR-REPORT.md`. Preserve prior evidence/gates,
main and the installed app. Stop for review before another native pair or main
merge/publication; Research/VoiceOver stay outside the work list and G9 is open.


**User authorization — 14 October 2026 (native cancel/recovery pair):** Jake
said “Go ahead and repair it then” after the remaining native control-check
recommendation. Proceed with `docs/WORKFLOW-STUDIO-NATIVE-CONTROLS-PLAN.md`, one
frozen pair, at most two native calls / three minutes with first-failure stopping,
using the same daily profile, unchanged user-authored recipe and explicit samples.
Use actual Studio text events to click a visible enabled Cancel control, then
verify closure/capacity and one single-block recovery/history/reload check.
Preserve all earlier failed trials and factual limitations. No new model/package/
runtime, application prompt/template/sampling/default change, Research/Search
experiment, native image job or main/live publication. Stop with H4 evidence.


**Native cancel/recovery closeout — 14 October 2026:** The frozen pair passes
using the existing daily profile, unchanged user-authored Draft and explicit
source samples. Actual node.text triggers a visible enabled hit-testable Cancel
control. An incomplete native stream closes without error, one byte of partial
output persists, no downstream block runs and capacity releases. A second
identical native request completes, survives reload, stays outside normal
history and passes manual review for all supplied facts/no additional claims.
Exactly two calls / 139.27 seconds; no retry or extra inference. Earlier failures
and general grounding limitations remain unqualified. Retain the zero-native
first offline setup failure (still following prior run) and its explicit Close
Run remedy. No assertion/timeout/target change; final offline UI pair passes.

H4: `docs/WORKFLOW-STUDIO-NATIVE-CONTROLS-REPORT.md`. Product source remains the
fully checked CI-C f8e301c2 candidate; main and installed app stay intact. No
runtime/model/default/sampling/dependency/application prompt/template change,
Research/Search restart, native image job or phone/VoiceOver pass. The missing
native control gate is closed. Stop for final branch review; merge and live
publication still require Jake's explicit okay. Factual outputs require review,
G9 remains open and future WS-E/reference editing remains separately gated.


**User acceptance and merge authorization — 14 October 2026:** Jake said
“Go ahead” after Codex recommended merging the reviewed checkpoint following
native cancellation/recovery verification. Accept the branch review and merge
`codex/workflow-studio` into main, pushing the reviewed source/history to GitHub.
Retain a source fallback to the accepted pre-Studio main and all earlier trial
failures. Preserve the untracked original Claude documents outside the checkout
before Git writes their identical tracked copies. Product source remains the
fully tested f8e301c2 candidate. Factual drafts retain their review requirement;
no general grounding, physical-phone or VoiceOver qualification is implied.
Future WS-E/reference editing and Research remain separately gated. This merge
operation preserves the installed service and production data.
