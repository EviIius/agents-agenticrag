# Deployment

The local app listens on `127.0.0.1:8787`; remote access uses the existing trusted HTTPS proxy. Preserve `.data`, `workbench-providers.json`, and conversation databases when updating.

For the installed macOS app:

1. Confirm there is no active question, or explicitly stop it through the app.
2. Back up the installed `src/agenticrag` package and SQLite databases using `scripts/backup_workbench.py`.
3. Sync `src/agenticrag` into `/Users/evilius/.local/share/agenticrag/src/agenticrag` with deletion enabled for obsolete package files. Do not sync or delete user data.
4. Copy current `pyproject.toml` and `README.md` if updating package metadata.
5. Restart `gui/$(id -u)/dev.agenticrag.workbench` with `launchctl kickstart -k`.
6. Check `/healthz`, `/api/v1/bootstrap`, and the served HTML/JS/CSS. Current version is **0.5.0**, with app asset version **50**.
7. Reload the browser or installed phone app to activate the new service worker and composer.

The service worker removes old shell caches during activation. Previously saved conversations remain readable, including old reports; the removed execution modes cannot be started through the API.

Docker uses the `documents,web` extras and mounts only the persistent data volume. Configure a reachable local runtime endpoint as described in `.env.example`.
