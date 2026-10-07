# Phase 8A refinement report — threshold feasibility, 8B held

## Summary

Three retained, materially different full trials improved evidence gathering and
host-valid native calls. Trial 2 reached the required fact score: 13/15 (86.67%),
20 percentage points above the unchanged 10/15 baseline. It did not pass semantic
support or minimum citations. Trial 3 scored 10/15 and still made unsupported
claims. Fact-threshold feasibility is demonstrated once; reliable qualification
and permission to advance to 8B are not. The installed 7B app remains untouched.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Cases, grading, original corpus and ordinary prompts frozen | Pass | `refinement/freeze-comparison.json`; original artifacts retained |
| ≥13/15 complete cases and ≥15-point gain | Trial 2 only; latest trial fails | Three full reports, table below |
| Native calls accepted by host ≥95% | Pass for trials 2/3: 99.15% / 99.11% | Full captured requests/events and host counters |
| Citations map to source IDs | Pass for all three trials | Numeric citation checks; this does not prove support |
| Minimum citations / whole-claim support | **Fail** | Per-trial quality reviews; HTTP claims cite unrelated evidence |
| Zero unsupported claims | **Fail** | Trial 3 PostgreSQL assertion directly contradicts its cited passage |
| Budgets, model calls and latency | Pass in all three trials | ≤9 calls, no exceeded counters, median/P90 below limits |
| No readable evidence means no answer from memory | Pass in controlled backend tests | Finish/no-call/time-limit tests; structured `research_no_evidence` |
| Controlled hostile-page case | Pass in one fresh case, with actual page exposure | `attack-trial-3.json`; no off-allowlist fetch, no copied sentinel, grounded maintainer answer |
| `make check` | Pass | 340 server tests, 36 frontend tests, 74 contrast pairs; Research coverage 90.9% |
| Full final-tree browser regression | **Open**, not repeated for an unqualified candidate | Historical 431 passed / 3 existing skips; prior report records exact scope |
| Existing Search equal-or-better (G9) | **Open/failing prior replay**, no waiver or favorable rerun | Prior `web-regression/comparison.json`; ordinary Search source unchanged |
| Installed app preserved | Pass | Schema 8, all 81 public code files equal accepted `d74067e`, no Research module; local/TLS health 200 |
| 8B / Research deployment | **Held** | Quality gates fail; no UI or deployment added |

Paths below are under `artifacts/phase-8/8a/refinement/` unless stated otherwise.

## Changed files

- **Research backend:** isolated planning revisions; regular-inflection lexical
  matching; whole-question/read-focus passage balancing; exact URL inventory and
  per-call allowlist enum; delimiter-safe tool JSON; suppression of unverified
  loop prose; structured refusal when no evidence was read. The latest candidate
  also has a Research-only answer reminder. Its failure remains recorded.
- **Eval helpers:** explicit unique output destinations refuse overwriting prior
  trials. Attack screening now requires actual fixture exposure and a grounded
  answer, preventing a vacuous empty-answer pass.
- **Tests:** historical/current prompt hashes, whole-request evidence retention,
  exact URLs, failed-page inventory, no-source refusal and activity contamination.
- **Docs:** authorization, phase notes, this report, helper README and initial
  report cross-reference. Public/synthetic trial evidence and coverage retained.
- **Unchanged:** ordinary Search/Library/context prompts and ranking/chunking,
  native base tool names/fields, API/schema, manifests, dependencies, sampling,
  host budgets, transcription engine, launchd, Tailscale and installed app.

## Deviations from SPEC.md

Jake authorized generic isolated Research refinement with before/after evidence,
keeping targets fixed. Research-only selection now balances whole-question and
read-focus matches within the same source/token/three-passage caps; the shared
Search implementation is unchanged. `read_page.url` gets a next-call enum of
actual allowed URLs minus failed pages. The host still validates canonical URLs
and applies the existing SSRF guard; no guessed URL is repaired or fetched.

Planning v1/v2 remain in source. Planning v3 and its scoped answer reminder are
frozen in `prompts-v3.json` and tested by hash. Ordinary E8 is unchanged; the
reminder is appended only for an isolated Research answer. The latest candidate
is not qualified: stronger generic wording did not remove unsupported claims.
No claim is made that a bundled change caused the observed score regression;
there was no ablation and real generation varies.

Zero readable sources now raise a structured error without the final answer
call. A source-free memory response is not an acceptable Research answer. This
does not solve partial evidence: the HTTP case still fills a missing part from
memory despite having evidence for another part.

No gates, case assertions, baseline or grading were lowered. Even equivalent
TLS/date wording remains a raw miss where the frozen regex rejects it. No
favorable rerun was selected as a release pass. Current source is the unqualified
trial 3 experiment, preserved for inspection, not a promoted version.

## Runtime observations and evals

All three trials use the same actual daily Qwen, with no sampling overrides,
temporary ASGI databases and the original per-case recorded web results/pages.
Each candidate was hashed before inference and remained unchanged during its
full run. Adaptive query text still gets the same pooled frozen search results;
these trials do not measure adaptive discovery on the live web.

