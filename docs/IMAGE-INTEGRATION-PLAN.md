# Proposed I1 scope — memory policy, durable jobs and images

10 October 2026. Prepared from I0 measurements; not implemented or authorized by
the I0 approval. No new package/model is proposed. Review I0 quality/latency first.

## Recommendation

Keep the tested MFLUX/klein 4B engine and its exact model/dependency revision.
First qualify memory handling, then build the queue and image UI together. Do
not create a temporary independent image queue that workflows must replace.

I0 generated the samples successfully, but host swap increased during the first
image while a chat model occupied 21.83 GB. The chat model later expired under
Ollama's ordinary keep-alive, so resident-image timing is not a persistent
two-model benchmark. A limit on active jobs alone does not bound loaded models.

## I1-0: bound memory before product wiring

Prepare a separately frozen resource test using the same prompts, seeds, model,
8-bit eligible layers, four steps and 1024-square settings. Preserve the I0
default-policy observations. Start by checking a 1 GiB MLX unused-allocation cache
limit; measure actual live/cached peaks, swap change, time, application health and
chat before/after. The test value is proposed, not a proven safe setting.

Use the photograph and text prompts at both original seeds. Verify that the
intended chat model is actually loaded before and after every image. If its normal
keep-alive expires, report the run as such; do not quietly force residency or
unload models. Verify next-worker recovery and generation cancellation with the
bounded policy. Retain every output and failure; no prompt/precision fallback.

The MLX cache limit concerns unused allocations, not live tensors, total host
memory, Ollama allocations or its context. Do not claim a hard overall memory
limit from this API. [MLX documentation](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html).

Stop and report if the intended loaded-model combination still causes material
swap growth, unusable latency, allocation failure or lingering worker activity.
Any image/model unload policy must be visible and approved. Do not change the
current Ollama runtime/default or existing chat sampling to improve this test.

## I1-A: durable execution, initially for one image engine

Use the existing SQLite, asyncio, subprocess and SSE stack. Preserve the current
service, port/bind, Tailscale route and all existing tables/rows/API shapes.
New job/step/artifact/event tables and APIs are additive and separately tested.

| Requirement | Behavior |
| --- | --- |
| Acceptance | Persist input files/manifest and queued job before reporting accepted. Duplicate submissions with the same request key do not start duplicate images. |
| Execution | One managed heavy invocation at a time; account for loaded model residency as well. Release capacity between native invocations, rather than while waiting for search/network/another step. |
| Interactive use | Prefer chat at invocation boundaries with bounded background starvation. Show when a chat must wait; do not promise interruption halfway through GPU work. Preserve existing chat payloads and sampling precedence. |
| State | queued, preparing, running, cancelling, complete, failed and interrupted; expose the actual stage instead of a fabricated percentage for initialization/decoding. |
| Progress | Push worker stage/completed-step events through SSE with persisted compact sequence IDs. Reconnect with snapshot plus replay; no job-progress polling. |
| Cancellation | Queued jobs cancel immediately. Running jobs remain cancelling until the owned worker exits/is reaped; capacity is not released merely because the HTTP requester disconnects. |
| Completion | Validate output format/dimensions/metadata/hash, commit files atomically, then mark completion. A partial file or missing artifact never counts as success. |
| Restart | Reconcile jobs, leases and artifacts at startup. Mark uncertain active work interrupted; an explicit retry creates a new attempt. Do not promise continuation midway through pixels or tokens. |
| Storage | Keep completed images/metadata, show totals and bulk removal. Pin reference inputs while needed, then follow the reviewed retention policy. Model weights are excluded from ordinary deployment copies/backups. |
| Backup | Define an image/output manifest and restore path; database-only backups cannot restore image files. Preserve existing successful-audio deletion/output retention. |

The worker must run from its private installed location with no Documents access
or interactive image app. I0's minimal-environment supervised subprocess is useful
evidence, but does not establish a production service deployment or crash recovery.

Generation/editing are the only new native calls in this proposed checkpoint.
No prompt rewriting, routing, quality judge, new chat model or workflow agent.
Do not expose arbitrary CLI flags, filesystem paths or commands as job inputs.

## I1-B: image UI and job visibility

Use shadcn primitives, existing design tokens/motion and `/design` synthetic
states. Add a lazy Images view and small Jobs view, rather than complicating the
chat model picker with image-only models. Keep runtime-reported text model
capabilities and the current chat default intact.

- Prompt, supported model and explicit visible settings; keep exact requested and
  resolved seed/settings in metadata. No hidden prompt/style expansion.
- One image per generation at first; reference editing only after reviewed file
  limits, durable input handling and preservation behavior are implemented.
- Gallery, actual stage/step progress, cancel, retry and output details.
- Reuse cancellable PNG/details save/share selection; cancellation starts no
  download or native share sheet. Private names/prompts do not enter QA evidence.
- Preserve composer/keyboard behavior, reduced motion, safe areas and ordinary
  focus/labels. No VoiceOver pass is claimed or added to this build's work list.

Release evidence: duplicate submission; disconnect/reconnect; server and worker
restart; cancellation during initialization/denoising; failed-step retry; missing
model/output; low disk; restoring output files; memory fit with intended loaded
chat models; unchanged chat/search/transcription regression gates. Use synthetic
inputs. Native image progress/cancellation must be verified, not only faked tests.

## After I1

W1 introduces ordered recording → transcription → optional cleanup → meeting-pack
drafts → Markdown/JSON. Keep source transcripts available and retry only failed
steps. W2 adds brief → image-prompt drafts → bounded image variants → human
selection. Workflow model calls and saved definitions need their own approved
scope/evals; image success does not qualify factual claims or reopen Research.

Autonomous agents remain a later, separately justified capability. The first
useful outcome is a dependable queue with explicit model/step assignments,
outputs and recovery that continues on the Mac when the phone closes.
