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


---

# Follow-up: Load selection, 32K context and option review

## Summary

The four new phone screenshots expose a remaining distinction: the row's Load button warmed a model but did not select it, whereas choosing the row did both. That left the header, composer and context controls on Gemma or base Qwen even when GPT-OSS or Qwen 32K was resident in Ollama. Load now selects the active chat model in both the picker and Settings → Models; Eject only unloads it. The active model has an accessible checkmark, highlighted row and name in chat settings.

Settings navigation centers the active tab on phones, and changing sections starts at the top. The chat drawer clips its outer surface while the inner controls scroll, keeping the title and close control outside that scrolling region. Buttons, selected-state feedback, settings sections and floating surfaces use brief functional transitions with the existing motion tokens; OS reduced motion and the app's Always setting remove them. Phase 3 remains unstarted.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Picker Load selects and loads in new/existing chats | Pass in Chromium/WebKit | `load-selection.spec.ts`, at 390/1440 in Chromium/WebKit; header, composer, active marker, stored chat and reload |
| Settings → Models Load uses the same selection path | Pass in Chromium/WebKit | The shared model action callback; visible Eject state and selected header after closing Settings |
| 32K configured model exposes and sends 32K context | Pass in Chromium/WebKit | Fake runtime explicitly reports a 32K configuration; preset, input ceiling, saved preference and the actual answer payload are checked. 64K remains absent |
| Failed load reports failure without claiming Loaded | Pass in Chromium/WebKit | Intercepted control failure, error notification, Not loaded state and usable retry button |
| Settings active tab and section start remain visible | Pass in Chromium/WebKit | All seven sections, four widths, both themes; active-tab intersection and zero section scroll offset |
| Motion respects both reduced-motion settings | Pass in Chromium/WebKit | OS preference and the app's Always setting; no token streaming/Markdown animation |
| Actual Ollama/Tailscale follow-up | Pass; physical iPhone review still required | Real GPT-OSS/Qwen 32K Load selection, context UI and API status, then restore the prior preview selection |

## Changed files

- **Web:** `LiveAppShell`, `ModelPicker`, `LiveSettings`, `LiveChatSettings`, `SettingsDialog`, `DesignPage` and `globals.css`.
- **Tests:** the fake runtime's vision fixture explicitly reports 32K; `load-selection.spec.ts` checks Load, context payloads and reduced motion; responsive assertions cover active-tab visibility and section scroll reset.
- **Docs/evidence:** SPEC correction, this follow-up, Phase 2 summary and `artifacts/phase-2/load-*` captures/logs.

## Deviations from SPEC.md

The user clarified that Load should also select the model. The existing load/unload API and model-selection path are reused; no adapter, dependency, inference call, prompt or sampling default is added. Configured context remains API-derived and is not inferred from a model name. `/design` includes selectable synthetic 16K/32K models and their bound settings.

## Runtime observations

Actual button-driven smokes confirm GPT-OSS loads at 16K and Qwen 32K loads at 32K over Tailscale. The corrected drawer retains a visible close control after scrolling to 32K; local and HTTPS health pass. Standard Qwen is restored and warm at 16K, with the test-loaded models ejected. These checks leave existing chats and saved sampling preferences unchanged. See `load-selection-live.json` and `load-live-*` screenshots.

Loaded and selected are separate concepts. Ollama can retain a model that a chat is not using. The old Load callback only changed residency, leaving the selected 16K model's correct controls visible; a 32K preset could therefore be absent even though a different 32K model was loaded. The fix binds all chat surfaces to the requested model while retaining truthful residency feedback.

## Design critique and option inventory

### Overall impression

The composer and reading area have a clear hierarchy. The largest usability problem was ambiguous model state: resident models moved to the top of the picker, while the selected model could remain elsewhere. Context and sampling controls need an explicit association with that selection. The phone Settings screenshot also shows a cropped active tab and carried-over section scrolling. Those findings are repaired here.

### Every current option reviewed

This inventory combines source review with the browser checks listed below. It does not claim fresh factual-answer evaluation or physical iPhone verification for every option.

