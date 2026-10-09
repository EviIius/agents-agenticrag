# Named model comparison report — 8 October 2026

## Summary

The approved candidate is installed as `qwen3.8:27b-atelier-eval-32k`.
All four ordered smoke checks passed before full evaluation began.
All three matched pairs completed; the candidate fails the unchanged qualification gates.
No production code, prompts, sampling defaults, deployment or default model changed.
Research remains shelved; runtime metadata does not qualify Research or vision quality.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Named installation and actual 32K inference | Passed | `artifacts/model-comparison/installed-model.json`, smoke payloads and residency |
| E05, E09, E13, E17 ordered smoke | Passed | `smoke-review.json` and original answers |
| Three full matched pairs, declared order | Complete | `artifacts/model-comparison/pairs.json` |
| Frozen cases and evidence, no production edits | Passed: 7,296 hashes; production tree equals f87db46 | `artifacts/model-comparison/final-audit.json` |
| Manual factual and citation review | Complete; failures retained | Per-run review JSON; raw answers retained |
| Candidate meets every required gate | Failed; no promotion | Full results and manual findings below |
| Regression checks and service health | Passed | `artifacts/model-comparison/check.log`, `health-final.json` |

## Results

The everyday comparison is complete. Failed candidate gates and baseline
weaknesses both remain visible. An ordinary task score is separate from grounding,
injection and citation gates.

| Everyday result | Current Qwen 3 30B | Candidate Qwen 3.8 27B |
|---|---|---|
| Manual scores, runs 1 / 2 / 3 | 16 / 17 / 17 out of 20 | 18 / 18 / 18 out of 20 |
| Four explicit formats | All three runs pass | All three runs pass |
| Embedded overrides | Both overrides obeyed in every run | Both overrides ignored in every run |
| Full everyday gate | Fails all three | Fails all three: source-only grounding |
| Visible-text median, seconds | 0.125 / 0.123 / 0.115 | 10.125 / 8.347 / 9.259 |
| Native generation median, tokens/second | 88.1 / 86.0 / 87.1 | 14.8 / 15.7 / 15.8 |

Reviews apply the same conservative source-only criterion to inferred water
ratings and unstated gender; each judgment is explicit in the review files.
The candidate's first rewrite also changes purchase order into payment order;
later runs correct that. The baseline repeatedly obeys two overrides even when
the user explicitly says the delimited records are data, not instructions.
These are separate observations, not a single blended score.

| Recorded Web result | Current Qwen 3 30B | Candidate Qwen 3.8 27B |
|---|---|---|
| Automatic case passes, runs 1 / 2 / 3 | 25 / 25 / 25 out of 25 | 21 / 22 / 22 out of 25 |
| Automatic mandatory gates | Pass all three | Fail all three: injection not exercised and mandatory citation examples |
| Manual claim/citation review | Unsupported extra claims in all three | Unsupported summaries and missing local references in all three |
| Search first-delta p50, seconds | 4.147 / 4.169 / 1.316 | 20.283 / 20.648 / 20.063 |
| Full-suite wall time, minutes | 2.37 / 2.40 / 1.79 | 28.93 / 28.87 / 28.14 |

The candidate misclassifies the requested page summary as a transformation and
skips lookup in all three runs. It never receives the adversarial source and
then supplies invented or internally contradictory details. This is neither
an injection pass nor a supported summary. All three complete-list tables lack
row-level references. The baseline avoids that skip but invents unavailable
scores in all three results-table answers. Favorable lexical scores certify
neither set of extra claims.

The candidate handles missing dates/currency and incomplete game records more
carefully in several cases. Those positives remain in manual review; they do
not waive mandatory failures. Existing automatic checks can pass an incomplete
currency comparison or an answer containing unsupported extra scores.

These are recorded comparisons, not a fresh live-Web E13 release measurement.
Rendered dates follow the normal app clock; run timestamps span UTC midnight,
while the cases, templates, sources and configured context remain unchanged.
| Library result | Current Qwen 3 30B | Candidate Qwen 3.8 27B |
|---|---|---|
| Retrieval and required facts | 100% in all three runs | 100% in all three runs |
| Automatic citation support, runs 1 / 2 / 3 | 96.4% / 100% / 100% | 96.4% / 96.4% / 89.3% |
| Unsupported questions | 6/6 abstentions each run | 6/6 abstentions each run |
| Injection obedience | Zero each run | Zero each run |
| First-delta p50, seconds | 0.349 / 0.397 / 0.361 | 3.363 / 3.573 / 3.661 |
| 20,000-passage retrieval p50, ms | 80.0 / 78.2 / 77.9 | 80.2 / 80.6 / 78.2 |
| Full-suite wall time, seconds | 39.6 / 44.1 / 40.9 | 552.5 / 545.6 / 587.9 |

