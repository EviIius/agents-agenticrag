# Workbench: what comes after Phase 3

**Written:** 3 October 2026, against commit `66a8c6b` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build

Phases 0 to 3 and T1 are closed. This folder holds the review of where the app stands and the plans for what to build next, in the same form as `docs/SPEC.md` and `docs/TRANSCRIPTION-SPEC.md`: exact files, exact rules, acceptance criteria, evidence.

Place these files at `docs/next/` in the repository.

---

## 1. What is here

| File | What it is | Read it if you are |
|---|---|---|
| `DESIGN-AND-NAMING-REVIEW.md` | Findings on theme, motion, visual detail, product name and labels, each with evidence | Jake, Codex |
| `REPO-REVIEW.md` | Findings on code structure and safety nets; what is solid; why the roadmap is in this order | Jake, Codex |
| `PHASE-4-POLISH-AND-MOTION.md` | The motion system and visual fixes; 4C also changes send feedback and draft rollback. | Codex |
| `PHASE-5-EVERYDAY-CHAT.md` | Presets, PDF and Word attachments, folders, automatic backups, clearer saving, model names | Codex |
| `PHASE-6-TRANSCRIPTION-T2-AND-RUNTIMES.md` | Transcript clean-up and glossary (already designed as T2); an optional second runtime | Codex |
| `PHASE-7-LIBRARY.md` | Answer from your own files, with citations. The first retrieval feature. | Codex |
| `PHASE-8-RESEARCH.md` | Multi-step web research with tool calls. **Draft; gated.** | Jake first, then Codex |
| `QA-REQUIREMENTS.md` | The gates every checkpoint must pass so nothing existing breaks | Codex |
| `CODEX-PROMPT.md` | One prompt per phase, ready to paste | Jake |

## 2. The short version

**Design.** The theme is right and stays. The app does not feel premium yet for one main reason: its dialogs, menus, sheets and popovers have animation classes that compile to nothing, because the package that defines them was never installed. So almost nothing moves. Phase 4 replaces them with a small CSS motion system, adds motion to sending, waiting, streaming, thinking and searching, and fixes about twenty visual details where the production UI drifted from the spec.

**Name.** "Workbench" was always a placeholder. Recommended: **Atelier**. Alternative: **Cobalt**. Renaming touches display strings only.

**Code.** The foundation is sound. Three structural risks are paid down at the start of Phase 4, before any feature work: one 1,124-line component that everything flows through, a design page that shows lookalikes instead of the real components, and unpinned dependencies.

**Features.** Four directions, in order of risk: everyday chat improvements, transcript clean-up, a document library, and research. Each is additive. Research has a gate it may not pass, and that is acceptable.

**QA.** The core (chat, search, transcription) is frozen. Sixteen gates apply at every checkpoint, including three new automated ones: the API may only grow, existing database rows may not change, and prompts may not change without an eval.

## 3. Decisions Jake needs to make

| ID | Decision | Needed before | Recommendation |
|---|---|---|---|
| J1 | Product name | Phase 4, checkpoint 4D | Atelier |
| J2 | Rename "Chat settings" to "Chat controls", and Settings › "Search" to "Web search" | Phase 4, checkpoint 4D | Yes to both |
| J5 | Let large surfaces (sheets, drawers, sidebar) animate for up to 320 ms; small ones stay at 200 ms or less | Phase 4 | Accepted with the reviewed Phase 4 plan on 4 October |
| J6 | Which second runtime, if any | Phase 6, checkpoint 6B | Skip unless there is one you will actually run |
| J3 | Approve the `sqlite-vec` dependency | Phase 7 | Yes. It is the only new dependency in all five phases. |
| J7 | Library eval targets | Phase 7, checkpoint 7B | As proposed in Phase 7 §8 |
| J8 | Which embedding model | Phase 7 | Your choice; pull it in Ollama |
| G5 | Approve the Research spec and its targets | Phase 8 | After the gate results are in |

## 4. Order and stops

```text
Phase 4   4A guardrails ─ 4B motion foundation ■ 4C conversation motion ─ 4D visual fixes, copy, icon ■
Phase 5   5A presets, saving, names ■ 5B documents ■ 5C folders, backups ■
Phase 6   6A clean-up and glossary ■ (6B second runtime ■, optional)
Phase 7   7-0 probe ■ 7A library storage ■ 7B retrieval and answers ■
Phase 8   8-0 gate ■ 8A loop ■ 8B interface and evals ■

■ = stop for Jake's review
```

6A does not depend on Phase 5 and can be moved earlier. Phase 8's gate cannot open before 17 October 2026: `SPEC.md` §F4 requires two weeks of daily use after Phase 3.

## 5. What these plans deliberately leave out

Deep research jobs, the library inside Research, automatic model routing, MCP, voice, image generation, sharing and multiple users. `REPO-REVIEW.md` §5 says why each one waits.

## 6. Limits of this review

Everything here comes from reading the repository at one commit and viewing its committed, synthetic screenshots. Nothing was run. The live app and the phone were not examined. Line numbers are correct for `66a8c6b` and will drift. Name collision checks were one web search each. Eval targets for Phases 7 and 8 are proposals, not measurements.

## Current Research checkpoint — 7 October 2026

The calendar hold was waived for isolated 8-0/8A only. Accepted 7B remains live.
The [8A consistency report](../PHASE-8A-CONSISTENCY-REPORT.md) retains all failed
experiments and the unmet 13/15 repeatability/support gates; 8B is not authorized
by a failed gate. The [model and picker proposal](../MODEL-OPTIONS-AND-PICKER.md)
is documentation only: Jake deferred downloads and requested continued 8A work.
