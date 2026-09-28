# Implementation update — 28 Sep 2026

The [gap review](GAP-REVIEW-2026-09-28.md) records the build inspected at 15:47 UTC. The work below was completed afterward.

- Fixed, Agentic, and Supervisor prompts now request numbered citations; the host removes markers that do not resolve to validated citations.
- Runtime reachability drives the status dots, warnings, and Models screen.
- Agentic runs stream timed steps and retrieved evidence to the chat while they run. Saved chats retain step events and compact evidence metadata.
- The Evidence panel shows the cited passage, section, citation count, source details, active citation state, and a copy action. Steps have readable labels and measured durations.
- The phone composer, answer tables, mode menu, navigation, and source preview fit small screens. Controls, focus, loading states, and transitions were refined with reduced-motion support.
- Models now show measured bars, failures, active runtime status, and connection settings in a dialog. Sources have search, filters, titles, and rendered previews.

Verification: 110 tests ran: 109 passed and one was skipped. A real local Fixed run returned an inline `[1]` citation whose evidence and steps remained available after reload. A real Agentic run emitted live plan, search, tool, review, and budget events; a deliberately short three-step test ended with a budget abstention. The local workbench was updated and its chat and embedding runtimes reported reachable.

Older saved chats retain their original answers and citations. They cannot gain inline markers or full evidence passages retroactively. The older hidden v1 markup remains for a later cleanup pass; it does not affect current functionality.
