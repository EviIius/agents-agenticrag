# Read-only snapshot and app-opening chat report

8–9 November 2026 · isolated `codex/assistant-as1b` · draft PR #17

## Summary

Typed app requests now use the existing durable task/chat/SSE path and native Ollama.
The real API opened/verified Notes in 9.029 s; Calculator was refused in 4.392 s.
The bounded self-window reader returned four text areas in 0.303 s; revocation refused.
These fields do not establish individual-message identity, recipient or direction.
Private snapshots stay outside model context; no reply/send, main merge or deployment.

## Done-when checklist

| Item | Result | Evidence |
| --- | --- | --- |
| Required modifiability metadata, no input authority | Pass | Version-two snapshot schema, read-only manifest, compiled symbol/fixture checks |
| Bounded selected-pane read | Pass on this exact build/window | `v2-read.summary.json`: four nonempty areas, 16 accepted bytes, 0.303 s |
| Actual permission revocation | Pass | `v2-revoked.summary.json`: permission_required, no target/snapshot, 0.138 s |
| Exact message/recipient/latest-incoming identity | **Unqualified** | Four area identifiers but only one distinct identifier; no descriptions/subroles |
| Native app task through existing HTTP/SSE path | Pass | `native-api-trial.json`: queued → choosing → opening → complete; Notes PID 8575 |
| Unsupported action refused without dispatch | Pass | Calculator → needs_input, no opened app / native dispatch |
| Request replay, Stop and restart | Pass offline; real replay verified | Unit lifecycle tests; actual duplicate POSTs retained the same task IDs/call count |
| User model settings and native capacity | Pass | Actual payloads match copied saved settings, native adapter/schema/keep-alive and 32K; shared native.lock |
| Default-off and dev-only configuration | Pass | Disabled/unconfigured API tests; absent native home ignored while disabled |
| Fake preview and ordinary chat compatibility | Pass | Existing 22 browser cases; Python suite; no provider/search/Library prompt change |
| New UI states, narrow viewport and accessibility checks | Pass in simulated browsers | Four new Chromium/WebKit cases and actual persisted chat at 390/1440; serious/critical axe findings zero on design states |
| Physical iPhone, native cancellation timing, broader tasks | **Not qualified here** | No new physical-phone claim or native cancellation job; no read/draft/search/send task |

## Changed files

- `mac_snapshot.py`, `ReadOnlySnapshot.swift`, its builder and fixture/operator
  scripts: separate protocol v2, observed boolean modifiability, read-only access,
  fixed pane/range/byte budgets, stable before/after data and enum-only failures.
- `assistant/contracts.py`, `opening.py`, `manager.py`: additive native-opening
  task fields, qualification, conservative durable two-request reservations,
  stored dispatch intent, OS result validation, refusal and unknown-outcome states.
- `config.py`, `main.py`, bootstrap features: explicit dev-only qualification
  directory; default-off unchanged; registry and worker share native capacity.
- Existing AssistantChat/TaskCard, Composer and LiveAppShell: typed native request,
  actual task labels/progress, no scripted fixture chooser or irrelevant composer
  tools in native opening; normal composer defaults are unchanged.
- `/design?assistant&native`, generated API types, new unit/browser tests and
  test-only fake setup; isolated QA server/operator scripts and checkpoint docs.
- Evidence: `artifacts/assistant-readonly-20261108/` and
  `artifacts/assistant-chat-open-20261108/`. Raw private snapshots/payloads stay
  in mode-0700 QA directories with mode-0600 files, outside Git.

## Deviations from SPEC.md

Jake continued the pilot and freshly confirmed the self-conversation/empty composer.
AX modifiability is now metadata rather than a read filter. The compiled helper
has no input/AX-write/action/screenshot/send operation; reading does not grant any
such authority. Old protocol-one contracts and their rejection tests remain intact.

The original exact content layout was not a durable selection boundary. V1 of
this checkpoint stopped at structure and is retained at `74c5b362` with its unused
refusal slot. A separate role-only check found a valid 58-node/four-area self pane;
the frozen v1 guard accepts that saved shape offline. Its exact transient failure
was not captured, so no sole-cause claim is made.

V2 limits before/after structure equality to the selected pane while retaining
fresh ancestor roles, window/group/control identity, modifiability and complete
bounded text/metadata equality. Invented sidebar-only changes pass; changed pane,
ancestry or values still fail. It passed one read and one post-disable refusal
in a separate two-request ledger. No old unused slot or automatic retry was used.

