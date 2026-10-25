# Aero — integration after visual review

24 October 2026. Jake approved integration after the local preview. Execute on
`codex/themes-aero-integration`; retain the seven-theme `c7758120` baseline and
all old reports. The old 856-pass result is not an eight-theme qualification.
Merge/deployment remain separate; stop for the independent UI review.

1. Confirm the glass/scene direction (J21) after the local day/night and fake
   conversation review. Preserve the existing theme-switch/greeting repairs.
2. Wire `PaletteScene` into the actual new-chat EmptyState, add Aero to server
   setting validation and its round-trip/rejection tests, and include all Aero
   public assets in the PWA fingerprint/cache. No schema migration or package.
3. Extend greeting/helper coverage only for the named bounded Aero keyframe;
   retain the 1 s guard for unrelated finite motion and the 4.5 s full greeting
   bound. Keep ordinary chat prompts/payloads and omitted sampling fields frozen.
4. Measure actual transparent/glossy text backgrounds, not token values alone.
   Check new chat, long conversations, composer, sidebar, menus, dialogs and
   sheets in both modes at phone/desktop widths; preserve ordinary focus/labels.
5. Run full `make check` and one complete Chromium/WebKit `make e2e`; no partial
   assembly, weakened assertions or new skips. Re-measure initial JS under the
   existing 256,000-byte limit, first-token overhead and streaming render budget.
6. Run the existing fake 100 tok/s/300-message performance workload with Aero
   selected. Separately measure the animated new-chat scene/compositor cost;
   render CPU duration and rAF intervals alone do not prove real phone GPU FPS.
   Real iPhone/Safari review remains explicit. If it stutters, remove sidebar
   blur first, then reduce bubbles; record every material/performance change.
7. Provide H4 evidence and the bounded joint server/web release/rollback plan.
   Publish only after separate approval; an old server rejects the new setting.
   Keep Home Screen icon guidance qualified until observed on the actual phone.

No new model/native calls, agent trials, watcher or automation is implied by
these theme steps. The recording-folder NS0 proposal remains a separate task.
