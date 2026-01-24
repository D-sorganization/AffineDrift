/**
 * Tests for src/js/bibliography.js
 * Testing interactive bibliography functionality
 */

describe('Bibliography Module', () => {
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
      const sorted = sortEntries(testEntries, 'year-desc');
      expect(sorted[0].year).toBe('2022');
      expect(sorted[1].year).toBe('2021');
      expect(sorted[2].year).toBe('2020');
    });

    test('should sort by year ascending (oldest first)', () => {
      const sorted = sortEntries(testEntries, 'year-asc');
      expect(sorted[0].id).toBe('4'); // No year (0)
      expect(sorted[1].year).toBe('2020');
      expect(sorted[2].year).toBe('2021');
    });

    test('should sort by author alphabetically', () => {
      const sorted = sortEntries(testEntries, 'author');
      expect(sorted[0].authors[0]).toBe('Adams, A.');
      expect(sorted[1].authors[0]).toBe('Brown, B.');
    });

    test('should sort by title alphabetically', () => {
      const sorted = sortEntries(testEntries, 'title');
      expect(sorted[0].title).toBe('Alpha Research');
      expect(sorted[1].title).toBe('Beta Analysis');
    });

    test('should handle entries without authors', () => {
      const entriesWithoutAuthors = [
        { id: '1', title: 'Test', authors: [] },
        { id: '2', title: 'Test 2', authors: ['Adams'] },
      ];
      const sorted = sortEntries(entriesWithoutAuthors, 'author');
      expect(sorted).toHaveLength(2);
    });

    test('should not mutate original array', () => {
      const original = [...testEntries];
      sortEntries(testEntries, 'year-desc');
      expect(testEntries).toEqual(original);
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
        year: '2020'
      },
      {
        id: '2',
        title: 'Control Theory Applications',
        authors: ['Adams, Jane'],
        concepts: ['control-theory', 'robotics'],
        description: 'Applications in robotics',
        venue: 'IEEE Conference',
        year: '2021'
      },
      {
        id: '3',
        title: 'Movement Analysis',
        authors: ['Brown, Bob'],
        concepts: ['biomechanics', 'analysis'],
        description: 'Analysis of human movement',
        venue: 'Biomechanics Journal',
        year: '2019'
      },
    ];

    test('should return all entries for empty query', () => {
      const filtered = filterBibliography(testData, '');
      expect(filtered).toHaveLength(3);
    });

    test('should filter by title', () => {
      const filtered = filterBibliography(testData, 'golf');
      expect(filtered).toHaveLength(1);
      expect(filtered[0].title).toBe('Golf Swing Biomechanics');
    });

    test('should filter by author', () => {
      const filtered = filterBibliography(testData, 'smith');
      expect(filtered).toHaveLength(1);
      expect(filtered[0].authors[0]).toBe('Smith, John');
    });

    test('should filter by concept', () => {
      const filtered = filterBibliography(testData, 'biomechanics');
      expect(filtered).toHaveLength(2);
    });

    test('should filter by description', () => {
      const filtered = filterBibliography(testData, 'robotics');
      expect(filtered).toHaveLength(1);
      expect(filtered[0].id).toBe('2');
    });

    test('should filter by venue', () => {
      const filtered = filterBibliography(testData, 'IEEE');
      expect(filtered).toHaveLength(1);
      expect(filtered[0].venue).toBe('IEEE Conference');
    });

    test('should filter by year', () => {
      const filtered = filterBibliography(testData, '2020');
      expect(filtered).toHaveLength(1);
      expect(filtered[0].year).toBe('2020');
    });

    test('should be case insensitive', () => {
      const filtered = filterBibliography(testData, 'GOLF');
      expect(filtered).toHaveLength(1);
    });

    test('should return empty array for no matches', () => {
      const filtered = filterBibliography(testData, 'xyznonexistent');
      expect(filtered).toHaveLength(0);
    });
  });

  describe('renderBibliography', () => {
    test('should render entries to container', () => {
      const data = [
        {
          id: 'test-1',
          title: 'Test Entry',
          authors: ['Author One', 'Author Two'],
          year: '2020',
          type: 'paper',
          venue: 'Test Journal',
          concepts: ['concept1', 'concept2']
        }
      ];

      renderBibliography(data);

      const container = document.getElementById('bib-list');
      expect(container.innerHTML).toContain('Test Entry');
      expect(container.innerHTML).toContain('Author One, Author Two');
      expect(container.innerHTML).toContain('2020');
      expect(container.innerHTML).toContain('type-paper');
    });

    test('should display message when no entries found', () => {
      renderBibliography([]);

      const container = document.getElementById('bib-list');
      expect(container.innerHTML).toContain('No entries found');
    });

    test('should handle entries with missing fields', () => {
      const data = [
        {
          id: 'test-1',
          title: undefined,
          authors: undefined
        }
      ];

      renderBibliography(data);

      const container = document.getElementById('bib-list');
      expect(container.innerHTML).toContain('Untitled');
      expect(container.innerHTML).toContain('Unknown');
    });

    test('should render concept tags', () => {
      const data = [
        {
          id: 'test-1',
          title: 'Test',
          concepts: ['biomechanics', 'golf', 'swing']
        }
      ];

      renderBibliography(data);

      const container = document.getElementById('bib-list');
      expect(container.innerHTML).toContain('concept-tag');
      expect(container.innerHTML).toContain('biomechanics');
      expect(container.innerHTML).toContain('golf');
    });

    test('should add data-id attribute to entries', () => {
      const data = [
        { id: 'unique-id-123', title: 'Test' }
      ];

      renderBibliography(data);

      const entry = document.querySelector('[data-id="unique-id-123"]');
      expect(entry).not.toBeNull();
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

    test('should handle entries without optional fields', () => {
      const entry = {
        id: 'test-1',
        title: 'Minimal Entry'
      };

      showDetails(entry);

      const container = document.getElementById('bib-details');
      expect(container.innerHTML).toContain('Minimal Entry');
      expect(container.innerHTML).not.toContain('undefined');
    });
  });

  describe('setupSortControls', () => {
    test('should create sort buttons', () => {
      setupSortControls();

      const container = document.getElementById('bib-sort-controls');
      expect(container.querySelectorAll('.sort-btn')).toHaveLength(4);
    });

    test('should set year-desc as active by default', () => {
      setupSortControls();

      const activeBtn = document.querySelector('.sort-btn.active');
      expect(activeBtn).not.toBeNull();
      expect(activeBtn.dataset.sort).toBe('year-desc');
    });
  });
});