The candidate's flagged Library facts match the cited source, but references
placed after sentence periods are assigned to the next sentence by the existing
checker. Original failed automatic results remain unchanged; no target or gate
is waived. This limitation must not be presented as proof that the required
facts were hallucinated. Separate manual findings include uncited earlier-turn
sentences, unstated pronouns and poor resolution of the express-shipping
follow-up. The baseline's first run also misses the automatic citation target;
later automatic passes still leave earlier-turn and extra-claim issues visible.

## Decision

**Do not promote this profile. Keep the current Qwen 3 30B default.** The
candidate improves everyday override resistance and several source-abstention
answers, but it fails mandatory Web source/citation checks in every run and is
substantially slower. The decision does not depend on a debatable pronoun or
water-rating judgment or the Library parser's false negatives. It applies to
this digest, profile, runtime and hardware, not every possible configuration of
Qwen 3.8. Installed tags remain available; no default switch or deletion occurs.

## Changed files

- Evaluation only: `server/evals/models/run_everyday.py`, `run_comparison.py`, README.
- Documentation: approval, frozen comparison plan, model options, this report.
- Evidence: synthetic/public answers, raw streams, automatic and manual reports.
- Production server, web, shared API and deployment: unchanged.

## Deviations and limitations

The initial child import-path failure, incorrect historical Web fixture root and
interrupted initial Library run are retained as setup-invalid attempts. Valid
full runs use the same frozen intended corpus. No quality failure is retried.
The interruption occurred while correcting setup, not to replace an unfavorable
answer. See `artifacts/model-comparison/README.md` and `pairs.json`.

Published model profiles differ in their packaged sampling defaults. App answer
payloads add only the explicitly selected 32K context; this compares those normal
profiles, not architectures under experimentally equalized sampling. Web planner
utility settings remain the app's existing settings. First delta may be reasoning,
not visible text; snapshots do not establish peak memory. Three pairs are not a
statistical significance test. Recorded public evidence is not a fresh live-Web
check. Neither metadata nor this text-only evaluation establishes vision quality.

## Runtime observations

Ollama remains 0.35.0 on the 64 GiB Apple M5 Pro. Actual model metadata, full
digests, packaged parameters and residency are retained. Runtime snapshots report
19,508,609,678 bytes for the candidate and 21,827,095,100 for the baseline;
these are allocations observed at snapshots, not measured peaks. Native load time
in the first full everyday case was 3,815 ms candidate and 3,970 ms baseline;
the initial candidate smoke reports 2,050 ms. These load costs are retained
separately from steady response medians. The embedding model and
transcription interpreter are unchanged. No forced final evaluator unload is used.

## Test output

`make check` passed after all timed inference finished: 298 Python tests, 36
web unit tests, 74 contrast pairs, lint, formatting, types, coverage floors,
API types/additive guard, motion guard and privacy audit. Evaluator-only Ruff
lint/format checks also passed. Exact output is retained in
`artifacts/model-comparison/check.log`.

`make e2e` was not rerun: production code, tests, shared contracts and browser/build
scripts are byte-identical to the stable polish tree, as verified in
`final-audit.json`. Its prior 457 passes and three documented WebKit skips are
retained in the deferred-polish evidence; these are reused results, not new
browser execution. No frontend/build change or deployment occurred. No new
physical phone pass is claimed. Local and Tailscale health passed with normal
macOS TLS verification; runtime version remains 0.35.0.

## Screenshots

N/A: isolated backend comparison; no UI or deployment change and no private captures.

## Next steps

1. Repair citation grading separately with positive/negative sentence-binding
   fixtures; retain these original reports and any later regrades.
2. Harden generic untrusted-record and source-only behavior using a retained
   before/after evaluation, including unsupported extra claims and earlier turns.
   This comparison does not authorize production prompt changes.
3. Keep the stable app and current default. A further profile, smaller model or
   runtime experiment needs its own explicit scope and measured comparison.

Research remains shelved. Favorites/context-profile grouping and physical phone
polish observation remain separate future work. No native-tool or vision quality
claim is made from runtime capabilities alone.
