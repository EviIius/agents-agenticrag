# AT-A review evidence

Synthetic files only. This branch is not installed or merged into main.

## Start here

- [AT-A assessment and H4 report](../../../docs/ATTACHMENTS-AT-A-REPORT.md)
- [Phone Tools, dark](browser/tools-390-dark-webkit-fake.png)
- [Phone photo warning, dark](browser/warning-390-dark-webkit-fake.png)
- [Desktop ready tray, light](browser/ready-1440-light-chromium-fake.png)
- [Original Claude prototype](../../../docs/next/attachments/prototype.html)

`browser/` retains light/dark × 390/1440 × Chromium/WebKit state captures and axe results. Native file pickers were never captured. WebKit emulation is not a physical-iPhone pass.

## Reproducibility

- `executed-web-source.json`: exact web source/tests used by the complete final run.
- `design-source.json`: hashes of the unchanged supplied package and its 29 references.
- `source-frozen.json`: unchanged server/API/dependency/send scope against base main.
- `payload-parity-fake.json`: 24 raw request-body comparisons, no real inference.
- `retained-attempts.json`: unsuccessful/interrupted attempts and remedies, retained separately.
- `test-ledger-audit.json`: existing test adaptations, no new skips or raised deadlines.
- `bundle.json`: gzip level-9 initial JS, recursive static imports only.

Final `make check` passes (673 Python / 121 frontend tests; 110 contrast pairs). One complete `make e2e` passes: 677 tests, three existing skips, zero failures. See `e2e.txt`, `check.txt`, `accessibility-summary.json` and `performance/summary.json`. AT-A is ready for branch review; AT-B and publication require later review.

`check.txt` and `e2e.txt` remove trailing whitespace for Git. Exact raw logs and their hashes are retained in `log-provenance.json`; no result or captured request body is changed.
