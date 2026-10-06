# Phase 7 report

## Checkpoint 7-0 — blocked at the extension prerequisite

### Summary

Jake approved `sqlite-vec` and the installed `qwen3-embedding:0.6b` by saying
“go ahead” after the explicit dependency/model question. Optional 6B is skipped;
Ollama remains the only runtime. Installed the pinned stable package
`sqlite-vec==0.1.9` in both existing server environments without changing any
other dependency. The first probe fails in both: Python 3.14.7's `sqlite3`
connection has no `enable_load_extension` method. Phase 7 §2 requires stopping
here. No Library product code, migration, embedding call or model download ran.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| J3 dependency approval | Approved | Jake: “go ahead” to the explicit `sqlite-vec` / installed embedding model question; `AGENTS.md` |
| J8 embedding model | Selected | `qwen3-embedding:0.6b`; Ollama `/api/show` reports `embedding`; `artifacts/phase-7/probe.json` |
| Step 1, development SQLite extension | **Blocked** | `probe-development.json`, exit 1, `AttributeError` |
| Step 1, installed interpreter SQLite extension | **Blocked** | `probe-installed.json`, exit 1, same `AttributeError` |
| Step 2, aiosqlite through `db/core.connect()` | Not run | Mandatory stop after step 1 |
| Step 3, 20,000 × 768 vectors / 50 queries | Not run | Mandatory stop after step 1 |
| Step 4, 3,000-character embedding without truncation | Not run | Mandatory stop after step 1 |
| Live app availability | Pass health only | Local and TLS-verified Tailscale HTTP 200 in `probe.json` |
| 7-0 complete | **No** | Requires an approved interpreter remedy and rerun |

### Changed files

- Server metadata: `server/pyproject.toml`, `server/uv.lock` add only
  `sqlite-vec==0.1.9`; existing package versions unchanged.
- Scripts: `scripts/probe_library_extension.py` performs step 1 against a synthetic
  in-memory database and prints only environment metadata; nonzero exit on failure.
- Privacy guard: `scripts/privacy_audit.py` extends existing artifact scanning and
  synthetic screenshot filename checks to Phase 7.
- Docs: `AGENTS.md` records the explicit approval; this report.
- Evidence: `artifacts/phase-7/probe.json`, individual interpreter results,
  `check.txt`, `privacy-audit.json`.
- No files under `server/app`, `server/tests`, `web`, `shared`, production
  migrations, transcription source, or existing phase evidence changed.

### Deviations from SPEC.md

No storage fallback or alternate SQLite package was introduced. The mandatory
stop in Phase 7 §2 applies. No later Library checkpoint is started. The roadmap's
suggested authorization text points to §6.3; the actual Library answer prompt
is §5.3, and `AGENTS.md` records the correct section. No prompt was created or edited.

### Runtime observations

Both virtual environments resolve to the same existing framework Python 3.14.7;
both report SQLite 3.50.4. Both can import `sqlite_vec` 0.1.9 and locate its ARM64
extension; both extension binaries hash to
`193e480c50b59a55977d166f4aaf0e1bc8832d6963516e5950f39e4d2ce0b793`.
The failure precedes extension loading: the Python connection lacks the enabling
method. This is a Python build capability issue; the installed embedding model
has not yet been exercised.

Package version and wheel hashes come from the [PyPI release](https://pypi.org/project/sqlite-vec/0.1.9/).
The required loading sequence follows the [author's Python documentation](https://alexgarcia.xyz/sqlite-vec/python.html).
A read-only `uv python list 3.14 --only-downloads` confirms a managed 3.14.7 build
is available. It has not been installed or probed. [uv supports separate managed
Python installations](https://docs.astral.sh/uv/concepts/python-versions/); whether
that build loads this extension must be verified before switching environments.

An initial health-evidence helper using framework `urllib` encountered its
missing default CA certificate store. The helper was rerun using the app's
existing `httpx` with certificate verification enabled; both health checks
returned 200. No SSL verification bypass or application change was made.

### Test output and gates

`make check` passed (exit 0): **257 Python tests**, **36 frontend tests**, **74
contrast pairs**; lint, types, API generation/additive guard, frozen prompt and
row guards, motion and privacy checks passed. Coverage remains providers 85.8%,
runs 89.2%, search 88.9%, transcribe 93.1%, documents 96.6%, backup 96.8%.
Output is in `artifacts/phase-7/check.txt`, coverage in `coverage.json`. Probe
script lint/format and `git diff --check` also passed. Existing application and
test code is unchanged.

No full E2E run, benchmark, new screenshots or phone check is claimed for this
blocked attempt. G-2 and the remaining completion gates are not discharged;
7-0 is **not done**. No UI state exists yet, so there are no new design states
or accessibility captures. No changes under search/runs/providers or model-facing
prompts, so no new web eval is triggered. No migration or production rollout
occurred; migration rollback is not triggered. Earlier 6A test results are the
fallback evidence, not presented as a new checkpoint pass.

### Test-diff ledger / core unchanged

No test file, assertion, timeout or skip changed. The sole existing guard edit
adds Phase 7 artifact coverage to `privacy_audit.py`; prior checks remain intact.
All C1–C16 product implementations remain byte-unchanged. Live health confirms
availability only, not a new pass of every user flow.

### Privacy, deployment and fallback

The probe opens only an in-memory synthetic database. It reads no production
chats, attachments, transcripts, document filenames or glossary entries.
Ollama `show` is a metadata request, not an embedding/model inference request.
No embedding vectors or document text were generated, logged or stored.

No app code, interpreter, launchd plist, port, Tailscale route or production
schema changed. The installed environment now has the one approved extra
package, unused by the unchanged running app; installed manifests still describe
6A. This was a package-only probe installation, not a production release.
A future frozen sync to the unchanged installed 6A lock removes that unused
package. The 6A source `533418b`, evidence `19c25a1`, and acceptance `4ada059`
remain the last accepted fallback. Sidebar motion and VoiceOver limitations
remain deferred; no physical device pass is invented.

### Screenshots

None: no product UI was changed, and the mandatory prerequisite failed.

### Open question for Jake

Phase 7 §2 and SPEC's observed-runtime stop rule require a decision before a
remedy. Recommended: prepare an isolated uv-managed Python **3.14.7** build,
verify extension loading first, then recreate server environments from the same
frozen dependency lock. Preserve the existing framework Python and current
virtual environments for rollback. Run the required checks and full browser
suite before any installed-app interpreter switch. Keep the live app on the
accepted 6A runtime while preparing this candidate. No change to the transcription
engine interpreter is proposed. No other SQLite dependency or storage design
is proposed. Authorization is pending.
