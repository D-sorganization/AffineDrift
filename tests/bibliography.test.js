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
      <input id="bib-search" type="text" />
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
