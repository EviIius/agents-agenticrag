# Mobile Tools layout correction

21 October 2026. Branch `codex/mobile-tools-polish`.

## Summary

The reported Tools popup was too tall and its full model-default label wrapped.
Rows are compacted, the heading and thinking controls stay fixed, and only the
action list scrolls when space is constrained. The visible default label is
`Default`, with `Model default` retained as its accessible name and tooltip.
The existing model choice, levels and request payloads are unchanged.

## Done-when checklist

| Item | Status | Evidence in `artifacts/mobile-tools-20261021/` |
| --- | --- | --- |
| All four tool rows shown on /design | Pass | Updated attachment fixture includes Edit photo |
| Phone, small phone, landscape and desktop fit | Pass | Geometry and screenshots, both themes/engines |
| Five thinking choices remain one line with touch targets | Pass | Geometry: no clipped text; phone controls ≥44 px |
| Short viewport action scrolling preserves thinking position | Pass | Four corrected keyboard-size cases |
| Persistent switches, thinking selection, Escape/focus | Pass | Existing functional case + focused layout checks |
| Photo upload/edit/comparison behavior retained | Pass, fake inference | Existing photo reference functional case in both browsers |
| Frontend gates/build/token contrast/motion | Pass | 132 unit tests, lint/types/format, build, 110 contrast pairs |
| Initial JS budget | Pass | 255,955 gzip bytes / unchanged 256,000-byte limit |
| Static-only publication and actual installed UI | Pending publication | Final release receipt follows |

## Changed files

- `ToolsMenu.tsx`: scrollable action group, fixed heading/thinking area, compact
  visible Default label, existing accessible name and selection semantics.
- `globals.css`: compact rows, consistent token-based surface and one-line grid;
  the outer menu does not scroll its heading offscreen.
- `AttachmentsPreview.tsx`: exposes the complete four-row menu in the existing
  synthetic design fixture.
- `tools-menu-layout.spec.ts`: geometry, scrolling, focus, control and axe checks.
- Authorization/report/evidence only beyond those web files. No backend edits.

## Deviations from SPEC.md

The user-requested narrow visual correction refines the older attachment spec's
full default label to a compact visible label without changing meaning. Existing
shadcn/Radix primitives, theme tokens and motion rules remain. The design-system
skill informed the local audit; no new component library or pattern was added.

## Runtime observations

No native inference, model load, network search or prompt evaluation is needed.
The short-screen test simulates visual viewport/safe-area limits; it does not
establish physical iPhone keyboard or VoiceOver support. VoiceOver stays deferred.

## Test output

Frontend check passes 132 tests plus TypeScript/ESLint/Prettier. Build passes;
initial static-import JS is 255,955 gzip bytes, within the existing 256,000 limit
with little remaining headroom. Motion guard and all 110 contrast pairs pass.

The focused browser invocation initially passes 20 cases and fails four keyboard
cases because the long design catalogue was scrolled to centre its Tools button.
Radix correctly chose the available space below that artificially centred anchor,
violating the test's above-composer assertion. The fixture now places its composer
at the visible bottom as in the app. All four keyboard cases pass in the focused
rerun, without changing product CSS or weakening the geometry assertions. Initial
source/log and corrective results are retained. The combined 24 cases cover both
engines/themes, existing menu behavior and photo-edit regression; this is not a
new invocation of the entire 739-case suite.

## Screenshots

`tools-phone-dark-webkit-synthetic.png` and the other viewport/theme captures
under the evidence folder use invented fixtures. Codex inspected the phone-width
dark menu. The user's supplied phone screenshots are not copied into the repo.

## Open questions / release boundary

Publish only the tested compiled static tree after its private UI backup. Preserve
old hashed assets for open tabs, verify live hashes and the actual installed menu,
and retain the existing backend/worker/data and service identity. Physical iPhone
review remains a user check; no new phone pass is claimed by browser automation.
