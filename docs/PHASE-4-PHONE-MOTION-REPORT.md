# Phase 4D phone motion follow-up

## Summary

Jake reported that Reduce motion › Always failed and that the app had no entrance.
Codex reproduced the stuck selector through iPhone Mirroring without saving the
phone screen. Selecting Follow system dismissed it; selecting Always did not.
The new browser regression reproduced the failure in both Chromium and WebKit.
The fix applies motion CSS before Radix checks its closing animation.

The app now enters over 200 ms after preferences, models and a restored chat are
ready. It works for new and restored chats, without a splash screen or input lock.
It runs once per page load, never on chat navigation. Both reduced-motion triggers
remove it. The empty-chat-only entrance was replaced with this app entrance.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Reproduce the physical phone failure | Confirmed | Transient Mirroring inspection: Always left the selector open; Follow system closed it |
| Reproduce automatically before fixing | Confirmed | `artifacts/phase-4/4d-phone-fix/selector-before.txt`: two failures at selector dismissal |
| Fix selector dismissal and restore usable controls | Automated pass | `phone-motion-after.txt`: 14 passed across Chromium/WebKit |
| Entrance on new and restored chats; neither reduced trigger animates | Automated pass | `phone-motion.spec.ts` |
| Types, lint, unit tests and frozen contracts | Pass | `check.txt`: 212 Python, 36 web, 58 contrast pairs |
| Production build | Pass | `build.txt` |
| Fully green browser run | Pass | `e2e.txt`: 321 passed, 3 existing skips, single complete run |
| Deploy and verify health/invariants | Pass | `deployment.txt`, `deployment-invariants.json`; health 200, production design 404 |
| Confirm the fix in iPhone Mirroring | Pass | Fresh launch: both System and Always dismiss and retain their selection |

## Changed files

- Web: `ThemeProvider.tsx`, `useAppEntrance.ts`, both app shells, `EmptyState.tsx`,
  `motion.css`; new `phone-motion.spec.ts` regression tests.
- Scripts: `capture_phone_motion.cjs`, isolated synthetic captures only.
- Docs: this report and the latest Phase 5 authorization in AGENTS/SPEC.

## Deviations from SPEC.md

Jake explicitly requested an app entrance. It replaces the previous entrance
that applied only to the first empty chat; duration, CSS-only motion and both
reduced-motion controls retain their approved limits.

## Runtime observations

Radix Presence determines whether to wait for a closing CSS animation in a layout
effect. The old passive preference effect disabled that animation afterward.
Its animation cancellation callback then found the computed animation name was
`none`, and did not remove the suspended selector. Applying the CSS in React's
insertion effect removes that ordering race without changing dependencies.

## Test output

`check.txt`, `build.txt`, `selector-before.txt`, `selector-after.txt` and
`phone-motion-after.txt` preserve the commands and results. The first after-fix
run passed WebKit but a new Chromium assertion incorrectly expected the desktop
picker to be a dialog. The regression now explicitly uses the phone viewport in
both engines; all 14 targeted cases pass. No existing assertion was weakened.
The full browser run passed: 321 tests and three existing skips.

## Screenshots

- `artifacts/phase-4/4d-phone-fix/appearance-always-390-dark-chromium-fake.png`
- `artifacts/phase-4/4d-phone-fix/appearance-always-390-dark-webkit-fake.png`

Both use intercepted synthetic API fixtures and were visually reviewed. Both
have zero serious/critical axe findings (`synthetic-observation.json`). Short
synthetic clips remain ignored under `artifacts/phase-4/motion/phone-fix/`.
No real recording, filename, transcript or phone image was saved.

## Test-diff ledger

No existing test file changed. `phone-motion.spec.ts` adds selector dismissal,
settings usability, new/restored chat entrance, both reduced triggers, typing,
and no replay on navigation. Tests reset the shared fake motion preference.

## Core and gates

No server, database migration, prompt, inference, search or transcription code
changed. The API/row preservation/prompt/payload guards pass in `make check`.
The full existing core/browser tests and performance gates passed against
frozen source (`tested-source-hashes.json`). No migration means no new rollback
rehearsal is required. Full checkpoint gate details retain the 4D report and are supplemented by the completed run and physical verification here.

## Known limitations carried forward

VoiceOver remains user-reported failed and deferred. The earlier iPhone keyboard
failure recovered after a restart; its cause remains unproven. No new claim is
made about either limitation. The natural 200 ms launch was not instrumented on the phone; browser tests cover
its timing and readiness. Physical CSS timing was checked with a temporary trigger.

## Open questions for Jake

None: Jake authorized fixing and confirming this on his mirrored iPhone, then
starting Phase 5. Phase 5A is the next review stop.

## Physical phone verification — 5 October 2026

The first post-deploy check resumed the old running page. After fully closing
and relaunching Atelier, tapping Follow system and Always both closed the selector
and persisted the selected value. Safari Inspector then confirmed the deployed
script `index-C5_O3LNm.js`, System motion and OS reduced motion off. A temporary
entrance attribute produced an `app-in` animationend event of exactly 200 ms.
This checks the real phone CSS engine with a synthetic trigger, not a measured
natural launch. The attribute and listener were removed afterward. Restoring
Always and reloading produced animation `none` and transition `0s`. No message
text, recording name or transcript was read or recorded during inspection.
Safari developer features were restored to their original off setting.

Initial gzip JS is 229,667 bytes, +61 bytes versus 4D and below 256,000.
Source commit: `ee65129`. Deployment performed its normal database backup first.
