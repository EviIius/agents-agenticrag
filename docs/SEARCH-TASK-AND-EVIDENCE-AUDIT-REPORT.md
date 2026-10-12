# Offline task and evidence audit report

11–12 October 2026. Scope: `SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md`.
Prior checkpoint: `cb5a1a4b`; no new native inference.

## Summary

The retained failures have distinct, measurable causes: contradictory task/query
fields, lost table structure, data displaced by introductory passages, missing
requested properties and unsupported answer claims. Three actual source
selections reproduce exactly, including their calibrated token budgets. A
complete relevant table fits the existing budget but loses all three source
slots to introductions. The next proposed correction is bounded data admission;
this audit does not qualify Search or release Images.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Replay actual creative/query contradictions without inference | Pass | `task-replay.json`; haiku/fiction retain lookup fallback |
| Inspect native-schema/host consistency | Diagnosed | Schema permits independent task/query fields; host rejects non-lookup queries; no conditional native grammar is claimed qualified |
| Preserve force, detected external/missing-source checks | Offline pass | Negative tests; unrelated factual creative label still exposes an unresolved guard limit |
| Raw page → extraction → chunks → actual selected passages | Exact replay | Three trace JSON files; selected text/headings and ranking/selection checked |
| Reconstruct changing context accounting | Pass | 28 original answer requests/usage records; original estimator recurrence |
| Separate query drift from evidence coverage | Pass | Frozen provider batches ignore new queries; original-question-only ranking selects the same ordinals |
| Identify actual source roles and table loss | Diagnosed | Raw header/row counts, extracted hashes, selected chunk hashes and original manual review |
| Measure feasible data admission within frozen limits | Pass, host-only counterfactual | Existing table 463 tokens; replacing one caption costs 5,333 of 5,502 available |
| Inspect missing currency and recent-results coverage | Diagnosed | Actual six supplied pages, all archived pages, selected/omitted game chunks and fixed provider queries |
| Meaningful diagnostic negative tests | **29 pass** | `tests-complete.log`; source-role reversal, missing property, wrong stage/year, missing headers, ambiguous columns and token admission |
| Preserve original scores, cases, reports and source | Pass | Prior 16,675 frozen files and 17,369 committed evidence/eval files verified; 400 generated test records/captures retained separately and originals restored |
| Product/native/Research/image/workflow change | None | Product diff empty; no model calls or release |
| Repository/browser regression checks | Pass | 508 Python / 39 frontend / 473 browser; three existing browser skips |
| Local/verified HTTPS health and runtime | Pass | Both health endpoints 200; Ollama 0.35.0; no deployment/restart |

## Changed files

- **Production server/web/shared/dependencies:** none.
- **Isolated audit:** `artifacts/images-i1/search-task-evidence-audit/` contains
  an offline trace/replay script, diagnostic exact-cell checks, tests, three
  source traces, task replay, diagnosis, input verification and test logs.
- **Docs:** this H4 report, `SEARCH-TABLE-ADMISSION-PLAN.md`, `AGENTS.md` and
  `DEFERRED-FIXES.md`. Earlier proposals/reports are preserved.

## Deviations from SPEC.md

The approved offline scope adds diagnostic tools only. It does not modify native
schema, planner or answer prompts, host policy, sampling, model/default/runtime,
packages, live data or the installed application. Original cases and automatic
scores remain unchanged. Counterfactual empty queries and passage replacement
are explicitly host-only diagnostics, not new model results or deployed repairs.

An initial audit test wrongly expected no currency-name/code occurrence anywhere
in the archive. It failed on an unfetched exchange-rate page's currency menu.
That failure is retained in `tests-initial.log`; the corrected diagnostic separates
name availability from an explicit country/property relationship in supplied
evidence. This changes no original benchmark assertion or score. Initial lint
preparation failures and repairs are also retained separately.

