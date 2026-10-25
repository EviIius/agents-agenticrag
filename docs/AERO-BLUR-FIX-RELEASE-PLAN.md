# Part A publication — 25 October 2026

Jake approved the completed Part A checkpoint. Release PR #12's exact qualified
product (`18a3f61a`), without starting the later chat/page changes.

1. Verify all 456 executed source hashes, the 166-file QA evidence manifest,
   recorded CSS hashes and 252,228-byte initial JS budget. Retain the completed
   785 Python /151 frontend /900 browser gates and four unchanged browser skips.
   No source or dependency change requires a rebuild or new inference.
2. Record approval and the release controller; dry-run it. Mark PR #12 ready,
   merge against its exact expected head, and use a separate checkout branch of
   merged main for publication. Preserve the original workspaces.
3. Require exact installed/current source parity outside static, the existing
   schema-aware worker and selectors, plist/bind/port/route and running PID.
   Use the established atomic static-file publication pattern; do not use the
   generic deployment path or its obsolete backend baseline.
4. Save the entire current static tree and a consistent online SQLite backup to
   a new private release directory. Verify backup integrity/schema/FKs. User work
   stays live; no job is cancelled, no model unloaded and no service restarted.
5. Copy all new assets atomically, retaining old hashed assets. Replace index,
   then service worker last. Verify all candidate static hashes, unchanged old
   hashed assets and exact local/verified HTTPS HTML/CSS/SW. Recheck backend,
   worker, environment/configuration, service PID and route.
6. On failure restore previous static bytes only, retaining newly added hashed
   assets for any clients that already loaded them. Keep the current backend,
   worker and current data; never restore the snapshot DB over new messages.
7. Verify real HTTPS assets in Chromium/WebKit using synthetic intercepted APIs:
   computed blur on composer/sidebar/header/Settings/Tools, 96% overlay backing,
   synthetic image behind overlays and normal/reduced motion. No live sends or
   preference writes. Publish the release report; physical iPhone remains pending.
