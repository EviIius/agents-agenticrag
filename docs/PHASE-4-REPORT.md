# Phase 4 report — working checkpoints

## Summary

4A.1–4A.5 are validated: contract, data, prompt and motion guards; locked dependency resolution; production components on `/design`; a shared engine-reported audio extension list; removal of duplicate fixtures and the tracked `.DS_Store`.
Production presentation is unchanged: all 50 synthetic screenshots match the original build pixel for pixel.
The app-shell split (4A.6) and motion foundation (4B) are next. Phase 4 is not complete; 4C/4D and the Atelier rename have not started.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Baseline | Pass | `artifacts/phase-4/baseline/check.txt`, `e2e.txt`, `bundle.json` |
| 4A.1–4A.5 guardrails and production fixtures | Pass | `artifacts/phase-4/4a-components/check.txt`; 212 Python, 36 frontend, 56 contrast checks |
| Complete component regression run | Pass | `artifacts/phase-4/4a-components/e2e-final.txt`: 223 passed, 3 existing skips |
| No production pixel changes | Pass | `artifacts/phase-4/4a-components/screenshot-diff-final.json`: 50 exact matches |
| Dependency resolution unchanged | Pass | `artifacts/phase-4/baseline/dependency-constraints.json`, `npm-ci.txt` |
| 4A.6 split | Pending | Prepared outside checkout; one full regression run required after application |
| 4B foundation | Pending | Outside-checkout synthetic preflight: 24 tests pass; not accepted as the checkpoint's full regression run |
| Phone review | Not checked | Required at the 4B stop |

## Changed files

- Server tests: `test_phase4_guards.py`, `test_prompt_hashes.py`, synthetic Phase 3 database fixture.
- Scripts: API compatibility, motion and privacy guards; database fixture generator; synthetic capture and pixel comparison tools.
- Web: dependency ranges; production fixture bindings; shared audio extensions; removal of five duplicate UI implementations; finite-animation settlement before screenshots/axe.
- Docs: reviewed `docs/next/` roadmap, authorization in `AGENTS.md`/`SPEC.md`, this report and checkpoint evidence.
- No `server/app` file changes and no database migration.

## Deviations from SPEC.md

The keyboard walkthrough exposed an existing Chromium race during model-switch/new-chat navigation. Original HEAD reproduced it in 1 of 3 isolated repetitions. The test now awaits the new-chat heading and finite motion and additionally verifies toggle focus before pressing Enter. No assertion, timeout, budget or skip was weakened. Six isolated repetitions then passed, followed by the complete green suite. See `keyboard-original-head.txt`, `keyboard-settled.txt` and `artifacts/phase-4/test-diff-ledger.md`.
An intermediate full run was interrupted during review to preserve the original picker behavior for cached models while offline; only the final complete invocation counts as the gate.

## Runtime observations

Synthetic fake runtime only. No new runtime, dependency, model call, sampling parameter or prompt. No live recording or transcript was captured.

## Test output

- Baseline: `make check` — 207 Python / 36 frontend; `make e2e` — 223 passed / 3 existing skips.
- 4A.1–4A.5: `make check` — 212 Python / 36 frontend; build succeeds; `make e2e` — 223 passed / 3 existing skips in one complete 15.7-minute invocation.
- API, prompt, ordinary-request and synthetic migration guards pass. Motion guard reports existing violations until 4B replaces the dead classes.

## Budgets

| Build | Initial JS gzip | Limit |
|---|---:|---:|
| Original HEAD | 224,491 bytes | 256,000 |
| 4A.1–4A.5 | 222,902 bytes | Original ± 2 KiB |

Resolved dependency versions and integrity values are unchanged. Caret ranges constrain future updates; the lockfile and `npm ci` reproduce this build.

## Screenshots

`artifacts/phase-4/baseline/*-fake.png` and `artifacts/phase-4/4a-components/*-fake.png`: 390/1440, light/dark, synthetic chat, web, reasoning, model picker, settings, palette, sources, sidebar and transcript states. Captures were inspected as contact sheets; all content is synthetic.

## Migrations, rollback and evals

No migration; rollback rehearsal is not applicable. The generated Phase 3 fixture preserves hashes projected onto existing columns. No server search/run/provider or model-facing prompt change, so no new web eval is required. Existing web checks remain part of the full regression run.

## Known limitations carried forward

VoiceOver was reported not working and deferred by Jake; it has not passed. The 3 October iOS keyboard issue recovered after a phone restart; its cause remains unproven. Three pre-existing browser skips remain documented in the Phase 3 evidence.

## Open questions for Jake

None at this intermediate commit. The review stop is after 4B; 4C/4D remain pending.
