# Themes: TH1 palettes + TH2 motion

**Written:** 22 October 2026, against `main` `4d33913c` · **By:** Claude (validator) · **For:** Jake to approve, Codex to apply

Seven palettes (Cobalt, Lime, Paper, Ember, Orchid, Midnight, Mono), each with its own greeting animation, thinking mark, status words, send motion and Home Screen icon. Built as a patch against the real repository and tested there, so Codex applies it rather than re-implementing it.

| File | What it is |
| --- | --- |
| `THEMES-SPEC.md` | The palettes, the motion, how it fits, the three rule changes, gates, evidence and decisions J18–J20 |
| `CODEX-PROMPT.md` | Paste-ready prompt |
| `aether-themes.patch` | The integration: `git apply --index docs/next/themes/aether-themes.patch` (binary icons included) |

**See it first:** the theme lab, https://claude.ai/artifact/Bou89Pj3er6WCU4cqqEKwc, is a standalone build of the same files. After merge it lives at `/design?themes`.
