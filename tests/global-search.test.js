/**
 * Tests for src/js/global-search.js
 * Testing global search functionality
 */

// Mock Fuse before importing the module
global.Fuse = require('fuse.js');
// Mock fetch globally
global.fetch = jest.fn();

const {
  search,
  loadIndex,
  openModal,
  closeModal,
  setIndex,
  setFuse,
  resetState
} = require('../src/js/global-search.js');

describe('Global Search Module', () => {
  const mockIndex = {
    entries: [
      {
        title: 'Article One',
        description: 'Description for article one',
        headings: ['Heading 1'],
        concepts: ['concept1'],
        body: 'Body text for article one',
        type: 'article',
        url: '/article-one.html'
      },
      {
        title: 'Model Two',
        description: 'Description for model two',
        headings: ['Heading 2'],
        concepts: ['concept2'],
        body: 'Body text for model two',
        type: 'model',
        url: '/model-two.html'
      }
    ]
  };

  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
    global.fetch = jest.fn();

    // Reset internal state
    if (resetState) {
        resetState();
    } else {
        setIndex(null);
        setFuse(null);
    }
  });

  describe('loadIndex', () => {
    test('should load search index and initialize Fuse', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockIndex
      });

      const success = await loadIndex();
      expect(success).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith('/data/search_index.json');
    });

    test('should handle load error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const success = await loadIndex();
      expect(success).toBe(false);
    });
  });

  describe('search', () => {
    beforeEach(async () => {
      // Setup fuse instance manually or via loadIndex
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockIndex
      });
      await loadIndex();
    });

    test('should return results for matching query', () => {
      const results = search('Article');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toBe('Article One');
    });

    test('should return empty array for short query', () => {
      const results = search('a');
      expect(results).toEqual([]);
    });

    test('should filter by type', () => {
      const results = search('Two', { type: 'model' });
      expect(results.length).toBe(1);
      expect(results[0].type).toBe('model');
    });

    test('should limit results', () => {
      // Assuming we had more data, but let's just check it doesn't crash
      const results = search('One', { limit: 1 });
      expect(results.length).toBeLessThanOrEqual(1);
    });
  });

  describe('Modal Interaction', () => {
    beforeEach(() => {
        // Mock loadIndex success
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => mockIndex
        });
    });

    test('openModal should create modal and load index', async () => {
      await openModal();

      const modal = document.getElementById('global-search-modal');
      expect(modal).toBeTruthy();
      expect(modal.classList.contains('active')).toBe(true);
    });

    test('closeModal should hide modal', async () => {
      await openModal();
      closeModal();

      const modal = document.getElementById('global-search-modal');
      expect(modal.classList.contains('active')).toBe(false);
    });

    test('Modal should contain search input and filters', async () => {
        await openModal();
        const modal = document.getElementById('global-search-modal');
        expect(modal.querySelector('#global-search-input')).toBeTruthy();
        expect(modal.querySelectorAll('.filter-btn').length).toBeGreaterThan(0);
    });

    test('should trigger search on input', async () => {
        jest.useFakeTimers();
        await openModal();
        const input = document.getElementById('global-search-input');

        // Mock fuse search result
        // We mocked Fuse constructor, but search is internal using the instance.
        // If we want to verify renderResults is called, we can inspect DOM.

        // Trigger input
        input.value = 'Article';
        input.dispatchEvent(new Event('input'));

        // Fast forward debounce
        jest.runAllTimers();

        const resultsContainer = document.getElementById('global-search-results');
        expect(resultsContainer.innerHTML).toContain('Article One');

        jest.useRealTimers();
    });

    test('should filter results on button click', async () => {
        jest.useFakeTimers();
        await openModal();
        const input = document.getElementById('global-search-input');
        input.value = 'Two';
        input.dispatchEvent(new Event('input'));
        jest.runAllTimers();

        const modelBtn = document.querySelector('.filter-btn[data-type="model"]');
        modelBtn.click();

        const resultsContainer = document.getElementById('global-search-results');
        expect(resultsContainer.innerHTML).toContain('Model Two');
        expect(resultsContainer.innerHTML).not.toContain('Article One');

        jest.useRealTimers();
    });
  });
});
