/**
 * AffineDrift - Interactive Bibliography
 * Loads and displays searchable bibliography from JSON data.
 */

(function () {
  "use strict";

  let bibliographyData = [];
  let filteredData = [];
  let currentSort = "year-desc"; // Default sort: newest first
  const TYPE_CLASS_MAP = {
    paper: "type-paper",
    book: "type-book",
    article: "type-article",
    thesis: "type-thesis",
    conference: "type-conference",
  };

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    loadBibliography();
    setupSearch();
    setupSortControls();
  }

  function toLowerSafe(value) {
    return String(value || "").toLowerCase();
  }

  function getEntryById(id) {
    return bibliographyData.find((entry) => entry.id === id);
  }

  function renderLoadError(error) {
    const listContainer = document.getElementById("bib-list");
    if (!listContainer) return;

    listContainer.innerHTML = `
      <div class="bib-empty-state">
        <p>Error loading bibliography data.</p>
        <p class="bib-empty-state-details">${error.message}</p>
      </div>
    `;
  }

  function matchesQuery(entry, query) {
    const searchableFields = [
      entry.title,
      entry.description,
      entry.venue,
      entry.year,
      ...(entry.authors || []),
      ...(entry.concepts || []),
    ];
    return searchableFields.some((field) => toLowerSafe(field).includes(query));
  }

  async function loadBibliography() {
    try {
      // Updated to fetch JSON relative to the site root or current location
      // Using /data/ ensures it looks at the root data folder
      const response = await fetch("/data/bibliography.json");
      if (!response.ok) {
        // Fallback for local testing or if base path differs
        const fallbackResponse = await fetch("data/bibliography.json");
        if (!fallbackResponse.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await processResponse(fallbackResponse);
      }
      await processResponse(response);
    } catch (error) {
      console.error("Error loading bibliography:", error);
      renderLoadError(error);
    }
  }

  async function processResponse(response) {
    const jsonData = await response.json();

    // No parsing needed for JSON
    bibliographyData = jsonData;
    filteredData = [...bibliographyData];

    // Apply initial sort and render
    sortAndRender();

    // Update entry count
    const countEl = document.getElementById("bib-count");
    if (countEl) {
      countEl.textContent = `${bibliographyData.length} entries`;
    }
  }

  // Legacy parseYAML function removed as we now use JSON

  /**
   * Render bibliography entries
   */
  function renderBibliography(data) {
    const listContainer = document.getElementById("bib-list");
    if (!listContainer) return;

    if (data.length === 0) {
      listContainer.innerHTML =
        '<p class="bib-empty-state">No entries found matching your search.</p>';
      return;
    }

    const html = data
      .map((entry) => {
        const authorStr =
          entry.authors && entry.authors.length > 0
            ? entry.authors.join(", ")
            : "Unknown";

        const typeClass = getTypeClass(entry.type);
        const typeBadge = `<span class="type-badge ${typeClass}">${
          entry.type || "unknown"
        }</span>`;

        return `
        <div class="bib-entry" data-id="${entry.id}">
          <div class="bib-header">
            <h3 class="bib-title">${entry.title || "Untitled"}</h3>
            ${typeBadge}
          </div>
          <div class="bib-meta">
            <span class="bib-authors">${authorStr}</span>
            ${entry.year ? `<span class="bib-year">(${entry.year})</span>` : ""}
          </div>
          ${entry.venue ? `<div class="bib-venue">${entry.venue}</div>` : ""}
          ${
            entry.concepts && entry.concepts.length > 0
              ? `
            <div class="bib-concepts">
              ${entry.concepts
                .map((c) => `<span class="concept-tag">${c}</span>`)
                .join("")}
            </div>
          `
              : ""
          }
        </div>
      `;
      })
      .join("");

    listContainer.innerHTML = html;

    // Add click handlers
    document.querySelectorAll(".bib-entry").forEach((el) => {
      el.addEventListener("click", () => {
        const id = el.dataset.id;
        const entry = getEntryById(id);
        if (entry) {
          showDetails(entry);
          // Track entry click in metrics
          if (window.AffineDriftMetrics) {
            window.AffineDriftMetrics.trackEntryClick(id, entry.title);
          }
        }
      });
    });
  }

  /**
   * Get CSS class for entry type
   */
  function getTypeClass(type) {
    return TYPE_CLASS_MAP[type?.toLowerCase()] || "type-other";
  }

  /**
   * Show details for a bibliography entry
   */
  function showDetails(entry) {
    const detailsContainer = document.getElementById("bib-details");
    if (!detailsContainer) return;

    const authorStr =
      entry.authors && entry.authors.length > 0
        ? entry.authors.join(", ")
        : "Unknown";

    const html = `
      <h3 class="sidebar-heading">Details</h3>
      <div class="bib-detail-content">
        <h4 class="detail-title">${entry.title || "Untitled"}</h4>

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
            : ""
        }

        ${
          entry.type
            ? `
          <div class="detail-section">
            <strong>Type:</strong>
            <p class="detail-text-capitalize">${entry.type}</p>
          </div>
        `
            : ""
        }

        ${
          entry.venue
            ? `
          <div class="detail-section">
            <strong>Venue:</strong>
            <p>${entry.venue}</p>
          </div>
        `
            : ""
        }

        ${
          entry.description
            ? `
          <div class="detail-section">
            <strong>Description:</strong>
            <p>${entry.description}</p>
          </div>
        `
            : ""
        }

        ${
          entry.concepts && entry.concepts.length > 0
            ? `
          <div class="detail-section">
            <strong>Concepts:</strong>
            <div class="detail-concepts">
              ${entry.concepts
                .map((c) => `<span class="concept-tag">${c}</span>`)
                .join(" ")}
            </div>
          </div>
        `
            : ""
        }

        ${
          entry.scholar_url
            ? `
          <div class="detail-section">
            <a href="${entry.scholar_url}" target="_blank" rel="noopener noreferrer"
               class="external-link detail-link">
              View on Google Scholar
            </a>
          </div>
        `
            : ""
        }

        ${
          entry.related_ids && entry.related_ids.length > 0
            ? `
          <div class="detail-section">
            <strong>Related References:</strong>
            <ul class="detail-related-list">
              ${entry.related_ids
                .map((id) => {
                  const related = getEntryById(id);
                  return related
                    ? `<li><a href="#" data-related-id="${id}">${
                        related.title || id
                      }</a></li>`
                    : `<li>${id}</li>`;
                })
                .join("")}
            </ul>
          </div>
        `
            : ""
        }
      </div>
    `;

    detailsContainer.innerHTML = html;

    // Add handlers for related links
    detailsContainer.querySelectorAll("[data-related-id]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const relatedId = link.dataset.relatedId;
        const relatedEntry = getEntryById(relatedId);
        if (relatedEntry) {
          showDetails(relatedEntry);

          // Highlight the related entry in the list
          document.querySelectorAll(".bib-entry").forEach((el) => {
            el.classList.remove("highlighted");
            if (el.dataset.id === relatedId) {
              el.classList.add("highlighted");
              el.scrollIntoView({ behavior: "smooth", block: "center" });
            }
          });
        }
      });
    });
  }

  /**
   * Setup search functionality
   */
  function setupSearch() {
    const searchInput = document.getElementById("bib-search");
    if (!searchInput) return;

    // Debounce search
    let searchTimeout;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const query = toLowerSafe(e.target.value).trim();
        filterBibliography(query);
        // Track search in metrics
        if (query.length >= 2 && window.AffineDriftMetrics) {
          window.AffineDriftMetrics.trackSearch(query);
        }
      }, 300);
    });
  }

  /**
   * Setup sort control buttons
   */
  function setupSortControls() {
    const sortContainer = document.getElementById("bib-sort-controls");
    if (!sortContainer) return;

    // Create sort buttons
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

    // Add click handlers
    sortContainer.querySelectorAll(".sort-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const sortType = btn.dataset.sort;
        if (sortType === currentSort) return;

        // Update active state
        sortContainer.querySelectorAll(".sort-btn").forEach((b) => {
          b.classList.remove("active");
        });
        btn.classList.add("active");

        // Apply new sort
        currentSort = sortType;
        sortAndRender();
      });
    });
  }

  /**
   * Sort entries based on current sort mode
   */
  function sortEntries(entries) {
    const sorted = [...entries];

    switch (currentSort) {
      case "year-desc":
        return sorted.sort((a, b) => {
          const yearA = parseInt(a.year) || 0;
          const yearB = parseInt(b.year) || 0;
          return yearB - yearA;
        });

      case "year-asc":
        return sorted.sort((a, b) => {
          const yearA = parseInt(a.year) || 0;
          const yearB = parseInt(b.year) || 0;
          return yearA - yearB;
        });

      case "author":
        return sorted.sort((a, b) => {
          const authorA =
            a.authors && a.authors[0] ? a.authors[0].toLowerCase() : "zzz";
          const authorB =
            b.authors && b.authors[0] ? b.authors[0].toLowerCase() : "zzz";
          return authorA.localeCompare(authorB);
        });

      case "title":
        return sorted.sort((a, b) => {
          const titleA = (a.title || "").toLowerCase();
          const titleB = (b.title || "").toLowerCase();
          return titleA.localeCompare(titleB);
        });

      default:
        return sorted;
    }
  }

  /**
   * Sort and re-render the current filtered data
   */
  function sortAndRender() {
    renderBibliography(sortEntries(filteredData));
  }

  /**
   * Filter bibliography based on search query
   */
  function filterBibliography(query) {
    if (!query) {
      filteredData = [...bibliographyData];
    } else {
      filteredData = bibliographyData.filter((entry) => {
        return matchesQuery(entry, query);
      });
    }

    // Apply current sort and render
    sortAndRender();
  }

  // Internal submodule surfaces for data/render/interaction responsibilities.
  const bibliographyDataModule = {
    loadBibliography,
    processResponse,
    setBibliographyData: (data) => {
      bibliographyData = data;
      filteredData = [...data];
    },
  };
  const bibliographyRenderModule = {
    getTypeClass,
    renderBibliography,
    showDetails,
  };
  const bibliographyInteractionModule = {
    setupSearch,
    setupSortControls,
    sortEntries,
    sortAndRender,
    filterBibliography,
  };

  // Expose for testing
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      init,
      loadBibliography,
      renderBibliography,
      filterBibliography,
      sortEntries,
      getTypeClass,
      showDetails,
      setupSortControls,
      // Helper to set data for testing since it's local scope
      setBibliographyData: bibliographyDataModule.setBibliographyData,
      bibliographyDataModule,
      bibliographyRenderModule,
      bibliographyInteractionModule,
    };
  }
})();
