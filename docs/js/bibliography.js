/**
 * AffineDrift bibliography page interactions.
 * Provides local search, sorting, and details rendering from data/bibliography.json.
 */
(function () {
  "use strict";

  const app = document.getElementById("bibliography-app");
  if (!app) return;

  const searchInput = document.getElementById("bib-search");
  const listEl = document.getElementById("bib-list");
  const detailsEl = document.getElementById("bib-details");
  const sortControlsEl = document.getElementById("bib-sort-controls");
  const countEl = document.getElementById("bib-count");

  if (!searchInput || !listEl || !detailsEl || !sortControlsEl || !countEl) {
    return;
  }

  const SORTS = {
    relevance: "Relevance",
    newest: "Newest",
    oldest: "Oldest",
    title: "Title A-Z",
  };

  const state = {
    entries: [],
    filtered: [],
    query: "",
    sort: "relevance",
  };

  const debounce = (fn, waitMs) => {
    let timeout;
    return (...args) => {
      window.clearTimeout(timeout);
      timeout = window.setTimeout(() => fn(...args), waitMs);
    };
  };

  const escapeHtml = (value) => {
    const el = document.createElement("div");
    el.textContent = value ?? "";
    return el.innerHTML;
  };

  const entrySearchText = (entry) => entry._haystack || "";

  const scoreEntry = (entry, queryTerms) => {
    if (queryTerms.length === 0) return 0;
    const haystack = entrySearchText(entry);
    let score = 0;

    for (const term of queryTerms) {
      if (entry._titleLower.includes(term)) score += 5;
      if (entry._authorsLower.includes(term)) score += 3;
      if (entry._conceptsLower.includes(term)) score += 2;
      if (haystack.includes(term)) score += 1;
    }

    return score;
  };

  const sortEntries = (entries) => {
    const queryTerms = state.query
      .toLowerCase()
      .split(/\s+/)
      .map((s) => s.trim())
      .filter(Boolean);

    const scored = entries.map((entry) => ({
      entry,
      score: scoreEntry(entry, queryTerms),
    }));

    scored.sort((a, b) => {
      if (state.sort === "newest")
        return (b.entry.year || 0) - (a.entry.year || 0);
      if (state.sort === "oldest")
        return (a.entry.year || 0) - (b.entry.year || 0);
      if (state.sort === "title")
        return a.entry.title.localeCompare(b.entry.title);
      if (b.score !== a.score) return b.score - a.score;
      return (b.entry.year || 0) - (a.entry.year || 0);
    });

    return scored.map((item) => item.entry);
  };

  const renderDetails = (entry) => {
    const authors = (entry.authors || []).join(", ");
    const concepts = (entry.concepts || [])
      .map((c) => `<span class="concept-tag">${escapeHtml(c)}</span>`)
      .join("");

    const links = [entry.url, entry.scholar_url]
      .filter(Boolean)
      .map(
        (url) =>
          `<li><a href="${escapeHtml(
            url,
          )}" target="_blank" rel="noopener noreferrer">${escapeHtml(url)}</a></li>`,
      )
      .join("");

    detailsEl.innerHTML = `
      <h3 class="sidebar-heading">Details</h3>
      <h4>${escapeHtml(entry.title)}</h4>
      <p><strong>Authors:</strong> ${escapeHtml(authors || "Unknown")}</p>
      <p><strong>Year:</strong> ${escapeHtml(
        String(entry.year || "Unknown"),
      )}</p>
      <p><strong>Type:</strong> ${escapeHtml(entry.type || "reference")}</p>
      <p><strong>Venue:</strong> ${escapeHtml(entry.venue || "N/A")}</p>
      <p>${escapeHtml(entry.description || "No description available.")}</p>
      ${
        concepts
          ? `<div><strong>Concepts:</strong><div class="bib-inline-concepts">${concepts}</div></div>`
          : ""
      }
      ${
        links
          ? `<div class="bib-inline-links"><strong>Links:</strong><ul>${links}</ul></div>`
          : ""
      }
    `;
  };

  const renderList = () => {
    const queryTerms = state.query
      .toLowerCase()
      .split(/\s+/)
      .map((s) => s.trim())
      .filter(Boolean);

    const filtered = state.entries.filter((entry) => {
      if (queryTerms.length === 0) return true;
      const haystack = entrySearchText(entry);
      return queryTerms.every((term) => haystack.includes(term));
    });

    state.filtered = sortEntries(filtered);
    countEl.textContent = `${state.filtered.length} reference${
      state.filtered.length === 1 ? "" : "s"
    }`;

    if (state.filtered.length === 0) {
      listEl.innerHTML = `<p>No matches found. Try a broader query.</p>`;
      return;
    }

    listEl.innerHTML = state.filtered
      .map((entry) => {
        const authors = (entry.authors || []).join(", ");
        const concepts = (entry.concepts || [])
          .slice(0, 4)
          .map((c) => `<span class="concept-tag">${escapeHtml(c)}</span>`)
          .join(" ");

        return `
          <article class="resource-card" data-entry-id="${escapeHtml(
            entry.id,
          )}">
            <h3>${escapeHtml(entry.title)}</h3>
            <p class="resource-description"><strong>${escapeHtml(
              String(entry.year || ""),
            )}</strong> · ${escapeHtml(authors || "Unknown authors")}</p>
            <p class="resource-description">${escapeHtml(
              entry.description || "",
            )}</p>
            ${
              concepts
                ? `<div class="bib-inline-concepts bib-inline-concepts-list">${concepts}</div>`
                : ""
            }
            <button class="resource-link" type="button" data-details-id="${escapeHtml(
              entry.id,
            )}" aria-label="View details for ${escapeHtml(
              entry.title,
            )}">View details</button>
          </article>
        `;
      })
      .join("");
  };

  const renderSortControls = () => {
    const buttons = Object.entries(SORTS)
      .map(
        ([key, label]) =>
          `<button type="button" class="resource-link" data-sort="${key}" aria-pressed="${
            state.sort === key ? "true" : "false"
          }">${label}</button>`,
      )
      .join("");

    const existing = sortControlsEl.querySelector(".bib-sort-actions");
    if (existing) existing.remove();

    const controls = document.createElement("div");
    controls.className = "bib-sort-actions";
    controls.innerHTML = buttons;
    sortControlsEl.prepend(controls);
  };

  const loadEntries = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
    try {
      const dataUrl = window.BIBLIOGRAPHY_DATA_URL || "data/bibliography.json";
      const response = await fetch(dataUrl, {
        cache: "no-cache",
        signal: controller.signal,
      });
      if (!response.ok) {
        throw new Error(`Failed to load bibliography data (${response.status})`);
      }
      const data = await response.json();
      if (!Array.isArray(data))
        throw new Error("Invalid bibliography data format");
      return data;
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error("Bibliography data request timed out after 10 seconds");
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  };

  const init = async () => {
    try {
      const rawEntries = await loadEntries();
      state.entries = rawEntries.map(entry => {
        const titleLower = entry.title ? entry.title.toLowerCase() : "";
        const authorsLower = (entry.authors || []).join(" ").toLowerCase();
        const conceptsLower = (entry.concepts || []).join(" ").toLowerCase();
        const haystack = [
          entry.title,
          entry.venue,
          entry.description,
          ...(entry.authors || []),
          ...(entry.concepts || [])
        ].join(" ").toLowerCase();

        return {
          ...entry,
          _titleLower: titleLower,
          _authorsLower: authorsLower,
          _conceptsLower: conceptsLower,
          _haystack: haystack
        };
      });
      countEl.textContent = `${state.entries.length} references`;
      renderSortControls();
      renderList();
    } catch (error) {
      listEl.innerHTML = `<p>Unable to load bibliography data.</p>`;
      countEl.textContent = "0 references";
      detailsEl.innerHTML = `<h3 class="sidebar-heading">Details</h3><p>${escapeHtml(
        error.message,
      )}</p>`;
      return;
    }

    searchInput.addEventListener(
      "input",
      debounce((event) => {
        state.query = event.target.value.trim();
        if (state.query.length > 1 && window.AffineDriftMetrics) {
          window.AffineDriftMetrics.trackSearch(state.query);
        }
        renderList();
      }, 180),
    );

    sortControlsEl.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-sort]");
      if (!button) return;
      state.sort = button.dataset.sort;
      renderSortControls();
      renderList();
    });

    listEl.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-details-id]");
      if (!button) return;
      const entry = state.entries.find(
        (item) => item.id === button.dataset.detailsId,
      );
      if (!entry) return;
      renderDetails(entry);
      if (window.AffineDriftMetrics) {
        window.AffineDriftMetrics.trackEntryClick(entry.id, entry.title);
      }
    });
  };

  init();
})();
