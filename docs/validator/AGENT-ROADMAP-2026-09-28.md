# Agent roadmap: from four modes to one dynamic agent (28 Sep 2026)

**For Codex to review.** Claude wrote this as the validator; Jake decides. It builds on `REVIEW-2026-09-28.md`, and that review's fix-first items still come first.

**Checked against:** the working tree on 29 Sep at 02:29 UTC. File references point to that tree.

## The goal

Jake wants an LM Studio-style local model host with agents that behave like Claude's or ChatGPT's:

- You type a request.
- The system decides how much work to do: answer directly, search your sources, research the web, use tools or delegate.
- It shows what it's doing, asks when it needs you, and stays out of the way otherwise.

All of this runs on open models on a 64 GB Apple-silicon Mac.

## Where the app stands today

| Area | Today (verified in code) | Target |
|---|---|---|
| Who decides the approach | The user picks one of four modes. "Auto" only swaps the model, and only in Fixed mode. | A router picks the route for each turn and escalates when needed. |
| How the agent calls tools | The agent sends one action per step as a JSON object (`response_format`). `ChatProvider.complete()` returns a plain string, and `ChatMessage` has no tool role (`providers/base.py`). | Native tool calls with tool-result messages, with the JSON-action format kept as a fallback. |
| The models' own tool calling | Actively suppressed: the retry prompt says "Do not call tools" (`openai_compatible.py:154`). | Used whenever the model and runtime pass the contract suite. |
| Thinking | Forced off for Ollama (`reasoning_effort: "none"`, `openai_compatible.py:96`). | Effort set per turn: off, low, medium or high. |
| Tools | `search`, `lookup` and `calculate`. Web search exists only inside Supervisor. | A tool registry covering corpus, web, memory, `ask_user`, a to-do list, delegation, MCP and a sandbox. |
| Conversation | Fixed and Agentic ignore chat history (`server.py:916–980`). Supervisor sees the last 4 turns, and only when web search is off. | Every route works across turns. |
| Sub-agents | Hard-coded roles, including `ad_strategist`. They run one after another and are chosen by English regexes (`supervisor.py:418`). | Agent definitions stored as data, plus a `delegate` tool. |
| Skills | A `SKILL.md` registry with hashes. This is the same open format Claude uses. | Keep it, and load skill bodies only when needed. |
| Context | Each step rebuilds one big user message from all the evidence plus the last 8 tool results (`agent.py:494`). | An append-only transcript that works with prompt caching, plus a budget and compaction. |
| Permissions | Read-only tools only, and no approval flow. | Tool annotations, permission modes and inline approvals. |
| Streaming | Direct streams tokens. The agent modes stream progress events only. | Stream tool calls, a collapsed thinking view and the final answer. |
| Runtime | One inference at a time (`openai_compatible.py:67`). Capability checks are Ollama-only (`runtimes.py:147`). | A capability registry that covers Ollama, LM Studio, llama.cpp and vLLM. |

## Realistic expectations

Local models of 12–30B parameters are much weaker than frontier models at long chains of tool calls. Expect:

- wrong arguments;
- loops;
- stopping too early;
- ignoring tool results.

A Claude-like experience is achievable; Claude-like autonomy isn't yet. So this app's harness has to do more of the work than Claude's does:

- fewer tools per turn;
- strict schemas;
- host-side checks;
- short step budgets;
- cheap routes by default.

The router should always prefer the cheapest route that passes the evals.

## Target architecture

```
message ─► Router (rules first; learned later) ─► Route {preset, effort, model, tools, budget, reasons}
                                                      │
                ┌─────────────────────────────────────┘
                ▼
          One agent loop, used by every route
          model turn ⇄ tool calls ⇄ Host gateway (validate · permission · execute · truncate · log)
                │                     ├─ corpus: search, read, expand, list
                │                     ├─ web: search, fetch (per-question consent)
                │                     ├─ calculate · python sandbox (later)
                │                     ├─ memory: read, propose (user approves)
                │                     ├─ ask_user · todo
                │                     ├─ delegate (sub-agent, later)
                │                     └─ MCP servers (later)
                ▼
          Answer gate (citations, quotes, numbers) ─► stream to UI
```

The four modes become route presets:

