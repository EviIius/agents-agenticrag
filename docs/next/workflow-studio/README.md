# Workflow Studio

**Written:** 12 October 2026, against commit `dce4c49` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build

A redesign of Workflows: no Chat / Workflows tabs, and a drag-and-drop block builder in the style of Copilot Studio, backed by a real graph engine on the existing durable runs.

Place this folder at `docs/next/workflow-studio/` in the repository.

| File | What it is | For |
|---|---|---|
| `WORKFLOW-STUDIO-SPEC.md` | The full spec: findings, information architecture, Studio layout and interactions, block catalog, visual design and tokens, motion, running, phone, architecture, API, checkpoints, QA, decisions | Jake, Codex |
| `prototype.html` | Interactive reference prototype with fake data. Open it in a browser: drag blocks, connect ports, press + on a connection, select a block, press Run and approve the email. Toggle theme and reduced motion at the bottom of the sidebar. | Jake, Codex |
| `reference/*-fake.png` | Screenshots of the prototype at 1440 and 390 px, dark and light, with the real fonts | Codex |
| `CODEX-PROMPT.md` | One prompt per checkpoint, ready to paste | Jake |

## Decisions needed (spec §14)

| ID | Decision | Before | Recommendation |
|---|---|---|---|
| J-W3 | Remove the tabs and the standalone Workflows page; add Workflows and Images to the sidebar | WS-A | Yes |
| J-W1 | Allow your own model calls inside workflow blocks | WS-B | Yes |
| J-W2 | Approve `@xyflow/react` (lazy-loaded); keep its attribution | WS-C | Yes; keep |
| J-W4 | Phones edit through the Outline | WS-C | Yes |
| J-W5 | Templates become read-only graphs you copy; the old fixed builder goes | WS-C | Yes |
| J-W6 | Allow `stroke-dashoffset` in the motion guard | WS-D | Yes |
| J-W7, J-W8 | Branching blocks; Classify eval targets | WS-E | Yes; as proposed |

## Order

```text
WS-A shell ■  WS-B engine ■  WS-C Studio editing ■  WS-D running on the canvas ■  WS-E knowledge and logic ■
■ = stop for Jake's review
```

WS-A changes no server code and can ship first.
