# AgenticRAG: next product phase

Updated 28 September 2026. This plan follows a review of the workbench, agent and
Supervisor code, and the first local-model comparison. It is a sequence of buildable
milestones, not a claim that the current agents are production-ready.

## What we have now

- The iPhone workbench can be installed as a web app. Chat, sources, models, tools,
  projects, search, explicit project notes, file ingestion, opt-in web research,
  Direct streaming, cancellation, and traces exist.
- Agentic mode has bounded read-only `search`, `lookup`, and `calculate` tools,
  evidence checks, and hard budgets. Supervisor creates up to three non-recursive
  specialist assignments, runs them sequentially, synthesizes, and reviews.
- The one-question, three-model smoke comparison found Fixed answered in 3.4–4.9s,
  while Agentic took 23–62s and Supervisor took 45–70s, sometimes abstaining.
  This establishes a latency problem, not a quality ranking.
- Runs are cancelled through the live server, but the work itself is not durable
  across a server restart or a closed phone connection. Project notes are explicitly
  saved by the user; the agent cannot write them autonomously.

## 1. Reliability and evaluation first

Build a frozen, representative question set across all installed chat models
and all four modes. Include simple lookup, multi-source synthesis, numeric checks,
web research, missing evidence, prompt injection, model-format failures, and a
cancelled phone run. Record answer quality, citation support, abstention quality,
tool failures, elapsed time, and memory use. Run each nondeterministic case more
than once. Show the resulting matrix in the Models page so a model choice has
measured tradeoffs. Record the runtime, context size, and structured-output mode
for each run so command-line and workbench results are comparable. Treat newly
installed large models as feasibility candidates until repeated cases show a
quality gain; see the [70B smoke test](model-feasibility-2026-09-28.md).

**Acceptance:** no mode/model combination silently fails; every failed run has a
clear trace; Fixed remains the recommended sourced mode unless a harder case shows
a reproducible Agentic or Supervisor gain.

## 2. Durable phone runs

Persist a run ID, status, bounded event stream, result, and cancellation state.
Let a phone reconnect and resume viewing an in-progress run without restarting
the model call. Add explicit run timeouts and a single active heavy local-model
run by default, with queued jobs visible in the UI. Keep completed results in the
conversation even if the tab closes. Back up the conversation and corpus databases
with a tested restore path.

**Acceptance:** close and reopen the Home Screen app during a Supervisor run;
progress and the final answer reappear once, and Stop remains effective.

## 3. Make Supervisor earn its cost

Add a routing check that sends simple grounded questions to Fixed and simple
ungrounded questions to Direct. Show why Supervisor was chosen and what each
specialist contributed. Run at most two independent specialists concurrently only
after tests establish the Mac mini's memory and latency headroom. Give one bounded
repair attempt when a synthesis fails review, with the unsupported claim shown to
the manager. Verify the final cited claims against the cited passages, including
web pages, before displaying a sourced answer.

The router should be host-owned, with a visible **Auto** choice and manual override.
It will inspect the task's need for sources, current project permissions, expected
complexity, and web consent, then select a workflow and an eligible model using
per-category evaluation results and latency limits. The host records its choice,
reason, alternatives, and final outcome so bad choices can be corrected. A model
is an inference engine; a specialist agent is a bounded role with tools and a
specific obligation. Route to specialists only when the task needs their work.
Keep the current explicit workflow and model selections until the evaluation set
has enough repeated cases to set useful thresholds. Future Claude or ChatGPT
provider adapters can participate in the same route contract when API access is
added; no hosted model API is part of this phase.

**Acceptance:** Supervisor improves quality on multi-part cases without adding
several model calls to simple cases; a failed review produces an actionable reason
or a supported partial answer, never a confident unsupported claim.

### Performance investigation: 70B web research

A phone run listing World Series winners took 88.9 seconds with the local 70B
model and web research. A reproduced 70B run took **92.0 seconds**: public
search and page gathering took **1.4 seconds**; its **one** model request took
**90.6 seconds**, with 2,141 input tokens, 404 output tokens, and zero reported
cached tokens. The findings sent to the model were 8,527 characters. This path
uses one bounded search followed by one logical answer call; the several-agent-
pass explanation does not apply to this run. Local web search already limits
itself to five results and fetches text from at most two pages. The new run trace
separates search and model wall time, but the model time still combines prompt
processing and token generation.

