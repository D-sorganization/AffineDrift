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
    trimCacheEntries,
    broadcastUpdate,
  };
});
