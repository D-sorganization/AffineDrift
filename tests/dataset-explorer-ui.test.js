/** DOM wiring for the Fixture and Dataset Explorer (#4541). dataset-explorer.js
 * is loaded as a real (unmocked) engine; only fetch and object-URL creation
 * are stubbed, since jsdom has no network or blob-URL registry.
 */
const { sha256Hex, utf8Encode } = require('../js/dataset-explorer');

const SIMPLE_SCHEMA = {
  type: 'object',
  required: ['schema_version'],
  properties: { schema_version: { const: 'demo/v1' } },
};
const VALID_FIXTURE = { schema_version: 'demo/v1', value: 42 };
const UNSCHEMAED_FIXTURE = { schema_version: 'demo-unschemaed/v1', note: 'no schema published' };

function jsonResponse(payload) {
  const bytes = utf8Encode(JSON.stringify(payload));
  return {
    ok: true,
    status: 200,
    arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
  };
}

function manifestFixture() {
  return {
    schema_version: 'affinedrift.dataset-explorer-manifest/v1',
    families: [
      {
        family_id: 'with_schema',
        label: 'Family With Schema',
        schema_path: 'data/with_schema/x.schema.json',
        fixtures: [{ path: 'data/with_schema/record.json', schema_version: 'demo/v1' }],
      },
      {
        family_id: 'without_schema',
        label: 'Family Without Schema',
        schema_path: null,
        fixtures: [
          { path: 'data/without_schema/record.json', schema_version: 'demo-unschemaed/v1' },
        ],
      },
    ],
  };
}

function installFetchMock() {
  global.fetch = jest.fn(async (url) => {
    if (url.endsWith('dataset_explorer_manifest.json')) return jsonResponse(manifestFixture());
    if (url.endsWith('with_schema/x.schema.json')) return jsonResponse(SIMPLE_SCHEMA);
    if (url.endsWith('with_schema/record.json')) return jsonResponse(VALID_FIXTURE);
    if (url.endsWith('without_schema/record.json')) return jsonResponse(UNSCHEMAED_FIXTURE);
    throw new Error(`unexpected fetch: ${url}`);
  });
}

let ui;

beforeEach(() => {
  jest.resetModules();
  document.body.innerHTML =
    '<div id="dataset-explorer-app"></div><p id="dataset-explorer-status"></p>';
  window.DatasetExplorer = require('../js/dataset-explorer');
  global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
  installFetchMock();
  ui = require('../js/dataset-explorer-ui');
});

afterEach(() => {
  delete global.fetch;
  jest.restoreAllMocks();
});

test('renders one section per manifest family', async () => {
  await ui.init();
  const headings = [...document.querySelectorAll('.de-family h2')].map((h) => h.textContent);
  expect(headings).toEqual(['Family With Schema', 'Family Without Schema']);
});

test('a fixture with a published schema that validates shows a Valid badge', async () => {
  await ui.init();
  const badge = document.querySelector('.de-family:nth-of-type(1) .de-badge');
  expect(badge.textContent).toBe('Valid');
  expect(badge.className).toContain('de-badge--valid');
});

test('a fixture with no published schema never claims validation and says so', async () => {
  await ui.init();
  const badge = document.querySelector('.de-family:nth-of-type(2) .de-badge');
  expect(badge.textContent).toBe('Schema unavailable');
  const status = document.querySelector('.de-family:nth-of-type(2) p');
  expect(status.textContent).toMatch(/no published schema/i);
});

test('the download control exposes the exact sha-256 of the fetched bytes', async () => {
  await ui.init();
  const expected = sha256Hex(utf8Encode(JSON.stringify(VALID_FIXTURE)));
  const hashEl = document.querySelector('.de-family:nth-of-type(1) .de-download__hash');
  expect(hashEl.textContent).toBe(`sha256:${expected}`);
  const link = document.querySelector('.de-family:nth-of-type(1) .de-download__button');
  expect(link.href).toBe('blob:mock-url');
  expect(link.download).toBe('record.json');
});

test('renders an accessible table with a caption and column headers', async () => {
  await ui.init();
  const table = document.querySelector('.de-family:nth-of-type(1) table.de-table');
  expect(table.querySelector('caption').textContent).toMatch(/record\.json/);
  expect([...table.querySelectorAll('thead th')].map((th) => th.textContent)).toEqual([
    'Field',
    'Value',
  ]);
  const bodyRows = table.querySelectorAll('tbody tr');
  expect(bodyRows.length).toBeGreaterThan(0);
  expect(table.querySelector('tbody th').getAttribute('scope')).toBe('row');
});

test('wraps each table in the site scroll region, as js/forms.js does for static tables', async () => {
  await ui.init();
  const table = document.querySelector('.de-family:nth-of-type(1) table.de-table');
  const wrapper = table.parentElement;
  expect(wrapper.classList.contains('table-wrapper')).toBe(true);
  expect(wrapper.getAttribute('role')).toBe('region');
  expect(wrapper.getAttribute('tabindex')).toBe('0');
  expect(wrapper.getAttribute('aria-label')).toMatch(/record\.json/);
});

test('a failed manifest fetch reports the problem instead of rendering nothing silently', async () => {
  global.fetch = jest.fn(async () => ({ ok: false, status: 500 }));
  await ui.init();
  expect(document.getElementById('dataset-explorer-status').textContent).toMatch(
    /could not load/i,
  );
});
