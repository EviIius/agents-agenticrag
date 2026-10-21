# Mobile Tools layout correction

21 October 2026. PR #7 merged as `91b2fdca`, with height-cap follow-up `954214cf`.
The correction is live in Aether.

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
| Initial JS budget | Pass | Final build: 255,946 gzip bytes / unchanged 256,000-byte limit |
| Static-only publication and actual installed UI | Pass | `publication-capped.json`, `installed-menu.json`; same service PID |

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
final initial static-import JS is 255,946 gzip bytes, within the existing 256,000 limit
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

The actual installed observer then exposed a longer disabled Library setup hint:
its second line made the panel exceed the intended compact size. A 328 px maximum
now bounds the menu alongside the existing safe/visual viewport limits; extra
text stays inside the action scroller. The capped build passes eight focused
phone/keyboard checks and both installed HTTPS observers. The first observer also
had an incorrect relative module path; it was corrected before running. Both
setup/height failures are retained separately. No product assertion was weakened.

The installed Chromium/WebKit checks use only intercepted synthetic API responses
and verify the final capped menu, last-action reachability, Default label,
selection, focus and typing. Menu height is 328 px in both observers, with no page
errors or failed assets. These contexts block service workers to guarantee API
interception, so they do not establish a fresh physical PWA pass.

## Screenshots

`tools-phone-dark-webkit-synthetic.png` and the other viewport/theme captures
under the evidence folder use invented fixtures. Codex inspected the phone-width
dark menu. The user's supplied phone screenshots are not copied into the repo.
`installed-tools-390-dark-webkit-synthetic.png` shows the deployed menu with the
long Library hint; Codex inspected that capture as well.

## Open questions / release boundary

The tested static update is published with private UI backups. All 429 incoming
files verify; old hashed assets remain available to open tabs. Local and normally
verified HTTPS index/service-worker hashes and health pass. The 124-file backend/
shared source, worker and plist hashes are unchanged; the service PID stayed the
same, with no restart, database operation, model call or task interruption.
Physical iPhone review remains a user check; no new phone pass is claimed by
browser automation. The photo-edit release's separate phone checklist is not
closed by this visual correction.
