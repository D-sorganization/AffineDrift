// AffineDrift Service Worker for offline support
// The cache version is the single source of truth (issue #3333): CACHE_NAME is
// bumped by scripts/update_sw_cache_version.py (run in deploy-website.yml during
// the CSS bundle step), and the human-readable comment is derived from it below
// rather than tracked separately, so the two can no longer drift.
// TODO #1459: Replace hardcoded version with content-hash cache busting via build pipeline
importScripts('/js/service-worker-utils.js');

const {
  MAX_CACHE_ENTRIES,
  UPDATE_MESSAGE_TYPE,
  DEFAULT_NAVIGATION_TIMEOUT_MS,
  broadcastUpdate,
  trimCacheEntries,
  networkFirstWithTimeout,
  cacheFirst,
} = self.AffineDriftServiceWorkerUtils;

// Network-first navigation timeout: returning visitors get the latest deploy,
// but a slow/offline network falls back to cache within this budget.
const NAV_TIMEOUT_MS = DEFAULT_NAVIGATION_TIMEOUT_MS || 3000;
// Single source of truth for the cache version. update_sw_cache_version.py
// rewrites this line; the version label is derived from it (no separate comment).
const CACHE_NAME = 'affinedrift-v5-0f1fa59f';
const SW_VERSION = CACHE_NAME; // human-readable version === cache name (no drift)
const OFFLINE_URL = '/offline.html';

// Critical above-the-fold assets - precached first for fast first paint.
// The splash-screen startup launcher was removed (issue #3329); the navbar
// logo remains a critical first-paint asset.
const STARTUP_ASSETS = [
  '/logo/logo-navbar.png'
];

// Assets to cache immediately on install (includes STARTUP_ASSETS via spread)
// The deployed /styles.css is a flattened bundle generated into docs/styles.css
// by scripts/bundle_css.py. Do not precache the source @import graph here; those
// files are no longer separate runtime requests once the site is rendered.
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  ...STARTUP_ASSETS,
  '/styles.css',
  '/css/search-metrics.css',
  '/js/main.js',
  '/favicon.ico',
  '/manifest.json',
  OFFLINE_URL
];

async function storeResponse(cache, request, response, shouldNotify = false) {
  await cache.put(request, response.clone());
  await trimCacheEntries(cache, MAX_CACHE_ENTRIES);

  if (shouldNotify) {
    await broadcastUpdate(self.clients, {
      type: UPDATE_MESSAGE_TYPE,
      url: request.url,
    });
  }
}

// Install event - precache essential assets.
// Use individual cache.add() calls wrapped in Promise.allSettled so that ONE
// renamed/404'd asset cannot reject the whole install and silently disable
// offline support for everyone (issue #3333). Failures are logged, not fatal.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log(`[ServiceWorker] Precaching app shell (${SW_VERSION})`);
        return Promise.allSettled(
          PRECACHE_ASSETS.map((asset) =>
            cache.add(asset).catch((err) => {
              console.warn(`[ServiceWorker] Precache skipped for ${asset}:`, err);
              throw err; // surfaced as a rejected result; allSettled ignores it
            })
          )
        );
      })
      .then((results) => {
        const failed = results.filter((r) => r.status === 'rejected').length;
        if (failed > 0) {
          console.warn(`[ServiceWorker] ${failed}/${PRECACHE_ASSETS.length} precache assets failed; offline support is degraded but installed.`);
        }
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[ServiceWorker] Removing old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fall back to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip cross-origin requests (fonts, CDN, etc.)
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // HTML navigations: network-first so returning visitors always get the latest
  // deploy (content-only article edits do not bust CACHE_NAME, so cache-first
  // would serve stale article HTML — see issue #3221). Falls back to the cached
  // copy, then offline.html, on a slow/failed network.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      networkFirstWithTimeout(event.request, {
        cacheName: CACHE_NAME,
        offlineUrl: OFFLINE_URL,
        timeoutMs: NAV_TIMEOUT_MS,
        persistFn: (cache, request, response) =>
          storeResponse(cache, request, response, true),
      })
    );
    return;
  }

  // Static subresources (CSS/JS/images/fonts) are content-hashed by CACHE_NAME,
  // so cache-first is correct and fastest. Keep a background revalidation so a
  // changed-but-same-URL asset still refreshes for the next load.
  const backgroundUpdate = caches.match(event.request).then((cachedResponse) => {
    if (!cachedResponse) return;

    return fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          return caches.open(CACHE_NAME).then((cache) =>
            storeResponse(cache, event.request, response, true)
          );
        }
      })
      .catch(() => {/* Network failed, but we have cache */ });
  });

  event.waitUntil(backgroundUpdate);

  event.respondWith(
    cacheFirst(event.request, {
      cacheName: CACHE_NAME,
      persistFn: (cache, request, response) => storeResponse(cache, request, response),
    })
  );
});
