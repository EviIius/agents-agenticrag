# Named evidence fields checkpoint report — 10 October 2026

## Summary

The prepared v14 contract was tested once on the original first Web case.
Named JSON references and required identity keys were valid, but two table rows
selected identity alone and another selected prose unit exceeded its quotation
limit. The host rejected the response before factual output and stopped the
trial. No remainder, Library, candidate or retry followed. The independent
context-warning correction passed its release gates and is now published as a
frontend-only update, with a private fallback. The failed answer contract remains
isolated.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Preserve original inputs and earlier executed source | Pass before and after execution | 7,296 original hashes, 194 prior frozen files, six prospective files and 204 current frozen files; `final-preservation.json` |
| Freeze prepared v14 before inference | Pass | `artifacts/reliability/evidence-v14/manifest.json`, 204 files; prepared module unchanged |
| Reject raw JSON/invalid selections before factual output | Pass in tests and native smoke | Six new stream/stage tests; rejected native trace |
| Named native references and identity fields | Pass for this response only | `smoke-review.json`; original supplied schema accepts the returned selections |
| Host protocol and complete supported answer | **Fail** | Identity-only rows fail minimum two-column requirement; separate long excerpt fails source budget |
| Full original Web/Library and consistency/performance qualification | **Not run / not passed** | Immediate stop; no second grounded stream or success-answer timing claim |
| Repository regression checks | Pass | 458 Python, 39 frontend; final `make check` |
| Independent context-warning focused browser checks | Pass | Six Chromium/WebKit checks, synthetic warning screenshots |
| Context-warning build/performance | Pass | Successful build; initial static-import JS gzip 240,843 bytes, below 256,000-byte budget |
| Full browser release and publication | Pass | One complete rerun: 463 passed, three existing skips; `context-warning/publication-20261010T182952757758Z.json` |

## Changed files

- Isolated evaluation tooling: `run_contract_v14.py`, `contract_stream_v14.py`
  and copied `trials/evidence-v14/app/{runs,search,library}` modules. The prepared
  `evidence_object_v14.py` is unchanged from its prospective freeze.
- Tests/tooling: six stream/stage tests in `test_evidence_object_stream.py`;
  a `.pyi` test interface for the frozen subprocess driver; guarded
  `scripts/publish_context_ui.py` for the independent static release.
- Documents/evidence: `EVIDENCE-OBJECT-PLAN.md`, this H4 report,
  `CONTEXT-WARNING-RELEASE.md`, AGENTS scope and raw public/synthetic traces under
  `artifacts/reliability/evidence-v14/`.
- Existing UI correction: six frontend/design modules already implemented in
  `92fc2d6`'s tree. No new server answer integration or provider/prompt edits.
- Browser test: `conversation-motion.spec.ts` brings the containing thread
  into the viewport before its nested code-copy control. Real copy interactions,
  local feedback, clipboard status and the 1.5-second clearing assertions remain.

## Deviations from SPEC.md

Native selector inference remains an explicitly authorized isolated experiment.
The declared failure stop was honored. No new model call was added: the existing
planner and one grounded answer stream ran, plus the harness's existing warming
request. Later Web cases, Library and a candidate would require the failed gate
to pass, and were not run. Research remains shelved.

The independent frontend release is limited to the previously authorized context
warning correction after Jake's remaining-work approval. It is unrelated to the
failed evidence answer contract. Existing server behavior, output reserves,
sampling and prompts remain unchanged. Required browser failures block publishing.

## Runtime observations

### Native smoke

The original `nba-2021` case ran on the daily installed 32K profile using the
unchanged recorded corpus, planner path and requested answer rubric. The model
returned normal-stop JSON after **8.16 seconds**. Four owned units were selected:
two table rows with only column zero, an 18-word recap sentence, and a prose
excerpt whose stored word cost was 73. IDs were not duplicated; identity keys
were present. All four selections satisfy the supplied named-field schema.

However, the schema allows identity-only rows, while host validation requires at
least two columns. The two rows therefore lacked the requested scores and failed
the host guard. This is a contract-design mismatch, not evidence that Ollama
ignored the requested object grammar. A host-only audit of each unchanged single
selection independently rejects the long prose unit for its quotation budget.
The shorter recap independently renders, but was not emitted or used to repair
the failed response. This diagnosis is not a passing answer or a revised score.

The child stopped automatically with exit 1 and retained raw requests, events,
catalogues and snapshots. There is one grounded and two outer planner/answer
streams. No factual text reached the test assistant. No full eval report, manual
answer qualification, successful answer latency or new model-comparison result
is claimed. Original failures and thresholds remain intact.

### Next reliability action

Before another native trial, make native schema and host admissibility agree:
reject identity-only row selections structurally, and expose only standalone
prose units that fit their source allowance with all required context intact.
Prototype legal original-field bundles and explicit source costs under a bounded
schema rather than assuming optional fields will be chosen correctly. Do not
clip qualifiers or insert missing values. Cumulative limits, relevance and
completeness still require host validation and manual review; structural validity
alone cannot qualify a model. No replacement contract was executed in this turn.

