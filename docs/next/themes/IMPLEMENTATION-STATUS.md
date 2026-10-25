# Themes — live integration status, 24 October 2026

All eight themes are integrated into main and live in Aether through PR #11,
merged as `326acbaa`. Claude UI review follows integration, as Jake requested.

- Start with `docs/THEMES-AERO-RELEASE-REPORT.md` for publication and QA evidence.
- Live theme lab: https://jakes-mac-mini.tailc4d343.ts.net/design?themes
- Live app: https://jakes-mac-mini.tailc4d343.ts.net/ → Settings → Appearance.
- Qualified source: 778 Python /151 frontend /892 browser passes, four existing
  skips; 969 token pairs and 64 actual-material audits pass. Release source hashes
  match; the unchanged service, data, runtimes and image worker are preserved.
- The earlier qualified seven-theme branch/commit `c7758120` remains preserved.
- Latest supplied eight-theme documents are in `aero-20261024/`; original input
  files remain unchanged in the original workspace. The raw patch stays private.
- The local 127.0.0.1:5173 preview still uses fake engines and temporary data.

For review, try all eight palettes in light/dark (Midnight is dark only), replay
normal/reduced greeting/send/thinking motion, and inspect actual new chat,
conversation, Settings, Tools, Workflows and Images at narrow/desktop widths.
A retained paused-workflow notice overlapping the phone Images header is an
existing review target. The real iPhone/PWA, saved icon and GPU feel are not
certified by browser automation; Jake's requested phone check remains pending.
VoiceOver is historically unresolved. No stopped agent/Research/precision-editing
trial or unattended automation is restarted by this release.
