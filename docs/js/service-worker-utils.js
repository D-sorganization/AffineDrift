;(function (root, factory) {
  const api = factory();
  root.AffineDriftServiceWorkerUtils = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof self !== 'undefined' ? self : globalThis, function () {
  const UPDATE_MESSAGE_TYPE = 'affinedrift:sw-update-available';
  const MAX_CACHE_ENTRIES = 100;

  async function trimCacheEntries(cache, maxEntries = MAX_CACHE_ENTRIES) {
    const keys = await cache.keys();
    if (keys.length <= maxEntries) {
      return 0;
    }

    const excess = keys.length - maxEntries;
    const removals = keys.slice(0, excess).map((request) => cache.delete(request));
    const results = await Promise.all(removals);
    return results.filter(Boolean).length;
  }

  const DEFAULT_NAVIGATION_TIMEOUT_MS = 3000;

  // Network-first strategy for HTML navigations: try the network (bounded by a
  // timeout) so returning visitors always see the latest deploy; fall back to the
  // cached copy, then the offline page. `deps` is injected so the function is
  // unit-testable with mocked fetch/caches in Jest.
  async function networkFirstWithTimeout(request, options = {}) {
    const {
      cacheName,
      offlineUrl,
      timeoutMs = DEFAULT_NAVIGATION_TIMEOUT_MS,
      fetchImpl = fetch,
      cachesImpl = (typeof caches !== 'undefined' ? caches : undefined),
      onStore,
    } = options;

    const fromCache = async () => {
      if (!cachesImpl) return undefined;
      const cached = await cachesImpl.match(request);
      if (cached) return cached;
      if (offlineUrl) {
        const offline = await cachesImpl.match(offlineUrl);
        if (offline) return offline;
      }
      return undefined;
    };

    let timeoutId;
    const timeout = new Promise((_resolve, reject) => {
      timeoutId = setTimeout(() => reject(new Error('network-timeout')), timeoutMs);
    });

    try {
      const response = await Promise.race([fetchImpl(request), timeout]);
      if (response && response.status === 200) {
        if (cachesImpl && cacheName) {
          const cache = await cachesImpl.open(cacheName);
          if (typeof onStore === 'function') {
            await onStore(cache, request, response);
          } else {
            await cache.put(request, response.clone());
          }
        }
        return response;
      }
      // Non-200 (e.g. 404/500): prefer a usable cached copy if we have one.
      const fallback = await fromCache();
      return fallback || response;
    } catch (_err) {
      return fromCache();
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // Cache-first strategy for content-hashed static subresources (CSS/JS/images).
  async function cacheFirst(request, options = {}) {
    const {
      cacheName,
      fetchImpl = fetch,
      cachesImpl = (typeof caches !== 'undefined' ? caches : undefined),
      onStore,
    } = options;

    if (cachesImpl) {
      const cached = await cachesImpl.match(request);
      if (cached) return cached;
    }

    const response = await fetchImpl(request);
    if (
      response &&
      response.status === 200 &&
      response.type === 'basic' &&
      cachesImpl &&
      cacheName
    ) {
      const cache = await cachesImpl.open(cacheName);
      if (typeof onStore === 'function') {
        await onStore(cache, request, response);
      } else {
        await cache.put(request, response.clone());
      }
    }
    return response;
  }

  async function broadcastUpdate(clients, payload) {
    const clientList = await clients.matchAll({
      type: 'window',
      includeUncontrolled: true,
    });

    await Promise.all(
      clientList.map((client) => client.postMessage(payload))
    );

    return clientList.length;
  }

  return {
    UPDATE_MESSAGE_TYPE,
    MAX_CACHE_ENTRIES,
    DEFAULT_NAVIGATION_TIMEOUT_MS,
    trimCacheEntries,
    broadcastUpdate,
    networkFirstWithTimeout,
    cacheFirst,
  };
});