### Independent context warning

The warning accurately distinguishes the full context window from usable input
space after output/safety reserves. Explicit chat limits precede saved model
defaults. Six focused browser checks pass, including payload assertions proving
only the user's chosen output limit is sent. The narrow-screen warning was
visually reviewed from a synthetic WebKit capture. This is not a physical iPhone
acceptance claim. The adjusted capture occurs while the controls drawer is
closing; state assertions, rather than that still, establish warning removal.

## Test output

- Preflight: **24 passed**, isolated-file lint passes.
- Full `make check`: **458 Python / 39 frontend passed**. Required coverage,
  contrast, types, API/prompt/motion guards and privacy scan pass.
- Initial isolated import sorting and shell-log path failures occurred before
  inference and are recorded in `setup-observations.json`.
- Initial full check failed because statically importing the subprocess driver
  caused mypy to traverse historically untyped eval tooling. A typed interface
  was added after inference without editing any frozen executed file. The final
  check passes; the initial failed log remains.
- First complete browser run: **462 passed, one WebKit failure, three existing
  documented skips** (38.1 minutes). The failure occurs at the viewport assertion
  before copying: nested scrolling moved the thread while the outer page stayed
  at the preview controls. The retained trace confirms that position.
- After explicitly scrolling the containing thread and settling finite motion,
  the unchanged real copy/feedback interactions passed **ten consecutive checks**
  (five each in Chromium and WebKit). These ten checks did not replace the
  required complete release invocation below.
- One complete Chromium/WebKit rerun after the scroll correction: **463 passed,
  zero failures, three existing documented skips** (38.2 minutes). All 5,081
  original tracked artifacts were preserved; 385 changed outputs were saved
  separately before restoring their original bytes.
- Frontend type/lint/format/unit checks also pass after the test correction.
- No new real-provider full Web/Library or consistency pass.
- Command logs and Playwright's diagnostic dump remain verbatim, including their
  trailing whitespace. Source/document diffs pass whitespace checks; raw evidence
  was not rewritten to make Git's evidence-file whitespace warnings disappear.

## Screenshots

`artifacts/reliability/evidence-v14/context-warning/input-reserved-webkit-fake.png`
shows the readable synthetic recording warning. Chromium and output-adjustment
captures are retained in the same folder. No real recording/document text or
filename was captured. Historical screenshots and coverage are restored after
test-generated updates; new results are kept separately.
Duplicated general synthetic stills from the full suites are archived under the
ignored `tmp/reliability/evidence-v14/` path, with per-file hashes in the capture
storage receipts. Logs, failed trace, focused changed-state captures and measured
performance JSON are retained with the checkpoint; the original committed stills
remain byte-for-byte unchanged.

## Gates

These statuses distinguish the independent frontend release from the failed
native answer experiment. A passing product regression check does not qualify
the experimental answer contract.

| Gate | Status | Evidence |
| --- | --- | --- |
| G-1 checks/coverage | Pass | `make-check-final.log`; 458 Python / 39 frontend, all required packages above 80% |
| G-2 single complete browser invocation | Pass after correction | `context-warning/full-browser-after-scroll-fix.log`: 463 passed, three existing skips; first failed full run and ten-check consistency retained separately |
| G-3 tests preserved | Pass | Ledger below; extra visibility and settling assertions, no removed assertions, skips or raised thresholds |
| G-4 budgets | Pass | `context-warning/bundle.json`; final render p95 3.1/3.0 ms and first-token overhead 65.8/59.0 ms in Chromium/WebKit |
| G-5 axe, contrast, keyboard | Automated checks pass | Complete browser rerun, 74 contrast pairs and keyboard walkthrough; no physical phone or VoiceOver pass claimed |
| G-6 additive API | Pass | `make-check-final.log`; installed server source unchanged |
| G-7 preserved database rows | Pass | Existing synthetic migration/unit checks; no schema or data migration in this release |
| G-8 frozen production prompts | Pass | Existing prompt-hash checks; isolated experiment remains outside production |
| G-9 production Web replay | Not triggered | No changes under production `server/app/{search,runs,providers}`; failed native smoke is retained, not a release eval |
| G-10 runtime payloads | Pass | Golden/parameter checks, focused context/output-limit captures and complete browser rerun |
| G-11 privacy | Scanner pass; synthetic capture discipline | `privacy-audit.json`; fake-only focused captures reviewed, no private source content used, old evidence restored; scanner limits retained |
| G-12 deployment invariants | Pass | Unit/PWA checks and publication receipt: local/HTTPS health, stable server parity, unchanged service/Tailscale and production `/design` 404 |
| G-13 reduced motion | Pass | Existing system/Always assertions passed in the complete browser rerun |
| G-14 design states | Pass in focused checks | Existing production-component transcript/document examples and synthetic captures |
| G-15 migration rollback | Not applicable | No migration; old static tree and consistent private database backup saved before successful publication |
| G-16 Jake's phone check | Not checked this checkpoint | Automated WebKit is not a physical iPhone acceptance result |

