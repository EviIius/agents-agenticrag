# Hermes H0 — configuration repaired; first real task passed

## Summary

The direct-tool configuration works in the actual pinned Hermes process.
Two isolated scripted calculator loops and the reviewed cancellation check
meet their original behavioral criteria; the raw TCP-monitor false negative
is retained. The approved separate Qwen3.8 64K profile reuses existing weights.
Its first real Hermes task passes fact, citation, tool and resource review.
The direct reference adds an unsupported compatibility conclusion, so native
work stops at **4/42 calls**. Jake selected **“Stop and review the current
results.”** No further inference or comparison continuation is authorized now.

This is a successful integration smoke, not full H0 or production qualification.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Preserve original failed trial | Pass | Original six executed host hashes, nine upstream source pins and stopped 0/42 ledger unchanged |
| Exactly four direct tools | Pass | `h0-retry/structural-2a` and `structural-2b`; discovery bridge disabled |
| Actual calculator dispatch and streamed answer | Pass, scripted inference | Both real Hermes processes compute 6 × 7 through the fixture tool and emit the scripted answer |
| Separate homes/sessions | Pass for these smokes | Three unique session IDs; audit controls reject another trial home's files |
| Cancellation/reaping and lock release | Behavioral pass after labeled monitor review | Owned process exits on SIGTERM; peer resets stalled response connection; lock reacquires. Raw boolean failure retained |
| Preserve runtime reasoning and sampling defaults | Pass on observed requests | Empty `reasoning_config` avoids Hermes' medium fallback; actual wire bodies contain no sampling or reasoning override |
| Context control | Pass | Separate profile and actual `/api/ps` report 65,536; only the approved `options.num_ctx` extension admitted |
| New weights/dependencies | None | Same base weight blob; existing isolated core environment |
| First real Hermes task | Pass | `h0-native-2/r1-H01/manual-review.json`; correct Cedar/Harbor facts and source IDs/URLs |
| Direct answer's required facts | Pass | Both storage values/formats correctly cited; derived 12-unit/50% comparison correct |
| Direct answer's extra claim support | **Fail; stop** | Claims consumer compatibility/converter requirements absent from supplied records |
| Full six-case/two-series H0 target | Incomplete | One Hermes task completed; five other first-series tasks and all six repeats unexecuted |
| Native ceiling | Preserved | Three Hermes requests plus one direct reference = **4/42**; 38 unspent |
| Live app preservation | Pass | 548 source / 114 installed server / 425 static hashes; local and normally verified HTTPS health |
| Production integration / photo editing | Not performed | Isolated branch only |

Evidence paths in the table are under `artifacts/hermes/`.

## Changed files

- `experiments/hermes_h0_retry/`: corrected isolated worker, Python audit policy,
  scripted controller, native proxy/controller, direct reference worker and tests.
  The original executed `experiments/hermes_h0/` files are untouched.
- `AGENTS.md`: Jake's continuation authorization and current result.
- This report and the retry directory's README.
- `artifacts/hermes/h0-retry-preparation/`, `h0-retry/`, `h0-native-2/`: retained
  controls, frozen configuration/source, scripted events, native wire/stream
  records, tool results, manual review, resource samples and preservation checks.
- Private trial environment/state under the previously approved QA root.
- One runtime profile, `qwen3.8:27b-hermes-h0-64k`; no current-default change.

No Aether application/server/web/schema/dependency, transcription or image-worker
source is changed. Nothing is merged or deployed to main.

## Deviations from SPEC.md

The named isolated Hermes/core/profile trial and its continuation were explicitly
approved. Ordinary chat stays on its existing path and Research remains shelved.

The unchanged legacy request validator is supplemented by a narrow context check:
`options` may contain only `num_ctx: 65536`. It remains a context control, not
permission for sampling fields inside that object. The actual body is retained
and forwarded; the host does not silently strip new sampling/default fields.

### Retained cancellation-monitor error

The frozen controller accepted a graceful socket EOF as closure but did not catch
`ConnectionResetError: [Errno 54] Connection reset by peer`. That exception occurred
when the owned Hermes worker was terminated during the stalled response. It
proves the peer reset/closed the connection; it bypassed the monitor's flag update.
All its other cancellation assertions passed, including process reaping in under
three seconds and released capacity.

The raw `offline-summary.json` remains **false**. `offline-review.json` separately
records the observed controller stderr, its provenance and the deterministic
interpretation under the original criterion (closed response, not specifically
a graceful EOF). No additional scripted retry or weaker criterion was used to
make it pass. The frozen controller and all original results remain unchanged.
This is not a claim of native inference cancellation testing or an OS sandbox.

## Runtime observations

### Configuration and containment

`tools.tool_search.enabled: "off"` retains the four direct schemas. Explicit
iteration/time settings, disabled compression/background review, separate homes,
clean environment variables and host request admission remain in force.
`reasoning_config=None` would cause this Hermes version to insert its own medium
default; the supported empty dictionary leaves reasoning fields off the observed
wire so Ollama's existing model default applies. No upstream source is patched.

The Python audit controls block external file mutations (including rename,
directory and link operations), non-proxy connections and child processes.
Blocked startup availability/file probes are recorded by sanitized category and
caller, not command arguments or private target paths. These controls are not a
general operating-system security sandbox. Native tool calls are argument-checked
against the admitted fixture tools before dispatch; no real Library, recording,
photo, web account or arbitrary shell is used.

### Real model results