Next, run the same cited question across the 70B, Qwen3 30B A3B, GPT-OSS 20B,
and Gemma models. Record cold and warm runs separately, including model load
time, prompt processing and generation durations, request attempts, answer
accuracy, citation support, context length, and peak memory pressure. Use native
Ollama timing or first-token streaming measurements to separate prompt reading
from generation before optimizing either one.

Then test small, cited search excerpts against larger page context, prompt reuse
or caching where the active runtime supports it, and an MLX-backed route if it
passes the same tool and citation checks. Compare answer accuracy and source
support as well as speed. Keep the faster MoE models as candidates for routine
web research; route to 70B only when repeated evaluation shows a useful gain.
Test a concise-answer preference for long enumerations, since output length is
part of local-model latency. Measure whether it reduces time without omitting
requested items or weakening citations; do not simply truncate the answer.
Also test a bounded-context Qwen3 30B A3B variant: the first matrix sampled about
45 GB loaded at its current large context, even though its answers were fast.
Measure whether a 16K or 32K context reduces memory pressure without truncating
the web evidence needed for a correct answer.

The 32K Qwen variant passed the same eight Fixed sample checks as the original
and loaded at about 22 GB. It is now the selected local chat model. However, a
long web-list trial revealed wrong winner/loser rows and a false 2025 uncertainty
claim from Qwen; a prompt-only revision did not reliably repair it. Before any
automatic web routing, freeze a representative search snapshot, preserve table
row and column meaning during page extraction, and check each factual row
against its cited source. Recheck answer length and latency after those support
checks are in place.

**Acceptance:** the Models page can show the measured time breakdown and paired
quality/latency tradeoff for this case; any caching or context reduction preserves
the correct year-by-year answer and checkable sources.

## 4. Expand capabilities through narrow permissions

Start with useful read-only tools: adjacent-section source expansion, searching
past chats within the current project, and opening a cited public page. Keep
retrieved files and web text as data rather than instructions. Then introduce one
write action at a time, beginning with a proposed project note: preview the exact
change, request approval, apply with an idempotency key, and record an audit event.
Use the same contract before adding file edits, browser actions, or connectors.
Avoid general shell or unrestricted network access in the chat agent.

**Acceptance:** every action's scope, inputs, result, and approval are visible;
replay cannot duplicate a write; untrusted source text cannot expand permissions.

## 5. Better research and multimodal input

Extend source ingestion to images using local OCR/vision, preserve page or image
provenance, and make source previews easy on a phone. Add local speech transcription
as an alternative to browser dictation. Keep the current per-question web consent
and expose whether a claim came from a search excerpt or a fetched page. Improve
retrieval with a reranker only after measuring a gain on the frozen evaluation set.

**Acceptance:** a photo, PDF, and public page can each be cited back to a visible
source location; users can tell when data leaves the Mac for hosted search.

## 6. Product finish and remote access

Continue physical-iPhone checks for keyboard, safe areas, scrolling, long tables,
source cards, and accessibility at small text widths. Keep Tailscale as the private
remote route. Add owner authentication, session handling, rate limits, and recovery
before considering exposure beyond the tailnet. Make setup and model labels clear
without requiring users to understand endpoint configuration.

**Acceptance:** the main task can be completed one-handed at phone width, and
remote access has a documented recovery and security story.

## Immediate next slice

Implement milestones 1 and 2 in that order. A small evaluation set will reveal
which agent failures deserve fixes; durable runs then make slow Supervisor work
usable from a phone. Only expand tools after both are observable and recoverable.

Background: [local model baseline](local-model-baseline.md),
[evaluation contract](evaluation.md), [agent boundary](agentic-workflow.md), and
[implementation roadmap](roadmap.md). External engineering guidance also favors
measured agent evaluations and explicit tool boundaries:
[Anthropic, *Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents),
[Anthropic, *Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents),
and [OWASP LLM Top 10 (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/).
