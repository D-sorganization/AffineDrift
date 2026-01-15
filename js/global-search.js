/**
 * AffineDrift - Global Full-Text Search
 * Provides site-wide search across all articles and content
 * Uses Fuse.js for fuzzy matching (already included by Quarto)
 */

(function () {
  "use strict";

  let searchIndex = null;
  let fuse = null;
  let isLoaded = false;

  // Fuse.js configuration for full-text search
  const fuseOptions = {
    keys: [
      { name: "title", weight: 0.4 },
      { name: "description", weight: 0.2 },
      { name: "headings", weight: 0.15 },
      { name: "concepts", weight: 0.15 },
      { name: "body", weight: 0.1 },
    ],
    threshold: 0.3,
    ignoreLocation: true,
    includeScore: true,
    includeMatches: true,
    minMatchCharLength: 2,
    useExtendedSearch: true,
  };

  // Type icons and labels
  const typeConfig = {
    theory: { icon: "📐", label: "Theory" },
    article: { icon: "📄", label: "Article" },
    model: { icon: "🔧", label: "Model" },
    resource: { icon: "📚", label: "Resource" },
    repository: { icon: "💾", label: "Repository" },
    reference: { icon: "📖", label: "Reference" },
    page: { icon: "📃", label: "Page" },
  };

  /**
   * Load the search index
   */
  async function loadIndex() {
    if (isLoaded) return true;

    try {
      const response = await fetch("/data/search_index.json");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      searchIndex = await response.json();

      // Initialize Fuse with the index
      if (typeof Fuse !== "undefined") {
        fuse = new Fuse(searchIndex.entries, fuseOptions);
        isLoaded = true;
        console.log(
          `Global search loaded: ${searchIndex.count} entries indexed`
        );
        return true;
      } else {
        console.warn("Fuse.js not available, search disabled");
        return false;
      }
    } catch (error) {
      console.error("Failed to load search index:", error);
      return false;
    }
  }

  /**
   * Perform a search query
   */
  function search(query, options = {}) {
    if (!fuse || !query || query.length < 2) {
      return [];
    }

    const limit = options.limit || 20;
    const typeFilter = options.type || null;

    let results = fuse.search(query, { limit: limit * 2 });

    // Apply type filter if specified
    if (typeFilter) {
      results = results.filter((r) => r.item.type === typeFilter);
    }

    // Limit results
    results = results.slice(0, limit);

    // Track search if metrics available
    if (window.AffineDriftMetrics) {
      window.AffineDriftMetrics.trackSearch(query);
    }

    return results.map((r) => ({
      ...r.item,
      score: r.score,
      matches: r.matches,
    }));
  }

  /**
   * Render search results
   */
  function renderResults(results, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (results.length === 0) {
      container.innerHTML = `
        <div class="search-no-results">
          <p>No results found. Try different keywords or browse by category.</p>
        </div>
      `;
      return;
    }

    const html = results
      .map((result) => {
        const type = typeConfig[result.type] || typeConfig.page;
        const relevance = Math.round((1 - result.score) * 100);

        return `
        <a href="${result.url}" class="search-result-item">
          <div class="result-header">
            <span class="result-type" title="${type.label}">${type.icon}</span>
            <h4 class="result-title">${escapeHtml(result.title)}</h4>
            <span class="result-relevance">${relevance}%</span>
          </div>
          ${result.description ? `<p class="result-description">${escapeHtml(truncate(result.description, 150))}</p>` : ""}
          ${result.excerpt ? `<p class="result-excerpt">${escapeHtml(truncate(result.excerpt, 100))}</p>` : ""}
          ${
            result.concepts && result.concepts.length > 0
              ? `
            <div class="result-concepts">
              ${result.concepts
                .slice(0, 5)
                .map((c) => `<span class="concept-tag-small">${escapeHtml(c)}</span>`)
                .join("")}
            </div>
          `
              : ""
          }
        </a>
      `;
      })
      .join("");

    container.innerHTML = `
      <div class="search-results-count">${results.length} result${results.length !== 1 ? "s" : ""} found</div>
      <div class="search-results-list">${html}</div>
    `;
  }

  /**
   * Create and inject the search modal
   */
  function createSearchModal() {
    if (document.getElementById("global-search-modal")) return;

    const modal = document.createElement("div");
    modal.id = "global-search-modal";
    modal.className = "search-modal";
    modal.innerHTML = `
      <div class="search-modal-backdrop" onclick="AffineDriftSearch.closeModal()"></div>
      <div class="search-modal-content">
        <div class="search-modal-header">
          <input type="text" id="global-search-input" placeholder="Search articles, models, resources..." autocomplete="off">
          <button class="search-close-btn" onclick="AffineDriftSearch.closeModal()">×</button>
        </div>
        <div class="search-filters">
          <button class="filter-btn active" data-type="">All</button>
          <button class="filter-btn" data-type="article">Articles</button>
          <button class="filter-btn" data-type="theory">Theory</button>
          <button class="filter-btn" data-type="model">Models</button>
          <button class="filter-btn" data-type="resource">Resources</button>
        </div>
        <div id="global-search-results" class="search-results"></div>
        <div class="search-modal-footer">
          <span class="search-hint">Press <kbd>↵</kbd> to select, <kbd>Esc</kbd> to close</span>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Setup event listeners
    const input = document.getElementById("global-search-input");
    let debounceTimer;
    let currentFilter = "";

    input.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const results = search(e.target.value, { type: currentFilter || null });
        renderResults(results, "global-search-results");
      }, 200);
    });

    // Filter buttons
    modal.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        modal
          .querySelectorAll(".filter-btn")
          .forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentFilter = btn.dataset.type;
        const results = search(input.value, { type: currentFilter || null });
        renderResults(results, "global-search-results");
      });
    });

    // Keyboard navigation
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeModal();
      } else if (e.key === "Enter") {
        const firstResult = document.querySelector(".search-result-item");
        if (firstResult) {
          firstResult.click();
        }
      }
    });
  }

  /**
   * Open the search modal
   */
  async function openModal() {
    await loadIndex();
    createSearchModal();

    const modal = document.getElementById("global-search-modal");
    modal.classList.add("active");
    document.body.style.overflow = "hidden";

    // Focus input
    setTimeout(() => {
      document.getElementById("global-search-input")?.focus();
    }, 100);
  }

  /**
   * Close the search modal
   */
  function closeModal() {
    const modal = document.getElementById("global-search-modal");
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  // Helper functions
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function truncate(str, len) {
    if (!str) return "";
    return str.length > len ? str.substring(0, len) + "..." : str;
  }

  // Keyboard shortcut (Ctrl+K or Cmd+K)
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      openModal();
    }
  });

  // Initialize on load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      // Pre-load index in background
      setTimeout(loadIndex, 2000);
    });
  } else {
    setTimeout(loadIndex, 2000);
  }

  // Expose public API
  window.AffineDriftSearch = {
    search,
    openModal,
    closeModal,
    loadIndex,
  };
})();
