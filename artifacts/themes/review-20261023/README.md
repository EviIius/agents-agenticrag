# TH1/TH2 evidence — synthetic fixtures

Checkpoint started 23 October 2026. See `docs/THEMES-INTEGRATION-REPORT.md` for
the gate details. The final complete run passes 856 cases, with four existing skips
and zero failures (all 88 new theme cases pass); partial runs are not substituted.
No native model/transcription call, model download, dependency installation,
main merge or publication is part of this checkpoint.

- `make-check.log`: complete static/type/unit/coverage/API/motion/contrast gate.
- `make-e2e.log` and `full-browser-exit.json`: final complete browser invocation
  and its exit status. The exit file is written only when that invocation ends.
- `original-*.log`, `*-failure.log`, earlier preference/preflight logs: retained
  defects and diagnostic attempts; never substitute them for the final run.
- `bundle.json`, `original-bundle.json`, `installed-bundle.json`: same-method
  gzip entry/static-import measurements, not total lazy-loaded application size.
- `final-executed-source.json`: source/test freeze before the complete invocation.
- `preservation-before.json`, `preservation-after.json`: installed public-code
  and supplied-input hashes, original workspace/remote main and health audit.
- `screens/` and `visual/`: synthetic captures; no real conversation, recording,
  Library document or photograph. `screenshot-lineage.json` maps test filenames
  to archived fake-labelled names without changing bytes.
- `regression-metrics/`: current small JSON results from the full regression run.
  Historical tracked artifacts are restored rather than overwritten; the
  preservation manifest records both historical and fresh capture hashes.
- Motion clips and unnormalized raw logs are retained outside Git under the
  private paths named by `motion-review.json` and `log-provenance.json`.

The before-React test verifies attributes before entry execution and resolved
CSS with React withheld. It is not an instrumented physical first-paint test.
The offline theme-asset test shuts down its own no-store loopback origin and
checks exact cached response hashes plus an uncached failure control. It does
not claim an iPhone offline/Home Screen pass.

The offline diagnostic source snapshot originally ran under `web/tests/`; it was
moved to this evidence folder before the final suite so it adds no test cases.
Its relative test imports retain that original location.
