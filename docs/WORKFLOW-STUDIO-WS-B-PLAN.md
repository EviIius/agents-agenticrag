# Workflow Studio WS-B implementation decisions

Scope: isolated `codex/workflow-studio`, following WS-A acceptance on 12 October
2026. Seven initial block kinds, definition storage and APIs, durable graph runs,
typed interpolation and exact legacy-template parity. Stop before WS-C.

## Corrections carried from the review

1. Graph runs/steps/attempts/sources/events use additive tables. Legacy rows and
   parsers keep their existing contracts. Migration 011 alters no existing table.
2. Execution order is topological, with stable ID ties. Canvas positions, titles,
   notes and viewport do not change the execution hash.
3. Immutable full snapshots have their own IDs. Two layouts may have the same
   execution hash without overwriting one another. Seeds are resolved after
   idempotency lookup and persist in the accepted snapshot.
   Autosave updates the current draft; immutable snapshots are created at run
   acceptance, so typing does not accumulate full document copies.
4. Retry retains completed blocks and completed images within a partly failed
   image block. Before submission it checks durable child request keys; cancellation
   also checks that namespace, closing the child-acceptance ownership gap.
5. Disabled/rejected paths are not taken. Joins wait for every incoming path to
   resolve and run when at least one is taken. Optional clean-up has an explicit
   original-transcript fallback edge, rather than implicit bypass.
6. Original transcripts are retained independently by run and source block, with
   their hashes. Cleanup checks source identity before and after its existing guard.
   Private-source ancestry is checked against actual loopback connection hosts.
7. File/media references are typed. Text interpolation supports literal values,
   exact tagged escaping, escaped braces and optional-line removal. There are no
   expressions, hidden instructions or truncation.

## API compatibility decisions

- New definitions, templates, block catalog, run-list and decision routes follow
  the proposal. Full definitions are returned for the initial list; summaries can
  be derived without another stored representation.
- Graph resume/cancel/sources/export use `/runs/{id}/v2/...`. The old routes retain
  their exact request/response schemas and legacy execution. The new builder will
  use the graph routes. V2 detail/list/stream project legacy runs read-only.
- Snapshot labels address snapshot IDs, not execution hashes, so naming one layout
  cannot rename a different immutable snapshot with the same execution hash.
- The merged SSE stream uses `legacySequence:graphSequence` as its durable cursor.
  Ephemeral text/progress have no ID and are not persisted. Each stream reads journal
  records under the existing conditions; it never polls for run status.
- The existing text-request construction is extracted into `text.py`. Legacy and
  graph performers share it through persistence callbacks. Legacy requests omit
  structured output; user-authored JSON blocks use the adapter's existing schema
  parameter, then validate the actual result strictly. Template prompt constants,
  provider adapters, ordinary chat pipeline and sampling precedence are unchanged.

## Remaining checkpoint boundaries

Cross-run reuse and single-block test modes belong to WS-D. No config-hash-only
reuse is implemented here. Their reviewed provenance/input/upstream-output checks
remain requirements. Knowledge/condition/Classify blocks belong to WS-E. The canvas
dependency belongs to WS-C. No native model experiment or live publication is part
of this checkpoint.

Jake's image preference is recorded in `docs/DEFERRED-FIXES.md`: ordinary composer
submission, progress and images as turns in the conversation, gallery secondary,
automatic seeds and optional repeat controls. It requires a separate durable chat
artifact scope and is not claimed as completed by WS-B.
