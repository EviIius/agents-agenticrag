# Phase 0 — Foundation

Date: 1 October 2026 · branch: `rebuild` · scope: SPEC §H1 Phase 0

## Summary

The previous app is frozen and backed up. The new FastAPI/SQLite foundation and React interface run independently of it.
The interface uses responsive fixture data, with explicit **Fake runtime** labels, both themes, and a development component guide.
The composer occupies its own layout row; phone pickers use drawers and wide desktop settings use a side panel.
The installed phone app remains Chat & Web 0.5.0. Live chat, web search, migration, and deployment belong to the next phases.

## Done-when checklist

- [x] `make setup`, `make check`, `make build`, and `make e2e` pass on this Mac mini.
- [x] `make dev` shows the fixture shell at <http://127.0.0.1:5173>; `/design` is available for review.
- [x] Twelve screenshots cover `/design` and the fixture chat, at 390 × 844, 768 × 1024, and 1440 × 900, in light and dark.
- [x] Legacy branch `legacy/chat-web-0.5` and tag `legacy-0.5` both point to `537456f92a1a26d19a23a6ea6b82435e635e1f0b`.
- [x] Full installed-app backup exists: `/Users/evilius/.local/share/workbench/backups/legacy-app-20261001.tar.gz` (58,689,188 bytes, mode 0600).
- [x] Axe finds zero serious or critical violations on `/design`, both themes, Chromium and WebKit.

Backup SHA-256: `2c697a7889692560a1d6e4712e3b9a5f7130371f6c119a427cf1ff97838ebe1b`.
Preservation metadata is in [preservation.json](../artifacts/phase-0/preservation.json).

## Changed files

| Area | Changes |
| --- | --- |
| Preservation | Previous source, tests, scripts, migrations, and docs moved to `legacy/`; fonts copied with licenses. New app imports no legacy modules. |
| Instructions and tooling | `AGENTS.md`, `Makefile`, `README.md`, setup/tool environment scripts, contrast check, OpenAPI type generator. |
| Server | App factory, health router, structured errors, security middleware, configuration, SQLite connection and transactional migration runner. |
| Database | Exact `001_init.sql` from the newer repo spec; isolated new data path and mode 0600 database. |
| Test runtime | Explicit `fake-*` models, Ollama NDJSON and OpenAI-compatible SSE, scripted replies, captured request bodies. |
| Web | React/Vite/strict TypeScript, shadcn New York primitives, token palette, fonts, prose, theme provider and theme script before paint. |
| Interface | App shell, sidebar/rail, top bar, model picker, thread, messages/reasoning, composer, chat settings and appearance dialog, `/design` fixture states. |
| Verification | Server tests, theme test, Chromium/WebKit tests, axe, keyboard walkthrough, Markdown safety checks, screenshots and command logs. |

Implementation commits before this report: `568d85b` (legacy archive), `8e4e800` (server foundation), `1f49702` (fixture interface and browser checks).

## Deviations from SPEC.md

1. **Newer repo spec retained.** `docs/SPEC.md` already contained 1 October corrections to the 30 September attachment. Those edits were preserved and used, including the corrected API behavior and fake-runtime labels.
2. **Development preview only on 5173.** The installed service continues owning 127.0.0.1:8787. `make dev` launches Vite against fixtures; it does not replace the installed app. The new production server and `make dev-server` retain the required 8787 loopback bind and one worker.
3. **Contrast discrepancy recorded.** The exact dark G2 `text/surface-3` pair measures 10.52:1, below the stated 11.8:1 body target. Pressed row labels retain that prescribed palette and are checked against AA 4.5:1. Normal body pairs use 11.8:1; dark `text/surface-2` is approximately 11.799:1 and uses a 0.001 numerical tolerance for the rounded spec figure. No palette colors were changed. All other implemented foreground pairs meet their applicable G2 targets; metadata is not placed on `surface-3`.
4. **CSS source paths corrected.** Streamdown's Tailwind sources point three levels up from `web/src/styles/globals.css` to `web/node_modules`.
5. **Future modules are directories, not placeholder implementations.** Provider adapters, generation runs, web search, real settings persistence, import, and deployment are deferred to their prescribed phases. Their coverage gate applies when they contain implementation code.
6. **Lint scope is explicit.** Strict TypeScript compilation checks TS/TSX, including unused variables and parameters; ESLint checks JavaScript; Prettier checks the interface and tests. No additional TypeScript ESLint parser dependency was introduced outside the prescribed stack.

## Runtime observations

