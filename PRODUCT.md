# AgenticRAG Product Context

## Product register

AgenticRAG is a product UI: a local-first developer control plane for configuring, inspecting, and running retrieval-augmented agents against private corpora.

## Primary user and purpose

The primary user is a developer and researcher operating open-source models locally. They need one place to:

- connect chat and embedding runtimes without hidden cloud fallback;
- inspect model, store, ingestion, and corpus readiness;
- see exactly which tools and skills an agent can use, with room for plugins later;
- ingest private sources and ask questions through fixed or bounded-agentic RAG;
- inspect citations, evidence, plans, tool calls, critic decisions, timing, and budget use;
- launch the workbench reliably on a workstation or in a small self-hosted deployment.

The architecture should preserve a clear backend/frontend seam so a simpler, nontechnical interface can be added later without replacing the core runtime.

## Brand personality

Calm, precise, capable, and inspectable. The interaction model should feel familiar to users of LM Studio and the ChatGPT desktop app: conversation is central, configuration is legible, and advanced details are close at hand without overwhelming the main task.

Avoid sci-fi terminal styling, gamer neon, generic SaaS card grids, excessive gradients, anthropomorphic agent theater, and opaque automation. Technical depth should come from visible evidence and state, not visual noise.

## Interface principles

1. **Conversation is the workspace.** Asking, reviewing an answer, and opening its evidence are the dominant flow.
2. **Capabilities are explicit.** Tools, skills, and future plugins have visible enabled/disabled state, descriptions, source, and constraints.
3. **Local means local.** Provider endpoints, network boundaries, and fallback behavior are always clear.
4. **Progressive disclosure.** Everyday controls stay simple; traces, hashes, scopes, and advanced deployment details are available in contextual inspectors.
5. **Operational truth over decoration.** Status surfaces must derive from real configuration and runtime checks.
6. **Backend/frontend separation.** The HTTP API is versioned and usable independently of the bundled interface.

## Accessibility baseline

Target WCAG 2.2 AA. All core workflows must support keyboard navigation, visible focus, semantic landmarks and labels, screen-reader status announcements, reduced motion, sufficient contrast, and status indicators that do not rely on color alone.

## Quality bar

- A developer should reach a useful readiness diagnosis within one minute of launch.
- A successful local setup should require one command after environment configuration.
- No capability is implied unless the backend reports it.
- Errors explain what failed, what remains safe, and the next corrective action.
- The interface remains usable at laptop widths and scales down to a future simplified experience.