The initial evidence archival guard excluded existing deferred-polish, Phase T
and reliability-browser capture directories. It stopped during complete-set
prevalidation before restoring any file. The original script, failure and source
hash remain intact. A separately frozen v2 admits only those existing synthetic
test output directories with the same type/name checks; it archives 400 generated
files and restores every original byte. `archive-v2.log`, source manifests,
`regenerated-test-evidence.json` and final closeout retain this remedy.

## Runtime observations

### 1. Creative/query inconsistency is mechanical; intent safety is separate

Both original native plans say **creative** and include a search query. The
schema allows those fields independently. The existing host rejects that
combination, catches the rejection and chooses lookup, causing the failed search
decisions. Exact offline replay reproduces both original host decisions.

Changing only the saved query array to empty makes the existing host stay local.
This does not establish that the pinned runtime can enforce a prospective
conditional/union grammar; no such grammar is executed or qualified here.

Blindly trusting the creative label is also insufficient: an offline negative
shows that a clearly factual request with a creative/empty-query label stays
local under the current guard. Detected external requirements and forced Search
remain protected, but this label/intent gap is unresolved. Dropping every stray
query without independent admissibility would conceal a failure.

### 2. A complete relevant table is available and affordable, but omitted

The original comprehensive-list case fetched a page whose extracted table
contains **28 rows**, including **23 explicitly positive loss rows** and five
literal dashes. Dashes are preserved as source values, not converted to zero.
The table has the original Team / Finals Lost / Finals Played / Finals Won roles.

| Measurement | Actual value |
| --- | ---: |
| Table chunk ordinal | 3 |
| Selected source ordinals | 0, 1, 2 — all introductions |
| Table characters | 1,684 |
| Calibrated tokens/character | 0.2629749331 |
| Selected evidence cost | 4,978 tokens |
| Evidence budget | 5,502 tokens |
| Unused budget | 524 tokens |
| Omitted table cost | 463 tokens |
| Cost after replacing one caption | 5,333 tokens |

The table fits even before replacing a caption; the **three-passages-per-source
cap**, together with ranking that prefers the introductions, prevents admission.
Increasing context or making another model call is unnecessary for this specific
failure. A one-caption replacement fits both existing passage and token limits.
No new answer is generated from that counterfactual.

### 3. Other source structure is lost before or during chunking

| Source stage | Observed loss | Consequence |
| --- | --- | --- |
| Primary champions HTML table | Raw main table has 81 rows; extraction preserves only four legend pipe rows | Main year/participant/result data is absent from that extracted page |
| All-series HTML table | Raw main table has 1,069 rows; extraction hits 80,000-character cap and starts with a data row used as a header | Historical coverage and column-role binding are incomplete; stages are mixed |
| Champion / Runner-Up page | Raw structured table becomes plain lines; only first selected chunk carries headers | Later selected values lack repeated roles |
| Complete loss-count table | Original header/rows survive extraction and chunking | Ranking/source-slot selection discards the whole data unit |

The original answer's champion/runner-up reversals remain genuine contradictions
of its cited source. Structure loss explains a risk; it does not excuse the
answer or turn it into a support pass. Column/header preservation, context and
coverage need separate evidence from citation ID validity or word overlap.

### 4. The replay cannot measure fresh query discovery

The eval uses recorded provider batches. New native queries affect passage
ranking, but do not fetch different search results. A plan's unrequested
"later won" relationship is real query drift; this run cannot establish that it
caused different discovery. Ranking with the original question alone selects
exactly the same passage ordinals in all three audited cases.

| Case | Calibrated ratio | Evidence budget | Exact actual selection reproduced |
| --- | ---: | ---: | --- |
| Comprehensive list | 0.2629749331 | 5,502 | Yes |
| Capital/currency comparison | 0.3454909707 | 5,506 | Yes |
| Recent results | 0.2557344139 | 5,512 | Yes |

A future query-aware live/supplemental comparison must be separate and expose both
arms to equivalent evidence. Original frozen replay scores remain useful for
regression; missing coverage must not be silently repaired in its corpus.

### 5. Missing properties and chronology cannot be filled from memory

