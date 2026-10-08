# Source closeout and model-comparison preparation — 8 October 2026

## Summary

Main now carries the verified production application from the deferred-polish
checkpoint. Unreleased Research runtime/schema/wiring is removed from the
current application tree; source and every failed trial remain on their existing
Research checkpoint and in preserved evidence. The live app was not redeployed.
The next candidate comparison is prepared, with named approval pending.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Current source matches verified polish | Pass | `artifacts/source-closeout/parity.json`: 448 production/tooling files match `41839b1`, whose application is unchanged from `85477f5` |
| Research remains shelved | Pass | Research runtime absent; 1,829 retained Research source/evidence files match the previous main checkpoint; original experimental application remains at `7737046` and `codex/phase-8a-research` |
| Checks/build pass on consolidated main | Pass | `check.txt`: 298 Python tests, 36 web unit tests, 74 contrast pairs, lint/types/format/API/prompt/row guards; `build.txt` |
| Build matches installed app | Pass | `build-parity.json`: index and service worker byte-identical; 240,526 compressed initial JS bytes within 256,000 |
| Browser evidence applicable | Pass by source parity | Same application and browser tests as the completed 457-pass/3-existing-skip suite in `artifacts/deferred-polish/e2e.txt`; no new browser assertion or production behavior changed in this closeout |
| Frozen ordinary comparison prepared | Pass | 20 synthetic everyday cases; unchanged 25 Search and 34 Library cases; 7,296 input/evidence hashes verified |
| Local and Tailscale app still healthy | Pass | `proposal-verification.json`; no service restart, data change or deployment |
| Candidate execution | Awaiting named approval | No download, profile, model call, runtime upgrade, new package or default switch |
| Physical phone follow-up | Not observed | No phone check or VoiceOver pass is invented; VoiceOver remains excluded from current work |

## Changed files

- **Server/shared/web/scripts:** restored the tested production tree instead of
  retaining the unqualified Research runtime and its unreleased API/schema/migration
  additions in main. This is source consolidation; no installed database is changed
  or downgraded. The test-only server isolation remains present.
- **Docs:** latest Research/VoiceOver scope, model proposal and frozen synthetic
  comparison inputs; this report and historical-harness warning.
- **Evidence:** parity, retained-history verification, checks/build and build parity
  under `artifacts/source-closeout/`. Earlier reports and benchmarks remain intact.

## Deviations from SPEC.md

The unqualified experimental Research API/schema additions were never released in
the installed 7B app. Removing their current source restores the accepted API;
it does not remove an accepted production endpoint. The existing additive-API guard
passes. The Research checkpoint remains recoverable rather than rewriting history.

No new product phase, dependency, prompt, sampling rule, model, automatic routing
or inference mode is introduced. Named-model approval remains required by AGENTS.md.

## Runtime observations

Read-only inventory confirms Apple M5 Pro, 64 GiB unified memory and Ollama 0.35.0.
The current daily model and embedding remain unchanged. Published candidate weight
sizes are not measured resident memory or local performance. Candidate compatibility
and actual `/api/show` capabilities still need verification after approval.

## Test output

- `make check`: pass; 298 Python and 36 web unit tests, 74 contrast pairs and all guards.
- `make build`: pass; compressed entry JS 240,526 bytes; built index/service worker
  match the installed frontend exactly.
- Frozen-input validation: all 7,296 hashes match; 20 unique everyday IDs and populated
  manual rubrics; original Search/Library cases and corpus unchanged.
- Prior complete `make e2e`: 457 passed, 3 existing skips. Not rerun because the 448
  application/tooling files, including browser tests and runtime fixtures, match
  that verified source. This closeout adds only documentation/evidence beyond it.
- Historical coverage artifacts were restored after the check; fresh coverage is
  stored separately in this checkpoint.

## Screenshots

Existing synthetic screenshots under `artifacts/deferred-polish/` remain applicable
by application-source parity. No new capture, actual filename, transcript or Library
content was used. No physical iPhone check was performed.

## Next steps / open questions

1. Named approval for `qwen3.8:27b-q4_K_M` (listed at 18 GB) and an isolated 32K
   comparison per [MODEL-COMPARISON-PLAN.md](MODEL-COMPARISON-PLAN.md). The approval
   question has been sent; no elapsed time is treated as consent.
2. After approval, verify compatibility and run the declared smoke and matched
   everyday/Search/Library comparisons. Keep all failures and existing release gates.
3. Present results before any default switch. Research remains shelved.

This handoff is committed locally on main, with a local fallback tag
`atelier-main-stable-2026-10-08`. No remote push is included in this closeout.
