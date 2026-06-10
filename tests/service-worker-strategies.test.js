const {
  networkFirstWithTimeout,
  cacheFirst,
} = require('../js/service-worker-utils.js');

function mockResponse(body, { status = 200, type = 'basic' } = {}) {
  return {
    status,
    type,
    body,
    clone() {
      return mockResponse(body, { status, type });
    },
  };
}

function makeCaches(stored = {}) {
  const putCalls = [];
  const cache = {
    put: jest.fn(async (request, response) => {
      putCalls.push({ request, response });
    }),
  };
  return {
    putCalls,
    cache,
    impl: {
      match: jest.fn(async (key) => {
        const url = typeof key === 'string' ? key : key.url;
        return stored[url];
      }),
      open: jest.fn(async () => cache),
    },
  };
}

describe('networkFirstWithTimeout (HTML navigations)', () => {
  test('returns the fresh network response when the network is fast', async () => {
    const fresh = mockResponse('fresh');
    const { impl, cache } = makeCaches({ '/article': mockResponse('stale') });
    const fetchImpl = jest.fn().mockResolvedValue(fresh);

    const result = await networkFirstWithTimeout('/article', {
      cacheName: 'v1',
      offlineUrl: '/offline.html',
      timeoutMs: 50,
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('fresh');
    // Fresh response is written back into the cache.
    expect(cache.put).toHaveBeenCalledTimes(1);
  });

  test('falls back to the cached copy when the network rejects', async () => {
    const { impl } = makeCaches({ '/article': mockResponse('cached') });
    const fetchImpl = jest.fn().mockRejectedValue(new Error('offline'));

    const result = await networkFirstWithTimeout('/article', {
      cacheName: 'v1',
      offlineUrl: '/offline.html',
      timeoutMs: 50,
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('cached');
  });

  test('falls back to the cached copy when the network times out', async () => {
    const { impl } = makeCaches({ '/article': mockResponse('cached') });
    // fetch never resolves before the timeout fires.
    const fetchImpl = jest.fn(() => new Promise(() => {}));

    const result = await networkFirstWithTimeout('/article', {
      cacheName: 'v1',
      offlineUrl: '/offline.html',
      timeoutMs: 10,
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('cached');
  });

  test('returns offline.html when both network and page cache miss', async () => {
    const { impl } = makeCaches({ '/offline.html': mockResponse('offline') });
    const fetchImpl = jest.fn().mockRejectedValue(new Error('offline'));

    const result = await networkFirstWithTimeout('/unseen', {
      cacheName: 'v1',
      offlineUrl: '/offline.html',
      timeoutMs: 10,
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('offline');
  });
});

describe('cacheFirst (static subresources)', () => {
  test('returns the cached copy without hitting the network', async () => {
    const { impl } = makeCaches({ '/styles.css': mockResponse('cached-css') });
    const fetchImpl = jest.fn();

    const result = await cacheFirst('/styles.css', {
      cacheName: 'v1',
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('cached-css');
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  test('fetches and caches on a cache miss', async () => {
    const { impl, cache } = makeCaches({});
    const fetchImpl = jest.fn().mockResolvedValue(mockResponse('net-css'));

    const result = await cacheFirst('/styles.css', {
      cacheName: 'v1',
      fetchImpl,
      cachesImpl: impl,
    });

    expect(result.body).toBe('net-css');
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(cache.put).toHaveBeenCalledTimes(1);
  });

  test('does not cache non-basic (cross-origin/opaque) responses', async () => {
    const { impl, cache } = makeCaches({});
    const fetchImpl = jest
      .fn()
      .mockResolvedValue(mockResponse('opaque', { type: 'opaque' }));

    await cacheFirst('/cdn/font.woff2', {
      cacheName: 'v1',
      fetchImpl,
      cachesImpl: impl,
    });

    expect(cache.put).not.toHaveBeenCalled();
  });
});