| Surface and options | Current behavior / finding | Improvement and priority |
|---|---|---|
| New chat: model, greeting, Explain/Write/Code/Search suggestions | Suggestions populate the composer; the model is selected independently from Ollama residency | **Fixed, high:** Load selects the intended model. **Next, moderate:** explain how “last used” versus a fixed default affects a fresh chat |
| Model picker: filter, row select, Load/Eject, vision/reasoning/tool icons | Capabilities and configured limits come from the runtime; residency and active selection now have distinct markers | **Fixed, high:** shared Load-and-select action, active check/highlight and explanatory footer. **Next, moderate:** show resident memory beside loaded state to explain large-model eviction; tool capability is informational until later agents |
| Composer: text, send/stop, file/image attachments, web toggle, reasoning, context meter | Phone Enter preserves newlines; desktop Enter sends; Cmd/Ctrl Enter also sends. Images are gated by runtime vision capability | **Fixed, minor:** functional press feedback. **Next, moderate:** attachment progress and clearer supported-file hints, plus a useful context-meter explanation before overflow |
| Chat: copy, regenerate, edit/cancel/submit, branch navigation, stats, scroll to latest | Existing branch/action and runtime-parameter tests remain the functional evidence | **Next, moderate:** make the active branch and regeneration progress easier to distinguish; keep completion metadata compact on small phones |
| History: search, new chat, rename, pin/unpin, Markdown/JSON export, delete/cancel | Named exports, cancellation and readable pin feedback were repaired in the previous checkpoint | **Next, minor:** highlight matching history text and add a visible streaming marker for background chats |
| Chat settings: system prompt/default, temperature, Top P/K, output tokens, seed, reasoning, context presets, Save/reset/model defaults | Only explicit overrides are sent; 16K/32K ceilings are operational. Settings now identify the selected model and pressed context preset; Reset restores the unsaved context value too | **Fixed, high:** correct model binding and 32K availability. **Next, moderate:** inline per-field validation; combine sampling/context saves into one awaited result to avoid partial-save ambiguity; explain that changed context applies to the next runtime request |
| Connections: name, URL, enabled/remove, concurrent requests, keep-alive, add | Changes save on blur; removal preserves chats; concurrency applies when idle | **Fixed, minor:** errors and saves use consistent typed notifications. **Next, moderate:** inline Saving/Saved/Error beside the changed field, clearer keep-alive units and validation before blur writes |
| Models: new-chat policy/default, utility model, titles, date, system prompt, display names, Load/Eject, Show/Hide, parameters/context | Settings Load now uses the same chat selection callback; metadata distinguishes configured limit from active context, replacing a misleading active/training-max fraction | **Fixed, high:** loading and context labels. **Next, moderate:** name the target chat beside Load when editing model settings; make hidden-model and fixed-default interactions explicit |
| Search: provider order/test, SearXNG URL, Ollama key save/remove, optional Brave key, default-on, source count, keyword/embedding ranking, cache duration, blocked sites | Free provider order remains intact; key fields are redacted; ranking/source caps are real settings. Touch users can move providers earlier without dragging | **Fixed, minor:** accessible provider-order button names. **Next, moderate:** label provider reachability separately from the last successful search test and show test time/results inline. Group the optional paid-provider field under Advanced to keep the free setup clear; do not imply higher source counts guarantee accuracy |
| Appearance: System/Light/Dark, serif/sans, S/M/L, reduced motion, user name | Preferences persist; all sections use bounded scrolling and reachable close controls | **Fixed, moderate:** selected phone tab is fully visible; each section resets scrolling. **Fixed, minor:** short pane transitions and press feedback, removed for reduced motion. **Next, minor:** a small live type-size preview |
| Data: export all chats, delete-all typed confirmation/cancel, future legacy import | Bulk export includes branches/citations; attachment bytes stay separate; import is deferred to Phase 3 | **Next, moderate:** give bulk export the same pre-download confirmation as per-chat export and clarify the attachment backup procedure; retain explicit destructive confirmation |
| Shortcuts/search palette: Send/newline, edit-last, stop, search, Settings, new chat | Current handlers are narrower than some old shortcut text: Esc stops from the composer, and desktop plain Enter also sends | **Fixed, minor:** shortcut copy matches those behaviors. **Next, moderate:** finish the full command palette and keyboard discoverability in Phase 3 |
| About: version, data folder, connections, local hosting/Tailscale copy | Basic runtime/storage information is available | **Next, minor:** show installed versus development-preview status and a copyable diagnostics summary without exposing credentials |
| Web answers: search activity, Retry/Search anyway, citations, source drawer, queries/providers/timings, Cited/Read not cited/failed pages, What the model saw, external links | Small numbered pills and bounded source cards preserve reading flow; raw saved passages are inspectable. Errors remain separate from message content | **Next, moderate:** show fetched/cache age beside publication date and distinguish a valid reference from factual entailment; retain the separate accuracy evaluation gates |

