# Review of Claude's native agent-loop proposal

18 October 2026. Reviewed the supplied plan against live-source `e7ffea2b`,
Hermes `4acc379f`, PydanticAI `d596ad53` and Research `7737046`.

## Verdict

**Proceed with N0 on Aether's native adapter, using its existing Pydantic.**
The engineering reason is strong: one payload builder, one HTTP client path,
existing thinking/keep-alive semantics, shared native capacity and no extra
framework dependencies. Ollama supports native tool calls and tool-result history;
Pydantic supplies argument validation and schemas.
([Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling),
[Pydantic models](https://pydantic.dev/docs/validation/latest/concepts/models/))

These mechanisms do not establish factual reliability or accelerate Qwen's token
generation. N0 is an offline implementation checkpoint; N1/N2 must measure the
new contract and real retrieval before the app can offer it.

## What the evidence supports, with corrections

- Hermes' pinned Ollama path enforces a minimum context of **64,000** tokens;
  our trial used 65,536. Its first task passed. Its direct reference failed, and
  Jake stopped that trial. This is an integration-fit decision, not proof that
  Hermes could not answer correctly.
- PydanticAI's four passing tasks and missing H05 citation are feasibility
  observations. The trial did not specify Aether's numbered citation syntax.
  That is a contract weakness, not proof that PydanticAI causes citation failures.
  It also does not prove that every framework would fail H05 identically.
- The fixture searches return all records **of the requested kind**, not all web
  and Library records indiscriminately. Neither trial evaluates real retrieval
  quality or proves an answer-quality advantage over another framework.
- P0's 26 packages are the **total isolated environment**, not necessarily 26 new
  packages in the app. The resolved Pydantic 2.14.1 does not prove the app would
  have to upgrade its 2.13.5. The native design avoids that integration question.
- P0 used the OpenAI-compatible endpoint; exact thinking levels and keep-alive
  behavior were not qualified there. This does not prove that endpoint cannot
  support them. A custom PydanticAI model could wrap the native adapter later.
- P0's usage-logging error was incorrect use of the installed API. There was no
  tested previous version demonstrating an upgrade regression. It should not be
  presented as a measured framework-induced app regression.
- Research failed completeness, support and repeatability gates. The later
  evidence-selector experiments also failed, but removing that layer alone does
  not establish that evidence gathering or unsupported answers are solved.
  Port transport/controls, not its prompts, selector, UI or qualification claims.
- A future N1 failure would not automatically identify the model or prompt as
  its cause. Inspect the native request, parser, tool results and host behavior
  first. Changing frameworks without that diagnosis would remain unjustified.

## Plan decisions and corrections

D1/D2 are covered by Jake's request to assess and follow the sound proposal.
Hermes and PydanticAI stay preserved as stopped reference branches. N0 is isolated
on `codex/native-agent-loop`, with no new package, native inference or deployment.

The plan's §7 combined authorization also grants N1, but §8 asks only for D1/D2
and explicitly stops after N0. The actual AGENTS amendment grants **N0 only**.
D3's model calls, N2, N3 and D5 tag removal remain unapproved.

D4's proposed median 120 s / p90 240 s are **looser** than the original 90 s /
200 s targets. They remain a pending decision. The prior completeness,
≥13/15 complete-case repeatability, support, citation, injection and budget gates
are preserved; no failed Research gate is waived or relabeled a pass.

### N1 fixture conflict to resolve before inference

Original H04 combines W1/W2 public specifications with the L1 Library budget.
P0 offered both web and Library tools. The new plan deliberately prohibits that
combination, so the literal original retrieval arrangement cannot be reused.

Recommended proposal: run H04 with Library tools only, placing unchanged W1/W2/L1
synthetic source text into that fixture's local collection. Preserve the old
corpus/case files and outcomes and record the new retrieval-scope mapping
separately. This would test the same facts/calculation without weakening privacy;
it would further preclude claims of a controlled framework-quality comparison.
**This mapping is proposed, not applied or approved for native execution.**

N1 also needs explicit admission for an experimental 32K profile, without claiming
that N0's scripted tests qualified a real model digest. Do not invent a probe pass
or add an unbudgeted probe outside D3's ceiling. Production offering remains gated
on actual qualification evidence.

### Deadline interpretation

The plan asks for a closing call after limits and also specifies a hard 180-second
budget. N0 allows at most one closing call, without tools, **within remaining
time**. It starts no new model request after the hard deadline has expired;
partial text/steps and a time-limit status remain. This preserves the hard budget.

## Implementation and maintenance cost

N0 preserves explicit sampling and model-default thinking; exact off/low/medium/
xhigh native payload values are tested with scripted transport. No capability
comes from a model name. Tools, source numbers, arguments, budgets and permissions
belong to the host; text from tools cannot grant new permissions.

The complete implementation is larger than the plan's approximate 200-line
estimate: the runner, contracts/calculator, source persistence and frozen prompt
are roughly 700 physical lines including imports/comments/spacing. Much of the
validation, source catalogue, SQL, scheduler and cancellation work would still be
needed with a framework. Review this maintenance cost honestly; do not install a
second loop to hide it or grow it into routing, MCP or multi-agent orchestration.

The citation checker validates issued references and flags a missing citation.
It cannot prove that a cited passage supports a claim, or that the answer is
complete. Those remain mandatory semantic evaluation checks at N1/N2.

## Other supplied status claims

Source review confirms the manual-title-before-first-send overwrite remains in
`api/chats.py`: its fallback update does not check `title_source='user'`, even
though the later title helper does. Workflows home still advertises “search”
while that block remains disabled. Both remain on the follow-up list; neither is
mixed into N0's dormant agent implementation.

Photo-reference editing is not integrated into the app. The earlier I0 image
worker trial did include one isolated synthetic reference edit; that was not a
production photo-editing workflow. Other disabled workflow blocks and the
Research product remain outside this checkpoint.

## Review boundary

N0's technical results and QA limitations are in `AGENT-LOOP-N0-REPORT.md`.
A successful offline checkpoint is not authorization for N1 calls, a beta setting,
a main merge, real-user data testing or deployment. All earlier failed trials and
original thresholds remain intact.
