# Approved rollout commands and scope

Run from the main checkout with scripts/tool-env.sh. Private control source and all whole-app/data snapshots remain in the fallback directory recorded in publication.json.

1. npm ci --prefix web --ignore-scripts (existing reviewed lock).
2. make build.
3. uv run --directory server python ../scripts/measure_bundle.py.
4. Installed Python runs PRIVATE/rollout.py prepare: fixed-service preflight, APFS-cloned whole app/data, consistent SQLite backup, copied candidate schema 13 startup and old-column comparison, whole schema-10 restore and prior-source startup.
5. Installed Python runs PRIVATE/rollout.py publish: require idle service; bootout existing launchd identity; refresh complete quiescent backup; rsync server/shared while preserving .venv/static; copy new static assets and index/sw last; apply authoritative migrations; compare all 45 old-column row projections before bootstrap; health/API/build-hash checks.
6. Installed Python runs PRIVATE/rollout.py verify.
7. Node runs PRIVATE/browser-live.mjs against the real Tailscale HTTPS URL. No screenshot, user text capture or generation. One synthetic definition per attempt is archived.
8. Verify 3,542 installed venv and 33 transcription files unchanged, exact plist and Tailscale route, Ollama version 0.35.0, and privacy audit.

## Whole-backup rollback

Stop the candidate through launchctl; preserve its current app/data under the private fallback; restore whole app/data and the exact original plist from the snapshot; bootstrap dev.agenticrag.workbench; verify health. The reviewed private helper performs this with its rollback action using the installed Python at its existing path. This is a complete restoration, not a reverse migration. The fallback database predates this deployment; subsequent work would be retained in the preserved candidate-data folder for recovery rather than merged automatically.

No deploy-script rewrite, inference experiment, dependency/model/runtime upgrade, Tailscale edit, prompt/default/sampling change, WS-E/reference-editing implementation or Research restart.
