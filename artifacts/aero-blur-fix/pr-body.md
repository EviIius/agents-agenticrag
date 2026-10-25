## Summary

Fix the Aero production blur regression identified by Claude's UI review. The unchanged release build exactly matches live CSS and loses the standard backdrop-filter in seven rules. All seven pairs are reordered; reading overlays gain a separate 96% light/dark backing.

Source order and actual minified CSS are now guarded. New browser coverage loads the real production app over an asserted high-contrast synthetic image, including the no-blur readability fallback. Existing contrast measurement was extracted unchanged for reuse.

## QA

- make check: **785 Python tests, 151 frontend tests, 969 contrast pairs**; all gates pass.
- One fresh complete browser run: **900 passed, four existing skips, zero failures (1.3 h)**, Chromium and WebKit.
- Eight production material cases: **584 sampled text runs**, no failures; minimum **5.64:1** with/without blur.
- Initial JS **252,228 / 256,000 gzip bytes**; Aero render p95 **2.8/3.0 ms**, scroll median **16.7/17 ms**; first-token overhead **73.30/61.86 ms**.
- 456 executed source files, 600 installed public files and 15 supplied input files verify unchanged. Original worktree/main unchanged. Old tracked artifacts restored after fresh results were preserved separately.
- Earlier fixture failures and the interrupted invocation remain recorded; no assertion, timeout, skip or threshold was weakened.

[H4 report](docs/AERO-BLUR-FIX-REPORT.md) · [Follow-up plan and approved J22–J25](docs/DESIGN-CRITIQUE-IMPLEMENTATION-PLAN.md)

## Scope / review stop

Part A only, on its own branch. **Not merged or deployed.** No backend/schema/dependency/runtime/prompt/sampling/model change or native inference. Private review screenshots remain in the original workspace; committed screenshots contain invented data only. Physical iPhone and the Safari application are not claimed tested.

After review/publication, Part B starts with source-photo/Create/Edit labels and visible stopped/empty replies. J22–J25 are approved for later checkpoints; archive schema/rules still need presentation before implementation.