- **Direct:** no tools.
- **Fixed:** one search is fetched up front, and the model answers once with no loop. This is the fast path.
- **Agentic:** the corpus tools plus a step budget.
- **Supervisor:** a route that exposes `delegate`.

The presets stay available as manual overrides and as the baselines for evaluation.

## The list

**Priority:**

- **Now:** safe work that adds no new capability and unblocks the rest.
- **Next:** new behaviour behind a feature flag, measured against Fixed.
- **Later:** new authority or reach; needs Jake's approval first.

### A. Harness foundation

**A1. Provider interface v2 (Now)**
- Add `chat(messages, tools, tool_choice, response_schema, reasoning, max_tokens, stream)`.
- It returns `ModelTurn{text, tool_calls[], thinking, usage, finish_reason}`.
- `ChatMessage` gains a `tool` role, `tool_call_id` and `tool_calls`.
- Keep `complete()` as a thin wrapper so the existing workflows don't change.
- *Done when:* all current tests pass through the wrapper, and new adapter tests use recorded responses from Ollama, LM Studio and llama.cpp, including streamed tool-call fragments.

**A2. Native tool calling, with the JSON-action format as fallback (Now)**
- For each model and runtime pair, choose `native` or `json_action` from the registry (A4).
- **Native:** send the tool schemas, parse `tool_calls`, and return results as `tool` messages.
- **Fallback:** today's `ACTION_SCHEMA`.
- Host validation is identical in both.
- Stop suppressing tool calls on the native path only.
- *Done when:* the agent test suite passes in both formats, and the contract suite (G2) records which format each model does better with.

**A3. Thinking and effort control (Now)**
- Replace the global `reasoning_effort: "none"` with a per-call setting: off, low, medium or high.
- Map it to each runtime:
  - Ollama `think`: true/false, or low/medium/high for GPT-OSS;
  - OpenAI-compatible `reasoning_effort`;
  - Qwen3's separate Instruct and Thinking models.
- Give thinking its own token budget so it can't use up the answer's tokens. That starvation is why thinking was turned off.
- Keep thinking in the trace and show it collapsed in the UI. Don't feed it back into later turns unless the model family requires it.
- *Done when:* a thinking model answers within budget at every level, and the trace counts thinking tokens separately.

**A4. Model capability registry (Now)**
- Keep one record per installed model:
  - runtime and configured context length;
  - native tools yes/no, thinking modes, vision;
  - role: chat, embedding or rerank;
  - loaded memory;
  - measured prompt and generation tokens per second;
  - contract-suite scores (G2);
  - time of the last probe.
- Sources: Ollama `/api/show` capabilities, LM Studio's REST model list and llama.cpp `/props`. Our contract tests have the final say.
- It replaces `ollama_supports_vision` and the Ollama-only routing.
- *Done when:* the Models page and the router (section C) both read from it.

**A5. One agent loop (Next)**
- `AgentLoop` repeats: build the context, take a model turn, run any tool calls through the gateway, and append the results.
- It stops at a final text answer or when a budget runs out.
- Direct, Fixed, Agentic and Supervisor become presets.
- Keep the old workflow classes until the presets match them, then delete them.
- *Done when:* the presets reproduce current results within noise on v1, v2 and v3, and the old classes have no callers.

**A6. Tool registry and gateway v2 (Now)**
- Declare each tool as data:
  - name, description and JSON schema;
  - annotations: `read_only`, `destructive`, `idempotent`, `open_world` (the same hints MCP uses);
  - cost class, output limit and permission policy.
- The gateway runs every call through the same steps:
  1. Validate the arguments.
  2. Check permissions.
  3. Execute with a timeout.
  4. Truncate or paginate the output, with a hint on how to get more.
  5. Emit an event.
- Run calls in parallel only when they're read-only and the runtime has parallel slots.
- *Done when:* `search`, `lookup` and `calculate` are migrated with no change in behaviour.

**A7. Run states and steering (Next)**
- Runs in `run_store` gain these states: `queued`, `running`, `waiting_for_user` (approval or question), `paused`, `completed`, `failed`, `stopped` and `interrupted`.
- A message sent during a run is queued and injected at the next turn boundary. This is the "steer" behaviour Claude has.
- *Done when:* a run can pause for approval, survive a page reload and resume.

