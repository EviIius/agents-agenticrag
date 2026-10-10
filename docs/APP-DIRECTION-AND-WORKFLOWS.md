# Atelier direction: images, durable jobs and workflows

Planning memo — 10 October 2026. Reviewed source: `1ec4897`.

This is a proposal for discussion, not an implementation authorization or a
replacement for existing gates. Research remains shelved. No inference, model
installation, runtime change, prompt edit or deployment was performed for this
memo. Future image dependencies and additional workflow calls need their own
reviewed scope.

## Recommendation

Finish one bounded grounding checkpoint, then make image generation the first
user of a durable job system. After images, add reusable ordered workflows with
explicit model assignments. Consider autonomous decisions only after those
workflows demonstrate useful results and reliable recovery.

The durable job system is the most valuable shared addition: images, batches,
transcription and later workflows all need saved inputs, outputs, progress,
cancellation and restart handling. Building an independent image queue first
would duplicate that work.

## What the existing work establishes

| Area | Evidence and limit | Consequence |
| --- | --- | --- |
| Current application | Latest checkpoint passed 458 Python, 39 frontend and one complete browser run with 463 passes and three existing skips. Context-warning correction is published; failed grounding prototype is isolated. | Preserve the working app and its fallback while testing additions. Regression passes do not establish factual answer quality. |
| Grounding prototype | Latest native response satisfied the supplied schema but selected incomplete table fields; host rejected it. A separate selected excerpt exceeded its source quotation allowance. | One repair to align admissible schema selections with host validation is rational. It does not resolve relevance, completeness or semantic support. |
| Model comparison | Named Qwen3.8 candidate missed mandatory Web checks in all three matched pairs. Some original Library failures were citation-parser limitations, documented separately. | Keep the current default. More models are not a substitute for diagnosing evidence handling. |
| Chat execution | Tasks and SSE replay events live in memory; saved messages survive, but startup marks active messages interrupted. | Browser reconnection works within a running server. A durable workflow queue still needs persisted steps and recovery. |
| Transcription | Outputs are saved before successful audio is removed. Startup interrupts unfinished jobs rather than automatically continuing them. | Reuse the engine boundary and output storage; add explicit workflow input references and restart rules. |
| Capacity | Chat and embedding share per-connection limits; transcription has its own semaphore. | Separate image and speech engines need coordination with chat. An Ollama queue alone cannot schedule every engine on the Mac. |

Evidence: [latest checkpoint](EVIDENCE-OBJECT-REPORT.md),
[model comparison](MODEL-COMPARISON-REPORT.md),
[deferred issues](DEFERRED-FIXES.md),
[Research closeout](RESEARCH-SHELVED.md).

## 1. Bound the remaining reliability investment

Prepare one generic correction before further native evaluation:

- Derive native selections and host checks from one admissibility contract.
  Offer complete legal field bundles preserving subject, property, units and
  qualifiers. Expose only standalone prose that fits its source allowance;
  continue checking cumulative allowance across selections.
- Test incomplete bundles, unknown references, crossed source bindings, lost
  qualifiers and quotation limits without inference before the original smoke.
- If the original native smoke passes, run the original Web and Library suites,
  unchanged thresholds and manual claim review. Predeclare repeated runs of the
  frozen candidate; retain every failure. Add a separate held-out suite for
  generalization without replacing the original gates.
- Score validity, support, relevance and completeness separately. A source
  citation, legal JSON or refusal alone is not a useful supported answer.
- Preserve sources and uncertainty through every transformation. Treat document
  instructions as untrusted content. Existing injection failures are relevant
  to future tool use; a prompt cannot be the permission boundary for actions.

Decision at that checkpoint: ship only a qualifying change. If the repair does
not yield useful supported answers, stop advancing this selector design and
review a simpler explicit source-excerpt presentation with abstention for missing
information. Do not respond by adding automatic judge/repair loops or quietly
lowering release targets. The existing application stays available.

This limits the investment in a plausible, diagnosed fix. It is not a promise
that a single repair will make grounding reliable. A failed grounding checkpoint
also need not prevent independent image work, whose result criteria differ.

## 2. Test one image model before committing to an integration

