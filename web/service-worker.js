/* Generated with a content-based build ID. No private/API data is cached. */
const CACHE = "workbench-shell-__BUILD__";
const PRECACHE = __PRECACHE__;
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)));
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) {
      if (key.startsWith("workbench-shell-") && key !== CACHE) await caches.delete(key);
    }
    await self.clients.claim();
  })());
});
self.addEventListener("message", event => {
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();
});
self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || url.pathname === "/api" || url.pathname.startsWith("/api/")) return;
  if (request.mode === "navigate") {
    // Never store navigation responses: a network index can belong to the next
    // build. Offline documents must match this worker's installed asset set.
    event.respondWith(fetch(request).catch(async () => (await caches.open(CACHE)).match("/index.html")));
    return;
  }
  const hashed = /^\/assets\/[^/]+[-.][\w-]{8,}\.(js|css|woff2?)$/.test(url.pathname);
  if (!hashed && !PRECACHE.includes(url.pathname)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(request);
    if (cached) return cached;
    const response = await fetch(request);
    if (response.ok && response.type === "basic" && !response.redirected) await cache.put(request, response.clone());
    return response;
  })());
});
