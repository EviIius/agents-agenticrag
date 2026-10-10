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

## Reliability follow-up — 10 October 2026

The comparison table above records its original proposed scope. The citation
grader's post-period/table binding has since been repaired with positive and
negative fixtures and separately labelled regrades; original answers and scores
are retained. This corrects measurement, not semantic support or model quality.

| Remaining item | Current state | Next action |
| --- | --- | --- |
| Grounded answer contract | v14 original-case native smoke rejected and stopped. Named references/identity keys are valid, but identity-only rows and an over-budget prose selection still fail the host guards. No candidate qualified. | Align native schema with host admissibility before another bounded original-case trial; preserve source context and all failures. |
| Retrieval, completeness and relevance | Full latest Web/Library trial remains gated; previous omissions and extra/irrelevant claims remain unresolved. | Evaluate unchanged cases and manual claim support only after the protocol smoke passes. |
| Ordinary-chat untrusted records | No production fix; retained unchanged-pipeline evaluation remains 16/20. | Separately evaluate generic untrusted-record treatment against original everyday and release checks. |
| Attachment context warning | Published the corrected input/output allowance, saved-default precedence and readable warning. Six focused checks and one complete 463-pass browser rerun passed; three existing skips retained. | Reopen/reload Atelier to receive the frontend update. Stable server preserved; private static/database fallback saved. No physical iPhone acceptance claimed. |
| Image generation | Documented Mac options only; nothing installed or downloaded. | Separately approve and benchmark a named Draw Things / FLUX.2 klein 4B trial before integration. |

See `EVIDENCE-OBJECT-REPORT.md` for this checkpoint's actual results. Research
remains shelved and VoiceOver stays off the current work list.

## Approved sequence, checkpoint R — 10 October 2026

The earlier table remains the v14 history. The approved bounded v15 repair now
passes the original first smoke, selecting complete Team/Wins fields with the
original context and citations. Its gated Web remainder then stops when six
individually admitted excerpts violate a source's combined quotation allowance.
No failed factual output, retry, full Web result, Library or consistency run
followed. This candidate is not qualified.

End this selector design at the declared checkpoint. Review a simpler presentation
through existing source cards/“What the model saw” and explicit missing-evidence
status. This proposed fallback is not implemented and does not resolve remaining
relevance, completeness or ordinary-chat injection failures. No release targets
are waived; factual automated outputs remain drafts for review.

The next independent checkpoint is the concrete MFLUX/FLUX.2 klein 4B worker
trial proposed in `IMAGE-TRIAL-PLAN.md`, followed by durable jobs and image UI,
then ordered workflows. No image dependency or weights were installed. See
`EVIDENCE-BUNDLES-REPORT.md` for actual results and the checkpoint review stop.
