# Workbench: repository review

**Date:** 3 October 2026 · **Commit:** `66a8c6b` · **Author:** Claude (validator)

**Read in full:** `web/src` (components, hooks, stores, lib, styles), `server/app` (api, db and migrations, providers, runs, search pipeline, config, main), `scripts/`, `Makefile`, `AGENTS.md`, `README.md`, `docs/SPEC.md` Parts B, C5–C6, F, G, H, the phase reports, and the built assets in `server/app/static`.

**Skimmed or listed only:** `server/app/transcribe`, `server/app/search/{selection,planner,extract,fetch}.py`, the test bodies (I read every test title, not every assertion), `server/evals`, `transcribe/`.

**Not run:** nothing was executed. No tests, no build, no live app.

---

## 1. Verdict

The foundation is sound and the method is right. The rules that matter were followed in the code, not only in the docs: capabilities come from the runtime, unset sampling parameters stay unset, runs are server tasks that survive a closed tab, the host runs the search pipeline and the model only plans and writes, and private recordings never reach Git.

The weaknesses are in the web app's structure and in a few missing safety nets. None of them is a bug in a core flow. All of them make the next five phases riskier than they need to be, which is why Phase 4 starts with a checkpoint that changes nothing visible.

## 2. What is solid

| Area | Why it can be trusted |
|---|---|
| Provider layer | One `Adapter` protocol; `ToolCall`, `role="tool"` and `embed()` are already reserved for later phases. Error mapping and timeouts match the spec. |
| Runs | `RunManager` keeps an event log per run with replay from any index; cancel, restart recovery and a per-connection queue are all there. Messages are flushed once a second while streaming. |
| Context budgeting | Tokens-per-character is learned per model from real usage and reused; oldest history is dropped first; overflow is an explicit error. |
| Search | A single planner call, deterministic ordering (search rank, never fetch-completion order), bounded reads, budget-aware selection, sources persisted exactly as sent. Changes were driven by a recorded eval with failures kept on file. |
| Security | Loopback bind, host and origin checks, SSRF guard with redirect revalidation, API docs disabled, attachments path-checked, the service worker never caches `/api`. |
| Transcription | External engine as a subprocess, sequential jobs, uploads streamed to disk, audio temporary by default, a web guard enforced on the server. |
| Deployment | Backup before install, plist rollback, label and route preserved, `/design` off in production. |
| Tests | 207 Python tests, 36 unit tests, about 220 browser cases on two engines against a fake runtime, a homemade coverage gate, a contrast gate, an API-type drift check. |

## 3. Findings

Severity is about risk to future work, not about today's behavior.

| ID | Severity | Finding | Evidence | Addressed in |
|---|---|---|---|---|
| R1 | **High** | **`LiveAppShell.tsx` does everything.** 1,124 lines; 15 `useState` calls, 8 refs, 8 queries and 9 effects; sending, regenerating, uploads, model operations, shortcuts, drag and drop, history, menus and all layout in one component. Every later phase adds state here. | `web/src/components/app/LiveAppShell.tsx` | Phase 4, 4A.6 |
| R2 | **High** | **`/design` is partly a set of lookalikes.** Five components exist only for the design route, and three production components carry fixture-only branches (`fake-*` model lists, "notes.md · fixture", "foundation preview" panes) that ship in the bundle. The real message row is not on `/design` at all. | Import graph of `AssistantMessage`, `UserMessage`, `Thread`, `ReasoningBlock`, `ChatSettingsPanel`; `Composer.tsx`, `ModelPicker.tsx`, `SettingsDialog.tsx` | Phase 4, 4A.5 |
| R3 | **High** | **Overlay animations are dead code.** Utility classes from a package that is not installed. | See the design review, F1 | Phase 4, 4B |
| R4 | Medium | **Twenty-one web dependencies are declared as `"latest"`.** `npm ci` is safe because the lockfile is committed. Any `npm install` can pull a new major of Streamdown, Vite, TypeScript, ESLint, Sonner, Vaul and others at once. | `web/package.json` | Phase 4, 4A.2 |
| R5 | Medium | **No backup between deployments.** The database is backed up when deploying and never otherwise. Since 3 October it is the only copy of every transcript, because audio is removed after transcription. | `scripts/deploy.py`; AGENTS amendment of 3 October | Phase 5, 5C |
| R6 | Medium | **Phase 3 closed without one fully green browser run.** 220 passed and 1 failed; the failure was fixed and re-run alone. Reported honestly, but the suite is the safety net for everything that follows. | `docs/PHASE-3-REPORT.md`, "Test output" | QA, G-2 |
| R7 | Medium | **Three guarantees rest on convention, not on a test:** prompts do not change without an eval; the API only grows; an upgrade leaves existing rows untouched. | No prompt hash test; no OpenAPI comparison; migration tests cover idempotence and the audio migration, not a full prior-phase database | QA, G-6, G-7, G-8 |
| R8 | Medium | **Ollama is assumed in places the schema does not assume it.** The `connections` table allows three kinds; the registry, three schema literals, several error strings and four web files assume one. | `providers/registry.py`, `schemas.py`, `Welcome.tsx`, `ModelPicker.tsx`, `LiveSettings.tsx`, `errors.ts` | Phase 6, 6B (only if a second runtime is wanted) |
| R9 | Medium | **Two focus-ring systems and two selection styles** in the component layer. | Design review, V11 and V13 | Phase 4, 4D.6 |
| R10 | Low | **Raw exception text reaches the UI.** Nine toasts use `String(e)` as their text, across `LiveAppShell`, `LiveSettings`, `TranscriptionSettings` and `AudioChip`; the offline screen prints the error object. | Design review, V15 | Phase 4, 4D.6 |
| R11 | Low | **The repository is large for its age.** `.git` is 279 MB after 42 commits; `artifacts/` holds 148 MB; `server/evals/` holds 373 MB in 7,538 tracked files. `artifacts/phase-3/regression/` re-commits earlier phases' screenshots. | `du`, `git count-objects` | Policy below |
| R12 | Low | **Small hygiene items.** `.DS_Store` is tracked (it is the latest commit). The version string lives in `config.py`, `package.json` and `pyproject.toml` separately and has not moved from `1.0.0-alpha.0`. The audio extension list is written out three times. | | Phase 4, 4A.7 |
| R13 | Low | **`search/pipeline.py` `__call__` is one 330-line method.** It works, it is covered, and the Phase 2 accuracy work lives in it. | | Leave it. Phases 7 and 8 import its pieces and do not edit it. |
| R14 | Low | **`bootstrap` and `models` are refetched every 30 seconds** while the tab is visible. This is not run polling and it is how loaded state stays current; it is noted only because the rules say "never poll". | `LiveAppShell.tsx` `refetchInterval` | Acceptable. No action. |