Start with **FLUX.2 klein 4B**. It supports generation/editing and has an Apache
2.0 license. The publisher's roughly 13 GB consumer-GPU figure is not a measured
Apple unified-memory peak or a Mac speed guarantee.
[Publisher model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B).

The documented host is an Apple M5 Pro Mac mini with 64 GB unified memory and
16 GPU cores. This makes a local trial credible, not yet qualified. Follow the
six synthetic prompts, two seeds, reference edit and cold/warm measurements in
[the image options memo](IMAGE-MODEL-OPTIONS.md). Preserve failures and evaluate
object counts, relationships, text, edit consistency, memory, swap, disk use and
chat responsiveness. Agree usable latency from measurements before phone release.

Choose the integration engine based on control as well as visual output:

- Draw Things is a sensible manual trial. The inspected HTTP server exposes
  generation routes and returns completed results. That file does not establish
  job progress or generation cancellation; other interfaces need investigation.
  [Inspected HTTP source](https://github.com/drawthingsai/draw-things-community/blob/main/Libraries/HTTPAPIServer/Sources/HTTPAPIServer.swift).
- MFLUX documents Apple MLX implementations and CLI/Python entry points. A
  separate supervised worker is a plausible automation boundary, provided actual
  progress, termination, memory release and unattended execution pass testing.
  Its first execution can download weights; none was run for this memo.
  [Project documentation](https://github.com/mflux-community/mflux).

Integrate one tested engine/model first. Compare Z-Image-Turbo later if the first
trial exposes a concrete photographic-quality or latency gap. Keep the larger
image candidates on the shortlist rather than installing the whole list.

## 3. Build durable jobs with the first image feature

Use the existing SQLite, asyncio, FastAPI and SSE foundations for this single
Mac. An external queue broker or agent framework is not justified by the current
requirements. This is an architectural recommendation, not a benchmark against
every framework. Preserve the existing listener, service and Tailscale setup.

Minimum job design:

| Requirement | Proposed behavior |
| --- | --- |
| Durable state | Save job, ordered steps, attempts, input/output references, cancellation intent and terminal status. Accept a job only after its inputs and queue record are durable. |
| Recovery | Reconcile worker state at startup. Resume from completed artifacts; mark uncertain work interrupted. Retry an approved interrupted step as a new attempt. Do not promise recovery halfway through token or pixel generation. |
| Artifacts | Commit validated outputs atomically, then commit step completion. Preserve original inputs and provenance; incomplete files never count as successful outputs. Reconcile files orphaned by a crash. |
| Events | Persist a compact transition journal and sequence IDs; serve snapshots plus SSE replay. Token/progress detail may be coalesced. No polling or unlimited token history in the database. |
| Cancellation | Cancel queued work immediately. Running work becomes cancelling until the engine acknowledges or exits. Closing an HTTP connection is not proof GPU work stopped. |
| Capacity | Initially allow one managed heavy invocation at a time across engines. Grant capacity at invocation boundaries; do not hold a GPU slot while waiting for retrieval, another step or another capacity acquisition. |
| Foreground use | Prefer interactive work at step boundaries while preventing background starvation. Do not claim instant preemption; show when chat must wait for an image step. Measure concurrency before enabling overlap. |
| Residency | Account for loaded models, contexts and worker peaks. Do not issue hidden app-initiated model unloads. Any loading/unloading policy must be visible and approved. |
| Storage | Keep outputs and metadata; show storage totals and bulk deletion. Pin inputs while queued steps still require them. Release successful audio after durable transcription; retry downstream from the saved transcript. Preserve current failed/cancelled audio policy. |
| Backups | Existing database backups do not alone back up image files. Define an output-file backup policy and restore manifest; avoid repeatedly copying model weights and temporary recordings. |

Ollama documents memory-dependent model concurrency and increased context memory
for parallel requests. This supports conservative scheduling; current online
defaults are not evidence about the installed 0.35.0 configuration.
[Ollama concurrency documentation](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests).

Expose a small Jobs screen with queue position, active step, actual progress
where available, cancel, retry and outputs. Add a lazy-loaded Images view with
explicit prompt/settings, gallery and the existing save/share flow. Record model
revision, seed, exact prompt and resolved settings; do not claim bitwise
reproducibility across backend/model revisions.

The Mac executes accepted jobs after the phone closes. If the Mac is unavailable,
the phone must not claim a job was accepted or running. Local execution does not
depend on Codex's account usage limit; it still depends on host availability,
disk space and runtime health.

Release evidence must include disconnect/reconnect, server and worker restart,
cancel during execution, failed step retry, duplicate submission, unavailable
model, low disk and restoring outputs. Use synthetic inputs; preserve existing
regression gates and add real-worker measurements.

## 4. After images: reusable ordered workflows

A queue executes jobs. A workflow supplies an ordered plan. An agent chooses
what to do next during execution. Start with user-defined plans: they deliver
the requested model-after-model sequence without adding autonomous planning.

First workflow: **recording to meeting pack**.

1. Transcribe with the existing engine.
2. Optionally run the existing guarded cleanup.
3. Produce a summary, decisions and action items from saved transcript inputs.
   Keep the original transcript accessible to this step; cleanup or an earlier
   summary is not a replacement source. Unstated owners/dates remain unstated.
4. Save Markdown/JSON outputs for review and download.

Second workflow: **brief to image set**.

1. A selected chat model drafts image prompts from a brief.
2. A selected image model produces a bounded set of variants.
3. The user chooses results and exports them. Do not add an automatic art-critic
   model call without evidence it improves the task.

First version: simple ordered steps and a few editable templates, explicit model
assignment, saved outputs, pause between steps, cancellation and retry of the
failed step. Scheduling and branching follow once manual queues recover reliably.
Use the same chat model across text steps until task-specific comparisons justify
another model. Assign by verified capabilities and measured task quality, never
by model-name heuristics or keyword routing.

Version workflow definitions and step input manifests. Preserve the source
references, prompt version and user-selected settings per attempt. If a user
edits an earlier step, invalidate dependent outputs or create a new run; do not
silently reuse stale downstream results. Do not silently truncate oversized
inputs. Any future long-document reduction strategy needs its own quality eval.

Structural validation and a second model's agreement do not establish factual
correctness. Qualification should measure whether the final pack meets the
user's task, plus source support, missing requested items, time and recoverability.
Initial factual workflows remain drafts for review until those checks pass.

## 5. Agents come after successful workflows

Consider an agent only where fixed steps repeatedly leave a demonstrated need
for a model to choose its next action. Reuse the same durable execution system;
bound allowed tools, steps, time and output storage. Start with narrowly scoped
read-only tools and host-enforced input permissions. External writes require
review of the concrete action; retries need idempotency rules.

This would be a separately reviewed capability. It does not reopen the shelved
Research prototype or waive its original failed qualification. Do not begin with
supervisors, arbitrary shell access, automatic specialists or model voting.

## Proposed sequence and decisions

| Checkpoint | Deliverable | Decision before continuing |
| --- | --- | --- |
| R | One admissibility repair and frozen evaluation | Qualify supported useful answers, or stop this design and choose the simpler evidence presentation. |
| I0 | One local image engine/model trial | Confirm usable quality, latency, resource fit, progress and actual cancellation. |
| I1 | Durable jobs plus image UI | Demonstrate recovery, storage, phone reconnection and unchanged chat behavior. |
| W1 | Recording-to-meeting-pack template | Demonstrate useful supported outputs and retry without rerunning successful steps. |
| W2 | Brief-to-images template; then scheduling/batching | Demonstrate bounded execution and resource fairness on this Mac. |
| A | Narrow autonomous decisions, if justified | Separate approved spec, tool qualification and held-out task evaluation. Research remains independently gated. |

The current fixes are rational maintenance and useful defenses. They are not
sufficient by themselves for unattended automation. The durable foundation is
consistent contracts, preserved sources, saved work, bounded resources and
visible failures. Add autonomy only when it solves a measured gap in that system.

## Planning checkpoint evidence

- Changed file: this proposal only.
- Inspection: current SPEC, latest reports, deferred issues, chat/transcription
  execution, Library ingestion and backup boundaries; official image/runtime
  documentation linked above.
- No application tests, screenshots, inference or deployment were run for this
  documentation-only checkpoint. Test counts above belong to the prior report.
- No new implementation authorization or gate waiver is claimed.