- Node 24.19.0, npm 12.2.0, uv 0.12.21, Python 3.14.7. Build tools are local; the deployed app will need only Python.
- FastAPI 0.142.2, React 19, Vite 8.3.1, TypeScript 5.9.3, Streamdown 2.7.0. Dependencies are locked in `server/uv.lock` and `web/package-lock.json`.
- The shadcn registry generated the primitives using New York/neutral configuration. Its optional `cn` package was removed; primitives use the local `clsx`/`tailwind-merge` helper.
- Streamdown/Shiki/math load through a lazy Markdown boundary; code and table scroll regions are keyboard focusable. Raw HTML is disabled, unsafe URLs are filtered, and remote images become links.
- The initial build entry is approximately 184 KB gzip. Vite warns about larger lazy Markdown/highlighter chunks. This is not a Phase 3 performance result; real iPhone load and streaming budgets still require measurement.
- WebKit's default Tab navigation skips buttons; Option+Tab reaches all controls. The scripted keyboard walkthrough uses that browser behavior and passes without mouse clicks.
- The walkthrough covers entering a fixture message, retaining composer focus after send, selecting a model, searching fixture chats, opening/closing settings, and starting a new chat. Live Stop, regenerate persistence, branches, and citations are not implemented in Phase 0. VoiceOver has not been tested; it remains a Phase 3 check.
- Local and Tailscale health checks still return installed version `0.5.0`, asset version `50`. Existing label `dev.agenticrag.workbench` and Tailscale proxy `http://127.0.0.1:8787` are preserved.
- **Model choice recorded:** exclude `llama3.3:70b-instruct-q4_K_M`; retain `llama3.3:70b-workbench-16k` and the other four chat variants. Phase 1 will apply an exact stored hidden-model preference. Model weights were preserved.

## Test output

| Command | Result | Evidence |
| --- | --- | --- |
| `make setup` | Pass; locked dependencies and Chromium/WebKit installed | [setup.log](../artifacts/phase-0/setup.log) |
| `make check` | Ruff, mypy, strict TS, JS lint, formatting, contract check, 10 server tests, 1 theme test pass | [check.log](../artifacts/phase-0/check.log) |
| Contrast | 56 foreground/background pairs pass with the discrepancy above documented | [check_contrast.py](../scripts/check_contrast.py) |
| `make build` | Pass; self-hosted fonts and static assets emitted | [build.log](../artifacts/phase-0/build.log) |
| `make e2e` | 27 pass; one duplicate screenshot capture intentionally skipped in WebKit | [e2e.log](../artifacts/phase-0/e2e.log) |
| Axe | No serious/critical findings on `/design`, two browsers × two themes | `design accessibility light/dark` in E2E log |
| Layout | No page overflow at 320, 390, 768, 1440; thread/composer boundaries checked; phone drawers and desktop panel exercised | `foundation.spec.ts` |
| Security | Host/origin/owner enforcement; security headers; cache and SPA behavior; migration rollback and privacy; untrusted Markdown checks | `test_foundation.py`, `foundation.spec.ts` |

## Screenshots

**All screenshots below use Fake runtime fixture data. No real model produced these answers.**
The twelve captures were visually inspected. The thread clips and scrolls above its separate composer row; that is deliberate, not an overlap.

| Viewport | Chat light | Chat dark | Design light | Design dark |
| --- | --- | --- | --- | --- |
| 390 × 844 | [Phone](../artifacts/phase-0/chat-390-light-fake-runtime.png) | [Phone](../artifacts/phase-0/chat-390-dark-fake-runtime.png) | [Phone](../artifacts/phase-0/design-390-light-fake-runtime.png) | [Phone](../artifacts/phase-0/design-390-dark-fake-runtime.png) |
| 768 × 1024 | [Tablet](../artifacts/phase-0/chat-768-light-fake-runtime.png) | [Tablet](../artifacts/phase-0/chat-768-dark-fake-runtime.png) | [Tablet](../artifacts/phase-0/design-768-light-fake-runtime.png) | [Tablet](../artifacts/phase-0/design-768-dark-fake-runtime.png) |
| 1440 × 900 | [Desktop](../artifacts/phase-0/chat-1440-light-fake-runtime.png) | [Desktop](../artifacts/phase-0/chat-1440-dark-fake-runtime.png) | [Desktop](../artifacts/phase-0/design-1440-light-fake-runtime.png) | [Desktop](../artifacts/phase-0/design-1440-dark-fake-runtime.png) |

## Open questions for Jake

No missing information blocks this phase. Review the fixture interface before Phase 1, as required by `AGENTS.md` and SPEC §H1/§H3.
Next is the Phase 1A provider checkpoint: recorded real runtime streams, five retained model variants, exact capabilities and defaults, then live chat.
