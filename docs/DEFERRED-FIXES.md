# Deferred fixes — resolved polish, 8 October 2026

| Issue | Current action | Verification |
|---|---|---|
| iPhone recording menu clips its first action and reaches the home indicator. | Implemented safe-area collision padding and a scrollable visible-viewport height limit. Preserve unavailable retry entries and their explanation. | Synthetic portrait, landscape and keyboard-sized viewport checks; first/last action access, dismissal and focus return. See deferred polish report for results. |
| Sidebar/other motion appears absent on the phone. | The installed preference is Always, which intentionally suppresses animations. Implemented effective status and guidance to follow the device preference in Appearance. Verified phone sidebar entrance/exit in normal, Always and system-reduced modes. Preserve the intentional desktop width snap because its WebKit candidate exceeded the frame budget. | No physical iPhone pass is invented. Automated browser results and remaining device observation are recorded in the polish report. |
| Model picker is difficult to scan. | Implemented All, Loaded, Images, Reasoning and Tools filters using reported capabilities; mark Selected separately from Loaded. | Synthetic filter, search, selection, loading/context and keyboard tests. |

VoiceOver was removed from the current work list at Jake’s request. Historical
reports retain the reported failure; this is not a successful VoiceOver test.
Ordinary labels, keyboard access and focus handling remain in place.

Research is shelved; see [RESEARCH-SHELVED.md](RESEARCH-SHELVED.md).

## Findings from the approved model comparison

The comparison is complete. These observed failures are the proposed next
repair scope; no production prompt or grader change was made during measurement.

| Finding | Proposed next action | Evidence |
|---|---|---|
| Current ordinary-chat model obeyed commands embedded in two invented records. | Design a generic untrusted-record treatment, retain the original prompts and run before/after everyday and release evaluations before a prompt change. No topic rules or extra model calls. | `artifacts/model-comparison/pair-1-baseline-everyday-review.json`, E17/E18. |
| Both models can add unsupported facts or omit local citation binding despite favorable automatic scores. | Strengthen claim review and test generic source-only/citation behavior with retained baselines. Do not lower required gates or use lexical overlap as proof. | Per-run Web and Library manual review JSON under `artifacts/model-comparison/`. |
| Library grader can attach a citation after a sentence period to the following sentence. | Add a focused positive/negative citation-binding fixture and repair the grader separately; preserve all original scores and avoid granting unsupported neighboring claims a citation. | Candidate pair 1 Library `resume`; raw report and manual review retain the 96.4% automatic result. |

No new production fix, model switch or Research restart is part of this comparison.
