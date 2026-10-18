# Offline citation coverage report

18 October 2026 · `codex/native-agent-loop` · **zero new model calls**.

## Summary

An isolated detector now identifies the four missing bullet citations in the
retained N1 H02 answer and finds no obvious list/table gap in H01. It demonstrates
a metadata warning on a copy, preserving the original answer and grade.
This improves detection, **not answer quality**. The app and old N1 worker stay
unchanged. One generic unexecuted prompt candidate and a concrete bounded C1
retest plan are ready for review; N1 remains failed at four calls.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Detect each uncited list item/table row locally | Pass within documented subset | `experiments/native_coverage/check.py`; 34 synthetic fixtures |
| Introduction/header/parent/sibling does not grant a citation | Pass | Scope fixtures and nested/paragraph tests |
| Code, escapes, links and unknown IDs handled | Pass for tested forms | Positive/negative fixtures, including slash parity |
| No false claim of semantic or sentence-level verification | Pass | Explicit false fields and limitation test |
| Metadata-only warning on a copy | Pass | Preserves content/reasoning/parts/status/stats; preserves existing notices |
| Ordinary/partial/error messages unchanged | Pass | Five state/notice controls |
| Recorded H01/H02 replay without rewriting or regrading | Pass | `replay.json`, source hashes |
| Old N1 source, prompts and stopped ledger preserved | Pass | 196 old frozen hashes, ledger remains stopped at four calls |
| New native answer improvement | **Unproven / unexecuted** | Candidate hashes explicitly marked unexecuted |

Artifacts below are under `artifacts/agent-loop/coverage-v1/`.

## Replay results

| Retained answer | Detected structure | New diagnostic | Original result |
|---|---|---|---|
| S1-H01 | Six cited list/table units | No obvious structural gaps; prose unchecked | Pass, unchanged |
| S1-H02 | Four uncited bullets, lines 3–6 | `citation_coverage` warning on a copy | Fail, unchanged |

The checker returns `no_obvious_gaps`, `gaps_detected` or `not_checked`. None means
“supported” or “qualified”. An issued reference inside a bullet can still cite
the wrong fact or leave another sentence unsupported. Every replay explicitly
reports `claim_support_checked=false` and `sentence_coverage_checked=false`.

The failed answer remains byte-identical; no source number is stamped onto it.
No warning is appended to model text. The proposed notice is metadata only, on a
deep copy; it is **not wired into a live app or the frozen N1 controller**.

## Changed files

- `experiments/native_coverage/`: pure detector, 34 synthetic fixtures, tests,
  offline replay and one generic v2 prompt candidate.
- New checkpoint plan/report, folder README and isolated AGENTS entries.
- New replay, candidate hashes, test output and source/preservation artifacts.

No server, web, script, dependency, existing test, N1 harness or historical artifact
is modified. No package, download, runtime/profile/default change or deployment.

## Deviations and parsing limits

This is an offline prototype, not product integration. It deliberately does not
add an app hook or trigger another full app release cycle. Existing source is
verified by hashes, rather than presenting old app-suite counts as fresh tests.

The scanner is a conservative subset, not a complete CommonMark/GFM parser. It
does not classify factual claims, verify source entailment, check every sentence,
or fully interpret HTML, math, all links and complex Markdown containers. Some
non-factual list items can be flagged; a citation anywhere within a structural
unit can still be inadequate for its individual assertions. Prose-only answers
return `not_checked`, never an invented coverage pass. Examples in code/quotes
cannot supply citations to answer items in the tested forms.

Additional review caught over-escaped test strings and the need to distinguish
odd/even backslashes and real link labels from numeric citation sequences. The
fixtures were corrected to the intended Markdown, four controls were added and
the implementation was repaired before final verification. The first 43-pass
result and final 47-pass result are retained separately.

## Test output

- **47 new offline tests pass** (`offline-final.txt`), including all 34 fixtures,
  copy-only warnings, ordinary/incomplete states, old answer replay, old prompt
  hashes and explicit semantic-blind-spot controls.
- Ruff lint and format checks pass; no existing test is edited or weakened.
- Final replay: H01 zero gaps / H02 four gaps; zero model calls.
- Source/preservation checks and privacy guard pass. All 196 prior frozen files,
  both stopped framework ledgers and the stopped N1 ledger are preserved.
- Old N0 full app suites are not rerun: app code/build remains unchanged. Their
  798 Python / 126 frontend / 719-browser results are historical references only.

## Gates, budgets and unchanged core

| Gates | Checkpoint evidence |
|---|---|
| G-1/G-2 | Fresh 47-test prototype check; unchanged app source verified, no fresh full-suite claim |
| G-3 | No existing test edits; test-diff ledger empty |
| G-4 | No frontend change; 425 build hashes/254,964-byte previous bundle retained |
| G-5/G-13/G-14/G-16 | No UI or motion changes; no new screen/phone/VoiceOver claim |
| G-6/G-7/G-15 | No API/schema/data change or migration; rollback evidence unchanged |
| G-8 | Original v1 hashes unchanged; new v2 candidate separately frozen and unexecuted |
| G-9/G-10 | No search/provider/run source or actual payload changes; fresh inference eval absent |
| G-11/G-12 | Synthetic evidence, privacy scan, installed hashes and verified health preserved |

Core C1–C16 remains on unchanged app code and N0 evidence. This experiment adds
no UI behavior or call to those flows. No performance or answer-quality gain is
claimed. Native-call budget here is **0**; the old N1 count remains **4/36** with
its first-failure stop intact. Original N2 targets remain unchanged.

## Candidate and next review

The unexecuted v2 candidate appends only the three-sentence generic list/table
format reminder in `AGENT-CITATION-COVERAGE-PLAN.md`. It does not mention the task,
facts, source IDs or model. The original v1 prompt/rules remain unchanged.
Exact web/Library v1/v2 hashes and candidate text are in `candidate-prompts.json`.

The proposed **C1 retest** is concrete: a new independent ledger; at most 36
native calls on the same 32K profile; original six tasks and H04 mapping, two
ordered series; no sampling override or helper calls; first required failure
stops. Require all 12 full manual passes, not just detector acceptance. Preserve
original source/quality/resource/time gates. A C1 failure ends this candidate;
no automatic new prompt/framework campaign follows. A pass allows only review
for separately budgeted N2 real retrieval, not deployment.

AGENTS.md's post-failure review boundary is still in force. **Review the prepared
C1 plan before any new native call.** The detector alone is not a rational reason
to spend calls replaying the unchanged model prompt; the frozen candidate must
be evaluated separately if approved.

## Screenshots and carried limitations

None: no UI state is added. Real user content and phone screenshots are not used.
Historical VoiceOver failure and the restart-recovered iPhone keyboard issue
remain unchanged; no new acceptance is invented.
