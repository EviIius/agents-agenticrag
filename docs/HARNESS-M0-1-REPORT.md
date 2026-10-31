# Harness M0.1 report

30 October 2026 · `codex/harness-m0-1` · documentation checkpoint

## Summary

Audited the supplied local-capability plan against production source
`e7bab217f8738cd31803afb1d732ae51c8d51a1f`, preserved it verbatim and documented
the existing architecture, reuse opportunities, conflicts and recommended order.
The main corrections concern existing workflows/capacity, Ollama-only transport,
private storage, transcript overlap, operation-specific approvals and unqualified
model/resource/latency claims. No feature implementation or inference occurred.
After this report, Jake clarified that conversational search/app actions and
Apple Messages replies are the priority. `ASSISTANT-FIRST-PLAN.md` and the audit's
revised §6 reflect that direction; the initial folder-first recommendation is
superseded, with the earlier commit/evidence retained.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Supplied plan retained without silently rewriting it | Pass | `docs/local-models-plan.md`; source SHA-256 in `observations.json` |
| Runtime, tools, loop, streaming, config, secrets, logging and tests mapped | Pass | `docs/harness-notes.md` §§2–3 and verification below |
| Seven projects mapped to existing source and missing work | Pass | Notes §3 |
| Phase 9, migration 010, priority and service checked | Pass | Notes §§2–4; actual SQL, capacity implementation and sanitized observations |
| External claims checked against primary documentation or marked unknown | Pass with explicit unknowns | Notes §4, including failed upstream URL retrievals and untested local compatibility |
| Practical next scope and deviations recorded | Pass | Notes §§5–7 and Assistant first; conversational app tasks take priority after Jake's clarification |
| No application, dependency, runtime, production data or UI changes | Pass | Docs-only diff, installed-code/plist before/after inventory and final health |
| Jake has reviewed and agreed with M0.1 | **Pending** | This is the supplied plan's human acceptance gate; not inferred from choosing the audit |

## Changed files

- `AGENTS.md`: scope/reference note for this docs-only checkpoint; no additional
  model-call, dependency or action permission.
- `docs/local-models-plan.md`: exact supplied document.
- `docs/harness-notes.md`: architecture map, corrections, primary sources and
  recommended build order.
- `docs/ASSISTANT-FIRST-PLAN.md`: clarified personal-assistant target, Apple
  Messages source-only preflight, concrete milestones and QA/review boundaries.
- This H4 report and `artifacts/harness-m0-1-20261030/`: sanitized host observations,
  code/plist preservation and focused verification. No screenshots or audio.

## Deviations from SPEC.md and supplied proposal

SPEC and accumulated user amendments remain authoritative. The proposal's
embedded kickoff/build prompts are not treated as new feature authorization.
No application specification or existing release threshold changes.

The revised product order starts with conversational app tasks and Apple Messages
drafts. Existing schema/queue/glossary mechanisms are reusable. Broad runtime
support, strict chat priority, repo-local production data,
blanket retry and arbitrary 40 GB residency are not accepted as current facts.

## Runtime observations

Read-only observations: M5 Pro, 64 GiB RAM, 1.8 TiB-class filesystem; installed
Python 3.14.7; Ollama 0.35.0, with no model resident when checked. Production
listener remains PID 77443 at 127.0.0.1:8787 under the original GUI LaunchAgent.
No configuration values containing tokens, private content, model weights,
database rows, real screen or microphone were read. No service was restarted.

## Test output

Evidence is under `artifacts/harness-m0-1-20261030/`.

- Three existing fake/CPU checks cover capacity fairness/cancelled waiters,
  unchanged chat payload under capacity, and admission by actual digest/context/
  size. Results: **3 passed** in `focused-checks.txt`.
- Documentation paths/required coverage, source-copy digest, docs-only diff,
  installed code/plist equality and local health: see `verification.json`.
- Existing privacy audit: see `privacy-check.txt`. It is a limited pattern check,
  not a semantic or image privacy proof.
- `git diff --check`: required clean for this documentation change.

Priority-clarification supplement: `assistant-priority-check.json` verifies 42
local links, the unchanged supplied plan, all 646 installed files and plist, and
local health. `messages-dictionary-preflight.json` records public command/class
names only: a send command exists, but no message-history class is exposed.
`assistant-priority-privacy.txt` records the new pattern scan. These checks did
not launch Messages, read a conversation, grant permissions or send anything.
No additional automated test suite or native call was run for this supplement.

`make check` and `make e2e` were **not rerun**: there is no executable/UI/API/schema
change. Their earlier passes are not represented as fresh QA. No native/model,
desktop-control, VM, DataHub, voice or image-generation test ran. No accuracy or
speed gain is claimed by source inspection or fake tests.

## Screenshots

None. This milestone has no UI change and intentionally captures no private screen.

## Open questions for Jake / review stop

The completed audit is ready for M0.1 review. The next recommended scope is AS0's
offline task contracts and review UI, followed by AS1's source/permission
preflight for a narrow Mac app/Apple Messages bridge. The exact scope and
acceptance criteria are in `ASSISTANT-FIRST-PLAN.md`.
M0.2/feature code, new dependencies/models/native trials and external actions
remain separate scopes. Main, the live app and pending design-critique PR #13
remain unchanged; no application merge or deployment occurred.
