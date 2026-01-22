/**
 * AffineDrift - Interactive Bibliography
 * Loads and displays searchable bibliography from YAML data
 */

(function () {
  "use strict";

  let bibliographyData = [];
  let filteredData = [];
  let currentSort = "year-desc"; // Default sort: newest first

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

  /**
   * Load bibliography data from YAML file
   */
  /**
   * Load bibliography data from JSON file
   */
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
      const listContainer = document.getElementById("bib-list");
      if (listContainer) {
        listContainer.innerHTML = `
          <div style="padding: 2rem; color: var(--text-muted); text-align: center;">
            <p>Error loading bibliography data.</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">${error.message}</p>
          </div>
        `;
      }
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
        '<p style="color: var(--text-muted); padding: 2rem;">No entries found matching your search.</p>';
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
        const entry = bibliographyData.find((e) => e.id === id);
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
    const typeMap = {
      paper: "type-paper",
      book: "type-book",
      article: "type-article",
      thesis: "type-thesis",
      conference: "type-conference",
    };
    return typeMap[type?.toLowerCase()] || "type-other";
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
            <p style="text-transform: capitalize;">${entry.type}</p>
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
            <div style="margin-top: 0.5rem;">
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
               class="external-link" style="display: inline-block; margin-top: 0.5rem;">
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
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
              ${entry.related_ids
                .map((id) => {
                  const related = bibliographyData.find((e) => e.id === id);
                  return related
                    ? `<li><a href="#" onclick="event.preventDefault()" data-related-id="${id}">${
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
        const relatedEntry = bibliographyData.find((e) => e.id === relatedId);
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
        const query = e.target.value.toLowerCase().trim();
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
          const authorA = (a.authors && a.authors[0]) ? a.authors[0].toLowerCase() : "zzz";
          const authorB = (b.authors && b.authors[0]) ? b.authors[0].toLowerCase() : "zzz";
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
        // Search in title
        if (entry.title && entry.title.toLowerCase().includes(query))
          return true;

        // Search in authors
        if (
          entry.authors &&
          entry.authors.some((a) => a.toLowerCase().includes(query))
        )
          return true;

        // Search in concepts
        if (
          entry.concepts &&
          entry.concepts.some((c) => c.toLowerCase().includes(query))
        )
          return true;

        // Search in description
        if (
          entry.description &&
          entry.description.toLowerCase().includes(query)
        )
          return true;

        // Search in venue
        if (entry.venue && entry.venue.toLowerCase().includes(query))
          return true;

        // Search in year
        if (entry.year && entry.year.toString().includes(query)) return true;

        return false;
      });
    }

    // Apply current sort and render
    sortAndRender();
  }

  // Add CSS for bibliography styling
  const style = document.createElement("style");
  style.textContent = `
    .bib-entry {
      background: var(--bg-body);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 1.25rem;
      margin-bottom: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .bib-entry:hover {
      border-color: var(--accent-blue);
      box-shadow: var(--shadow-sm);
    }

    .bib-entry.highlighted {
      border-color: var(--primary-blue);
      background: var(--light-blue);
    }

    .bib-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 0.5rem;
    }

    .bib-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--primary-dark);
      margin: 0;
      flex: 1;
    }

    .type-badge {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .type-paper { background: #e3f2fd; color: #1976d2; }
    .type-book { background: #f3e5f5; color: #7b1fa2; }
    .type-article { background: #e8f5e9; color: #388e3c; }
    .type-thesis { background: #fff3e0; color: #f57c00; }
    .type-conference { background: #fce4ec; color: #c2185b; }
    .type-other { background: var(--bg-alt); color: var(--text-muted); }

    .bib-meta {
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-bottom: 0.5rem;
    }

    .bib-authors {
      font-style: italic;
    }

    .bib-year {
      margin-left: 0.5rem;
    }

    .bib-venue {
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 0.5rem;
    }

    .bib-concepts {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }

    .concept-tag {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      background: var(--bg-alt);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      font-size: 0.8rem;
      color: var(--text-main);
    }

    .bib-detail-content {
      padding-top: 1rem;
    }

    .detail-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--primary-dark);
      margin-bottom: 1rem;
      line-height: 1.4;
    }

    .detail-section {
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--border-color);
    }

    .detail-section:last-child {
      border-bottom: none;
    }

    .detail-section strong {
      display: block;
      color: var(--primary-blue);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }

    .detail-section p {
      margin: 0;
      color: var(--text-main);
      line-height: 1.6;
    }

    .detail-section ul {
      list-style: none;
      padding-left: 0;
    }

    .detail-section li {
      margin-bottom: 0.5rem;
    }

    .detail-section a {
      color: var(--accent-blue);
      text-decoration: none;
    }

    .detail-section a:hover {
      color: var(--primary-blue);
      text-decoration: underline;
    }

    .resource-grid {
      display: flex;
      flex-direction: column;
    }

    /* Sort Controls */
    #bib-sort-controls {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .sort-label {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-right: 0.25rem;
    }

    .sort-btn {
      padding: 0.4rem 0.75rem;
      font-size: 0.85rem;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      background: var(--bg-body);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .sort-btn:hover {
      border-color: var(--accent-blue);
      background: var(--bg-alt);
    }

    .sort-btn.active {
      background: var(--primary-blue);
      border-color: var(--primary-blue);
      color: white;
    }

    #bib-count {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-left: auto;
    }

    @media (max-width: 600px) {
      #bib-sort-controls {
        justify-content: center;
      }
      #bib-count {
        width: 100%;
        text-align: center;
        margin-left: 0;
        margin-top: 0.5rem;
      }
    }
  `;
  document.head.appendChild(style);
})();
