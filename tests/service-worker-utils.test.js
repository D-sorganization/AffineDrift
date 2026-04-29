const {
  MAX_CACHE_ENTRIES,
  UPDATE_MESSAGE_TYPE,
  trimCacheEntries,
  broadcastUpdate,
} = require('../js/service-worker-utils.js');

describe('service-worker-utils', () => {
  test('exports the shared update message type', () => {
    expect(UPDATE_MESSAGE_TYPE).toBe('affinedrift:sw-update-available');
  });

  test('trims the oldest cache entries beyond the maximum', async () => {
    const keys = Array.from({ length: MAX_CACHE_ENTRIES + 3 }, (_, index) => ({
      url: `https://example.com/asset-${index}`,
    }));
    const deleted = [];
    const cache = {
      keys: jest.fn().mockResolvedValue(keys),
      delete: jest.fn().mockImplementation(async (request) => {
        deleted.push(request.url);
        return true;
      }),
    };

    const removed = await trimCacheEntries(cache, MAX_CACHE_ENTRIES);

    expect(removed).toBe(3);
    expect(cache.delete).toHaveBeenCalledTimes(3);
    expect(deleted).toEqual([
      'https://example.com/asset-0',
      'https://example.com/asset-1',
      'https://example.com/asset-2',
    ]);
  });

  test('broadcasts an update message to all window clients', async () => {
    const postMessage = jest.fn();
    const clients = {
      matchAll: jest.fn().mockResolvedValue([
        { postMessage },
        { postMessage: jest.fn() },
      ]),
    };

    const clientCount = await broadcastUpdate(clients, {
      type: UPDATE_MESSAGE_TYPE,
      url: 'https://example.com',
    });

    expect(clientCount).toBe(2);
    expect(clients.matchAll).toHaveBeenCalledWith({
      type: 'window',
      includeUncontrolled: true,
    });
    expect(postMessage).toHaveBeenCalledWith({
      type: UPDATE_MESSAGE_TYPE,
      url: 'https://example.com',
    });
  });
});
