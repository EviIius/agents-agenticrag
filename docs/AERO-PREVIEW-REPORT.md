# Aero local preview — review checkpoint

24 October 2026 · local branch `codex/aero-theme-preview`, based on the verified
seven-theme commit `c7758120`. Preview: `http://127.0.0.1:5173/design?themes`.

## Summary

Aero is the eighth choice in the local theme lab. The supplied glass, gel,
skyline/water/hills, sun/clouds, night aurora, bubbles, font stack, thinking
personality and icons are retained. Source was extracted as an Aero-only delta
between the two supplied patches, preserving the earlier theme repairs.
This is a visual-review candidate. It is not a new release qualification.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Aero in local theme picker, day/night scenes and conversation | Implemented | `ThemesPreview.tsx`, `PaletteScene.tsx`, `aero.css`, synthetic captures |
| Frontend type/lint/format/unit check | Pass, 151 unit tests | `web-check.log` |
| Eight-palette token contrast | Pass, 969 pairs | `contrast.log`; transparent-material limits below |
| Motion guard | Pass | `motion.log` |
| Bounded Chromium/WebKit preview checks | Pass, 12/12, no skips | `browser.log` |
| Server settings / live-chat EmptyState integration | Deferred until review | No server source or live EmptyState edit |
| Full regression suite, bundle and Aero performance qualification | Deferred until integration review | Previous 856-pass report qualifies `c7758120` only |
| Real iPhone/Safari GPU and saved-icon behavior | Not checked | No physical result claimed |
| Merge/deploy | Not performed | Main, the installed app and PR #10 remain unchanged |

Evidence root: `artifacts/themes/aero-preview-20261024/`.

## Changed files

- Theme lab / design shell: `ThemesPreview.tsx`, design `AppShell.tsx`,
  `theme-lab.css`, new `PaletteScene.tsx` and `styles/aero.css`.
- Shared preview support: Aero palette registry/tokens, first-load palette list,
  greeting timing table, Aero motion and CSS import. This preview frontend would
  still require server validation and live-chat wiring before publication.
- Assets: five Aero icons and a manifest; no font download or new dependency.
- Checks: one additive supplied Aero case in `themes.spec.ts`, new bounded
  `aero-preview.spec.ts` and its standalone configuration.
- Docs: preview scope amendment, this report and post-review integration plan.

## Deviations and retained findings

- Preserve the existing 700 ms language slots, 200 ms name fade, guarded theme
  transitions and narrow motion-check exemptions. Do not reapply the full raw
  patch over the repaired branch. No three-way text merge conflict occurred.
- Aero's supplied 340 ms character entrance exceeds the existing 320 ms large-
  motion ceiling. Both the CSS keyframe invocation and timing table use 320 ms.
  No palette hex value or scene material/blur/bubble count was changed.
- Eight choices make the sticky phone controls taller than before; they overlap
  the app preview at 390 px. Make the controls non-sticky below 640 px. Desktop
  controls remain sticky. Retain the initial synthetic capture.
- Initial bounded runs: the layouts/materials/reduced-motion cases pass, while
  both named-greeting checks fail because the synthetic preview profile has an
  empty name. Set the same synthetic name (`Taylor`) used by the existing theme
  timing tests. Keep the 4,500 ms full-animation assertion; do not relax it.
  The retained failure log and private trace/capture hashes document that setup
  failure. A repeated invocation happened before the fixture edit applied.
- The new timing test also exposed a TypeScript element union (`HTMLElement |
  SVGElement`). Retain `web-check-button-type-failure.log`; require a real
  HTMLButtonElement before clicking. Final type/lint/format/unit checks pass.

## Runtime observations and test output

No model, transcription, image-generation, embedding or other native experiment
is used. The design checks abort any API request and assert none occurred. The
preview uses the existing installed JavaScript dependencies via a local symlink.
The new browser configuration runs only against the isolated local Vite preview;
it starts no app backend and does not proxy to the installed service.

- `npm run check`: 151 tests in 18 files pass, plus types/lint/format.
- `check_contrast.py`: 969 token pairs across eight palettes pass.
- `check_motion.py`: pass.
- Complete bounded preview result: **12 passed / zero failed / zero skipped**,
  both engines, 1.2 minutes. Includes the 4,500 ms complete named-greeting bound.
- No full `make check` or full `make e2e` is claimed for this Aero candidate.

## Screenshots and limits

Synthetic day/night new-chat and conversation captures at 390/1440, in Chromium
and WebKit, are under `screens/` with `fake` names. They use fake conversations
and a synthetic profile; no real photo, recording or Library content is used.

The token contrast check uses the supplied opaque composite assumptions; it does
not prove every moving/blurred background has that contrast. Axe does not fully
resolve all gradient/transparent-text combinations. Sampled visual inspection
and actual scene/material contrast qualification remain distinct from the token
math. WebKit here is browser automation on the Mac, not a real iPhone test.

Keep the requested glass and nine bubbles for this review. GPU/compositor cost
and real phone animation feel remain unqualified. The actual selected humanist
font depends on installed fonts; no Frutiger/Myriad installation is implied.
VoiceOver's historical limitation remains unresolved.

## Next step after review

If Aero's appearance is accepted, follow `THEMES-AERO-INTEGRATION-PLAN.md` to
complete app/settings integration and the full gates. J21 acceptance for product
use and release approval are not inferred from the request for this local
preview. The supplied Codex prompt's deployment instruction is not authorization.
