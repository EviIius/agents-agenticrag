# Data contract v2.1: backend and static-asset changes

These are all additive. They continue the numbering from v2 (B1–B9).

| Item | Priority | Needed for |
|---|---|---|
| Static assets (fonts, `boot.js`, `sw.js`, manifest) | P1 | themes, fonts, offline |
| B10 `GET /api/v1/health` | P1 | launch intro, offline detection |
| B11 runtime-status additions | P1 | launch intro, runtime-down popover |
| B12 model warm-up | P2 | the launch "loading" row |
| B13 service worker contract | P1 | the offline screen |
| B14 keyword-only search fallback | P3 | the "Keyword search in sources" line |
| B15 chat soft delete | P3 | Undo instead of a confirmation |

## Static assets

- **`UI_FILES` gains these entries:**
  - `/boot.js`
  - `/sw.js`
  - `/components-v21.css` (only if you keep the component CSS as its own file)
  - six fonts: `Literata-Variable.woff2`, `Literata-Variable-LatinExt.woff2`, `Literata-Variable-Italic.woff2`, `AtkinsonHyperlegibleNext-Variable.woff2`, `AtkinsonHyperlegibleNext-Variable-LatinExt.woff2` and `AtkinsonHyperlegibleNext-Variable-Italic.woff2`.
  - `pyproject.toml` package data already globs `ui/fonts/*.woff2`, `ui/fonts/LICENSE-*` and `ui/*.js`.
- **`/sw.js`:**
  - served with `Content-Type: text/javascript; charset=utf-8` and `Cache-Control: no-cache`;
  - it must be at the root so its scope is `/`;
  - the existing CSP allows it: `default-src 'self'` covers `worker-src`.
- **`/boot.js`:** `Cache-Control: no-cache`. It's tiny and must stay under about 2 KB.
- **`manifest.webmanifest`:** set `background_color` and `theme_color` to `#0C0C0D`, and bump its `?v=`.
- **Tests:**
  - each new font returns `font/woff2` with the long cache header;
  - `sw.js` and `boot.js` return `no-cache`;
  - the CSP header is unchanged.

## B10. `GET /api/v1/health`

A cheap liveness check. It makes no provider calls and must never block on the model.

```json
{"ok": true, "version": "0.4.x", "asset_version": "18", "started_at": "2026-09-29T20:14:00Z", "server_time": "2026-09-29T21:02:11Z"}
```

- **`Cache-Control: no-store`.**
- **No Origin check,** because it's a GET. It returns nothing sensitive.
- **`asset_version`** lets the app notice that the server was updated, and prompt "Update ready · Reload".
- **Test:** it responds in under 50 ms while `runtime-status` is probing a dead endpoint.

## B11. `runtime-status` additions

Add these per-role fields. Keep every existing field.

| Field | Type | Meaning |
|---|---|---|
| `runtime` | `"ollama" \| "lm-studio" \| "llama-cpp" \| "vllm" \| "openai" \| null` | from the runtime selection |
| `endpoint` | string | `host:port` from the configured `base_url`. No scheme, path, query or credentials. Never the API key. |
| `error_kind` | `"refused" \| "timeout" \| "http" \| "invalid" \| "model_missing" \| null` | classified from the probe. `model_missing` when reachable but `model_present === false`. |
| `loaded` | `true \| false \| null` | whether the model is in memory now. `null` when the runtime can't say. |

**Where `loaded` comes from:**

- **Ollama:** `GET /api/ps`. The model is listed when it's loaded.
- **LM Studio:** its REST model list reports a loaded/not-loaded state (`/api/v0/models` in current releases; confirm against the installed version).
- **Otherwise:** `null`.

**Other changes:**

- **`GET /api/v1/runtime-status?fresh=1`** bypasses the 15 s cache. Rate-limit it to one fresh probe every 3 s, and return the cached result inside that window.
- **Tests** cover each `error_kind`, `endpoint` redaction (credentials in the URL are stripped), and the `fresh` rate limit.

## B12. Model warm-up (optional)

`POST /api/v1/runtime/warm` with `{"role": "chat"}` returns `202 {"started": true}` straight away. It works in the background:

- **Ollama:** `POST /api/generate {"model": m, "keep_alive": "30m"}` with no prompt. Ollama loads the model without generating.
- **LM Studio and the others:** a 1-token chat completion, which triggers just-in-time loading.

**Rules:**

- Same-origin required (`_require_same_origin`).
- At most one warm-up at a time.
- It never runs while a user run is active, and it uses the same inference lock.
- The result shows up through `runtime-status.loaded`.

**Setting:** "Warm up the model when the app opens" in Settings › Models, default on. The Mac mini is a dedicated machine, and without a warm-up the first answer pays the load cost.

## B13. Service worker contract

The worker's behaviour is in SPEC §4.3. What the backend needs to guarantee:

- **The app's GET JSON endpoints return consistent `Content-Type`s,** so the worker can cache them.
- **Cache-control headers** are `no-store` on health and runtime-status, and on streams (the worker also skips these by URL).
- **Pages still work without the worker.** When it's missing or blocked, everything must behave as it does today.

## B14. Keyword-only search fallback (optional)

When the embedding provider is unreachable, `HybridRetriever.retrieve(..., allow_degraded=True)` runs **lexical search only**, and marks the result with `retrieval_mode: "lexical_only"` and an event.

- **Use it only for Sources search and the source preview.** Grounded answer modes keep failing clearly; they need the chat model anyway.
- **The UI claims "Keyword search in sources" only when this exists.**

## B15. Chat soft delete (optional)

`DELETE /api/v1/chats/{id}` marks the chat deleted. `POST /api/v1/chats/{id}/restore` undoes it within 30 s, and a sweep then deletes it permanently.

- **Only once this exists,** switch Delete chat from the confirmation dialog to the Undo toast (SPEC §2.2).