### Evidence policy from Phase 4 on (R11)

Do not rewrite history. Going forward:

- Commit reports, JSON and text outputs.
- Commit screenshots only for states that are new or changed in that phase, plus the twelve review screens. Do not re-commit earlier phases' images.
- Keep videos out of Git (`artifacts/phase-*/motion/` in `.gitignore`).
- Keep one copy of each recorded web fixture; reports reference it by hash.

## 4. Known limitations carried forward

These are recorded in the Phase 3 report and are not addressed by any phase here. They should stay visible.

- **VoiceOver did not work on the iPhone** and was never diagnosed. Jake deferred it. For an app that otherwise treats accessibility seriously, this is the largest open gap. A time-boxed look with the phone connected to Safari's inspector would at least establish the cause.
- **The installed app once refused keyboard focus** on iOS 18.7.8 until the phone restarted. The cause is unproven and recurrence is possible.
- **Full answer accuracy is established for the main model, not for all five** in the picker (Phase 2 report).
- **Physical-phone load time was confirmed by Jake, not measured.**

## 5. Is the roadmap the right one?

Yes, in this order, for these reasons:

1. **Phase 4 (polish and motion).** It is what Jake asked for, it carries the least risk, and its first checkpoint pays down R1 to R4 before anything else is built on them.
2. **Phase 5 (everyday chat).** Small, separate, immediately useful. It also produces the document extractor that Phase 7 needs and the automatic backup that every later migration should have behind it.
3. **Phase 6A (transcript clean-up and glossary).** Already designed. It is the cheapest feature on the list and independent of the rest.
4. **Phase 7 (Library).** The first step toward the project's stated goal. Deterministic, measurable, and built from parts that already passed their evals.
5. **Phase 8 (Research).** Last, and only if its gate passes. `SPEC.md` §F4 already requires two weeks of daily use first, which the earlier phases fill.

Phase 6B (a second runtime) is optional and can go anywhere after Phase 4, or nowhere.

**The one thing I would not do** is start Research early because it is the most interesting. The previous attempt at agents is documented in `SPEC.md` §F1, and its failure modes were exactly the ones the gate tests for.

### Later, not specified here

| Idea | Why it waits |
|---|---|
| Deep research jobs (long, resumable, many sources) | Needs Research (Phase 8) proven first. |
| Library inside Research | Needs Phases 7 and 8 and a privacy guard on outgoing queries. |
| Automatic model routing ("pick the right model for me") | Needs an eval set per task type; §F2 says the same. Without one it is guesswork. |
| MCP client | Needs a tool loop that already works and a permission model. |
| Voice output, image generation, sharing links, multiple users | Outside the product statement in §B1. |
