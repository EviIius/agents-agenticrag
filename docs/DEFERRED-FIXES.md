# Deferred fixes

| Issue | Status | Later verification |
|---|---|---|
| iPhone recording attachment dropdown clips the upper item and reaches the bottom home indicator. Constrain its height to the available safe viewport and allow scrolling so every action stays reachable. | Deferred at Jake’s request, 6 October 2026. Reproduce with synthetic audio; no real filename or screenshot retained. | Open the menu with a recording near the lower screen; verify the first and last actions, scrolling, dismissal, and safe areas in portrait/landscape and with the keyboard open. |
| Sidebar and other animations stopped appearing on the phone. | Deferred at Jake’s request, 5 October 2026. Existing automated motion checks pass; physical regression remains unresolved. | Verify installed-app motion with normal, system-reduced, and Always-reduced settings. |
| VoiceOver did not work on the iPhone. | Reported failure; deferred for this build, 3 October 2026. Never recorded as a pass. | Repeat the physical VoiceOver walkthrough when scheduled. |
