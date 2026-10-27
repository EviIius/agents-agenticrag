# Design critique B evidence

Started 25 October; continued 26–27 October 2026. Synthetic data only.
Candidate source is isolated on `codex/design-critique-b`; no native inference,
new package, migration, merge or deployment is part of this checkpoint.

## Authoritative final results

- `make-check-final.log`: complete lint, type, Python/frontend, contrast,
  privacy, API, motion and production CSS checks.
- `make-e2e-final.log`: only this complete invocation can qualify G2. Earlier
  partial passes are never combined into it. It must finish with 918 passes,
  four existing skips and zero failures/interruption.
- `executed-source.json`: hashes of all 526 executed source/config/test files.
- `bundle-final.json`: output of the unchanged `scripts/measure_bundle.py`.
- `test-list-final.log`: full discovery list, 922 cases in 64 files. Video-enabled
  image suites run later than the initial non-video chat suites.
- `verification.json`: generated only after the final gates and installed-file,
  supplied-input and historical-evidence preservation checks pass.
- `metrics/`, `coverage-final.json`, `browser/`: copied final measurements and
  synthetic screenshots. Physical iPhone/Safari and VoiceOver are not inferred
  from browser-engine results.

## Retained intermediate results

The report and `test-diff-ledger.md` explain all earlier attempts. Functional
fixture/readiness corrections, the picker accessibility repair, compact drawer
scrolling, hover-action containment, fake-model preference cleanup, mobile edit
card wrapping and the visible Stopped/Retry selectors all retain their logs and
failure contexts under `failures/`. The QA bundle-wrapper error is described in
`bundle-controller-error.md`; the repository measurement and limit never change.

Raw browser traces and regenerated historical captures are preserved privately
under `~/.local/share/workbench/qa/design-critique-b-20261025/`. The original
tracked historical bytes are restored after the final run. The supplied live
critique photos remain outside this evidence set.
