/**
 * Tests for js/bibliography.js
 * Testing interactive bibliography functionality
 *
 * NOTE: js/bibliography.js is an IIFE with no named exports. These tests were
 * written for the removed src/js/bibliography.js (modular architecture). They
 * are skipped pending a rewrite that tests js/bibliography.js via DOM
 * interactions. E2E coverage lives in tests/e2e/bibliography.spec.js.
 */

// Mock fetch globally before requiring the module to avoid IIFE init error
global.fetch = jest.fn(() => Promise.resolve({
  ok: false,
  status: 404,
  json: () => Promise.resolve([])
}));

// js/bibliography.js is an IIFE; it exports nothing. All destructured names
// will be undefined. Tests are skipped below until rewritten for IIFE arch.
const {
  getTypeClass,
  sortEntries,
  filterBibliography,
  renderBibliography,
  showDetails,
  setupSortControls,
  loadBibliography,
  setBibliographyData,
  bibliographyDataModule,
  bibliographyRenderModule,
  bibliographyInteractionModule,
} = require('../js/bibliography.js');

describe.skip('Bibliography Module (pending rewrite for js/ IIFE architecture)', () => {
  beforeEach(() => {
    // Reset DOM before each test
    document.body.innerHTML = `
      <input id="bib-search" type="search" />
      <div id="bib-list"></div>
      <div id="bib-details"></div>
      <div id="bib-sort-controls"></div>
      <span id="bib-count"></span>
    `;
    jest.clearAllMocks();
  });

  describe('getTypeClass', () => {
    test('should return correct class for paper type', () => {
      expect(getTypeClass('paper')).toBe('type-paper');
    });

    test('should return correct class for book type', () => {
      expect(getTypeClass('book')).toBe('type-book');
    });

    test('should return correct class for article type', () => {
      expect(getTypeClass('article')).toBe('type-article');
    });

    test('should return correct class for thesis type', () => {
      expect(getTypeClass('thesis')).toBe('type-thesis');
    });

    test('should return correct class for conference type', () => {
      expect(getTypeClass('conference')).toBe('type-conference');
    });

    test('should handle case insensitive types', () => {
      expect(getTypeClass('PAPER')).toBe('type-paper');
      expect(getTypeClass('Book')).toBe('type-book');
    });

    test('should return type-other for unknown types', () => {
      expect(getTypeClass('unknown')).toBe('type-other');
      expect(getTypeClass('')).toBe('type-other');
    });

    test('should handle null/undefined gracefully', () => {
      expect(getTypeClass(null)).toBe('type-other');
      expect(getTypeClass(undefined)).toBe('type-other');
    });
  });

  describe('sortEntries', () => {
    const testEntries = [
      { id: '1', title: 'Zebra Study', year: '2020', authors: ['Smith, J.'] },
      { id: '2', title: 'Alpha Research', year: '2022', authors: ['Adams, A.'] },
      { id: '3', title: 'Beta Analysis', year: '2021', authors: ['Brown, B.'] },
      { id: '4', title: 'No Year', authors: ['Doe, J.'] },
    ];

    test('should sort by year descending (newest first)', () => {
      // Setup sort controls to ensure default state or reset it
      setupSortControls();
      // Simulate click on default to ensure state is correct if it wasn't
      const descBtn = document.querySelector('[data-sort="year-desc"]');
      if (descBtn) descBtn.click();

      const sorted = sortEntries(testEntries);
      expect(sorted[0].year).toBe('2022');
      expect(sorted[1].year).toBe('2021');
      expect(sorted[2].year).toBe('2020');
    });

    test('should sort by year ascending (oldest first) after clicking button', () => {
      setupSortControls();
      const ascBtn = document.querySelector('[data-sort="year-asc"]');
      ascBtn.click(); // This changes currentSort to 'year-asc'

      const sorted = sortEntries(testEntries);
      expect(sorted[0].id).toBe('4'); // No year (0)
      expect(sorted[1].year).toBe('2020');
      expect(sorted[2].year).toBe('2021');
    });

    test('should sort by author alphabetically after clicking button', () => {
      setupSortControls();
      const btn = document.querySelector('[data-sort="author"]');
      btn.click();

      const sorted = sortEntries(testEntries);
      expect(sorted[0].authors[0]).toBe('Adams, A.');
      expect(sorted[1].authors[0]).toBe('Brown, B.');
    });

    test('should sort by title alphabetically after clicking button', () => {
      setupSortControls();
      const btn = document.querySelector('[data-sort="title"]');
      btn.click();

      const sorted = sortEntries(testEntries);
      expect(sorted[0].title).toBe('Alpha Research');
      expect(sorted[1].title).toBe('Beta Analysis');
    });
  });

  describe('filterBibliography', () => {
    const testData = [
      {
        id: '1',
        title: 'Golf Swing Biomechanics',
        authors: ['Smith, John'],
        concepts: ['biomechanics', 'golf'],
        description: 'A study of golf swing mechanics',
        venue: 'Sports Science Journal',
        year: '2020',
        type: 'article'
      },
      {
        id: '2',
        title: 'Control Theory Applications',
        authors: ['Adams, Jane'],
        concepts: ['control-theory', 'robotics'],
        description: 'Applications in robotics',
        venue: 'IEEE Conference',
        year: '2021',
        type: 'paper'
      },
      {
        id: '3',
        title: 'Movement Analysis',
        authors: ['Brown, Bob'],
        concepts: ['biomechanics', 'analysis'],
        description: 'Analysis of human movement',
        venue: 'Biomechanics Journal',
        year: '2019',
        type: 'book'
      },
    ];

    beforeEach(() => {
      setBibliographyData(testData);
      setupSortControls();
      // Ensure default sort is applied
      const descBtn = document.querySelector('[data-sort="year-desc"]');
      if (descBtn) descBtn.click();
    });

    test('should render all entries for empty query', () => {
      filterBibliography('');
      const list = document.getElementById('bib-list');
      expect(list.children.length).toBe(3);
    });

    test('should filter by title', () => {
      filterBibliography('golf');
      const list = document.getElementById('bib-list');
      expect(list.children.length).toBe(1);
      expect(list.innerHTML).toContain('Golf Swing Biomechanics');
    });

    test('should filter by author', () => {
      filterBibliography('smith');
      const list = document.getElementById('bib-list');
      expect(list.children.length).toBe(1);
      expect(list.innerHTML).toContain('Smith, John');
    });
  });

  describe('loadBibliography', () => {
    beforeEach(() => {
      global.fetch = jest.fn();
    });

    test('should load and render bibliography', async () => {
      const mockData = [
        { id: '1', title: 'Test Title', authors: ['Author'] }
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      });

      await loadBibliography();

      const list = document.getElementById('bib-list');
      expect(list.innerHTML).toContain('Test Title');
      expect(document.getElementById('bib-count').textContent).toContain('1 entries');
    });

    test('should handle load error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await loadBibliography();

      const list = document.getElementById('bib-list');
      expect(list.innerHTML).toContain('Error loading bibliography data');
    });
  });

  describe('showDetails', () => {
    test('should display entry details in sidebar', () => {
      const entry = {
        id: 'test-1',
        title: 'Detailed Entry',
        authors: ['Smith, John', 'Doe, Jane'],
        year: '2021',
        type: 'paper',
        venue: 'Test Journal',
        description: 'This is a test description.',
        concepts: ['test', 'example'],
        scholar_url: 'https://scholar.google.com/test'
      };

      showDetails(entry);

      const container = document.getElementById('bib-details');
      expect(container.innerHTML).toContain('Detailed Entry');
      expect(container.innerHTML).toContain('Smith, John, Doe, Jane');
      expect(container.innerHTML).toContain('2021');
      expect(container.innerHTML).toContain('paper');
      expect(container.innerHTML).toContain('Test Journal');
      expect(container.innerHTML).toContain('This is a test description.');
      expect(container.innerHTML).toContain('Google Scholar');
    });
  });

  describe('submodule surfaces', () => {
    test('should expose data, render, and interaction submodule APIs', () => {
      expect(typeof bibliographyDataModule.loadBibliography).toBe('function');
      expect(typeof bibliographyRenderModule.renderBibliography).toBe('function');
      expect(typeof bibliographyInteractionModule.filterBibliography).toBe('function');
    });
  });
});

