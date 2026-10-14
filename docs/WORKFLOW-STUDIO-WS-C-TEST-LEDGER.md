# WS-C test-diff ledger

Baseline: WS-B `e3042eaeb16fe339d8a152b1d7e681049bbab263`.
No existing skip, retry, timeout, release threshold or assertion is removed.

| Existing test/helper | Change | Reason | Retained behavior |
| --- | --- | --- | --- |
| `workflows.spec.ts` creative workflow | Copy template; configure its blocks through the Inspector; submit the Start form; use durable graph result controls | Fixed builder replaced by Studio | Explicit model, two seeds/images, review/edit/approve, reconnect/reload, format-selection/cancel/save; source and result checks |
| `workflows.spec.ts` recording workflow | Same template-copy/Inspector/Start path; saved recording chosen in Run inputs | Phone and desktop now share graph definitions | Original sources, only explicit output-limit/temperature overrides, captured request parameters, no tools and healthy app |
| `composer-workflows.spec.ts` workflow count | Submit to additive definition-run endpoint; capture accepted run and wait for the response capture before comparing it | The server now resolves automatic seeds durably at graph acceptance | Same request key/body on uncertain retry, identical accepted run ID and persisted seeds, requested count and unset parameter values |
| `composer-workflows.spec.ts` visual builder | Open production `/design?studio`; configure each real block through keyboard/Outline; close Inspector between theme changes | Each block now has its own Setup panel; phone sheets correctly hide the background | Both themes, 320/390/1440 widths, all settings reachable, actual keyboard focus, no overflow, zero serious/critical axe findings |
| `composer-workflows.spec.ts` cancellation/navigation | Template is a button; use its Inspector model selector | Actual Home template copies replace old links/form | Image cancellation stays in composer; saved chat and same-chat return survive workspace navigation |
| `workflow-studio-shell.spec.ts` template path | Template button creates a definition; Run opens Start inputs | Fixed `/new` form replaced by copy/Studio | Shared shell/sidebar/rail, draft preservation, source chooser and legacy API/run navigation |
| `workflow-studio-shell.spec.ts` Home design-state tests | Synthetic fixture now renders the production `WorkflowHomeContent`, definition cards and run rows | The previous Home preview was obsolete | All seven states, both themes/widths/engines, screenshot, overflow and axe assertions unchanged |
| `workspace-helpers.ts` workspace navigation | Wait for the clicked workspace URL before callers invoke Back | Lazy route transition was still pending | Real sidebar link click and browser-history round trip, without replacing navigation or adding retries |
| `test_workflow_graph_engine.py` | Add template-copy metadata test | Editable copies should keep their public description/icon | Existing tests unmodified; frozen template graph equals copied graph |

New tests add 38 shared structural validation cases on both sides, editing/history/
prompt-preview units, native drag/insertion, keyboard wiring, phone reorder/branches,
conflicts, server-authoritative availability, and the production design-state sweep.
Focused failed development attempts and traces are retained under
`artifacts/workflow-studio/ws-c/attempts/`; they are not counted as final passes.

The second full invocation retained 528 passes, three existing skips and one new
WebKit reduced-motion failure. Initial preference hydration was publishing the
old UI values 300 ms later, overwriting the externally saved Always setting.
`usePreferenceSync` now hydrates before enabling write-back. The new motion test
forces a differing saved/local theme, asserts hydration sends no settings PATCH,
checks the saved Always response and verifies reload. Existing phone settings
assertions are unchanged; three repeats in each engine pass (12 checks).