**A8. Fix-first items from the review (Now)**
- Stop plan and review failures from crashing the whole run.
- Drop the wasted planning call.
- Add the shared answer gate. The unified loop's final answer must pass through it.

### B. Context engineering

**B1. Append-only, cache-friendly transcript (Next)**
- Order the prompt as: system prompt, then tool definitions, then stable memory, then the turns, appended in order.
- Never rewrite earlier content between steps. Today the full rebuild at `agent.py:494` defeats prompt-prefix caching in llama.cpp, LM Studio and Ollama.
- *Done when:* agent steps after the first show cached prompt tokens and less prompt-processing time. The provider already records cached tokens when the runtime reports them.

**B2. Context budget per model (Now)**
- Budget = configured context minus the reserved answer and thinking tokens.
- Split it across: system and tools, memory, conversation, evidence, tool results.
- Enforce it before every call. Runtimes differ on overflow, and some silently truncate the start of the prompt.
- *Done when:* long runs never exceed the budget, and each call logs its allocation.

**B3. Clean tool results (Now)**
- Every result puts IDs first and keeps its text short.
- Results are cut at a limit, with a hint such as "call `read_source(id, offset)` for more".
- Errors say what to do next.
- *Done when:* no tool result exceeds its limit, and every error tells the model how to fix the call.

**B4. Compaction (Later)**
- Near the budget, summarise older turns into a structured note: the task, decisions made, evidence IDs and open obligations. Keep the recent turns as they are.
- Evidence IDs must survive compaction so citations still resolve.
- *Done when:* a 20-step run finishes on a 16K-context model with its citations intact.

**B5. Conversation-aware retrieval (Now)**
- Rewrite follow-ups into a standalone question before retrieval, using a fast model or rules over the last few turns.
- Pass the recent turns to the loop.
- *Done when:* a follow-up like "what about the nachos one?" retrieves the right source. Add 10 follow-up cases to eval v3.

