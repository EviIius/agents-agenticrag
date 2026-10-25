# TH1 + TH2 · Palettes and the motion that goes with them

**Written:** 22 October 2026, against `main` `4d33913c` · **Updated:** 24 October 2026, Aero added · **By:** Claude (validator) · **For:** Jake to approve, Codex to apply · **Place at:** `docs/next/themes/`
**Theme lab (live, built from this patch):** https://claude.ai/artifact/Bou89Pj3er6WCU4cqqEKwc · in the app after merge: `/design?themes`

## 1. What this is

One patch, `aether-themes.patch`, adds eight palettes, each in light and dark (Midnight is dark only), and the motion that belongs to each one: an animated multilingual greeting, a thinking loop for the Aether mark, status words, a send motion and a circular theme switch. It also adds a palette picker in Settings › Appearance, a Home Screen icon set per palette, and the server setting that syncs the choice between the Mac and the phone. The eighth, **Aero**, is different from the rest: it brings materials as well as colours (§2a).

It is integration code, not a mock-up. It was written and tested against a copy of `main` `4d33913c`, and `git apply --check` also passes on `main` `8f38ef7b` (24 October). The theme lab artifact is a standalone build of the same files. Codex applies it with `git apply`, then runs the gates in §6.

81 files, 42 of them icons and manifests; 4,008 lines added and 99 removed. No new dependencies, no model calls, no change to any request payload.

## 2. The palettes

| Palette | Mode | Page | User bubble | Text | Accent (text, links, focus) | Fill / label (send, primary buttons, switches, mark dot) |
| --- | --- | --- | --- | --- | --- | --- |
| Cobalt (today) | light | #faf9f6 | #efede7 | #1d1c1a | #2f5bea | #2f5bea / #ffffff |
| | dark | #1b1b1a | #2a2a28 | #eceae5 | #7c9dff | #7c9dff / #0d1430 |
| **Lime** | light | #f9f9f4 | #edf0e2 | #0e100b | #3d5f10 | #84cc16 / #0e1405 |
| | dark | #121410 | #20251b | #eef2e6 | #a3e635 | #a3e635 / #10160a |
| Paper | light | #f6f1e7 | #ebe3d1 | #1b1712 | #2b2118 | #2b2118 / #fbf8f1 |
| | dark | #1c1915 | #2a251f | #efe7d8 | #efe7d8 | #efe7d8 / #1c1915 |
| Ember | light | #fbf8f5 | #f2e8df | #1f1611 | #b03a0b | #f06a1d / #1c0c03 |
| | dark | #1a1512 | #29211c | #f4eae2 | #ff9a5c | #ff8a3d / #1c0c03 |
| Orchid | light | #faf8fc | #eee8f6 | #1c1724 | #7a2fd0 | #8b3fe6 / #ffffff |
| | dark | #17141c | #251f2e | #f2edf8 | #c9a5ff | #c9a5ff / #1a0c33 |
| Midnight | dark only | #000000 | #10131a | #f3f5fa | #8fa8ff | #7f9cff / #020612 |
| Mono | light | #ffffff | #f1f1f1 | #0a0a0a | #1f1f1f | #0a0a0a / #ffffff |
| | dark | #0f0f0f | #1c1c1c | #f2f2f2 | #f2f2f2 | #f2f2f2 / #0f0f0f |
| **Aero** | light | #d5ecf9 (frosted) | #cfeaff (gel) | #04162a | #04508f | #0a6fc0 / #ffffff, glossy |
| | dark | #0a3541 (frosted) | #0a3349 (gel) | #eaf7ff | #6fd3ff | #2bb6f2 / #021424, glossy |

Each palette sets the same 25 colour tokens; the full sets are in `web/src/styles/palettes.css`.

