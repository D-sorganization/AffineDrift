// AffineDrift Service Worker for offline support
// Version 3: Updated 2026-03-13 (batch fixes for content accuracy, CSS, PWA manifest)
// TODO #1459: Replace hardcoded version with content-hash cache busting via build pipeline
const CACHE_NAME = 'affinedrift-v4-1a0bcd4a';
const OFFLINE_URL = '/offline.html';

// Critical startup assets - loaded first for fast splash screen
// NOTE: These are spread into PRECACHE_ASSETS below for unified caching,
// but kept as a separate array for clarity and potential future prioritization
const STARTUP_ASSETS = [
  '/css/startup-launcher.css',
  '/js/startup-launcher.js',
  '/logo/logo_transparent_1.png'
];

// Assets to cache immediately on install (includes STARTUP_ASSETS via spread)
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  ...STARTUP_ASSETS,
  '/styles.css',
  '/script.js',
  '/favicon.ico',
  '/manifest.json',
  OFFLINE_URL
];

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
          return caches.open(CACHE_NAME).then((cache) => {
            return cache.put(event.request, response.clone());
          });
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
            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseClone);
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
