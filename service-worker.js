/**
 * service-worker.js — PWA offline cache for P&L Dashboard
 *
 * Strategy: stale-while-revalidate for the main HTML, cache-first for
 * static assets (icons, manifest). Bumps CACHE_VERSION to invalidate
 * old caches on updates.
 *
 * Notes:
 *  - Cross-origin requests (Google Sheets API, Supabase, Google OAuth)
 *    are NOT cached — passed through to network. This is essential so
 *    Sheets sync works in real time and credentials don't get cached.
 *  - When offline and network fails for the main HTML, the cached copy
 *    is served. All app logic + libraries are inlined in the HTML so
 *    one cached file is enough to run.
 */

const CACHE_VERSION = 'pl-dashboard-v8.6.0';
const CORE_ASSETS = [
  './',
  './index.html',
  './pl-dashboard-v8.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './version.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(cache => {
      // Use addAll with no-cors fallback so a missing icon doesn't break install
      return Promise.all(
        CORE_ASSETS.map(url =>
          cache.add(url).catch(err => console.warn('[sw] skip cache for', url, err))
        )
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Only handle same-origin GET requests; everything else passes through.
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
    return;
  }

  // Stale-while-revalidate for app shell.
  event.respondWith(
    caches.open(CACHE_VERSION).then(async cache => {
      const cached = await cache.match(event.request);
      const fetchPromise = fetch(event.request).then(resp => {
        // Only cache successful responses.
        if (resp && resp.status === 200 && resp.type === 'basic') {
          cache.put(event.request, resp.clone());
        }
        return resp;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

// Listen for skipWaiting message from the page (lets users trigger an update).
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});