# Phase 2 UI review report

## Summary

The ten iPhone screenshots exposed layout problems and missing behavior in model loading, exports and configured context limits.
The picker search now fits its own row; safe areas and the visual viewport bound settings, dialogs and drawers.
Selecting an unloaded model warms it, refreshes runtime status, and reports progress/success/failure without adding an answer call.
Exports require confirmation, support Cancel, and use the chat title; pins have a visible marker and readable notifications.
Numbered inline citations keep prose compact, with source details in a dismissible card. Phase 3 has not started.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Search input, focus and model filtering | Pass in final affected-screen run | `ui-regressions.spec.ts`; `foundation.spec.ts` keyboard walkthrough also rejects page errors. Removed an unnecessary wrapper that caused cmdk to try sorting a missing node. |
| Model selection, loading and refreshed status | Pass: browser and actual Ollama switch | `ui-regressions.spec.ts`: existing-chat switch, visible loading state, loaded status and persistence after reload; real GPT-OSS selection/loading verified through the Tailscale UI at 16K; see `mobile-review-live-runtime.json`. |
| Settings close buttons and keyboard bounds | Pass in final affected-screen run | All seven settings sections at 320/390/768/1440 in both themes; simulated 47px status bar, 34px home indicator, reduced and panned visual viewport. Chat settings retain a close control while scrolling. |
| Pins and notifications | Pass in final affected-screen run | Explicit pin/unpin success text, title, pinned row marker, 44px dismiss button; `actions.spec.ts`. Sonner selectors use Workbench tokens and override its default low-contrast description. |
| Export cancellation and title-based filenames | Pass in final action checks | Current branch Markdown/JSON; Cancel makes no export request; download filenames match chat titles. Server tests cover ASCII, Unicode and unsafe filename characters. |
| Operational context constraints | Pass: server and browser constraints | `context_limit` is distinct from architecture `context_max`. API rejects oversized load/preference overrides; old saved oversized preferences are clamped in memory. UI hides presets above the limit and disables invalid saves. |
| Reasoning labels | Pass in final switching checks | Visible On/Off labels retain exact runtime values in payloads; parameter payload regression remains intact. |
| Citation size and touch/hover behavior | Pass in final affected-screen run | 20px visual pills, enlarged hit area, 340px bounded card, explicit close. Hover only with a fine pointer; touch opens via tap. `web.spec.ts` verifies close and source-drawer access afterward. |
| All changed states on /design | Implemented | Export confirmations, pin/loading/error notifications, pinned row and constrained context form are synthetic previews. Preview downloads do not request a real chat. |
| Physical iPhone verification | Awaiting review of the updated preview | Browser WebKit emulation and simulated insets cannot prove native keyboard, status bar or iOS file handling. |

## Changed files

- **Server:** schemas, Ollama model inventory, registry, model validation, chat export and chat tests.
- **Web:** picker/command input, shell/model actions, chat actions/history, reasoning labels, chat settings, global settings, citations, notifications, viewport styles, generated API types and /design states.
- **Tests:** action/export/pin tests, keyboard filtering error assertion, citation interactions and a new responsive regression suite.
- **Docs/evidence:** this report, SPEC user correction, Phase 2 status and `artifacts/phase-2/mobile-review-*` / `review-*` evidence.

## Deviations from SPEC.md

The user's screenshot correction adds a confirmation before exports and changes hash filenames to chat titles.
It also replaces architecture-max context controls with operational configuration ceilings, and domain-sized citation chips with compact source numbers. The domain/title/evidence remain in the citation card.
A control request warms an explicitly selected unloaded model; it is the existing load API, not a planner or answer generation. No dependencies, agents, prompt changes or sampling defaults were added.

## Runtime observations