**Why two accent tokens.** Lime on off-white is 1.9:1, so lime can never be text. The existing `--brand` stays the readable accent (links, focus rings, selected text, the mark's stroke) and still has to pass 4.7:1 on every surface. The new `--brand-fill` / `--on-brand-fill` pair is the vivid fill: the send button, primary buttons (`--primary` now maps to it), switches and the mark's dot. In Cobalt the two are identical, so Cobalt looks as it does today.

## 2a. Aero: glass, sky and water

Aero brings back the bright, glossy future of the late 2000s: sky gradients, frosted glass, gel buttons, bubbles and lush green. It is the one palette with materials, so it has its own stylesheet (`styles/aero.css`) and a scene component (`components/app/PaletteScene.tsx`).

| Layer | Day | Night |
| --- | --- | --- |
| Behind the app | Sky from deep blue to white, sun glow top right | Navy to teal, moon glow |
| Main column | Frosted white at 80 %; clear on a new chat so the scene shows | Frosted navy at 74 % |
| Sidebar | Glass at 66 % with an 18 px blur and a white edge | Dark glass at 74 % |
| Composer, dialogs, menus, sheets, cards | Glass at 86 % with blur, white edge, soft blue shadow | Dark glass at 84 %, cyan edge |
| Primary buttons, send, switches | Gel: gloss on the upper 40 %, dark-blue edge, bottom glow, white label | Luminous cyan gel, dark label |
| Your messages | Gel bubbles with a glass edge | Dark gel, highlight kept above the text |
| Greeting | Glossy ink lettering with a white glow | White-to-cyan lettering with a cyan glow |
| New-chat scene | Sun with slow-turning rays and a lens flare, drifting clouds, a glass skyline with a monorail over water with its reflection, green hills, nine rising bubbles | Aurora instead of sun and clouds; towers with lit windows; glowing bubbles |
| Type | The era's humanist sans: Frutiger, Myriad Pro or Segoe UI where installed, otherwise Avenir Next on Apple devices | Same |
| Home Screen icon | Glossy sky tile, white mark, a green glass orb for the dot | Same icon |

**Contrast with glass.** Aero's 25 tokens are not the colours you see; they are what each glass layer composites to over the darkest part of the scene behind it (deep sky by day, lit teal and aurora by night). So `check_contrast.py` measures what text actually sits on, and all 57 pairs pass in both modes. `aero.css` says to keep its alphas in step with those tokens.

## 3. Motion personality

| Palette | Greeting | Thinking mark | Send (new row) | Theme switch |
| --- | --- | --- | --- | --- |
| Cobalt | Letters rise in a quick stagger | Dot bobs (today's loop) | Lifts 8 px, eased, 200 ms | Circle from the tap |
| Lime | Slot-machine roll with a spring | Dot bounces and squashes | Pops from 96 % with a spring | Circle from the tap |
| Paper | Typewriter with a caret | Ink blot swells; slower stroke | Settles 2 px, slow ease | Circle from the tap |
| Ember | Rises over a warm glow | Glow pulses behind the dot | Lifts 10 px | Circle from the tap |
| Orchid | Blooms from the middle out | Dot orbits | Glides 4 px from 98 % | Circle from the tap |
| Midnight | Decodes from scrambled glyphs | Dot twinkles, slow glow | Lifts 8 px | Circle from the tap |
| Mono | Plain crossfade | Dot fades | 4 px in 120 ms | Crossfade |
| Aero | Glossy letters float up like bubbles | Dot rises as a bubble, with a glow | Pops from 94 % with a spring | Circle from the tap |

**The greeting.** On a new chat it plays Spanish, French, Japanese, Korean and Italian, then lands on English with the name fading in last ("Good morning, Jake"). Afternoon and evening use their own words. Each word gets a 780 ms slot; the whole run is 4.0–4.5 s, checked by a unit test for every palette and time of day. It plays once per new chat; a new chat within a minute shows the still line. Settings offers Five languages (default), Surprise me (five random of nine) and English only. Screen readers hear only the English line. Japanese, Korean, Chinese and Hindi fall back to each script's system serif, because Newsreader has none of them.

**Other touches.** A faint wash of the palette sits behind the greeting (7 % in Cobalt, none in Mono); Midnight adds a still field of faint stars. Aero's new chat is alive: bubbles rise on 11–24 s loops, clouds drift, the sun's rays turn once every 160 s, and the aurora breathes at night. All of it is transform and opacity, infinite and decorative, and stops with reduced motion. Each palette has its own 12–16 playful status words (Lime: "Zesting", Paper: "Inking", Midnight: "Stargazing"); Cobalt keeps the original 36.

## 4. How it fits together

| File | What it does |
| --- | --- |
| `styles/palettes.css` (new) | 25 tokens per palette and mode, plus each palette's personality tokens (`--send-*`, `--mark-draw`, `--aura`, `--reveal-dur`; Paper also sets `--font-ui` to Newsreader). Attribute selectors only, so a nested `data-palette` + `data-theme` element (Settings swatches, `/design`) gets its own palette |
| `styles/globals.css` | `--brand-fill` / `--on-brand-fill` in the base tokens and Tailwind theme; `--primary` maps to the fill; shadcn mapping also re-resolves inside `[data-palette]`; greeting, aura and palette-picker styles |
| `styles/aero.css` (new) | Aero's materials: sky behind the app, frosted main column, glass sidebar, panels and overlays, gel buttons and bubbles, glossy greeting ink, the scene's static styles, and its swatch in Settings |
| `components/app/PaletteScene.tsx` (new) | Aero's new-chat scene (sun, rays, flare, aurora, clouds, SVG skyline over water, hills, bubbles). Renders nothing for other palettes; used by `EmptyState`, the `/design` shell and the theme lab |
| `styles/motion.css` | Send personality (row-in reads `--send-*`), mark loops per palette, greeting keyframes, theme reveal. Opacity and transform only, except `theme-reveal` |
| `lib/palettes.ts` (new) | Registry: names, modes, greeting style, reveal style, status words, icon paths |
| `lib/appearance.ts` (new) | `applyAppearance()` sets `data-theme` + `data-palette`, runs the view transition with the circle from the last tap, and points theme-color, the tab icon, the Apple touch icon and the manifest at the palette |
| `lib/greetings.ts` (new) | Words per language and time of day, run builder, character timing, Midnight's scramble |
| `components/app/AnimatedGreeting.tsx` (new) | The greeting; used by `EmptyState` and the `/design` shell |
| `components/settings/PalettePicker.tsx` (new) | Palette swatches and the greeting choice in Settings › Appearance. Theme buttons other than Dark are disabled while Midnight is on, with a note |
| `ThemeProvider.tsx`, `stores/ui.ts`, `usePreferenceSync.ts`, `theme-init.js` | Palette and greeting in the store, synced as `appearance.palette` and `appearance.greeting`, and applied before first paint |
| `AtelierMark.tsx`, `WorkingLine.tsx`, `status-words.ts` | Glow circle in the mark; palette status words |
| `Composer.tsx`, `ui/switch.tsx`, `ui/button.tsx`, `ui/slider.tsx` | Send and switches use the fill; the link button and slider thumb keep the readable accent |
| `design/ThemesPreview.tsx`, `design/theme-lab.css` (new) | The theme lab at `/design?themes`, lazy-loaded |
| `public/icons/<palette>/`, `public/manifests/` (new) | Mark SVG, Apple touch icon (full bleed), 192, 512 and maskable PNGs, one manifest per palette. Cobalt keeps the original paths |
| `server/app/db/settings.py` | Accepts `appearance.palette` (eight values) and `appearance.greeting` (three) |
| `scripts/check_contrast.py`, `scripts/check_motion.py` | Contrast check covers every palette and mode; motion guard allows `clip-path` only in `theme-reveal` |
| Tests | `lib/palettes.test.ts`, `lib/greetings.test.ts`, `tests/themes.spec.ts`, `server/tests/test_appearance_settings.py`, a guard case in `test_phase4_guards.py`; `tests/helpers.ts` skips ambient motion in `settle()` |

## 5. Rules kept, and the three that change

Kept: no new dependencies; no model calls; payloads byte-identical; every keyframe in `motion.css`; small motion ≤ 200 ms and large ≤ 320 ms (J5); reduced motion (system or Always) removes all of it, and the greeting then renders the English line without spans; every state on `/design`.

Aero adds `backdrop-filter` blur to six kinds of surface. That is a material, not motion, so no rule changes for it, but it has a cost on the phone (see the gates and J21).

Changed, and why:

1. **§G2 tokens grow** by `--brand-fill` and `--on-brand-fill`, and by eight palette blocks. Contrast is enforced on all of them: 969 pairs (57 per mode) pass, including the new on-fill ≥ 4.5 and citation ≥ 7 pairs.
2. **`clip-path` is allowed in one keyframe**, `theme-reveal`, which clips the view-transition snapshot of the new theme. It runs once per theme change, on the transition layer. `test_phase4_guards.py` proves any other `clip-path` keyframe still fails.
3. **The greeting is outside the 1 s settle budget.** The heading carries `data-motion="ambient"`: decorative, opacity and transform only, never blocks input, capped at 4.5 s. `settle()` skips animations inside it. Without this, `deferred-polish.spec.ts` › "phone sidebar motion … normal" fails on the new-chat screen.

## 6. Gates for Codex

| Gate | Pass when |
| --- | --- |
| `make check` | Ruff, mypy, Python tests, coverage floors, contrast (969 pairs), motion guard, API types, and the web check all pass |
| `make e2e`, both engines | All existing specs pass; `themes.spec.ts` passes in Chromium and WebKit. If WebKit's view-transition support differs, the reveal test skips itself |
| Deploy order | Server and web ship together. An older server rejects the new keys, and the web app's settings PATCH would then fail with "Couldn't save preferences" |
| Visual pass | `/design?themes` at 390 and 1440, every palette, both modes: no text under 4.5:1, no clipped greeting, Paper's Newsreader UI does not overflow menus or the sidebar |
| Aero on the phone | Run the frame-time budget in `performance.spec.ts` once with Aero selected. If the new chat drops frames on the iPhone, remove the sidebar blur first, then halve the bubbles |
| Phone check (Jake) | Open Aether on the iPhone, pick Lime, then Aero, removing and re-adding the Home Screen icon each time: the palette's icon appears and the bars match the page |

## 7. Evidence from this review

Run in a Linux container against a copy of `main` `4d33913c` with the patch applied (re-run on 24 October with Aero):

- `npm run check`: tsc, ESLint, Prettier and Vitest, 148 tests in 17 files, all pass (16 new).
- `check_contrast.py`: 969 token pairs pass across 8 palettes. `check_motion.py`: pass.
- pytest: `test_appearance_settings.py` (4, including every palette) and the motion guard test pass on Python 3.13. The golden-payload test was not run; it needs `artifacts/baseline`.
- Playwright, Chromium only, against `vite` without the Python app: `themes.spec.ts` 7/7 (one checks that Aero brings glass, its scene and its icon, and that no other palette does). With Aero added, `foundation`, `motion` and `themes` specs: 32 of 33 pass; the one failure needs the fake runtime. Earlier, of 93 cases in the design-page specs, the only failures were cases that need the fake runtime; the same cases fail on the untouched baseline in the same setup.
- `vite build` of the app succeeds.

Not run: WebKit and the iPhone project, the full `make e2e` with the fake runtime, a real phone, macOS-only tests.

## 8. Decisions for Jake

| ID | Decision | Recommendation |
| --- | --- | --- |
| J12 | Palettes to ship | All eight. They are built and pass contrast; dropping one is deleting a block and a registry entry |
| J13 | Greeting languages | Spanish, French, Japanese, Korean, Italian, then English (as built) |
| J18 | Greeting exempt from the 1 s settle budget as ambient motion | Yes |
| J19 | Allow `clip-path` in the `theme-reveal` keyframe only | Yes |
| J20 | Paper uses Newsreader for the whole interface | Yes; revert by deleting one line in `palettes.css` if menus feel loose |
| J21 | Aero's glass (`backdrop-filter`) and animated scene on the new chat | Yes. If the iPhone drops frames, remove the sidebar blur first |

**`AGENTS.md` text to append when J18–J21 are given:**

> **User authorization (date) — TH1/TH2 palettes and motion:** Apply `docs/next/themes/aether-themes.patch` on a branch. It extends §G2 with `--brand-fill`/`--on-brand-fill` and eight palettes in `web/src/styles/palettes.css`; adds Aero's glass materials in `web/src/styles/aero.css` (`backdrop-filter` on the sidebar, composer and overlays) and its decorative new-chat scene (`PaletteScene.tsx`, infinite transform/opacity loops, stopped by reduced motion); adds `appearance.palette` and `appearance.greeting` settings; per-palette icons and manifests; an animated new-chat greeting (≤ 4.5 s, opacity/transform only, `data-motion="ambient"`, exempt from the 1 s settle budget in `tests/helpers.ts`); per-palette mark loops, status words and send motion; and a circular theme reveal, the only `clip-path` keyframe, allowed by name in `scripts/check_motion.py`. No new dependencies or model calls; payloads unchanged. Palette hex values and motion timings change only with a recorded reason and a passing contrast check. Stop after `make check`, `make e2e` and the visual pass, with a report.

## 9. Limits

- iPhone keeps the Home Screen icon it saved when Aether was added; a new icon needs remove-and-add. Settings says so.
- Safari 26 and later ignore `theme-color` and tint the bars from the page background, so each palette's `--bg` colours them. Open dialogs also recolour the bars (a WebKit behaviour).
- Lime's character is in its fills. Text-coloured accents (links, the mark's stroke) are deep lime, because bright lime fails contrast as text.
- `theme-init.js` repeats the palette list so the first paint is right; `palettes.test.ts` fails if it drifts.
- Colour choices were checked by contrast maths and screenshots in Chromium, not on the iPhone's display.
- Aero's typeface depends on what is installed: Frutiger, Myriad Pro or Segoe UI if present, otherwise Avenir Next on the Mac and iPhone. No font file is added.
- Aero's glass contrast assumes the alphas in `aero.css`. A lighter glass would need new token values and a passing contrast check.
- Blur over large areas costs GPU time on the phone; the gate above measures it.
