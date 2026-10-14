# Workflow Studio WS-C report

## Summary

Claude's Studio layout is retained: Blocks panel, neutral category cards, dotted
canvas, Inspector, Quick add, minimap and phone Outline with bottom sheets.
The editor now creates, connects, inserts, deletes, copies, renames and saves real
workflow definitions. Templates create editable copies. The two existing flows
retain basic input, run, approval, cancellation, retry, source and save controls.
This is an isolated branch checkpoint; main and the installed app are unchanged.
Source commits `c3ecd3bd`, `f066599e` and `62a822e4` retain the implementation
and fixes. The final complete regression is green; stop for WS-C review.

## Done-when checklist

| Item | Evidence |
| --- | --- |
| WS-AC10: native drag in space and on a connection | `workflow-studio-editor.spec.ts`, both engines |
| WS-AC11: keyboard add, Inspector wiring and run | Same suite; fake runtime only |
| WS-AC12: delete auto-heal as one undo; 20 mixed actions restore exactly | Browser test and `graph.test.ts` |
| WS-AC13: reload persistence and both conflict choices | Browser autosave/conflict test |
| WS-AC14: copy/paste remaps IDs, keys and internal references | Pure graph unit test; external references retained |
| WS-AC15: identical structural validation | 38 literal shared vectors, browser units and Python; runtime availability/privacy remains server-authoritative and is displayed through the validate endpoint |
| WS-AC16: phone insert, edit, reorder, branches and non-nestable notice | 390 px Chromium/WebKit Outline tests; no physical phone pass claimed |
| WS-AC17: deterministic tidy | Pure unit test; saved-layout browser check |
| Claude's references/prototype retained | All 11 reference images reviewed; prototype opened in Chromium; supplied files preserved exactly |

## Changed files

- Web: initial preference hydration reads without writing stale appearance values;
  lazy Studio route; real Home cards/templates; Blocks, Quick add, canvas,
  nodes/edges, Outline, per-kind Setup fields, variable picker, Connections,
  notes, history, autosave/conflict handling and prompt preview. Existing fixed
  builder/form removed; legacy run presentation retained.
- Server: editing validation for required prompts and disabled references;
  normalized validate-response document; expanded display-icon choices;
  template copies retain public descriptions/icons. No new migration or executor.
- Dependency: exact `@xyflow/react@12.12.0`, base.css only, lazy Studio loading,
  retained attribution and MIT notice. No other direct package added.
- Tests: shared validation corpus, pure editing/history/preview tests, new editor
  browser checks, updated existing workflow paths and synthetic design states.
- Docs: authorization, checkpoint plan, report, license and test-diff ledger.

## Deviations from the proposal

- Stable ID ordering remains WS-B's reviewed execution rule; positions never
  change execution. Autosave updates the draft; run snapshots remain immutable.
- Live model/engine availability and private-source connection checks use the
  authoritative server validation, avoiding browser guesses about capabilities
  or local hosts. Structural rules use the same 38 exact vectors on both sides.
- Basic Run inputs/results/approval stay available now to preserve existing
  template use. Live canvas execution, reuse/testing, versions, favorites and
  running-edge pulses remain WS-D. Future block types are visible but unavailable.
- Skipped blocks retain dashed borders and dimmed tiles, while their editable
  labels keep full contrast. Dimming the entire row produced real axe failures.
- An explicit initial static-import bundle group prevents the new lazy library
  from increasing first-load JavaScript through changed shared-chunk compression.
- Setup is organized by kind within the shared Setup component; no separate
  package or hidden model prompt is introduced by the editor.

## Runtime observations

All new run evidence uses fake Ollama/image workers and synthetic inputs. No native
inference, runtime/model/default/sampling/application-authored prompt change, Research restart, main
merge or live publication occurs. Blank optional sampling fields remain absent.
The six byte-identical legacy-template parity cases remain mandatory and retained.

Development failures are retained separately: selection callbacks conflicted;
inactive tab and skipped-row contrast were insufficient; decorative problem dots
needed a semantic role; synthetic card-gallery scrolling needed keyboard focus.
These were corrected in product markup/state/CSS without suppressing axe rules.
The first full-suite attempt stops with one failed chat-return assertion
and 44 passes: initial automatic canvas fitting incorrectly dirtied the definition.
The correction distinguishes presentation fitting from user pan/zoom/controls,
with a new no-edit/explicit-zoom browser test and unchanged original chat-return
assertions. The failed log, trace and source hashes remain in `attempts/e2e-first/`.