The comparison's native queries correctly request capitals and currencies for
both subjects. Its old recorded provider queries request only Japan's capital,
Japan's currency and Australia's capital. All six actual supplied pages lack
Australian-dollar/AUD text. One unfetched archived exchange-rate page lists
"AUD - Australian Dollar" in a currency menu; that string alone does not
establish the requested country/property relation in the supplied evidence.
The original answer explicitly admits adding the currency from memory. It
remains unsupported despite its automatic pass and correct world fact.

The original comparison rubric requires Tokyo, Canberra, yen and **dollar**.
That lexical requirement does not validate the missing country/currency relation.
Neither adding the expected word without support nor accepting a memory-filled
answer repairs evidence coverage. A table-admission change cannot supply an
absent fact. Retain the original case/score as history and regression evidence;
review a separately declared, coverage-checked equal-evidence comparison before
using another full run as grounding qualification. No corpus/target change or
silent regrade is made in this audit.

The recent-results archive was collected for **2022/2023/2024**, while the fresh
plan mentions 2026. It cannot establish five current seasons. The user's exact
granularity could mean series or games; the answer is unqualified under either
completeness claim. Even within its game interpretation, fetched 2024 games 4/5
exist in chunks 7/9, but selection retains games 1/2/3, and the answer mixes older
2022/2023 games as most recent. These are coverage/time failures, not equivalent
wording. Original automatic scores are retained rather than silently regraded.

## Test output

- Initial diagnostic attempt: **26 pass / 1 fail**; corrected the archive-wide
  absence hypothesis after inspecting the actual unfetched menu, retaining the log.
- Initial corrected diagnostic suite: **27 pass**. Two admission/chronology
  negatives added; complete suite: **29 pass**, 18.03 seconds. Existing third-party
  `codecs.open` deprecation warning retained.
- Offline audit: **two task replays**, **three exact source/rank/selection
  replays**, **28 retained usage/context records** accounted for. **Zero native
  calls**; network connections forbidden during the audit and diagnostic tests.
- `make check`: **508 Python / 39 frontend tests pass**, lint/format/types,
  coverage, contrast, API/additivity, motion and privacy checks pass.
- `make e2e`: **473 passed / three existing skips**, 39.2 minutes; no failures.
- Final closeout: **16,675 frozen files / 17,369 prior committed evidence/eval
  files unchanged**, 400 fresh test outputs retained separately; local and normally
  verified Tailscale HTTPS health 200, Ollama 0.35.0. The archival helper performs
  restoration before the final health script, whose own remaining restore count
  is consequently zero. No historical result is replaced by fresh output.
- The same existing settings screenshot loop also creates **40 previously
  untracked captures**. These are archived under this checkpoint with provenance
  and byte hashes, giving **440 fresh test outputs retained** in total; the 400
  restored originals and every earlier input remain intact.
- Prior original full score remains **baseline 24/25, candidate 22/25**. No new
  E12/G9, semantic/full consistency, live Web or physical phone pass is claimed.

## Screenshots

No new product UI or physical-phone screenshots. Browser regression captures use
the fake runtime and synthetic content. Fresh generated evidence is retained
separately; prior tracked screenshots and coverage data are restored exactly.
No real recording, document name or private content is captured.

## Open questions for Jake / recommended next checkpoint

Proceed with **one bounded data-admission correction** in
`SEARCH-TABLE-ADMISSION-PLAN.md`: give an eligible, relevant original table a
source slot within the existing budgets, retaining its complete header/rows and
excluding captions or ambiguous pseudo-tables. Start with offline tests and the
original omission replay; stop before native inference. This is a necessary
mechanical repair, not a promise of safe factual answers.

Task/query consistency, extraction fidelity, missing facets, chronology and
model adherence remain open. Do not launch another full model run while these
known independent failures remain untreated or required facts lack supporting
corpus coverage. Images stays held, Research stays
shelved, and ordered workflows remain after qualified reliability/image release.
