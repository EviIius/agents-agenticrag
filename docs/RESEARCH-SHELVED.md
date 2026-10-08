# Research shelved — 7 October 2026

Jake asked to stop pursuing Research and return to deferred product polish.

- Do not run additional 8A experiments or begin 8B UI/deployment.
- Preserve the original benchmark, targets, baseline, every trial and prompt hashes. The retained Research checkpoint is `7737046`; merge `a55041f` preserves that history on main.
- The latest frozen candidate completed only 4 of 15 cases under strict grading. Earlier raw 13/15 results did not establish consistent supported answers. No Research qualification or lowered threshold is claimed.
- The installed app remains the accepted 7B feature set: chat, single-shot Web search, transcription and cited Library answers. Production polish is developed from `d74067e` so isolated Research modules are not copied into the installed app.
- Model options remain documented. No candidate weights or runtime upgrade are authorized by shelving.

Reconsider Research only after a material change in evidence collection or a separately approved model test, with the original completeness, support, citation and budget gates intact. It is not the next product milestone.

**8 October source closeout:** Main now uses the tested production application
tree. Unreleased Research runtime/schema/wiring is absent; original source is
recoverable at `7737046` / `codex/phase-8a-research`. Historical harnesses and
all failed inputs/reports remain, with execution marked shelved. See
[SOURCE-CLOSEOUT-REPORT.md](SOURCE-CLOSEOUT-REPORT.md).