The second complete invocation retains 528 passes, three existing skips and one
WebKit failure. Initial appearance hydration scheduled a redundant PATCH of old
preferences that overwrote a newly saved Always choice. Hydration now reads before
enabling the preference subscriber. A forced saved/local theme mismatch and
no-hydration-write assertion reproduce the original precondition; 12 repeated
motion/settings checks pass. The failed full log, trace and source remain in
`attempts/e2e-second/`. It is not combined with reruns into a full-suite pass.

Test-path corrections wait for Studio mounting/focus, close phone sheets before
background actions, wait for accepted responses before comparison, and complete
lazy-route navigation before Back. A manually synthesized second native drag
failed in WebKit; Playwright's actual `dragTo` gesture plus settled saved geometry
passes without weakening insertion assertions. Early wrong-command/fixture/type
and formatting attempts are retained and are not final pass evidence.

## QA gates and test output

| Gate | Status / evidence |
| --- | --- |
| G-1 | Passed: 630 Python / 87 frontend; workflow coverage 89.2%; `check-final.log` |
| G-2 | Passed: one complete 48.7-minute invocation, 529 passes and three existing skips; `e2e-final.log` |
| G-3 | Existing assertions, skips, retries and timeouts retained; `WORKFLOW-STUDIO-WS-C-TEST-LEDGER.md` |
| G-4 | Initial JS 241,658 gzip bytes, 3,591 below WS-B. Studio 77,306 gzip bytes; 91,078 additional lazy static-import bytes. Render p95 2.7 / 3 ms; first-token overhead 85.57 / 66.31 ms; 300-message scroll p95 16.7 / 21 ms |
| G-5 | Zero serious/critical axe findings in both engines/themes/sizes across the new catalogue and actual Home states; 110 contrast pairs; keyboard/Outline checks pass |
| G-6 | Full WS-B and baseline API comparisons have zero errors; `api-additive-full.json`, full check |
| G-7 | No new migration or old-row rewrite; existing preservation guards pass |
| G-8 | All application-authored prompt hashes and exact legacy-template parity guards pass |
| G-9 | Not triggered: no edits under server search/runs/providers |
| G-10 | Ordinary-chat golden payload and six workflow parity cases retained |
| G-11 | Synthetic captures only; privacy scan zero findings. 23,116 historical evidence/eval/fixture blobs, 15 references and 509 source/config/test files verified |
| G-12 | Installed 97 server / 410 static hashes and main unchanged; local/verified HTTPS health pass; live `/design` remains 404 |
| G-13 | Both triggers, including saved Always/reload, pass; all first-party motion in `motion.css`; no guard extension |
| G-14 | Production Studio panels, Quick add, cards, Outline and Home content represented on `/design` |
| G-15 | Not triggered: no migration; WS-B copied-data rehearsal remains preserved |
| G-16 | Review pending; browser phone emulation only. No physical iPhone or VoiceOver pass claimed |

The final third invocation is a complete pass, not an assembly of focused reruns.
Both earlier failing full-suite attempts and frozen sources are preserved.
`make build` passes; the approved canvas remains lazy and attribution stays visible.
Existing package versions are unchanged; 20 transitive lock entries are added.
The dependency audit retains five pre-existing low-severity findings.

1,037 fresh regression outputs are archived separately; 997 historical outputs
are restored and 40 new fake captures relocated. Preservation proof is
`preservation-final.json`; evidence and raw metrics are under
`artifacts/workflow-studio/ws-c/`.

## Screenshots and motion evidence

Production design states include all seven Setup panels, canvas/empty/selected,
Problems, conflict, settings, Run inputs, Quick add, block/definition cards,
Outline and non-nestable layouts. Both themes and 390/1440 sizes are scanned with
axe and captured under `artifacts/workflow-studio/ws-c/browser/`.
Existing Home preview now renders the actual Home content with synthetic data.
182 synthetic videos (34,457,870 bytes) are retained outside Git at
`~/.local/share/workbench/qa/workflow-studio/ws-c/videos`; the manifest records
paths, sizes and hashes. Native drag/insertion, tidy and reduced-motion cases
are included. Representative actual screenshots were visually reviewed against
the supplied prototype/reference layouts.
Full run/approval/failure/retry canvas videos belong to WS-D.

## Open review items

- Stop for WS-C review before WS-D, merge or deployment. The preview uses fake data.
- Next is live canvas execution/approvals/retry/reuse and run/version screens in
  WS-D; its motion-guard extension retains the separate review gate.
- The requested ordinary chat-composer image mode with image results in the same
  conversation remains tracked in `docs/DEFERRED-FIXES.md`.
- Research remains shelved. VoiceOver is outside the current work list; its
  historical reported failure is preserved, with no support/pass claim.