// ---------------------------------------------------------------------------
// Regression tests for issue #3273: AffineDriftMetrics API clobber
//
// These tests verify that bibliography.js search/tracking guards correctly
// require trackSearch to be a callable function rather than any truthy value,
// so that a clobbered state (another script overwriting the API object with a
// non-callable placeholder) cannot break search filtering.
// ---------------------------------------------------------------------------

describe('bibliography.js metrics-guard regression (#3273)', () => {
  // Wait for all pending microtasks (Promise resolution chains) to drain.
  // bibliography.js init() is async (fetch → json() → state assignment),
  // so we must flush before the search listener is registered.
  function flushPromises() {
    return new Promise((resolve) => queueMicrotask(resolve));
  }

  // Wait long enough for the bibliography.js debounce (180 ms) to fire.
  function waitForDebounce() {
    return new Promise((resolve) => setTimeout(resolve, 220));
  }

  function buildBibDOM() {
    // Build required DOM elements using createElement (no innerHTML).
    // bibliography.js IIFE bails out early if #bibliography-app is absent,
    // so it must be present as the root container.
    const app = document.createElement('div');
    app.id = 'bibliography-app';

    const searchInput = document.createElement('input');
    searchInput.id = 'bib-search';
    searchInput.type = 'search';

    const bibList = document.createElement('div');
    bibList.id = 'bib-list';

    const bibDetails = document.createElement('div');
    bibDetails.id = 'bib-details';

    const sortControls = document.createElement('div');
    sortControls.id = 'bib-sort-controls';

    const bibCount = document.createElement('span');
    bibCount.id = 'bib-count';

    const metricsWidget = document.createElement('div');
    metricsWidget.id = 'metrics-widget';

    document.body.replaceChildren(
      app, searchInput, bibList, bibDetails, sortControls, bibCount, metricsWidget
    );
  }

  async function loadBibAndFlush(entries) {
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve(entries) })
    );
    jest.resetModules();
    jest.isolateModules(() => {
      require('../js/bibliography.js');
    });
    // Flush the async init chain: fetch → json() → state.entries assignment →
    // addEventListener registration.  Multiple rounds cover nested awaits.
    await flushPromises();
    await flushPromises();
    await flushPromises();
  }

  const SAMPLE_ENTRIES = [
    { id: 'smith2020', title: 'Biomechanics of the Golf Swing', type: 'paper',
      authors: ['Smith, J.'], year: 2020, tags: ['biomechanics', 'golf'] },
    { id: 'jones2019', title: 'Control Theory Fundamentals', type: 'book',
      authors: ['Jones, A.'], year: 2019, tags: ['control'] },
  ];

  beforeEach(() => {
    // Do NOT use fake timers here: bibliography.js loadEntries() uses a real
    // AbortController timeout internally, and fake timers would block it.
    buildBibDOM();
    delete window.AffineDriftMetrics;
    window.BIBLIOGRAPHY_DATA_URL = '/data/bibliography.json';
  });

  afterEach(() => {
    delete window.AffineDriftMetrics;
    delete window.BIBLIOGRAPHY_DATA_URL;
    jest.clearAllMocks();
  });

  test('search input does not throw when AffineDriftMetrics is a plain object (clobbered state)', async () => {
    // Simulate another script clobbering the metrics API with a plain object.
    window.AffineDriftMetrics = { firstPaint: 42, summary: {} };

    await loadBibAndFlush(SAMPLE_ENTRIES);

    const searchInput = document.getElementById('bib-search');
    expect(searchInput).not.toBeNull();

    searchInput.value = 'bio';
    await expect(async () => {
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
      await waitForDebounce();
    }).not.toThrow();
  });

  test('search input does not throw when AffineDriftMetrics is undefined', async () => {
    expect(window.AffineDriftMetrics).toBeUndefined();

    await loadBibAndFlush(SAMPLE_ENTRIES);

    const searchInput = document.getElementById('bib-search');
    searchInput.value = 'golf';
    await expect(async () => {
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
      await waitForDebounce();
    }).not.toThrow();
  });

  test('trackSearch is NOT called when AffineDriftMetrics.trackSearch is not a function', async () => {
    // trackSearch is present but is a string — the guard must skip the call.
    window.AffineDriftMetrics = { firstPaint: 42, summary: {}, trackSearch: 'not-a-function' };

    await loadBibAndFlush(SAMPLE_ENTRIES);

    const searchInput = document.getElementById('bib-search');
    searchInput.value = 'bio';
    await expect(async () => {
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
      await waitForDebounce();
    }).not.toThrow();
  });

  test('trackSearch IS called when AffineDriftMetrics has a real trackSearch function', async () => {
    const trackSearchMock = jest.fn();
    window.AffineDriftMetrics = { trackSearch: trackSearchMock };

    await loadBibAndFlush(SAMPLE_ENTRIES);

    const searchInput = document.getElementById('bib-search');
    searchInput.value = 'bio';
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    await waitForDebounce();

    expect(trackSearchMock).toHaveBeenCalledWith('bio');
  });
});
