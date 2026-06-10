// AffineDrift Service Worker for offline support
// Version 6: Updated 2026-06-09 (network-first for HTML navigations — issue #3221)
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
const CACHE_NAME = 'affinedrift-v4-27f68dec';
const OFFLINE_URL = '/offline.html';

// Critical startup assets - loaded first for fast splash screen
// NOTE: These are spread into PRECACHE_ASSETS below for unified caching,
// but kept as a separate array for clarity and potential future prioritization
const STARTUP_ASSETS = [
  '/css/startup-launcher.css',
  '/js/startup-launcher.js',
  '/logo/logo-navbar.png'
];

// Stylesheets pulled in via @import from styles.css (directly, and
// transitively via css/tokens/design-tokens.css). styles.css is useless
// offline without these — @import sub-resources are NOT cached by caching
// the parent stylesheet, so precache them explicitly.
// Contract test: tests/service-worker-precache.test.js keeps this list in
// sync with the @import graph.
const IMPORTED_STYLESHEETS = [
  '/css/tokens/design-tokens.css',
  '/css/tokens/colors.css',
  '/css/tokens/typography.css',
  '/css/tokens/spacing.css',
  '/css/tokens/breakpoints.css',
  '/css/tokens/shadows.css',
  '/css/tokens/animations.css',
  '/css/tokens/borders.css',
  '/css/tokens/z-index.css',
  '/css/tokens/interactive-states.css',
  '/css/breakpoints.css',
  '/css/bibliography.css',
  '/css/critics-corner.css',
  '/css/resources.css',
  '/css/components/site-card.css',
  '/css/components/site-button.css',
  '/css/components/section-stack.css',
  '/css/components/page-sidebar.css',
  '/css/components/entry-list.css',
  '/css/components/provenance-note.css',
  '/css/components/home-hero.css',
  '/css/components/status-banner.css',
  '/css/utilities/spacing.css'
];

// Assets to cache immediately on install (includes STARTUP_ASSETS via spread)
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  ...STARTUP_ASSETS,
  '/styles.css',
  ...IMPORTED_STYLESHEETS,
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

// Install event - precache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Precaching app shell');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
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
        onStore: (cache, request, response) =>
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
      onStore: (cache, request, response) => storeResponse(cache, request, response),
    })
  );
});