The native app-opening feature remains default-off and dev-only. Its qualification
file pins the tested executable, installed profile/context, shared lock and a
two-request trial budget. No database migration or new dependency was needed;
new task fields use existing durable JSON/event storage. Completed native trials
are not permission to send or enable an unrestricted desktop driver.

PR #17 is still stacked on the unreleased AS0/AS1 work in PRs #15/#16. “No new
migration” here means no additional migration beyond that already prepared task
schema; it does not assert the whole stack is already installed or release-ready.

## Runtime observations

- The current Messages areas advertise AXValue as settable despite exposing
  bounded text APIs. V2 read four areas successfully, without setting any value.
  Four areas are **not** asserted to be four messages. Their shared identifier
  does not establish individual-message identity; no recipient/direction parser
  or local-model draft was enabled. No private values or private-text digests
  enter tool output, Git, task storage or model requests.
- Helper access was disabled after the read; a fresh helper genuinely refused.
  Other Settings permission entries were unchanged. Exact-build ad-hoc signing
  is still trial-only; cross-version permission survival is not qualified.
- The real HTTP trial made exactly **two** new `/api/chat` requests, with no
  preload/title/helper/retry call. With the previous CLI trial, the pilot total
  is four native model requests. One desktop opening was dispatched in this API
  trial; Calculator refusal dispatched none. Duplicate HTTP requests were also
  checked and caused neither inference nor another opening.
- Cold-start Notes task: 9.029 s. Calculator refusal: 4.392 s. Free-memory
  snapshots 94% → 64% → 65%; swap remained zero. These are snapshots, not peaks
  or a general latency/reliability qualification.
- The first QA server startup failed because changing a seeded connection ID
  conflicted with its hidden-model preference foreign key. The failed QA database
  and prepared source manifest were preserved. Atomic insertion using the declared
  ID fixed the test setup; a lifecycle/shared-lock preflight passed before any
  model call. This changed no production code, database or call budget.

## Test output

- Full `make check`: **982 Python**, **156 frontend**, **969 contrast pairs**,
  lint/format/strict types, API/additive/motion/privacy guards, production build
  and glass CSS check pass. Assistant coverage **1,452/1,599 = 90.8%**.
- Snapshot: **41 Python cases**, **32 compiled privacy/protocol checks**, five
  scoped-stability fixtures and five fake operator budget/privacy scenarios pass.
  Original reader/probe and app-opening tests remain included in the full suite.
- New opening-controller/API tests cover successful durable events, refusal,
  wrong app, request replay, cancellation before/after dispatch, restart without
  replay, invalid native authority fields, disabled setup, saved settings and
  two-call limits. They use fake operations; actual API results are separate.
- Browser first run: **25 pass / one test assertion fails**. The assertion counted
  five metadata-only `/api/show` requests as inference; its trace confirms each
  body only contains `model`. Corrected the test filter, preserving the first
  run/log/trace. Focused new cases then pass **4/4**; existing **22/22** passed
  on the same product source. No product behavior or target was changed for this.
- The actual persisted native-task chat was rendered at 390 and 1440 pixels,
  with both results present and no horizontal overflow. Capturing it made no
  additional model request. Real Mac Notes/Messages content was not screenshotted.
- All 32,543 older tracked artifact hashes were checked; regenerated outputs
  were archived before restoration. Fresh final verification records the scope
  and intentional source changes. Older reports/builds/stopped ledgers remain.

## Screenshots

- `artifacts/assistant-chat-open-20261108/browser/`: invented native-style states
  in Chromium/WebKit; explicitly synthetic, no Mac operation in these tests.
- `actual-chat-390.png`, `actual-chat-1440.png`: isolated app showing the real
  persisted API outcomes, with synthetic task text only. Codex inspected the
  phone-width capture; this is not Jake's physical iPhone acceptance.

## Review and next steps

The local review server is bound only to 127.0.0.1:18787. Open the retained chat
and choose Tools → Use computer to see the actual results. Its two-call allowance
is exhausted and intentionally paused; no additional inference is enabled by
leaving the review page running. Production 8787/service/Tailscale are unchanged.

App opening is now an implemented, tested chat capability on the isolated branch.
Review/promote that narrow operation before expanding its trial limits or release
configuration. Then qualify selected bubble/participant metadata for Messages
before drafting a reply. The current attributes alone are insufficient; use a
specific bounded bridge proposal rather than manufacturing IDs or guessing a
recipient from content/display names. Exact external sends still require approval
of the final recipient/text. Broader app control and physical-phone release checks
remain separate from these two successful primitives.