### Visual hierarchy, consistency and accessibility

- The answer remains the largest reading surface; model/context metadata stays secondary. The selected model now has a checkmark and highlighted row rather than relying on residency color.
- Settings keep a fixed title/close area and one scrolling content region. The active horizontal phone tab is centered without animated auto-scrolling; pane changes start at the heading.
- New motion uses the existing 120/200ms tokens and affects opacity/transforms or control feedback, not streamed text or layout dimensions. Reduced motion removes transitions, reveal animations and press scaling.
- Existing contrast-token checks, 44px controls, accessible model/status labels and bounded overlays are retained. Real iOS keyboard and status-bar behavior still require the phone review.

### Priority recommendations after this checkpoint

1. Inline settings validation and one clear save result, particularly for sampling plus context.
2. Provider test history and cache-age feedback, so availability and freshness are understandable.
3. Finish Phase 3's command palette, installed-preview labeling, import/deployment and bundle budget work after physical phone confirmation.

## Test output

- Final `make check`: **193 Python tests**, **36 Vitest tests**, **56 contrast pairs**, formatting/lint/types, coverage and API contract pass (`load-selection-check-final.txt`).
- `make build` passes (`load-selection-build.txt`); the existing Phase 3 bundle budget remains open.
- Broad functional run: **111 passed, 8 failed, 1 skipped** (`load-selection-e2e.txt`). All eight failures were the new full-visibility assertion for the last Settings tab on narrow phones: fractional clipping at the horizontal scroll edge. Navigation edge padding fixes it; the stricter assertion remains.
- Corrected affected scope: **54 passed** (`load-selection-e2e-final.txt`), covering `ui-regressions`, `load-selection` and `review` in Chromium/WebKit. All four widths, both themes, reopening Settings, scrolled-section transitions, new/existing-chat Load, actual 32K answer payloads and reduced motion pass.
- Live GPT-OSS and Qwen 32K Load buttons update header/composer/selection markers and report Loaded/Eject. Ollama confirms 16384 and 32768 respectively (`load-selection-live.json`). This verifies residency and UI binding, not factual answer accuracy.
- Live screenshot review then exposed outer-drawer scrolling after navigating to lower controls, which could hide its close button. Outer overflow is now clipped; a regression requires zero outer scroll and a fully visible close control after selecting/saving 32K. The final **18/18** Chromium/WebKit checks pass (`load-selection-drawer-e2e.txt`); a real Tailscale screenshot and DOM geometry confirm zero outer scroll and a visible 44px close button.
- No prompt/evidence-selection changes were made, so the existing accuracy/temperature reports remain the acceptance evidence for those paths.

## Screenshots

- `load-selected-{390,1440}-{new,existing}-{chromium,webkit}.png`: synthetic loaded and selected state.
- `load-context-32k-{390,1440}-{chromium,webkit}.png`: synthetic 32K controls.
- `review-settings-*`: updated synthetic navigation/section captures.
- `load-live-gpt-selected-390.jpg` and `load-live-context-32k-390.jpg`: actual Ollama/Tailscale Load selection and context controls, distinct from fake-runtime checks.

## Open questions for Jake

The updated preview is restored. Recheck the Load button and Qwen 32K chat settings on the iPhone. The option inventory above records later polish priorities; it does not add agents or begin Phase 3.
