/**
 * Search Module
 * Handles search functionality and modal interactions
 */

/**
 * Initialize search functionality
 */
export function initSearch() {
  const searchButton = document.querySelector('.search-trigger');
  const searchModal = document.querySelector('.search-modal');
  const searchInput = document.querySelector('.search-input');

  if (!searchButton) return;

  // Open search modal
  searchButton.addEventListener('click', () => {
    if (searchModal) {
      searchModal.classList.add('show');
      searchModal.setAttribute('aria-hidden', 'false');
      
      if (searchInput) {
        searchInput.focus();
      }
    }
  });

  // Close search modal
  const closeSearch = () => {
    if (searchModal) {
      searchModal.classList.remove('show');
      searchModal.setAttribute('aria-hidden', 'true');
    }
  };

  // Close button
  const closeButton = searchModal?.querySelector('.close, .search-close');
  if (closeButton) {
    closeButton.addEventListener('click', closeSearch);
  }

  // Close on backdrop click
  if (searchModal) {
    searchModal.addEventListener('click', (e) => {
      if (e.target === searchModal) {
        closeSearch();
      }
    });
  }

  // Close on Escape key (handled in accessibility.js)
}

/**
 * Setup search autocomplete
 * @param {Array} searchIndex - Search index data
 */
export function setupSearchAutocomplete(searchIndex) {
  const searchInput = document.querySelector('.search-input');
  const resultsContainer = document.querySelector('.search-results');

  if (!searchInput || !resultsContainer) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();

    if (query.length < 2) {
      resultsContainer.innerHTML = '';
      return;
    }

    // Simple search implementation
    const results = searchIndex
      .filter((item) => {
        return (
          item.title?.toLowerCase().includes(query) ||
          item.content?.toLowerCase().includes(query)
        );
      })
      .slice(0, 10);

    displaySearchResults(results, resultsContainer);
  });
}

/**
 * Display search results
 * @param {Array} results - Search results
 * @param {HTMLElement} container - Results container
 */
function displaySearchResults(results, container) {
  if (results.length === 0) {
    container.innerHTML = '<div class="no-results">No results found</div>';
    return;
  }

  const html = results
    .map((result) => {
      return `
        <a href="${result.url}" class="search-result-item">
          <h4>${result.title}</h4>
          <p>${result.excerpt || ''}</p>
        </a>
      `;
    })
    .join('');

  container.innerHTML = html;
}
