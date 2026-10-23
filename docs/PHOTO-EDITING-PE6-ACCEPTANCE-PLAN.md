# PE6 — overlap review and one acceptance check

23 October 2026 · `codex/masked-photo-editing`, isolated draft PR #9.

Jake accepted the recommendation to make one mask-handling correction, run one
bounded acceptance check, and shelve precision editing if quality remains poor.
This new scope does not reopen any PE2–PE5 ledger.

## Correction

The existing compositor correctly preserves unselected pixels. The earlier
outlined-face protection excluded forehead/hair pixels a natural brim needs to
cover. Keep the same ordered paint/erase contract and exact pixel verifier.
Add an explicit editable-area review before applying a selection, explaining
that adding an object can require selecting the existing details it covers.
Users can return to adjust the selection; review cannot add accidental strokes.
Retain keyboard access, Cancel, Undo/Redo, zoom/pan and phone reachability. Expose
the review through the existing synthetic `/design` selection states.

No automatic face detection, inferred model capabilities, schema migration,
library, new prompt pipeline, production model routing or default change.

## One native acceptance invocation maximum

Use the installed FLUX recipe and original private photograph. Prepare a new
head selection that explicitly permits intended cap occlusion over hair/upper
forehead while protecting the remaining visible face, eyes, nose and mouth.
Record the protected-feature polygon and overlap area privately. Inspect CPU
coverage and a separately labelled old-native recomposition diagnostic first;
freeze the final selection/request/source before the fresh invocation. Never
change that selection after seeing the new output.

Exactly one new FLUX head edit, existing four steps / guidance 1 / seed 42 /
8-bit eligible components / 1024-square native context. No Qwen invocation,
retry, extra helpers, download or package/runtime change. Failed/cancelled
invocations consume the single slot. Keep existing shared lease, empty Ollama
residency, parent-death watch and owned reaping; 24 GiB measured MLX peak,
1 GiB cache, 512 MiB swap growth, two-second health, and 120-second init /
60-second generation+decode / 180-second wall bounds. Stop on any technical,
resource, provenance or preservation failure.

For the whole-photo review, predeclare reuse of the PE5 **FLUX front and rear
glove** outputs. Do not select another engine/result after seeing acceptance
quality. These are retained old outputs, not new generations or an end-to-end
fresh three-step run. All masks must be disjoint; final CPU combination preserves
every pixel outside their union and the revised protected facial features.

## Decision and evidence

Inspect cap placement/fit, detached fragments, visible seams/background patches,
both gloves and hand anatomy separately. The new head edit must allow the brim
to overlap the intended forehead area and retain all remaining protected pixels.
The whole-photo result must still be judged for the full request, including
known retained-glove limitations. Pixel preservation alone cannot qualify it.

If the correction/full result still fails quality, shelve precision editing and
stop native testing. Retain source/evidence and existing live image functionality;
return to roadmap review without starting an unapproved theme/automation scope.
If quality improves sufficiently, stop for Jake's acceptance before integration.

Synthetic CPU occlusion/protection checks, focused Chromium/WebKit selection/
review/rejection/retry/short-phone checks, frontend lint/types/tests/bundle and
privacy evidence accompany the SPEC H4 report. Product-wide release gates remain
required before any later merge/publication. All real media, exact instructions,
mask coordinates and review images stay private. No merge or deployment here.