**B6. To-do tool instead of the up-front planner (Next)**
- The model keeps a live task list (like Claude's TaskCreate and TaskUpdate), and the host tracks it.
- The model can't finish until every item is resolved or explicitly marked unanswerable.
- This keeps the obligation-ledger idea from the design brief, but makes it drive the search as the run goes rather than only being checked at the end.
- *Done when:* obligation coverage comes from the to-do state, not from a single `finish` payload.

**B7. Skills loaded on demand (Next)**
- Only skill names and descriptions sit in context. A `load_skill(name)` tool fetches the body.
- Keep the hashing and the rule that skills grant no authority.
- *Done when:* 20 installed skills cost almost nothing until one is loaded.

### C. Routing ("Auto")

**C1. A route object (Now)**
- `Route = {preset, effort, chat_model, toolset, budgets, reasons[]}`.
- Logged on every run and shown in the UI as "Why this route".
- *Done when:* every run record has a route.

**C2. Rules router v1 (Next)**

The rules, cheap and deterministic:

- An image or attachment goes to a vision model.
- No sources and no web consent goes to Direct.
- Explicit intent ("search the web", "think hard", "use my notes") is honoured.
- A follow-up to a sourced answer keeps the same route.
- Anything else takes the Fixed fast path.

Don't depend on English keyword regexes like the ones at `supervisor.py:418`.

*Done when:* route accuracy on the router eval (G3) beats "always Fixed".

**C3. Escalate instead of predicting (Next)**
- Start cheap, and escalate only on evidence:
  - Fixed escalates to the Agentic loop when the answer gate fails, retrieval confidence is low or the question has several parts. The loop reuses the evidence already gathered, with no restart.
  - Agentic escalates to web tools only when the question is unresolved and web consent was given.
- This makes the app dynamic without needing a smart router, and it works well with small models.
- *Done when:* each escalation is logged with its reason, and median latency on simple questions is unchanged.

**C4. Learned router v2 (Later)**
- A small local classifier: a 1–4B model with a schema, or a simple feature model.
- Train it on logged signals: user overrides, thumbs up/down, answer-gate outcomes and latency. OpenAI says GPT-5's router is trained on similar signals: model switches, preference rates and measured correctness.
- Ship it only if it beats C2 + C3 on the locked router eval.

**C5. Choose models by capability and measured quality (Next)**
- Replace `model_routing.py`'s Fixed-only formula.
- Pick the cheapest model that meets the route's needs (native tools, context, thinking) and passes that route's quality bar on eval v3's locked split, with confidence intervals.
- Never decide on fewer than 30 cases.
- *Done when:* every choice is explained, for example "Qwen3 30B: passes the tools contract, 2.1 s median".

**C6. Manual override stays first-class**
- The mode, effort and model pickers stay.
- Every override is logged as a signal for the router.

### D. Tools, in order

**D1. Corpus tools v2 (Now → Next)**
- `search_sources` with filters: collection, path, date.
- `read_source`: a span, with pagination. It absorbs `lookup`.
- `expand_context`: fetch adjacent chunks.
- `list_sources`.

**D2. Web tools in the loop (Next)**
- `web_search` and `web_fetch` become ordinary tools, not just a Supervisor specialist.
- Keep the per-question consent and the private-address checks.
- Add fetch allow and deny lists.
- Extract pages in a way that keeps tables intact.
- Mark all web text as untrusted (E3).

**D3. Chat and memory tools (Next)**
- `search_chats`, scoped to the project.
- `read_memory`.
- `propose_memory`: the user approves before anything is saved. Unverified claims are never saved automatically.

**D4. `ask_user` (Next)**
- The model can ask one clarifying question, and the run waits for the answer (A7).
- Limit: 1–2 questions per run.

**D5. `delegate` (Later)** — see section F.

**D6. MCP client (Later)**
- **Role:** the app becomes an MCP host.
- **Transports and spec:** support stdio and Streamable HTTP, targeting the 2026-07-28 spec. That spec removed the `initialize` handshake and makes every request self-contained, which makes a stdlib-only client simpler.
- **Controls:**
  - enable each server individually;
  - keep a per-tool allowlist;
  - respect tool annotations;
  - cache `tools/list` using `ttlMs`;
  - treat all MCP output as untrusted.
- **Why the app, not LM Studio:** LM Studio can run MCP itself through its `/api/v1/chat` integrations. Keep the app as the host anyway, so permissions, evidence and traces stay in one place.
- *Done when:* a read-only server (for example, read access to one folder) works end to end, and anything not read-only asks for approval.

**D7. Python sandbox (Later; Jake decides)**
- Code execution for data questions such as CSVs and charts.
- A container with no network, CPU/memory/time limits, an ephemeral working folder and only explicitly chosen input files mounted.
- Outputs come back as files.
- `Dockerfile` and `compose.yaml` are a starting point.
- This is never a general shell.

**D8. File outputs (Later)**
- `create_file` writes Markdown, CSV or a chart PNG into a per-project outputs folder, with versions, shown in the UI.
- It's a write action, so the approval policy applies.

**D9. Write actions (Later)**
- One at a time, each going through: preview, approve, apply with an idempotency key, audit. This is milestone 4 in `next-phase-plan.md`.
- The first one: save a project note.

**Tool design rules, for every tool:**

- Expose few tools per route; small models get worse as tools are added.
- Use clear, namespaced names (`corpus.search`, `web.fetch`) and descriptions with an example.
- Return short, high-signal text, plus only the IDs the host needs for citations.
- Write errors that say how to fix the call.

### E. Safety and permissions

**E1. Permission modes per project (Next)**
- The modes: `read_only` (the default), `ask` (approve anything that isn't read-only) and `auto` (read-only and pre-approved tools run without asking).
- Approvals appear inline in the chat and are audited.

**E2. The host enforces tool annotations (Next)**
- `destructive` tools always ask.
- `open_world` tools (network) need consent.
- `read_only` tools may run in parallel.

**E3. Treat outside content as tainted, and block exfiltration (Next; important)**
- **The rule:** once web pages, MCP output or uploaded-file text enter the context, any tool that sends data out (a free-form web search, a fetch of an arbitrary URL, an open-world MCP tool) needs approval or an allowlisted domain.
- **What never goes out:** project memory and private source text, verbatim.
- **Why:** an agent with private data, untrusted content and a way to send data out can be tricked into leaking.
- Web runs already leave out project memory; generalise that.
- *Done when:* injection fixtures that try to smuggle a private passage into a search query or URL fail (G4).

**E4. Real owner authentication (Later, before sharing access)** — see review P2-7.

**E5. Budgets and kill switches (Now)**
- Per-run limits on steps, wall time, tool calls and tokens.
- Stall detection (already exists).
- Per-tool timeouts.
- Stop always works (already true).

### F. Sub-agents

**F1. A sub-agent is a tool (Later)**
- `delegate(agent, task, budget)` returns a summary plus evidence IDs.
- The child gets a fresh context, a limited toolset and its own budget.
- Children can't delegate further (keep this rule).

**F2. Agent definitions as data (Later)**
- Stored as `.agenticrag/agents/<name>.md`: frontmatter with name, description, tools, model tier, effort and `max_steps`, then the prompt, the same way skills work.
- These replace the hard-coded `corpus_researcher`, `quantitative_analyst` and `ad_strategist`.
- Ship only the corpus and web researchers by default.

**F3. Parallel only where it pays (Later)**
- On a 64 GB Mac, parallel sub-agents compete for one GPU and the same memory.
- Allow two at once only when the runtime has parallel slots and both fit in memory, and measure it.
- Anthropic's multi-agent research system used about 15× the tokens of a chat. It suits broad research that splits into parallel parts, not most personal-RAG questions.

**F4. Retiring Supervisor**
- Keep it until F1–F3 match it on the multi-part v3 cases, then remove it.

### G. Evaluating agents (extends the v3 plan)

**G1. Trajectory logging and replay (Now)**
- Record every model turn and tool result.
- Replay a run with the recorded tool outputs, to debug or re-score without calling any tools.

**G2. Model contract suite (Now)**
- Run per model × runtime × format (native vs JSON).
- A local suite in the style of the Berkeley Function Calling Leaderboard (BFCL), with these checks:
  - a single call;
  - choosing among tools;
  - parallel calls;
  - multiple turns with tool results;
  - irrelevance: the model should *not* call a tool;
  - argument types;
  - a long tool output;
  - an instruction injected into a tool output.
- Results feed the registry (A4).
- BFCL is fine for shortlisting models; our suite makes the final call.

**G3. Router eval set (Next)**
- 150+ prompts, each labelled with acceptable and unacceptable routes.
- Include follow-ups, images, web-needed and unanswerable prompts.
- Metrics: accuracy, over-escalation, under-escalation, latency.

**G4. Agent task suite (Next)**
- Cover:
  - multi-hop corpus tasks from v3;
  - web tasks against frozen snapshots;
  - recovery from tool errors;
  - injection and exfiltration attempts;
  - `ask_user` cases.
- Metrics: task success, citation support, steps, tool errors, tokens, time and injection success rate. The target injection success rate is 0.

**G5. Paired comparisons with confidence intervals (Next)**
- A new capability ships only if it beats the cheaper baseline on the locked split with a paired-bootstrap confidence interval above zero.
- Otherwise it stays behind a flag.

### H. Runtime and performance

**H1. Which models stay loaded (Next)**
- Within 64 GB, keep a fast router model, the main model, the embedding model and the reranker loaded.
- The 70B loads only on explicit request, evicts the others and shows a warning.
- Set keep-alive/TTL per runtime.

**H2. Parallel slots and a queue (Later)**
- Configure runtime parallelism (`OLLAMA_NUM_PARALLEL`, llama.cpp `-np`).
- Interactive work goes ahead of background work.
- Keep one heavy run at a time (already true).

**H3. Timing breakdown (Now)**
- For every model call, record queue wait, prompt processing, generation and cached tokens.
- For every tool call, record its time.

**H4. Runtime parity tests (Next)**
- The same agent contract must pass on LM Studio, Ollama and llama.cpp.
- Document each runtime's quirks. For example, llama.cpp needs `--jinja` for tool calls, and heavy KV-cache quantisation hurts tool calling.

### I. UI (ties into the design handoff)

- **I1.** Auto is the default, with an effort control (Quick / Balanced / Deep). The old modes move under Advanced.
- **I2.** A live timeline of tool calls with human-readable titles (SPEC §3.4), with thinking collapsed.
- **I3.** Inline approval and `ask_user` cards that can be answered from the phone.
- **I4.** "Why this route" and "Escalated because…" disclosures.
- **I5.** The Tools & agents page lets you:
  - turn tools on and off;
  - manage MCP servers;
  - set the permission mode per project;
  - edit agent definitions.
- **I6.** Steering: typing during a run queues the message for the next turn.

## What not to build yet

- A general shell tool or unrestricted browser automation.
- Recursive sub-agents, or more hard-coded specialists.
- Automatic memory writes.
- A learned router before C2 + C3 have been measured.
- A framework such as LangGraph. The plain loop plus A7 is enough until pausing and resuming across processes becomes painful.
- Anything tuned against eval v2 (see the review).

## Order of work

Each slice starts only after the previous slice's evals pass on the locked split.

- **Slice 0 (from the review):**
  - turn auto-routing off by default;
  - fix the reproduced bugs;
  - add the answer gate;
  - extend the eval v3 harness.
- **Slice 1 (foundation, nothing new for the user yet):** A1, A2, A3, A4, A6, B2, B3, B5, C1, E5, G1, G2, H3.
- **Slice 2 (the unified loop, behind a flag):** A5, A7, B1, B6, C2, C3, C5, D1, G3, G4, G5, I1, I2, I4.
- **Slice 3 (more reach; each item needs Jake's OK):** D2, D3, D4, E1–E3, B7, H1, I3, I5, I6.
- **Slice 4 (big new authority):** D6 MCP, D7 sandbox, D8 files, D9 writes, F1–F4, C4, B4, H2, E4.

## Decisions for Jake

1. **Primary runtime:** LM Studio, Ollama, or both equally? The vision says "LM Studio"; the code is Ollama-first.
2. **Code execution (D7):** yes or no? It's the biggest jump in capability, and the biggest risk.
3. **First MCP servers:** which matter most — files, calendar, GitHub, a browser?
4. **Default permission mode:** read-only or ask?
5. **Thinking in the UI:** show it collapsed (recommended), or hide it?
6. **Hosted models:** may a hard turn go to Claude or OpenAI through their APIs, or must everything stay local? The route contract can support either; the current plan has no hosted API in this phase.

## Prompt for Codex (Slice 1)

```
Read docs/validator/REVIEW-2026-09-28.md and docs/validator/AGENT-ROADMAP-2026-09-28.md.
Finish Slice 0 from the review first if it isn't done. Then do Slice 1 only:
A1, A2, A3, A4, A6, B2, B3, B5, C1, E5, G1, G2, H3.

Constraints:
- No new user-visible capability in this slice. Existing Direct/Fixed/Agentic/
  Supervisor behaviour and all current tests must keep passing.
- Stdlib only, zero-build UI, additive /api/v1 changes, CSP unchanged.
- Host validation is identical for native tool calls and JSON actions; native
  calls never grant authority.
- Thinking tokens get their own budget and are stored in traces, not fed back.
- Record fixtures from real Ollama, LM Studio and llama.cpp responses for
  adapter tests (including streamed tool-call deltas); don't hit a live
  runtime in unit tests.
- Contract suite (G2) runs from the CLI: `agenticrag contract --all-installed`,
  writes a JSON report the registry (A4) reads, and never mutates settings.
- Don't tune prompts against examples/evaluation-v2.jsonl.

Report: changed files, new tests, the contract-suite table for every installed
model (native vs JSON), and the timing breakdown for one Fixed and one Agentic
run.
```

## Sources

- [Anthropic: How the agent loop works (Agent SDK)](https://code.claude.com/docs/en/agent-sdk/agent-loop). Covers the turn cycle, parallel read-only tools, permission modes, hooks, compaction and sub-agents.
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [OpenAI: Introducing GPT-5 (router design and training signals)](https://openai.com/index/introducing-gpt-5/)
- [MCP 2026-07-28 specification release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [LM Studio: Using MCP via API](https://lmstudio.ai/docs/developer/core/mcp)
- [LM Studio: Tool use](https://lmstudio.ai/docs/developer/openai-compat/tools)
- [Ollama: Thinking](https://docs.ollama.com/capabilities/thinking)
- [Ollama: Streaming (thinking and tool calls)](https://docs.ollama.com/capabilities/streaming)
- [llama.cpp: Function calling](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Simon Willison: The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
