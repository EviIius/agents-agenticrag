# Part B test-diff ledger

The approved B3/B5/B6/B7/B8 presentation and commit-flow changes supersede the
corresponding old labels and separate Apply/immediate-reset interactions. No
assertion, timeout, performance limit, skip or release threshold is relaxed.

| Existing file | Change | Behavior retained |
| --- | --- | --- |
| attachments-redesign.spec.ts | Xhigh → Max labels | Same `xhigh` choice, checked state and active chip |
| tools-menu-layout.spec.ts | Xhigh → Max labels | Layout, touch targets, keyboard arrows and chosen state |
| chat.spec.ts | Stopped state selector uses the visible outcome line | Partial text persists; runtime disconnect still asserted |
| composer-workflows.spec.ts | Model choice uses the grid cell slot | Real model selection/loading before image/workflow tests |
| deferred-polish.spec.ts | Grid choice selectors; Vision filter; current marker replaces redundant Selected pill | Counts, capabilities, loaded filters, dual-name search, scroll and touch layout |
| documents.spec.ts | Model choice selector only | Vision selection before document/image attachment checks |
| foundation.spec.ts | Picker choice role option → gridcell | Real choice, header update, keyboard and axe assertions unchanged |
| load-selection.spec.ts | Grid role, generic Message placeholder and one Save | Load selects the model; configured limits and real 32K payloads remain asserted |
| mobile-layout.spec.ts | Picker choice role only | Drawer, keyboard, visibility and overflow limits unchanged |
| parameters.spec.ts | One Save replaces context Apply + Save; reset is staged then saved | Exact runtime sampling/system/context captures and absent unset parameters unchanged |
| phase3-accessibility.spec.ts | Grid choice role; visible Stopped status and Retry replace the old stats/regenerate selectors | Keyboard-only send, stop, focus, retry, branch, model switch and citation assertions unchanged |
| phase5a.spec.ts | Grid role; unified Save; context Apply case asserts combined commit | Dirty drafts, validation, no premature new-chat PATCH, real context persistence, preset precedence and rename search preserved |
| polish.spec.ts | Picker choice role only | Command palette, model picker visibility and Escape behavior preserved |
| review.spec.ts | Grid role; feature starter replaces Explain/Search starter actions | Starter/tool interaction, editable focused composer, web toggle, layout, axe and screenshots retained |
| transcription.spec.ts | Picker choice role only | Actual vision choice; transcript/recording assertions unchanged |
| ui-regressions.spec.ts | Grid role and one Save selector | Loading/selection, clamped context limits, invalid-state and layout assertions preserved |

New files: `web/tests/chat-state.spec.ts` and
`web/src/lib/chat-presentation.test.ts`. Tests cover both real fake-server flows
and explicit synthetic UI fixtures. New fixture corrections retain every failure
and strengthen readiness, source/payload and application-error assertions.

The spacing regression exposed by `actions.spec.ts` is fixed in product code.
That test is unchanged; no forced click, overlay bypass or larger timeout is used.

The new chat-state tests snapshot and restore fake-app default selection and
model preferences after each case, including failures. A complete run exposed
the earlier shared-state leak; no core test is changed to accept that leak.
