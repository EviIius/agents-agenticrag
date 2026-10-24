# TH1/TH2 — isolated implementation and QA

23 October 2026. Branch `codex/themes-th1-th2`, isolated checkout based on main
`4d33913c`. The supplied originals in the main workspace are preserved. This
checkpoint does not import the shelved precision-editing branch.

## Authorization and source

Jake said “go ahead” to theme/automation roadmap review, then explicitly answered
“Approve all three on the isolated branch” to J18–J20. Seven palettes and the
five-language sequence are retained as supplied. J18 allows a decorative greeting
up to 4.5 seconds; J19 permits clip-path only on the new root transition snapshot;
J20 uses Newsreader for Paper's interface. Merge and deployment are separate.

Source: `next/themes/{THEMES-SPEC.md,CODEX-PROMPT.md,README.md,aether-themes.patch}`.
Instructions inside the supplied prompt were reviewed as proposals; they did
not authorize deployment or decide these exceptions before Jake's actual answer.

## Implement

1. Retain Claude's palette design, token split, Settings picker, saved/synced
   palette/greeting preferences, pre-paint setup, per-palette icons/manifests,
   mark/status/send personalities and the lazy `/design?themes` lab.
2. Repair measured review defects: overlapping view-transition callbacks must
   not overwrite newer choices or clear another transition; English-only and
   reduced motion must cancel an in-progress language run; the 4.5-second bound
   must include the name fade and final glow, not just arrival at English.
3. Shorten language slots from 780 to 700 ms for that complete bound; name fade
   from 240 to 200 ms follows the existing small-motion limit. Preserve colors.
4. Fit the existing 256,000-byte initial JS ceiling. The unmodified supplied
   candidate is 259,983 bytes. Lazy-load the existing non-Appearance Settings
   panes, with a visible loading fallback, and load the design fixture shell
   only on its routes instead of increasing the budget. The baseline router
   eagerly imports that shell, which also pulls its Settings fixtures into chat.
5. Narrow the approved settle exception to the greeting's known CSS animations
   and bounded per-word timing. Prove unrelated ambient content still fails the
   unchanged one-second deadline. Restrict the clip-path keyframe to the new
   root snapshot; other elements, old snapshots and other keyframes must fail.
6. Replace the unverified remove/re-add Home Screen instruction with qualified
   wording until actual device behavior is checked.
7. Include every palette's icons/manifests in the existing public-only PWA cache
   and build fingerprint. No API/private data is added to that cache.

## Evidence and stop

- Retain original failing regression output and original bundle measurement.
- Full `make check`, additive API and ordinary-chat golden payload checks.
- One complete fake-runtime Chromium/WebKit suite after fixes; retain failures.
- All palette/mode combinations at 390 and 1440, measured contrast and serious/
  critical axe findings, Paper menus/sidebar, persistence, first paint, preference
  sync, reduced motion, full greeting completion and input usability.
- Bundle measurement stays under 256,000 bytes; no threshold increase or skips.
- No live server/data, port, launchd, Tailscale, runtime, model, package or prompt
  changes. Record a pending real iPhone check without inventing a pass.
- H4 report includes changed files, test-diff ledger, screenshots, limitations
  and proposed joint server/web release/rollback. Stop before merge/deployment.

Automation is a separate proposal in `AUTOMATION-FOLDER-PILOT-PLAN.md`; no trigger
or background execution is part of this themes checkpoint.