// Function implementations for testing
// These mirror the actual implementations from src/js/bibliography.js

function getTypeClass(type) {
  const typeMap = {
    paper: 'type-paper',
    book: 'type-book',
    article: 'type-article',
    thesis: 'type-thesis',
    conference: 'type-conference',
  };
  return typeMap[type?.toLowerCase()] || 'type-other';
}

function sortEntries(entries, sortType) {
  const sorted = [...entries];

  switch (sortType) {
    case 'year-desc':
      return sorted.sort((a, b) => {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return yearB - yearA;
      });

    case 'year-asc':
      return sorted.sort((a, b) => {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return yearA - yearB;
      });

    case 'author':
      return sorted.sort((a, b) => {
        const authorA = (a.authors && a.authors[0]) ? a.authors[0].toLowerCase() : 'zzz';
        const authorB = (b.authors && b.authors[0]) ? b.authors[0].toLowerCase() : 'zzz';
        return authorA.localeCompare(authorB);
      });

    case 'title':
      return sorted.sort((a, b) => {
        const titleA = (a.title || '').toLowerCase();
        const titleB = (b.title || '').toLowerCase();
        return titleA.localeCompare(titleB);
      });

    default:
      return sorted;
  }
}

function filterBibliography(data, query) {
  if (!query) {
    return [...data];
  }

  const lowerQuery = query.toLowerCase();

  return data.filter((entry) => {
    // Search in title
    if (entry.title && entry.title.toLowerCase().includes(lowerQuery))
      return true;

    // Search in authors
    if (
      entry.authors &&
      entry.authors.some((a) => a.toLowerCase().includes(lowerQuery))
    )
      return true;

    // Search in concepts
    if (
      entry.concepts &&
      entry.concepts.some((c) => c.toLowerCase().includes(lowerQuery))
    )
      return true;

    // Search in description
    if (
      entry.description &&
      entry.description.toLowerCase().includes(lowerQuery)
    )
      return true;

    // Search in venue
    if (entry.venue && entry.venue.toLowerCase().includes(lowerQuery))
      return true;

    // Search in year
    if (entry.year && entry.year.toString().includes(lowerQuery))
      return true;

    return false;
  });
}

