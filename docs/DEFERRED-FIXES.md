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
