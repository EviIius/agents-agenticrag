# Prompts to paste into Codex

One checkpoint at a time. Each prompt assumes this folder is at `docs/next/workflow-studio/` in the repository, including `prototype.html` and `reference/`.

Before the first prompt, give Codex your decisions from `WORKFLOW-STUDIO-SPEC.md` §14. WS-A needs only J-W3. WS-B needs J-W1. WS-C needs J-W2, J-W4 and J-W5.

---

## WS-A: one shell, no tabs

```text
Read AGENTS.md, docs/SPEC.md Part G and Part H, docs/next/QA-REQUIREMENTS.md, then
docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md (all of it) and open
docs/next/workflow-studio/prototype.html in a browser. The prototype shows the intended
layout and motion; where it and the spec differ, the spec wins.

Build checkpoint WS-A only (spec §3, §4 and §12). Stop with docs/WORKFLOW-STUDIO-WS-A-REPORT.md
using the SPEC §H4 template plus QA §8, with evidence for WS-AC1 to WS-AC4 and every gate.

My decisions: J-W3 = yes.

Rules that matter most here:
- No server change. No endpoint, schema, prompt, model call, table or dependency is added.
- Remove SectionTabs.tsx and every use. Workflows and Images become sidebar rows (§3.1), in the
  expanded sidebar, the collapsed rail and the phone drawer.
- Workflow routes render inside the app shell (§3.2). /workflows becomes the home in §4, built
  from the existing runs API and the two existing templates.
- The current builder keeps working, moved to /workflows/new?template=… inside the shell, with
  today's behavior. Nothing a user can do today may be lost at this checkpoint.
- The Studio sidebar-to-rail behavior waits for WS-C.
- Existing chat behavior, drafts and the composer image action do not change.
- Every edit to an existing test goes in the test-diff ledger. Screenshots use synthetic data
  and "fake" in the file name.
```

## WS-B: the graph engine

```text
Read AGENTS.md, docs/next/QA-REQUIREMENTS.md and docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md
§6, §11, §12, §13 and Appendix C. Read server/app/workflows/ (jobs.py, templates.py, schemas.py,
source.py), server/app/api/workflows.py, server/app/capacity.py and migration 010 first.

Build checkpoint WS-B only. Add the AGENTS.md amendment from §14 first, with today's date and
only the parts I approved. Stop with docs/WORKFLOW-STUDIO-WS-B-REPORT.md (§H4 plus QA §8),
evidence for WS-AC5 to WS-AC9 and every gate.

My decisions: J-W1 = <yes / no>.

Rules that matter most here:
- Additive only: migration 011 as written in §11.3, new tables, new nullable or defaulted
  columns, new routes. G-6 (API only grows) and G-7 (rows unchanged) must pass.
- The legacy POST /api/workflows/runs path and its execution code stay untouched and working.
- Blocks in this checkpoint: Start, Generate text, Transcribe recording, Clean up transcript,
  Create images, Approve or edit, Save results. Each reuses the existing performer code.
- The parity test (§11.6, WS-AC7) is the gate: both templates as graphs must record
  byte-identical model messages, params and context length, and identical image prompts and
  seeds, versus the legacy path on the fake runtime. If it fails, stop and tell me.
- Templating (§11.4): references and the tagged filter only. No expressions. No truncation.
  No hidden text around user prompts. Template prompts keep their hashes (G-8).
- One block at a time per run; native work leases the existing Capacity per invocation.
- Never poll. Persisted run.updated events replay; node.progress and node.text are ephemeral.
- Recording, document and library text and filenames never appear in logs, fixtures,
  screenshots or reports.
```

## WS-C: Studio editing

```text
Read AGENTS.md, docs/next/QA-REQUIREMENTS.md and docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md
§5, §6, §7, §8, §10 and §11.1. Open docs/next/workflow-studio/prototype.html and the images in
docs/next/workflow-studio/reference/. Match their layout, spacing, states and motion.

Build checkpoint WS-C only. Stop with docs/WORKFLOW-STUDIO-WS-C-REPORT.md (§H4 plus QA §8),
evidence for WS-AC10 to WS-AC17 and every gate, plus the motion videos in §13.2.

My decisions: J-W2 = <approve; keep / hide attribution>. J-W4 = <yes / no>. J-W5 = <yes / no>.

Rules that matter most here:
- One new dependency: @xyflow/react, exact pinned version (latest 12.x that is at least two
  weeks old), loaded only in the lazy Studio and run-view chunks. Import only its base.css.
  The initial bundle must not grow (G-4). Report the Studio chunk size.
- Use the existing tokens plus the new category tokens in §7.1. Extend the contrast script to
  cover them. shadcn primitives and existing components first; cmdk for Quick add; vaul for
  phone sheets.
- graph.ts functions are pure and unit-tested, and validation rules give identical results
  to the server's graph.py on shared fixtures (WS-AC15).
- Keyboard and screen-reader path: Inspector › Connections must allow full wiring without a
  pointer; Outline view is the accessible view. Axe zero serious or critical (G-5).
- All motion in web/src/styles/motion.css, within the Phase 4 limits; everything disappears
  under both reduced-motion triggers. Never leave a transform transition on during dragging.
- Phones edit through Outline mode (§10). The canvas on phones is read-only.
- Remove WorkflowCanvas.tsx and WorkflowForm once the Studio replaces them; old runs still
  open through the run page.
- Every new state is on /design, built from production components (G-14).
```

## WS-D: running on the canvas

```text
Read docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md §7.3, §8, §9 and §13, and look at
reference/run-writing-*, run-paused-* and run-complete-* and the prototype's Run button.

Build checkpoint WS-D only. Stop with docs/WORKFLOW-STUDIO-WS-D-REPORT.md (§H4 plus QA §8),
evidence for WS-AC18 to WS-AC24 and every gate, plus the motion videos in §13.2.

My decisions: J-W6 = <yes / no>.

Rules that matter most here:
- Run states come only from the server (v2 stream). The canvas never invents progress.
- Follow mode yields to manual panning for 5 seconds (§8.2).
- Run from here and Test this block reuse outputs only when the per-block config hash is
  unchanged (§9.5). Test runs are hidden from Recent runs.
- SSE disconnect and server restart mid-run must recover the correct state (WS-AC20, WS-AC23).
- Add stroke-dashoffset to ALLOWED in scripts/check_motion.py only if I approved J-W6;
  otherwise the active connection is a static brand line.
- Meeting packs and other text from private sources keep the draft-for-review label.
```

## WS-E: knowledge and logic blocks

```text
Read docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md §6.3 (Search the web, Search my files,
Read a document, If / else, Compose text, Classify), §11.4 and §13.3.

Build checkpoint WS-E only. Stop with docs/WORKFLOW-STUDIO-WS-E-REPORT.md (§H4 plus QA §8),
evidence for WS-AC25 to WS-AC29, the Classify eval report and every gate.

My decisions: J-W7 = <yes / no>. J-W8 = <targets as proposed / changed to …>.

Rules that matter most here:
- Extract search_sources(query, limit, fetch) from search/pipeline.py without changing chat
  search. G-9: make eval-web offline replay equal or better on every aggregate, no case flips.
- The Classify prompt is new, frozen and hashed (G-8), with the eval in §13.3 before release.
- Search my files and Read a document are private sources: the local-connection rule applies.
- Ship the three new templates only after each runs end to end on the fake runtime.
```