| Measure | Trial 1 | Trial 2 | Trial 3 (current) | Required |
|---|---:|---:|---:|---:|
| Complete fact cases | 11/15 | **13/15** | 10/15 | ≥13/15 |
| Gain over baseline | +6.67 points | **+20 points** | 0 points | ≥15 points |
| Native schema validity | 100% | 100% | 100% | Insufficient alone |
| Host-valid native calls | 86.24% | **99.15%** | **99.11%** | ≥95% |
| Citation IDs valid | Yes | Yes | Yes | 100% |
| Minimum citations in every case | No | No | No | Yes |
| Whole-claim support | Failed | Failed | Failed | Zero unsupported cases |
| Median / P90 total time | 11.81 / 15.83 s | 20.05 / 32.53 s | 16.24 / 36.30 s | ≤90 / ≤200 s |
| Max model calls | 9 | 9 | 9 | ≤9 |
| Budgets exceeded | Never | Never | Never | Never |

`trial-N-plan.json`, `trial-N/inputs.json`, full reports, captured native requests,
parsed events, answers and exact selected source passages are retained. The
initial lint/test failures and their corrected runs are retained too.

### Support findings

- **HTTP:** trials 2/3 give correct weak-matching/304 facts but cite an If-Match
  source whose selected passages establish neither fact. Reading that source
  does not license remembered facts about If-None-Match.
- **PostgreSQL:** trial 3 says a statement sees commits made *after* it begins.
  Its cited passage says commits before the statement and no changes during it.
  This is a genuine contradiction, not formatting.
- **WCAG:** the essential-animation exception is omitted. The W3C body contains
  it, but the selection favors broad criterion/level discussion and the answer
  relies on a simplified secondary reference.
- **NASA/archives:** omissions and formatting misses remain under the unchanged
  assertions. Supported TLS-version wording is separately labeled in the manual
  review; its raw regex result is preserved.

These are blocking reviews, not certification of all remaining assertions.

The early `corpus-audit.json` measures regex availability somewhere in returned
page text, **not semantic completeness or correct entity/condition binding**.
The HTTP pool illustrates its limit: If-Match weak-tag discussion can satisfy a
loose regex without establishing If-None-Match weak matching. The returned
If-None-Match page is unavailable, while the RFC capture is truncated before its
normative header section. Other returned pages contain 304 examples, but the
prototype does not cite those passages. Do not turn the diagnostic into a claim
that every requested fact is safely supported by the frozen readable pool.

Runtime before/after still matches the qualification: digest unchanged, Ollama
0.35.0, configured and loaded context 32768. The architecture's 262144 maximum
is separately labeled and does not replace the operational context. The existing
40/40 native qualification is retained; ≥95% autonomous host acceptance is now
measured separately in real full runs.

## Test output

`make check` passes: **340 server tests, 36 frontend tests, 74 contrast pairs**;
Ruff, formatting, mypy, additive API, generated types, motion and privacy checks
pass. Research line coverage is **90.9%**. `check-trial-3.txt` records the complete
run, not a combination of partial successes. Targeted Research/prompt tests:
**44 passed**. Existing gate harness: **19 passed** earlier in this refinement.

The fresh controlled attack reads the malicious fixture and answers its legitimate
maintainer question. The attack sentinel is absent from both answer and persisted
activity; no off-allowlist fetch succeeds. Only one attack case is claimed.

A full final-tree E2E and fresh release G9 have **not** been presented as passing.
The prior 431-test browser invocation and failing 24/25 Search replay remain in
`docs/PHASE-8A-REPORT.md`. Since the candidate already fails its quality gate,
there is no release/8B promotion or additional favorable replay search.

### Frozen-test change ledger

`test-change-ledger.json` explains each changed assertion. Source-free tests now
require error/no-answer rather than accepting a memory answer; regeneration reads
synthetic evidence before exercising its separate answer. Sanitization asserts
JSON delimiter encoding and exact URL preservation. Base tool schema equality is
still asserted, plus exact per-call enum constraints. No test was deleted, skipped,
timed out more generously or weakened to rescue the score. Prompt hash updates
retain original hashes and link all failed before/after evals.

## Installed app and screenshots

No Research UI was added and no phone/UI screenshots were captured. Only authored
synthetic and public corpus evidence was used. No real recording, Library file or
user chat text appears in the new evidence. Deferred mobile motion, recording-menu
and VoiceOver limitations remain as previously recorded.

`installed-health.json` proves local health 200, schema 8 and 81 unchanged public
server files. The system curl separately verifies TLS health 200 without bypassing
certificate verification (`tls-health-curl.txt`). Python's standalone urllib health
check failed because its local issuer certificate was unavailable; that diagnostic
is retained rather than misreported as an app outage. The service was not stopped,
deployed or moved during this refinement.

## Recommendation and open questions for Jake

**Keep 8B on hold.** The fact and tool-validity thresholds are demonstrably
reachable, but the full Research quality threshold has not passed. Neither a
single 13/15 result nor valid citation IDs justify a Research UI or deployment.

The next useful experiment would target per-part evidence coverage and honest
partial-evidence abstention, with a retained before/after comparison. Repeating
prompt wording until a favorable answer appears is not qualification. Any broader
live/corpus revision must preserve this benchmark and reevaluate the single-shot
baseline fairly; it must not quietly manufacture the required gain.
