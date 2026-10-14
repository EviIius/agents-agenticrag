# Chat images CI-B execution

13 October 2026 · isolated `codex/workflow-studio` · baseline `72619f46`.

Implement CI-AC7–16 with Claude's composer/cards and existing image worker/SSE.
Migration 013 adds message kind, ordered image links and retained request origins.
Prepare files/jobs under the existing image lock; commit both messages, every job,
links, origin and current leaf together; only then schedule. Failure removes
prepared files. Repeated identical request keys return the original turn; changed
inputs conflict. Retry is a sibling; cancellation addresses only its linked jobs.
Keep active text runs protected by the same-chat lock/guard. Image jobs retain
their existing resource/cancellation/recovery semantics and Gallery ownership.

Traverse normal ancestry, then omit both image roles before context budgeting or
provider requests. Ordinary golden captures must remain identical. Image-first
titles use 48 prompt characters at a word boundary without a title call.

One composer holds separate text/image drafts, count and optional fixed seeds.
Resolve seeds/request identity once for uncertain retries, including new chats.
Cards derive progress solely from job events; snapshots repair reconnections.
Reveal only observed session completions, once; history is immediate. Save uses
the cancellable format dialog. Gallery creation moves to new-chat image mode;
provenance survives chat deletion. Keep viewer/iteration/export for CI-C.

Verify migration preservation/rollback, atomic failures, idempotence, mixed
context, branches, scoped cancellation, all frame states, real progress, dropped
responses and SSE reconnection. Update only approved old UI-flow assertions,
preserving and strengthening coverage; record changes in the test ledger. Run
full check, offline web replay, one complete browser invocation, initial bundle,
motion, axe, privacy and installed/main preservation. Retain failed attempts and
synthetic screenshots; put videos outside Git. Stop with the CI-B H4 report.
