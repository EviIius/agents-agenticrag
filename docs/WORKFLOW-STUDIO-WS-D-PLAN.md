# Workflow Studio WS-D execution plan

13 October 2026 · isolated base `96bfcbfd` · `codex/workflow-studio`

Implement Claude's Run panel, canvas states, follow controls, approvals, block
retry/optional skip, Run from here, Test this block, Pick favorites, immutable
run view, paged/filterable history, named versions, palette actions and paused
notifications. Keep its neutral cards, category tiles, desktop panels and phone
Outline/sheets. States and progress come from existing v2 SSE, rAF-batched.

## Reviewed details

- Per-block configuration alone is insufficient for cross-run reuse. Verify
  resolved model settings, identical Start inputs, connections and original
  source text/timestamps. Copy durable originals and rebind typed source pointers;
  never rewrite literal user text. Removed images cannot qualify for reuse.
- Single-block tests use verified upstream outputs or explicitly typed text/
  number/boolean samples. File/transcript/image samples require an actual saved
  run. They are hidden from Recent runs; expiry removes test records and leaves
  image files owned by the Gallery. No invisible native request is added.
- Reconnect snapshots contain the actual current text/progress. Older journal
  events cannot overwrite the snapshot. Timers never invent work progress.
- Run snapshots remain immutable. Restore changes the current draft with undo;
  layout changes do not alter invocation order or qualify reuse.
- Extend the motion guard only for the requested `stroke-dashoffset` activity
  pulse. Reduced-motion preferences remove both this loop and the sweep ring.
- No opacity reduction on whole text cards: dim only decorations, preserving
  existing text contrast. This carries forward the WS-C accessibility correction.

## Chat-image review, next

Read all three supplied Markdown files and prototype source; inspect all thirteen
synthetic reference images and exercise the prototype's text reasoning, image
creation and saved result in Chromium. References are copied byte-identically,
with hashes in `artifacts/workflow-studio/ws-d/provided-chat-images-sha256.json`.
The prototype simulates progress and images; its timers are not production logic.

CI-A precedes CI-B and CI-C, each with a review stop. Resolve impossible future-
phase prediction (the proposed 400 ms pre-phase word freeze) with immediate real
stage priority, rather than delaying tokens. Respect the existing motion limits
and use transform scale for progress fill rather than adding a longer small-
surface width transition. Transactional image acceptance must commit messages,
job rows and request identity before workers start. Text context exclusion needs
positive mixed-thread capture tests as well as unchanged ordinary captures.

## Evidence

Focused backend/browser tests before a frozen final source and one complete
`make check` / `make e2e` invocation. Keep failed attempts, original artifacts and
synthetic references, rehearse additive migration rollback on copied fake data,
verify initial/lazy bundle limits and both reduced-motion triggers. Retain videos
outside Git. No native calls, real private screenshots, main merge or deployment.
