# QA and roadmap repairs — checkpoint 1

User authorization: 16 October 2026, “Based on the roadmap and then implement it,
I also want you to do a proper QA analysis too to make sure the fixes are working.”
Source: Jake's pasted Claude review summary. The original detailed report/run log
is unavailable; its model scores and Linux failure classifications are unverified.

## Scope and acceptance

Work on `codex/qa-roadmap-repairs`, based on accepted main `74eae6d8`. Preserve the
installed app and stop with an H4 review report before publication.

| Repair | Evidence required |
| --- | --- |
| Draft ownership after rejected sends | Reproduce delayed failure across chat switches; retain the rejected source draft without overwriting another/newer/cleared draft; test both browser engines. |
| Unsupported thinking | Reject invalid explicit levels before inference; preserve supported wire values and omission/default precedence. Rename Auto to Model default. |
| Workflow Document input | Accept extracted PDF/DOCX attachments as documents, reject other kinds, and execute a synthetic graph through the real workflow API. |
| Library/image conflict | Permit explicit Eject of loaded non-chat/embedding models in Models; retain hidden status, Library configuration and indexes. Preserve all existing image admission/memory limits and no automatic unloading. |
| Long thinking | Show truthful elapsed-time guidance using the existing activity clock; stopping uses the existing cancellation action. No promise to force an answer and no hidden second call. |
| Aether display name | Change current display/export labels and PWA metadata; preserve service, schema identifiers, data directories, preferences, listener and Tailscale route. |

## QA protocol

1. Retain failing focused reproductions before repairs. Investigate rather than
   assume that Claude's failures are machine slowness.
2. Run synthetic server/API and request-contract tests, then focused Chromium and
   iPhone-profile WebKit regressions, including draft ownership and manual Eject.
3. Run full `make check`, a complete `make e2e`, and build/bundle/motion/privacy
   guards on the frozen candidate. Preserve original tests, thresholds, inputs,
   failures and evidence. Browser fixtures never call installed runtimes.
4. Record actual test counts, supported behavior, screenshots, unresolved limits
   and whether each bug reproduced. Browser geometry is not a physical iPhone
   acceptance or a model factual-quality evaluation.

No dependency, model/runtime installation, production prompt/sampling/default
change, native inference, Research, agent/tool loop or automatic routing. Future
Answer now semantics and stronger thinking budgets need separate evaluation if
they alter model requests; a cancelled stream alone is not a final answer.

Later checkpoints: remaining workflow blocks, then bounded read-only chat tools
under a separately reviewed scope, then routing if task-specific evidence supports
it. The shelved Research qualification is not reopened by this repair checkpoint.
