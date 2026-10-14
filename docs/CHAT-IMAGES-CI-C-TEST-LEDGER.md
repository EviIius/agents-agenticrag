# CI-C test changes and retained outcomes

Baseline `6c317a5a`; final candidate source `f8e301c2`.
No assertion threshold, timeout, release target or existing skip is relaxed.

| Existing test | Change | Evidence / reason |
| --- | --- | --- |
| `phase5a.spec.ts`: delayed requested-chat controls | Await the separate model/header bootstrap before clicking; chat detail remains deliberately blocked | Full attempt's WebKit click did not open controls during bootstrap. Loading text, absent Save, restored Top K 42 and disabled unchanged Save assertions remain intact. Six focused WebKit repetitions pass. |

New `chat-image-viewer.spec.ts` covers viewer geometry/focus, conversation ordering,
keyboard arrows including nested Save ownership, swipe/pinch/double-tap/pan,
phone scroll snapping/dots/touch actions, lineage, uncertain-request identity,
separate text drafts across Workflows, removable refinement source, metadata-only
vision gating and the existing upload path, both motion preferences, and viewer/
refine axe at both themes and widths in both engines. A Python test proves job
lineage and selected-branch Markdown/JSON export without embedding images.

Retain focused attempts (12/8; 10/2; 20/0; two selector failures; two label
failures; 2/0; 18/0 repeated WebKit checks), the 60-pass interrupted full attempt,
and the 613-pass/two-failure full attempt. Every available trace/recording is
archived before a subsequent invocation; synthetic videos stay outside Git.
The closing-focus fix addresses a measured modal cleanup race; it does not add
an arbitrary delay. The portal measurement fix measures the actual mounted node.
The final single complete invocation passes 615 tests with three existing skips
and zero failures (1.0 hour); focused passes were not stitched into that result. The native workflow trial is separate from Web accuracy qualification.
