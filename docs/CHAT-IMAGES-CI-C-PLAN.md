# CI-C implementation and verification

Authorized 14 October 2026: CI-C followed by the bounded native workflow trial.
Baseline: `6c317a5a197356895a7a6c116d0df8ab8714ea81` on the isolated branch.

## Implementation

- Keep Claude's supplied prototype and references unchanged. Use the existing
  Radix Dialog for a lazy viewer, CSS FLIP (320 ms) from/to the opening frame,
  200 ms navigation, keyboard arrows, drag/swipe and pinch/double-tap zoom.
  Viewer navigation follows the selected conversation branch in thread order;
  unavailable/removed outputs are excluded. Return focus to the opening frame.
- Share Save/Copy/Details controls between frames and viewer; add More like this
  and Refine with source-job lineage using the existing endpoint. Refine uses a
  removable thumbnail/seed chip and a prompt draft; no reference-image editing.
  Preserve separate text/image drafts and uncertain-request identity/seed rules.
- Offer Ask about it only when the selected runtime metadata reports vision true.
  Fetch the PNG on explicit action, enter text mode and use the existing upload
  path. Never send automatically or attach into a different chat after navigation.
- Add three-frame phone scroll snapping, position dots and visible touch actions.
- Markdown includes prompt and numbered PNG-name/seed lines; JSON retains all
  existing fields with explicit prompt/job ids/seeds. No embedded image bytes.
  No schema migration, inference, new packages or provider/prompt changes.

## Evidence

Meaningful lineage/export/branch tests; Chromium/WebKit viewer focus/zoom/swipe,
vision attachment and draft tests; both themes and widths with axe; both reduced
motion triggers; existing request/context parity; make check and one complete
make e2e invocation; unchanged supplied/history/main/installed hashes. Retain
failures before further tests overwrite temporary evidence. Synthetic videos
stay outside Git. Keep the existing native Web accuracy gate open.

After verification, run only the separately documented seven-call workflow trial,
retain exact synthetic requests/outputs/events and stop with both H4 reports.