Ollama's training context metadata is much larger than the configured contexts on this Mac. `num_ctx` is reported as 16K for the retained Llama and 32K for the Qwen 32K variant; the other three retain Workbench's existing 16K default ceiling.
Actual Tailscale verification starts with all models unloaded, selects GPT-OSS 20B, observes header/placeholder/loading progress, then confirms Loaded/Eject in the filtered picker and Ollama `context_length=16384`. Both local and HTTPS health pass; exactly five approved variants remain visible. See `mobile-review-live-runtime.json` and `review-live-picker-390.jpg`. Restored standard Qwen selection and warmed it at 16K, then ejected the test-loaded GPT model. This is a model-load smoke, not a new accuracy evaluation.
The old model action button was hidden on touch devices, and selection only patched the chat. Both paths now invoke the supported load/unload API and refresh inventory on completion.
Sonner's built-in selector specificity overrode the first notification style attempt; direct visual review exposed its dark, unreadable description and 20px close control. The corrected selectors use existing design tokens and a 44px target.
The initial browser run retained six failures: five new geometry assertions sampled a moving drawer across separate layout reads, and a touch-emulated mouse event reopened a dismissed citation card. Geometry now uses one layout snapshot after the drawer footer is visible; hover additionally requires `(hover: hover) and (pointer: fine)`.

A subsequent repeat exposed a keyboard transition that briefly retained the previous visual-viewport height. Shell and sheet height now also respect native `100dvh`; thread/composer assertions use one layout snapshot. Another repeat exposed modal pointer locking: a drawer overlay intercepted notification dismissal. Visible notifications explicitly receive pointer events, and modal primitives treat notification interaction as non-dismissal. Pin assertions are scoped to the specific chat row, so unrelated pinned chats cannot make the test ambiguous.

## Accessibility review

The high-impact findings were inaccessible close controls beneath the status bar, oversized search focus geometry, unreadable notification descriptions and tiny dismiss targets. These are repaired with bounded overlays, existing contrast tokens, 44px targets and accessible labels. Axe checks cover all seven settings sections and chat/sources views in both themes. Citation pills remain visually small with an enlarged 44px hit area and accessible source titles. Browser simulation cannot establish physical iOS keyboard or status-bar behavior.

## Test output

- `make check`: **193 Python tests**, **36 Vitest tests**, **56 contrast token pairs** pass; lint, formatting, types, coverage and generated API contract pass.
- `make build`: passes. Existing large Markdown/code chunks remain a Phase 3 bundle-budget item.
- Initial `make e2e`: **122 passed, 6 failed, 2 skipped**, retained in `mobile-review-e2e-initial.txt`; failures described above.
- Repeat full `make e2e`: **127 passed, 1 failed, 2 skipped**, retained in `mobile-review-e2e.txt`; the intermittent keyboard transition described above was still failing.
- Corrective full UI run (excluding the unchanged long-stream gate): **124 passed, 3 failed, 1 skipped**, retained in `mobile-review-e2e-corrective.txt`; two notification-dismissal failures and one ambiguous pin assertion described above.
- Final affected-screen/action regression run: **54 passed**, retained in `mobile-review-e2e-final.txt` (`actions`, `review`, `ui-regressions`, `web`; Chromium and WebKit). No failing assertion remains in the affected scope. The unchanged long-stream/timeout gate passed in both earlier full runs; its results are not relabelled as a final full-suite run.
- The two skips are intentional: run the long stream/timeout gate once on Chromium; fixture screenshot duplication is skipped on WebKit.

## Screenshots

Screens named `review-*` are fake-runtime browser evidence, not real-model accuracy evidence.

- `review-picker-{320,390,768,1440}-{light,dark}.png`
- `review-settings-{connections,models,search,appearance,data,shortcuts,about}-{390,1440}-{light,dark}.png`
- `review-pin-{390,1440}-{chromium,webkit}.png`
- `review-export-{390,1440}-{chromium,webkit}.png`
- `review-live-picker-390.jpg`: actual Ollama/Tailscale model selection, filtered search and Loaded state.
- `review-live-settings-desktop.jpg`: actual Tailscale settings bounds and reachable close control.
- Existing regenerated Phase 2 citation, source drawer, safe panel and model keyboard screenshots supplement these views.

## Open questions for Jake

The rebuilt preview is restored at https://jakes-mac-mini.tailc4d343.ts.net/ . Recheck it on the real iPhone. Confirm model search/loading, settings close, pin feedback, export Cancel/title and citation dismissal. No credentials or paid services are needed for these changes. Phase 3 remains behind this physical-phone review.
