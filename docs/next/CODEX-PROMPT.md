# Prompts to paste into Codex

One phase at a time. Each prompt assumes the files in this folder are at `docs/next/` in the repository.

Before the first prompt, tell Codex your decisions (see `README.md` §3). At minimum: J1 (name) and J2 (two label renames). If you have not decided, say "keep Workbench" and "no renames"; both can be done later without rework.

---

## Phase 4: polish and motion

```text
Read AGENTS.md, docs/SPEC.md Part G and Part H, then everything in docs/next/: README.md,
DESIGN-AND-NAMING-REVIEW.md, REPO-REVIEW.md, PHASE-4-POLISH-AND-MOTION.md and QA-REQUIREMENTS.md.

Build Phase 4 from docs/next/PHASE-4-POLISH-AND-MOTION.md. It has four checkpoints: 4A, 4B, 4C, 4D.
Stop after 4B and after 4D and give me docs/PHASE-4-REPORT.md using the SPEC §H4 template plus the
sections in QA-REQUIREMENTS §8, with evidence for every P4-AC and every gate in QA §3.

Start with §2 (add the amendments to SPEC.md and AGENTS.md verbatim), then 4A.1 (the baseline),
before changing any code.

My decisions: J1 = <name, or "keep Workbench">. J2 = <yes / no>. J5 = yes.

Rules that matter most here:
- This phase changes how the app looks and moves, not what it does. No file under server/app
  changes. No endpoint, schema, prompt, model call, table or dependency is added.
- CSS only. No JavaScript animation library and no tw-animate-css. All motion lives in
  web/src/styles/motion.css and uses the tokens in §4.1.
- 4A must produce an empty screenshot diff. If the LiveAppShell split (4A.6) is not green in one
  full e2e run, revert it and continue.
- Performance thresholds do not move. If streaming word animation (C4) misses the frame budget,
  ship the caret without it and report the numbers.
- Every animation is removed under prefers-reduced-motion and under Reduce motion: Always.
- Any edit to an existing test goes in the test-diff ledger. Do not delete, skip or loosen a test.
- Internal identifiers never change: the launchd label, the WORKBENCH_ prefix, data paths,
  workbench.db, cache and storage keys, event names.
- Screenshots and recordings use synthetic data only.
```

## Phase 5: everyday chat

```text
Read AGENTS.md, docs/next/PHASE-5-EVERYDAY-CHAT.md and docs/next/QA-REQUIREMENTS.md.

Build Phase 5. Three checkpoints: 5A, 5B, 5C. Stop after each with docs/PHASE-5-REPORT.md
(§H4 template plus QA §8). Add the AGENTS.md amendment in §1 first.

Rules that matter most here:
- Additive only: new tables, new nullable columns, new routes. The additive-API check, the
  migration test against the Phase 3 fixture database and the prompt-hash test must pass.
- No new packages and no new model calls. pypdf is already installed; read Word files with the
  standard library.
- A preset copies values into a chat. It never changes which pipeline runs and never sends a
  parameter it does not store.
- Document text and filenames are private, like recordings: not in logs, fixtures, screenshots or
  reports. Use the synthetic files in §3.5.
- Web search and transcription behavior must not change. make eval-web offline must match baseline.
- 4.3 (fork a chat) is optional. Do it only if everything else in 5C is finished and green.
```

## Phase 6: transcript clean-up, glossary, and a second runtime

```text
Read AGENTS.md, docs/TRANSCRIPTION-SPEC.md, docs/SPEC.md §C5–C6,
docs/next/PHASE-6-TRANSCRIPTION-T2-AND-RUNTIMES.md and docs/next/QA-REQUIREMENTS.md.

Build checkpoint 6A (T2) exactly as TRANSCRIPTION-SPEC §6–§7 describe, with the changes in
PHASE-6 §1.1. Stop and report as a "T2 checkpoint" section in docs/PHASE-T-REPORT.md.

Do not start 6B until I name the runtime (J6). When I do: record fixtures from the real runtime
first, then build only that adapter per SPEC §C5.

Rules that matter most here:
- The clean-up prompt is used exactly as written. One call per chunk, no retries, no judge.
- Clean-up runs only on a local connection and never blocks chat.
- Never commit, log or screenshot real glossary content, a real recording or transcript text.
- Ollama behavior must be byte-identical after 6B: existing adapter fixtures and request captures
  pass without edits.
```

## Phase 7: Library

```text
Read AGENTS.md, docs/SPEC.md Part E and Part F, docs/next/PHASE-7-LIBRARY.md and
docs/next/QA-REQUIREMENTS.md.

Start with checkpoint 7-0 (the probe) and stop. Do not write product code until I have seen
artifacts/phase-7/probe.json and confirmed J3 (sqlite-vec), J7 (eval targets) and J8 (embedding
model).

Then 7A (storage, ingestion, Settings › Library; chat untouched) and stop. Then 7B (retrieval,
the composer toggle, cited answers, the eval harness) and stop. Report as docs/PHASE-7-REPORT.md.

Rules that matter most here:
- Library or Search, never both in one message. The server enforces it.
- The host retrieves; the model writes. One chat-model call per library answer.
- Do not edit search/pipeline.py or rebuild message_sources. Import search building blocks.
- The answer prompt in §5.3 is used exactly as written and is hash-guarded.
- Library text goes only to a local connection by default, and never into logs, fixtures,
  screenshots or reports. The eval corpus is invented.
- If an eval target is missed, report the numbers and stop. Do not tune prompts to pass.
```

## Phase 8: Research

```text
Read AGENTS.md, docs/SPEC.md Part F, docs/next/PHASE-8-RESEARCH.md and
docs/next/QA-REQUIREMENTS.md.

Do gate 8-0 only: the research eval set, the single-shot baseline, and the tool-call probe on my
installed models. No product code. Stop and give me the results under artifacts/phase-8/gate/ and
a one-page summary. I will decide whether to continue.

Rules that matter most here:
- Native tool calls only. If no model I use daily reaches 95% valid calls, say so and stop.
- With Research off, requests to the runtime stay byte-identical.
- If Research does not beat the single-shot baseline by the agreed margin, it does not ship.
```

---

## If something goes wrong

```text
Stop. Do not work around it. Tell me: which gate or acceptance criterion failed, the exact
command and output, what you believe the cause is, and the options you see. Do not change a
test, a threshold or a prompt to get past it.
```
