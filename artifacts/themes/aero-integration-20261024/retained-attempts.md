# Retained diagnostic attempts

The logs are not qualification evidence. `make-e2e.log` is the separate complete gate.

- `focused-before.log`: 6 pass, 8 fail; initial PNG audit required unavailable Pillow.
- `focused-materials-v2.log`: hidden text contaminated glyph mask; AA pixel assumptions.
- `focused-materials-v3.log`: mask isolation repaired; remaining AA/material findings.
- `focused-materials-v4.log`: 9 pass, 1 trace-close ENOENT after runner overlap.
- `focused-materials-v5.log`: startup refused an already occupied fake-runtime port.
- `focused-materials-v6.log`: real gloss/sky material findings before final corrections.
- `focused-materials-v7.log`: 10 pass sequential run, including 64 material audits.

All raw captures/traces from these attempts are retained outside Git at
`~/.local/share/workbench/qa/aero-integration-20261024/`. Earlier versions of the
new harness are not qualification; no original release assertion was weakened.
Two temporary TS errors (Node.remove) and a shell command without a configured
Python alias were corrected before the full gate; neither changed app state.

- `make-e2e-initial-aborted.log`: 290 pass, one fail (Aero performance fixture's
  shared saved-palette leak), one interrupted, one existing skip, 601 not run.
  Trace confirms Aero under the unchanged Cobalt border assertion. Original
  performance source bytes match `initial-executed-source.json` and are retained
  privately in `performance-initial-failing.ts`.
- `performance-isolation-regression.log`: six ordered performance/layout cases
  pass after restoring the shared preference; original layout assertions retained.

- `make-e2e-second-aborted.log`: 464 pass, two false contrast failures at
  covered glyphs under a workflow toast, one interrupted, one existing skip,
  426 not run; 44.1 minutes. Chromium completed without failures.
- `occlusion-regression-first.log`: 17 pass, one negative-control fixture
  failure from missing mobile viewport meta (980 CSS /390 PNG mismatch).
  The corrected fixture retains the visible-low-contrast and partial-label assertions.
- `final-frontend-check-v3.log`: temporary inference error on the new elementId;
  explicit string annotation resolves it. No app code changed.

## Third complete invocation and notification-timer repair

The third complete invocation finished with 891 passed, four existing skips and
one failed case (1.3 h). The WebKit dark desktop Tools audit lost a measured DOM
element while its workflow notification expired between PNG passes. The original
log is `make-e2e-third-complete-failed.log`; the exact executed source inventory is
`third-executed-source.json`. Trace and original audit source are archived under
the private `third-complete-failure/` directory. This is a failed complete gate.

The repaired new audit installs Playwright's clock before app timers are created
and freezes it only across the three PNG captures and pixel analysis, resuming
in finally. It does not hide notifications or skip disappeared text. Its existing
two-engine negative control now adds an expiring readable notification, requires
it to be measured, and verifies expiry resumes afterward. The exposed low-contrast
text still must fail the contrast calculation.

The first clock probe used a just-read timestamp; IPC delay made that timestamp
past. `clock-control.log` retains eight failed app cases and two passing controls.
The correction chooses a timestamp one second ahead, before collecting text. A
wrong-working-directory rerun was interrupted and retained separately in
`clock-control-wrong-cwd-aborted.log`; it did not execute the correction.
