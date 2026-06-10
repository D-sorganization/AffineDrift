// AffineDrift Service Worker for offline support
// Version 5: Updated 2026-04-11 (drop legacy script.js runtime path)
// TODO #1459: Replace hardcoded version with content-hash cache busting via build pipeline
importScripts('/js/service-worker-utils.js');

const {
  MAX_CACHE_ENTRIES,
  UPDATE_MESSAGE_TYPE,
  broadcastUpdate,
  trimCacheEntries,
} = self.AffineDriftServiceWorkerUtils;
const CACHE_NAME = 'affinedrift-v4-27f68dec';
const OFFLINE_URL = '/offline.html';

// Critical startup assets - loaded first for fast splash screen
// NOTE: These are spread into PRECACHE_ASSETS below for unified caching,
// but kept as a separate array for clarity and potential future prioritization
const STARTUP_ASSETS = [
  '/css/startup-launcher.css',
  '/js/startup-launcher.js',
  '/logo/logo_transparent_1.png'
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

  // Background cache update promise - runs outside respondWith to avoid race conditions
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
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        // No cache - fetch from network
        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Cache successful responses
            caches.open(CACHE_NAME).then((cache) => {
              storeResponse(cache, event.request, response);
            });

            return response;
          })
          .catch(() => {
            // Network failed and no cache - return offline page for navigation
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});
