# Bounded agentic workflow

## What “agent” means here

The language model does not receive ambient computer authority. It receives a structured view of
the question, checkable obligations, selected skills, retained evidence, prior tool summaries, and
remaining budget. It proposes exactly one schema-constrained action. Application code decides
whether that action is valid and performs it.

This supports the same fundamental pattern used by modern hosted agents—model-directed tool use,
reusable instructions, stateful iteration, structured outputs, and review—without claiming that a
local model has the same reasoning quality, training, context window, or tool-use reliability.

The Supervisor workflow adds manager-style orchestration: one model creates bounded assignments,
the host calls specialist agents as tools, and the manager retains responsibility for synthesis.
This is distinct from an unrestricted handoff: specialists receive only their assigned task, have
no recursive delegation capability, and cannot expand the host tool or skill allowlists.

## Control flow

```text
question
  -> obligation and skill plan
  -> choose one action
       -> search authorized corpus
       -> lookup bounded span from an observed source
       -> calculate safe arithmetic
       -> finish with per-obligation evidence
  -> host citation and obligation validation
  -> independent evidence-review prompt
       -> accepted answer
       -> feedback into remaining bounded steps
       -> explicit abstention at hard cap
```

The workflow never persists or exposes private chain-of-thought. `purpose` fields are short action
summaries. Critical behavior comes from decomposition, external evidence, explicit support status,
critique, and deterministic host checks rather than requesting hidden reasoning text.

For a single factual corpus question, the host starts with authorized retrieval and reduces the
plan to one checkable obligation. Supervisor uses the fixed retrieval path for a single simple
corpus assignment. Multi-part questions still use bounded model-directed actions or specialist
delegations. This keeps routine questions responsive while preserving citation validation.

The web workbench saves conversations in a local SQLite database beside the corpus. The most
recent 20 completed turns, capped to 1,500 characters per message, are provided to Direct mode
after a page reload or model change. New chat starts with no earlier turns, while older chats can
be reopened or deleted. A question explicitly asking about earlier chat questions uses that
conversation history even when a grounded mode is selected. Other grounded questions still use
the current question and authorized corpus evidence. Project memory is a separate set of notes
the user explicitly saves, edits, or removes. It is passed to later model calls in that project
as context, never as citable corpus evidence, and omitted from web-enabled runs to avoid sending
private notes into external search queries. The harness does not infer or write memories on its
own.

## Skill format

```markdown
---
name: evidence-analysis
description: Analyze multi-part questions against retrieved evidence.
---

Instructions used only when this skill is selected.
```

The registry reads direct `<skills-root>/<directory>/SKILL.md` files from the configured project
root and, when the default is used, `.agents/skills`. It follows resolved-path containment checks,
accepts only UTF-8, caps file/count/context sizes, accepts `name`, `description`, and standard
`metadata` frontmatter, rejects duplicate names, records provenance, and hashes the exact bytes.
Skills are operator configuration, so review them like code before installation. They shape model
behavior but never add tool, filesystem, network, or account permissions.

## Current tool boundary

| Tool | Authority | Hard checks |
| --- | --- | --- |
| `search` | Read authorized chunks in one collection | Existing SQL ACL predicates, query/search/evidence limits |
| `lookup` | Read a parsed source span | Source must have appeared in search, same collection, ACL before fetch, offset/length cap |
| `calculate` | Arithmetic only | AST allowlist, depth/exponent/literal/result limits; no names, calls, attributes, or code |

There is deliberately no shell, arbitrary code execution, URL fetch, filesystem mutation,
credential access, or write connector. Adding any state-changing tool requires a separate preview,
approval, idempotency, and audit design.

The capability inspector also lists `web_search`. It is not part of the base gateway. The
Supervisor may construct that specialist only for a run with explicit web consent and an
available local or hosted search provider. Local search reads a bounded set of snippets and up
to two public HTTPS pages with private-address checks. Returned URLs are displayed separately
from immutable corpus citations.

## Quality and evaluation

Planning and critique improve process discipline but do not manufacture intelligence. Evaluate
each candidate local model on frozen cases for tool-selection accuracy, invalid action rate,
evidence recall, citation resolution, unsupported-claim rate, review false accepts/rejects,
termination, latency, and resource use. Keep fixed RAG as the default until agentic RAG shows a
measured advantage worth its extra latency and complexity.
