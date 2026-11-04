/* Vedic Astro service worker — static-asset caching only.
 *
 * Installability (manifest + icons) without an "offline charts"
 * promise: kundali computation is server-side, so API responses are
 * never cached and the app shell alone does not work offline. When a
 * fetch fails, the page's own error handling applies, unchanged.
 */
const CACHE = "vedic-astro-static-v8";
const ASSETS = [
  "/",
  "/static/styles.css",
  "/static/app.js",
  "/static/date_entry.js",
  "/static/router.js",
  "/static/share.js",
  "/static/life_questions.js",
  "/static/ai_astrologer.js",
  "/static/coords.js",
  "/static/scene3d.js",
  "/static/sw-update.js",
  "/static/manifest.webmanifest",
  "/static/icon-192.png",
  "/static/icon-512.png",
];

self.addEventListener("message", (event) => {
  // Sent by the update prompt (static/sw-update.js) when the user taps
  // Refresh while a new worker is waiting: let it take over at once.
  // (The install handler also calls skipWaiting, so this is the path for
  // a worker that reached "waiting" before activating.)
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Never cache API calls or cross-origin requests (fonts, maps).
  if (url.pathname.startsWith("/api/") || url.origin !== self.location.origin) return;
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request).then((response) => {
        if (response.ok && ASSETS.includes(url.pathname)) {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        }
        return response;
      });
      return cached || network;
    }),
  );
});
