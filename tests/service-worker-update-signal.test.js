/**
 * Service-worker update signal and data freshness (issue #5315).
 *
 * The "New content is available" banner must only appear when a cached copy
 * the visitor saw was replaced by different bytes, and JSON/CSV data must be
 * network-first so it is never served stale while online.
 */

const fs = require('fs');
const path = require('path');
const { routeFor, responseChanged } = require('../js/service-worker-utils.js');

const ORIGIN = 'https://affinedrift.com';

const request = (url, { method = 'GET', mode = 'cors' } = {}) => ({ url, method, mode });

describe('routeFor', () => {
  test('skips non-GET and cross-origin requests', () => {
    expect(routeFor(request(`${ORIGIN}/x`, { method: 'POST' }), ORIGIN)).toBe('skip');
    expect(routeFor(request('https://cdn.example.com/a.js'), ORIGIN)).toBe('skip');
  });

  test('routes HTML navigations network-first', () => {
    expect(routeFor(request(`${ORIGIN}/articles/a.html`, { mode: 'navigate' }), ORIGIN)).toBe('navigate');
  });

  test.each(['/search.json', '/listings.json', '/data/bibliography.json', '/data/x.csv', '/data/x.json?v=2'])(
    'routes data file %s network-first',
    (p) => {
      expect(routeFor(request(`${ORIGIN}${p}`), ORIGIN)).toBe('data');
    },
  );

  test('keeps the web manifest and content-hashed assets cache-first', () => {
    for (const p of ['/manifest.json', '/styles.css', '/js/main.js', '/logo/logo-navbar.png']) {
      expect(routeFor(request(`${ORIGIN}${p}`), ORIGIN)).toBe('static');
    }
  });
});

describe('responseChanged', () => {
  // Minimal Response stand-in (jsdom has no fetch Response): case-insensitive
  // headers, single-use body, clone().
  const res = (body, headers = {}) => {
    const lower = Object.fromEntries(Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v]));
    let used = false;
    const read = () => {
      if (used) throw new TypeError('body already used');
      used = true;
      return Buffer.from(body);
    };
    return {
      status: 200,
      headers: { get: (name) => lower[name.toLowerCase()] ?? null },
      clone: () => res(body, headers),
      arrayBuffer: async () => {
        const b = read();
        return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
      },
      text: async () => read().toString(),
    };
  };

  test('is false without a cached copy (first fetch is not an update)', async () => {
    expect(await responseChanged(undefined, res('a'))).toBe(false);
  });

  test('compares ETags when both responses carry one', async () => {
    expect(await responseChanged(res('a', { ETag: '"1"' }), res('b', { ETag: '"1"' }))).toBe(false);
    expect(await responseChanged(res('a', { ETag: '"1"' }), res('a', { ETag: '"2"' }))).toBe(true);
  });

  test('falls back to Last-Modified', async () => {
    const t1 = 'Mon, 02 Nov 2026 08:00:00 GMT';
    const t2 = 'Mon, 02 Nov 2026 09:00:00 GMT';
    expect(await responseChanged(res('a', { 'Last-Modified': t1 }), res('b', { 'Last-Modified': t1 }))).toBe(false);
    expect(await responseChanged(res('a', { 'Last-Modified': t1 }), res('a', { 'Last-Modified': t2 }))).toBe(true);
  });

  test('falls back to comparing bodies, without consuming the originals', async () => {
    const cached = res('same');
    const fresh = res('same');
    expect(await responseChanged(cached, fresh)).toBe(false);
    expect(await fresh.text()).toBe('same');
    expect(await responseChanged(res('old'), res('new'))).toBe(true);
  });
});

describe('service-worker.js wiring', () => {
  const sw = fs.readFileSync(path.join(__dirname, '..', 'service-worker.js'), 'utf8');

  test('routes requests through routeFor and gates the banner on responseChanged', () => {
    expect(sw).toMatch(/routeFor\(event\.request, self\.location\.origin\)/);
    expect(sw).toMatch(/responseChanged\(/);
  });

  test('a fresh network navigation never broadcasts an update', () => {
    expect(sw).not.toMatch(/storeResponse\(cache, request, response, true\)/);
  });
});

describe('update notice on phones', () => {
  const css = fs.readFileSync(
    path.join(__dirname, '..', 'css', 'components', 'update-notice.css'),
    'utf8'
  );
  const phone = css.slice(css.indexOf('@media (width < 480px)'));

  test('stays one compact row instead of stacking full-width buttons', () => {
    expect(phone).not.toMatch(/flex-direction:\s*column/);
    expect(phone).not.toMatch(/width:\s*100%/);
  });

  test('keeps 44px touch targets', () => {
    expect(css).toMatch(/\.site-update-notice__button\s*\{[^}]*min-height:\s*2\.75rem/);
  });
});