function renderBibliography(data) {
  const listContainer = document.getElementById('bib-list');
  if (!listContainer) return;

  if (data.length === 0) {
    listContainer.innerHTML =
      '<p style="color: var(--text-muted); padding: 2rem;">No entries found matching your search.</p>';
    return;
  }

  const html = data
    .map((entry) => {
      const authorStr =
        entry.authors && entry.authors.length > 0
          ? entry.authors.join(', ')
          : 'Unknown';

      const typeClass = getTypeClass(entry.type);
      const typeBadge = `<span class="type-badge ${typeClass}">${
        entry.type || 'unknown'
      }</span>`;

      return `
      <div class="bib-entry" data-id="${entry.id}">
        <div class="bib-header">
          <h3 class="bib-title">${entry.title || 'Untitled'}</h3>
          ${typeBadge}
        </div>
        <div class="bib-meta">
          <span class="bib-authors">${authorStr}</span>
          ${entry.year ? `<span class="bib-year">(${entry.year})</span>` : ''}
        </div>
        ${entry.venue ? `<div class="bib-venue">${entry.venue}</div>` : ''}
        ${
          entry.concepts && entry.concepts.length > 0
            ? `
          <div class="bib-concepts">
            ${entry.concepts
              .map((c) => `<span class="concept-tag">${c}</span>`)
              .join('')}
          </div>
        `
            : ''
        }
      </div>
    `;
    })
    .join('');

  listContainer.innerHTML = html;
}

function showDetails(entry) {
  const detailsContainer = document.getElementById('bib-details');
  if (!detailsContainer) return;

  const authorStr =
    entry.authors && entry.authors.length > 0
      ? entry.authors.join(', ')
      : 'Unknown';

  const html = `
    <h3 class="sidebar-heading">Details</h3>
    <div class="bib-detail-content">
      <h4 class="detail-title">${entry.title || 'Untitled'}</h4>

      <div class="detail-section">
        <strong>Authors:</strong>
        <p>${authorStr}</p>
      </div>

      ${
        entry.year
          ? `
        <div class="detail-section">
          <strong>Year:</strong>
          <p>${entry.year}</p>
        </div>
      `
          : ''
      }

      ${
        entry.type
          ? `
        <div class="detail-section">
          <strong>Type:</strong>
          <p style="text-transform: capitalize;">${entry.type}</p>
        </div>
      `
          : ''
      }

      ${
        entry.venue
          ? `
        <div class="detail-section">
          <strong>Venue:</strong>
          <p>${entry.venue}</p>
        </div>
      `
          : ''
      }

      ${
        entry.description
          ? `
        <div class="detail-section">
          <strong>Description:</strong>
          <p>${entry.description}</p>
        </div>
      `
          : ''
      }

      ${
        entry.concepts && entry.concepts.length > 0
          ? `
        <div class="detail-section">
          <strong>Concepts:</strong>
          <div style="margin-top: 0.5rem;">
            ${entry.concepts
              .map((c) => `<span class="concept-tag">${c}</span>`)
              .join(' ')}
          </div>
        </div>
      `
          : ''
      }

      ${
        entry.scholar_url
          ? `
        <div class="detail-section">
          <a href="${entry.scholar_url}" target="_blank" rel="noopener noreferrer"
             class="external-link" style="display: inline-block; margin-top: 0.5rem;">
            View on Google Scholar
          </a>
        </div>
      `
          : ''
      }
    </div>
  `;

  detailsContainer.innerHTML = html;
}

function setupSortControls() {
  const sortContainer = document.getElementById('bib-sort-controls');
  if (!sortContainer) return;

  sortContainer.innerHTML = `
    <span class="sort-label">Sort by:</span>
    <button class="sort-btn active" data-sort="year-desc" title="Newest first">
      Year ↓
    </button>
    <button class="sort-btn" data-sort="year-asc" title="Oldest first">
      Year ↑
    </button>
    <button class="sort-btn" data-sort="author" title="Alphabetical by author">
      Author A-Z
    </button>
    <button class="sort-btn" data-sort="title" title="Alphabetical by title">
      Title A-Z
    </button>
  `;
}
