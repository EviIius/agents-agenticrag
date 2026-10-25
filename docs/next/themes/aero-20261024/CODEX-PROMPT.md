# Prompt for Codex · TH1 + TH2 palettes and motion

Paste after Jake gives J18–J21 (THEMES-SPEC §8).

```text
Read AGENTS.md, docs/next/themes/THEMES-SPEC.md and docs/next/QA-REQUIREMENTS.md.

My decisions: J12 all eight palettes. J13 as built. J18 yes. J19 yes. J20 yes. J21 yes.
First append the AGENTS.md authorization text in THEMES-SPEC §8, with today's date.

1. Branch codex/themes-th1-th2 from main.
2. git apply --index docs/next/themes/aether-themes.patch
   It was made against main 4d33913c. If it does not apply cleanly, use --3way, keep both
   sides, and list every conflict and how you resolved it in the report.
3. make check. Then make e2e in both engines, including tests/themes.spec.ts.
4. Visual pass on /design?themes at 390 and 1440: every palette, light and dark (Midnight dark
   only). Screenshot each into artifacts/themes/. Check that no text is clipped, Paper's
   Newsreader UI does not overflow menus or the sidebar, and the greeting lands on English.
   For Aero, also check the glass is legible over the scene and run the performance.spec
   frame-time budget once with Aero selected; if it fails on WebKit, remove the sidebar blur
   first and record it.
5. Settings › Appearance: pick each palette, reload, confirm it persists and syncs through
   /api/settings (appearance.palette, appearance.greeting).
6. Deploy server and web together (an older server rejects the new settings keys).
7. Stop and write docs/THEMES-TH1-TH2-REPORT.md (SPEC §H4 plus QA §8) for Jake's phone check:
   pick Lime on the iPhone, remove the Home Screen icon, add it again.

Rules:
- Do not change palette hex values, motion timings or the greeting run without recording
  why; any colour change must pass scripts/check_contrast.py.
- No new dependencies, no model calls. All keyframes stay in web/src/styles/motion.css.
- If a gate fails on the Mac in a way this spec does not explain, stop and report.
```
