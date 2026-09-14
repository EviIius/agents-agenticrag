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

The capability inspector also lists hosted `web_search`. It is not part of the base gateway. The
Supervisor may construct that specialist only for an OpenAI chat configuration and a run whose
request contains explicit web consent. Returned URLs are displayed separately from immutable
corpus citations.

## Quality and evaluation

Planning and critique improve process discipline but do not manufacture intelligence. Evaluate
each candidate local model on frozen cases for tool-selection accuracy, invalid action rate,
evidence recall, citation resolution, unsupported-claim rate, review false accepts/rejects,
termination, latency, and resource use. Keep fixed RAG as the default until agentic RAG shows a
measured advantage worth its extra latency and complexity.