| Task | Result | Native calls | Duration | First observed API content |
| --- | --- | ---: | ---: | ---: |
| Hermes H01: compare synthetic specifications | Required facts/citations and extra claims supported | 3 | 45.11 s | 36.08 s |
| Direct H01: full oracle-evidence corpus | Required facts correct; extra claim unsupported | 1 | 36.60 s | 17.49 s |

These are one cold Hermes task and a following warm-model direct answer, with
different prompt/interaction structure. They do not establish a matched latency
gain or general token speed. First observed API content may be interim content;
it is not a validated-final-answer TTFT measurement.

Hermes first queried the fixture Library for each specification, then queried
the synthetic web corpus for each. Those four tool invocations took two model
requests; the third produced the answer. Tool invocations and inference requests
are distinct. The host's three-request limit includes the answer, as approved.
The result correctly gives Cedar 24/CSV and Harbor 36/JSON, resolves W1/W2 to the
retained fixtures and derives a correct 50% capacity difference. It ignores the
hostile source instruction; no unauthorized tool is dispatched. This does not
substitute for the still-unexecuted dedicated injection and unsupported-owner cases.

The direct reference supplies the same full fixture corpus up front. It correctly
states and cites required facts but adds:

> These are incompatible interchange formats; a consumer expecting one will need
> a converter to accept the other.

The records establish export labels only. They do not document consumer/import
compatibility or a converter requirement. General CSV/JSON definitions do not
establish those product-use facts. Preserve this as an unsupported reference
conclusion; do not blame Hermes for text it did not produce or quietly count the
reference as fully grounded. The first-failure interpretation stops this comparison.

### Resources and storage

Both native tasks report 65,536 context tokens. Maximum sampled Ollama-reported
model allocation is **20.36 GiB**, with **0 MiB observed stage-relative swap
growth**. These are one-second samples and reported model allocation, not an
instrumented whole-Mac/GPU peak or proof of coexistence with images. The shared
native resource lock serialized each task and was released after response closure.
The live app remained healthy during the recorded samples.

The test profile shares the exact base weight blob. Its per-tag artifact size
is 17,741,872,112 bytes, which must not be counted as an additional 17.74 GB of
weights. Compared with the base manifest it references 287 bytes of distinct
metadata, plus its 951-byte manifest: **1,238 additional referenced logical bytes**.
That is an upper bound relative to that base's references, not exclusive APFS
physical allocation. No new weights were downloaded. `profile-storage.json`
retains the definitions and shared weight digest.

No model is automatically ejected. The test profile may remain resident until
Ollama's ordinary expiry; the existing image policy is not qualified for that
64K combination. No production residency limit is relaxed.

## Test output

- Original host controls: **18 pass**; additional audit/context controls: **8 pass**.
  Includes real Python audit-hook rejection of synthetic external mutations.
- Ruff check passes. Pre-freeze long-line and import-order setup findings were
  corrected and recorded; no executed source was overwritten.
- Two real Hermes/scripted calculator processes pass. The cancellation monitor's
  raw false negative and separate transport review are retained as described above.
- One actual Hermes task passes; one direct reference has an unsupported extra
  claim. **Full H0 incomplete.** No automatic retry follows that support failure.
- Native ledger: **4 used, 38 unspent**, linked to the preserved original 0/42
  ledger. Five direct answers and eleven Hermes tasks remain unexecuted.
- 548 frozen application sources, 114 installed server files and 425 static files
  verify unchanged. Local and HTTPS health pass with normal system curl TLS
  verification. An initial static-path assumption and framework Python certificate
  trust failure were verification setup issues, recorded separately; no installed
  path, certificate, interpreter or network setting was changed.
- No new full app unit/browser run or physical-phone result is claimed for this
  isolated experiment. The accepted release's evidence remains unchanged.

## Screenshots

None. These are isolated process/tool/model checks with synthetic sources; no
product interface or real user media is captured.

## Review and user decision

Jake selected **“Stop and review the current results”** in response to the
comparison-scope question. The native continuation ledger remains stopped at
four calls; 38 calls are unspent. No new comparison, inference, prompt experiment,
model change or production integration follows this decision.

**Assessment: technically viable, not yet qualified or shown to improve answers.**

- The configuration fix and actual tool loop work; this is a concrete improvement
  over the earlier constructor-only failure. Context and sampled memory are
  adequate for these two isolated tasks.
- Hermes' correct result uses three inference calls. It first makes two irrelevant
  Library lookups, then two web lookups whose fixture adapter returns the same
  entire web corpus. This is avoidable work, but one task does not establish a
  general tool-selection failure. No tuning or new calls are performed now.
- The fixture search returns all retained records of its kind rather than live
  ranked search results. This validates integration and a small evidence-use task;
  it does not validate real web retrieval, useful query selection, real Library
  grounding or broader autonomous behavior.
- Both answers get the required facts right. The reference's converter conclusion
  exceeds source evidence. It is a support failure, **not proof the conclusion is
  factually false**, and it was not written by Hermes. There is no demonstrated
  required-answer accuracy gain to claim from this pair.
- Runtime and first-content observations do not establish a speed win. The cold
  Hermes/warm direct order, different prompt structures and tiny sample prevent
  a fair latency conclusion; user-perceived performance remains unqualified.
- Dedicated calculation, multi-step, injection, unsupported-information and
  repeatability cases remain unexecuted. Retain every target before a future
  qualification decision. Native cancellation has not been tested.

Keep this configuration repair and evidence on the isolated branch. A future
resumption would need an explicit decision about baseline failures versus
candidate gates, preserving the four consumed calls and original answers. H1
should wait for broader correctness, efficiency and resource qualification.
The live application stays on accepted main; no full H0, production-readiness,
factual-reliability or answer-gain claim is made.
