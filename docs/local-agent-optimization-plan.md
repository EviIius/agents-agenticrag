# Local agent optimization decision (29 Sep 2026)

This is the implementation decision after reviewing `docs/validator/REVIEW-2026-09-28.md`
and `docs/validator/AGENT-ROADMAP-2026-09-28.md`. Keep the validator's findings and
its original roadmap as references; this document records the route we will take.

## Decision

Use **Ollama as the reliable current workbench runtime** and make **LM Studio a first-class
alternative** behind one provider contract. Model/runtime pairs compete on measured
task success, citation support, tool-call correctness, memory use, and latency. A
runtime's advertised tool support is only a candidate signal, not proof of quality.

Keep Qwen3 30B-A3B as the default chat model for now. Test GPT-OSS 20B as an alternate
tool model, Gemma 4 12B for vision, and Llama 3.3 70B as a deliberate escalation.
Qwen3 Embedding 0.6B remains the embedding model until a retrieval comparison says
otherwise. On this Mac, a single native tool-call smoke test produced a valid call
from Qwen3 30B-A3B in 1.7 s and GPT-OSS 20B in 3.5 s; most of that was model loading.
This is one prompt, not a reliability benchmark or a reason to change the default.

## Order of work

1. **Measure reality.** Build a private evaluation set from the material actually used:
   100–300 documents, at least 2,000 passages, and about 150 questions with document
   paths and exact gold quotes. Include follow-ups, long PDFs, tables, near-duplicates,
   changed document versions, unanswerable cases, and multi-hop questions. Freeze a
   locked split before tuning. Record retrieval recall, quote recall, grounded-answer
   quality, tool errors, abstentions, median and tail latency, and loaded memory.
   Treat the current 24 questions as a development smoke test only.
2. **Make existing modes reliable.** Keep Auto off unless a held-out paired comparison
   shows a clear gain. Fix format bugs, use one final answer gate for all sourced modes,
   and verify model-supplied verbatim quotes against immutable source text. Quote
   presence verifies provenance, not that the quote logically supports a claim; a
   separate claim-support evaluation remains necessary. Protect the loopback server
   with a Host allowlist and later bind project scopes to a verified owner identity.
3. **Unify the host contract before the loop.** Introduce a provider turn type with
   text, native tool calls, thinking and usage; keep JSON actions as a fallback.
   Use the same host-side schema, scope, permission and budget checks for both paths.
   Add model/runtime contract probes and measure thinking on/off at fixed answer
   budgets. Do not turn thinking on globally.
4. **Add dynamic routing behind a flag.** Start with the current Fixed fast path,
   reuse its evidence, and escalate only when retrieval or the answer gate signals
   uncertainty. Keep Direct, Fixed, Agentic and Supervisor as manual overrides and
   baselines. Build the common agent loop incrementally; retire a pipeline only after
   it matches or beats that baseline on the locked split. Skills remain guidance,
   loaded on demand, and grant no tool authority.
5. **Expand tools one at a time.** Add conversation-aware retrieval, bounded source
   reading, then web search under per-run consent. Add MCP and write actions only
   after the host can pause for approval, resume, audit actions and contain untrusted
   tool output. More specialist agents come last; each needs measured task gain.

## Gmail pilot

Gmail is a useful **separate agent task benchmark**, not a substitute for document
retrieval evaluation. Start with a read-only sample of recent inbox threads and
classify each as action required, personal, receipt, newsletter, or uncertain.
Show the user a review queue with the message ID, sender, subject, proposed action,
reason and confidence. Measure false-archive and missed-action rates against human
labels. Then allow one approved batch to add a label or remove `INBOX`, with a saved
undo plan. Do not send, permanently delete, mark spam or change filters in the
first pilot. The model may propose actions; the app decides what can execute.

Google's official Gmail MCP server is currently a **developer preview** requiring
program enrollment and Google Cloud OAuth setup. It supports search, read, drafts
and label actions, but its published setup asks for `gmail.readonly` and
`gmail.compose`; we should verify its exact archive/label behavior before relying
on it. A narrow Gmail API adapter is an alternative if the MCP preview is unavailable
or cannot express the approved action. Gmail's `gmail.modify` scope can modify
labels; it is a restricted scope, so authorization and data handling need care.

The app, not the model runtime, should host MCP so permission checks, traces and
approvals stay in one place. Email text is untrusted: never let content from a
message choose a new destination, tool, recipient, URL or approval rule. Keep Gmail
read-only until the review queue and owner authentication work end to end.

## Gates

- No automatic model switch from the existing eight-question report. A future
  router needs a locked split, at least 30 answerable and 10 unanswerable cases per
  model, a positive paired confidence interval, and a meaningful benefit when a
  candidate is much slower. The current evaluator does not yet compute paired
  intervals, so automatic switching remains effectively disabled.
- No claim that citation numbers imply factual support. Quote matching is a first
  check; evaluate sentence-level support separately.
- No new tool or sub-agent becomes default until it improves the locked task set
  without unacceptable failure or latency regressions.
- No Gmail write capability before explicit, itemized approval and an undo path.

## Primary references

- [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling) and
  [thinking](https://docs.ollama.com/capabilities/thinking)
- [LM Studio tool use](https://lmstudio.ai/docs/developer/openai-compat/tools)
- [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Google Gmail MCP preview](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server)
- [Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes) and
  [batch label modifications](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/batchModify)