## Test-diff ledger

| File/test | Change | Why | Behavior still asserted? |
| --- | --- | --- | --- |
| `web/tests/conversation-motion.spec.ts`: code/transcript copy feedback | Wait for visibility and finite motion; scroll/assert the containing thread before scrolling/asserting its nested copy control | WebKit's nested scroll left the outer page at the preview buttons, failing before copy | Yes: real clicks, code/transcript copied status, local check, 1.5-second clearing and no toast remain; no forced clicks, removed assertions, new skips or timeout changes |

## Budgets

| Measure | Recorded baseline / previous | This checkpoint |
| --- | --- | --- |
| Initial static-import JavaScript gzip | Phase 3: 224,491 bytes; previous stable polish: 240,526 | 240,843; +317 bytes, within both 256,000-byte total and 8,192-byte growth limits |
| Required line coverage | At least 80% | Providers 87.0%; runs 89.4%; search 88.9%; transcribe 93.1%; documents 96.6%; library 92.6%; backup 96.8% |
| Streaming render p95 / 300-message scroll p95 | Stable: 1.3/2.0 ms render, 16.8/18.0 ms scroll; render limit ≤8 ms | Current: 3.1/3.0 ms render, 16.8/19.0 ms scroll; complete performance tests pass, only the streaming row renders |
| First-token UI overhead | Stable: 101.0/61.1 ms; limit ≤150 ms | Current: 65.8/59.0 ms Chromium/WebKit |

## Core unchanged

Every browser guard below passed in the single complete corrected invocation
(`context-warning/full-browser-after-scroll-fix.log`). Python guards passed in
`make-check-final.log`; installed invariants are in the publication receipt.

| Core | Retained guard |
| --- | --- |
| C1 send/stream/stats | `chat.spec.ts` live-chat tests |
| C2 stop/partial text | `chat.spec.ts` Stop and keyboard Escape tests |
| C3 reopen/resume | `chat.spec.ts` reopen and `web.spec.ts` late-snapshot tests |
| C4 long answer/idle timeout | `chat.spec.ts` real-time timeout gate |
| C5 actions/export | `actions.spec.ts` |
| C6 model/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 chosen parameters | `parameters.spec.ts`; Python golden/request tests passed |
| C8 Web citations/recovery | `web.spec.ts`; Python search/evidence/grader tests passed; production source unchanged |
| C9 transcription/storage/save | Transcription/download/audio-storage suites; Python transcription tests passed |
| C10 phone layout/drawers | Mobile layout/composer suites; existing context-warning focused checks passed |
| C11 shortcuts/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12 read-only legacy import | Python import tests passed in `make check` |
| C13 deployment identity | Python deployment tests passed; publisher verifies the installed service |
| C14 untrusted markup/SSRF | `foundation.spec.ts`; Python SSRF tests passed |
| C15 performance | `performance.spec.ts` and streaming/first-token gates |
| C16 automated accessibility | Foundation/review/keyboard suites; VoiceOver remains excluded and historically failed |

## Migrations and rollback

No production schema, API, server source or data migration was added. Static
publication followed the complete passing browser gate. The publisher saved a
private consistent database backup and old static tree, retained old hashed
assets, then atomically wrote the index and service worker last. Publication
succeeded at 18:29:53 UTC; local and normal-TLS Tailscale health both return 200,
index/service-worker hashes match, and all 81 installed server files match stable
`f87db46`. The runtime was not restarted; saved settings were not edited.
The fallback directory is recorded in
`context-warning/publication-20261010T182952757758Z.json`. The static rollback path
restores the old entrypoints without rewinding chats or transcript outputs; no
forced failure/rehearsal is claimed because no migration was added.
Final verification also found no extra installed server-source files; Ollama
remains 0.35.0 and the private fallback database has owner-only permissions.

## Evals

One original-case native smoke ran and failed. The unchanged 24-case remainder,
Library, candidate comparisons and repeated native runs were not executed.
Source-schema validity did not imply host admissibility or semantic completeness.
No new production Web/Library/everyday qualification is claimed. Original input
hashes, reports, thresholds and prior failures remain preserved.

## Known limitations carried forward

- Reliable complete grounded answers are still unqualified: schema/host parity,
  retrieval, relevance, completeness and semantic support need further work.
- Ordinary-chat untrusted-record treatment remains unresolved and unchanged.
- The prior iOS keyboard issue recovered after an iPhone restart; its cause was
  not proven. No new physical phone test occurred in this checkpoint.
- VoiceOver's historical reported failure remains recorded; Jake excluded it
  from the current work list. No pass is claimed.
- Research is shelved and image generation is researched only; no installation.

## Open questions for Jake / next scope

This checkpoint stops for review after the one failed native smoke, as required
by `AGENTS.md` and the frozen plan. No Qwen3.8 qualification, Research restart,
image installation or production answer-contract promotion occurred. The next
bounded repair is native/host admissibility parity before another original-case
trial. Image generation remains the separately documented proposal.
