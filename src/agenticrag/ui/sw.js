/* App shell and explicitly limited read-only offline data. */
const VERSION = "v21-7";
const SHELL = `rag-shell-${VERSION}`;
const DATA = `rag-offline-data-${VERSION}`;
const PREF = "rag-offline-preferences";
const ASSETS = ["/", "/index.html", "/styles.css?v=17", "/tokens.css?v=21", "/design-v2.css?v=21", "/components-v21.css?v=22", "/boot.js", "/app.js?v=22", "/v21.js?v=25", "/vendor/marked.umd.js", "/vendor/purify.min.js", "/manifest.webmanifest?v=3", "/icon-180.png?v=2", "/icon-192.png?v=2", "/icon-512.png?v=2", "/fonts/Geist-Variable.woff2", "/fonts/Geist-Variable-LatinExt.woff2", "/fonts/Newsreader-Variable.woff2", "/fonts/Newsreader-Variable-LatinExt.woff2", "/fonts/Newsreader-Variable-Italic.woff2", "/fonts/GeistMono-Variable.woff2", "/fonts/GeistMono-Variable-LatinExt.woff2"];
let cacheChats = true;

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SHELL).then((cache) => cache.addAll(ASSETS)));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith("rag-shell-") && key !== SHELL || key.startsWith("rag-offline-data-") && key !== DATA).map((key) => caches.delete(key)))));
});
self.addEventListener("message", (event) => {
  if (event.data?.type === "activate-update") event.waitUntil(self.skipWaiting());
  if (event.data?.type === "offline-chats") {
    cacheChats = Boolean(event.data.enabled);
    event.waitUntil((async () => {
      const preferences = await caches.open(PREF);
      await preferences.put("/offline-chats", new Response(cacheChats ? "1" : "0"));
      if (!cacheChats) await caches.delete(DATA);
    })());
  }
  if (event.data?.type === "clear-offline-copy") event.waitUntil(caches.delete(DATA));
});

const allowedData = (path) => path === "/api/v1/chats" || /^\/api\/v1\/chats\/[0-9a-f]{32}$/.test(path) || path === "/api/v1/projects" || path === "/api/v1/sources";
const withTimestamp = async (response) => {
  const headers = new Headers(response.headers);
  headers.set("X-AgenticRAG-Cached-At", new Date().toISOString());
  return new Response(await response.clone().blob(), { status: response.status, statusText: response.statusText, headers });
};
self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 4000);
        try {
          const response = await fetch(request, { signal: controller.signal });
          if (response.ok) (await caches.open(SHELL)).put("/index.html", response.clone());
          return response;
        } finally { clearTimeout(timeout); }
      } catch { return await caches.match("/index.html") || Response.error(); }
    })());
    return;
  }
  if (allowedData(url.pathname) && cacheChats) {
    event.respondWith((async () => {
      const preference = await (await caches.open(PREF)).match("/offline-chats");
      if (preference && await preference.text() === "0") return fetch(request);
      try {
        const response = await fetch(request);
        if (response.ok && (response.headers.get("content-type") || "").includes("application/json")) (await caches.open(DATA)).put(request, await withTimestamp(response));
        return response;
      } catch { return await caches.match(request) || Response.error(); }
    })());
    return;
  }
  if (/^\/fonts\/[A-Za-z0-9-]+\.woff2$/.test(url.pathname)) {
    event.respondWith((async () => {
      const cache = await caches.open(SHELL);
      const saved = await cache.match(request);
      if (saved) return saved;
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    })());
    return;
  }
  if (ASSETS.some((asset) => new URL(asset, self.location.origin).pathname === url.pathname)) {
    event.respondWith(fetch(request).catch(async () => await caches.match(request) || await caches.match(url.pathname) || Response.error()));
  }
});
