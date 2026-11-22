// Service worker: keeps the whole app offline. 46695aade1 is replaced at build time,
// so each new build gets a new cache and the old one is removed.
const VERSION = "46695aade1";
const APP_CACHE = "nch-app-" + VERSION;
const FONT_CACHE = "nch-fonts-v1";
const SHELL = ["./", "index.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(APP_CACHE)
    .then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: "reload" }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith("nch-app-") && k !== APP_CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Google Fonts: cache on first use, then serve offline.
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    event.respondWith(caches.open(FONT_CACHE).then(async (c) => {
      const hit = await c.match(req);
      if (hit) return hit;
      try { const res = await fetch(req); if (res.ok || res.type === "opaque") c.put(req, res.clone()); return res; }
      catch (e) { return new Response("", { status: 504 }); }
    }));
    return;
  }
  if (url.origin !== self.location.origin) return;

  // App: offline first. Page loads come from the cache; a new build arrives with a new sw.js.
  event.respondWith((async () => {
    const c = await caches.open(APP_CACHE);
    const key = req.mode === "navigate" ? "index.html" : req;
    const hit = await c.match(key, { ignoreSearch: req.mode === "navigate" });
    if (hit) return hit;
    try { return await fetch(req); }
    catch (e) { return (await c.match("index.html")) || new Response("Offline", { status: 503 }); }
  })());
});
