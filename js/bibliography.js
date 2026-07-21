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

  // Use canonical implementations from utils.js (exposed via window.AffineDriftUtils by
  // main.js before this script runs). Inline fallbacks keep Jest / Node test environments
  // working where the ES-module globals are not loaded.
  const debounce = (window.AffineDriftUtils && window.AffineDriftUtils.debounce)
    ? window.AffineDriftUtils.debounce
    : (fn, waitMs) => {
        let timeout;
        return (...args) => {
          window.clearTimeout(timeout);
          window.setTimeout(() => fn(...args), waitMs);
        };
      };
  const escapeHtml = (window.AffineDriftUtils && window.AffineDriftUtils.escapeHtml)
    ? window.AffineDriftUtils.escapeHtml
    : (value) => {
        if (value == null) return "";
        return String(value)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");
      };

  const entrySearchText = (entry) => entry._searchText;

  const scoreEntry = (entry, queryTerms) => {
    if (queryTerms.length === 0) return 0;
    const haystack = entrySearchText(entry);
    let score = 0;

    for (const term of queryTerms) {
      if (entry._searchTitle.includes(term)) score += 5;
      if (entry._searchAuthors.includes(term)) score += 3;
      if (entry._searchConcepts.includes(term)) score += 2;
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
    const concepts = (entry.concepts || []);
    const links = [entry.url, entry.scholar_url].filter(Boolean);

    detailsEl.textContent = "";

    const h3 = document.createElement("h3");
    h3.className = "sidebar-heading";
    h3.textContent = "Details";

    const h4 = document.createElement("h4");
    h4.textContent = entry.title;

    const pAuthors = document.createElement("p");
    const strongAuthors = document.createElement("strong");
    strongAuthors.textContent = "Authors: ";
    pAuthors.appendChild(strongAuthors);
    pAuthors.appendChild(document.createTextNode(authors || "Unknown"));

    const pYear = document.createElement("p");
    const strongYear = document.createElement("strong");
    strongYear.textContent = "Year: ";
    pYear.appendChild(strongYear);
    pYear.appendChild(document.createTextNode(String(entry.year || "Unknown")));

    const pType = document.createElement("p");
    const strongType = document.createElement("strong");
    strongType.textContent = "Type: ";
    pType.appendChild(strongType);
    pType.appendChild(document.createTextNode(entry.type || "reference"));

    const pVenue = document.createElement("p");
    const strongVenue = document.createElement("strong");
    strongVenue.textContent = "Venue: ";
    pVenue.appendChild(strongVenue);
    pVenue.appendChild(document.createTextNode(entry.venue || "N/A"));

    const pDesc = document.createElement("p");
    pDesc.textContent = entry.description || "No description available.";

    detailsEl.append(h3, h4, pAuthors, pYear, pType, pVenue, pDesc);

    if (entry.concepts && entry.concepts.length > 0) {
      const divC = document.createElement("div");
      const strongC = document.createElement("strong");
      strongC.textContent = "Concepts:";
      const divCInner = document.createElement("div");
      divCInner.className = "bib-inline-concepts";
      for (const c of entry.concepts) {
        const span = document.createElement("span");
        span.className = "concept-tag";
        span.textContent = c;
        divCInner.appendChild(span);
      }
      divC.append(strongC, divCInner);
      detailsEl.appendChild(divC);
    }

    if (links.length > 0) {
      const divL = document.createElement("div");
      divL.className = "bib-inline-links";
      const strongL = document.createElement("strong");
      strongL.textContent = "Links:";
      const ulL = document.createElement("ul");
      for (const url of links) {
        let safeUrl = "#";
        try {
          const parsed = new URL(url, window.location.origin);
          if (parsed.protocol === "http:" || parsed.protocol === "https:") {
            safeUrl = parsed.href;
          }
        } catch (e) {}
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = safeUrl;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = url;
        li.appendChild(a);
        ulL.appendChild(li);
      }
      divL.append(strongL, ulL);
      detailsEl.appendChild(divL);
    }
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
      listEl.textContent = "";
      const emptyDiv = document.createElement("div");
      emptyDiv.className = "bib-empty-state";
      emptyDiv.setAttribute("role", "status");
      emptyDiv.setAttribute("aria-live", "polite");

      const p = document.createElement("p");
      p.textContent = 'No matches found for "';
      const strong = document.createElement("strong");
      strong.textContent = state.query;
      p.appendChild(strong);
      p.appendChild(document.createTextNode('". Try a broader query.'));
      emptyDiv.appendChild(p);

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sort-btn";
      btn.id = "bib-clear-search";
      btn.style.marginTop = "1rem";
      btn.setAttribute("aria-label", "Clear search and show all references");
      btn.setAttribute("title", "Clear search and show all references");
      btn.textContent = "Clear Search";
      emptyDiv.appendChild(btn);

      listEl.appendChild(emptyDiv);
      return;
    }

    listEl.textContent = "";
    const fragment = document.createDocumentFragment();

    for (const entry of state.filtered) {
        const authors = (entry.authors || []).join(", ");
        const type = entry.type || "reference";
        const typeClass = `type-${type.toLowerCase()}`;

        const article = document.createElement("article");
        article.className = "resource-card bib-entry bibliography-entry reference-item";
        article.dataset.entryId = entry.id;

        const header = document.createElement("div");
        header.className = "bib-header";
        const h3 = document.createElement("h3");
        h3.className = "bib-title";
        h3.textContent = entry.title;
        const badge = document.createElement("span");
        badge.className = `type-badge entry-type ${typeClass}`;
        badge.textContent = type;
        header.append(h3, badge);

        const p1 = document.createElement("p");
        p1.className = "resource-description";
        const strong1 = document.createElement("strong");
        strong1.textContent = String(entry.year || "");
        p1.append(strong1, document.createTextNode(` · ${authors || "Unknown authors"}`));

        const p2 = document.createElement("p");
        p2.className = "resource-description";
        p2.textContent = entry.description || "";

        article.append(header, p1, p2);

        if (entry.concepts && entry.concepts.length > 0) {
            const conceptsDiv = document.createElement("div");
            conceptsDiv.className = "bib-inline-concepts bib-inline-concepts-list";
            for (const c of entry.concepts.slice(0, 4)) {
                const span = document.createElement("span");
                span.className = "concept-tag";
                span.textContent = c;
                conceptsDiv.appendChild(span);
            }
            article.appendChild(conceptsDiv);
        }

        const btn = document.createElement("button");
        btn.className = "resource-link";
        btn.type = "button";
        btn.dataset.detailsId = entry.id;
        btn.setAttribute("aria-label", `View details for ${entry.title}`);
        btn.textContent = "View details";
        article.appendChild(btn);

        fragment.appendChild(article);
    }
    listEl.appendChild(fragment);
  };

  const renderSortControls = () => {
    const existing = sortControlsEl.querySelector(".bib-sort-actions");
    if (existing) existing.remove();

    const controls = document.createElement("div");
    controls.className = "bib-sort-actions";

    for (const [key, label] of Object.entries(SORTS)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "resource-link";
      button.dataset.sort = key;
      button.setAttribute("aria-pressed", state.sort === key ? "true" : "false");
      button.textContent = label;
      controls.appendChild(button);
    }

    sortControlsEl.prepend(controls);
  };

  const loadEntries = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
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

      // ⚡ Bolt Optimization: Pre-compute lowercase strings for search to avoid O(N*M) allocations per keystroke
      for (const entry of data) {
        const authorsList = Array.isArray(entry.authors) ? entry.authors : (entry.authors ? [entry.authors] : []);
        const conceptsList = Array.isArray(entry.concepts) ? entry.concepts : (entry.concepts ? [entry.concepts] : []);

        entry._searchTitle = (entry.title || "").toLowerCase();
        entry._searchAuthors = authorsList.join(" ").toLowerCase();
        entry._searchConcepts = conceptsList.join(" ").toLowerCase();
        entry._searchText = [
          entry.title || "",
          entry.venue || "",
          entry.description || "",
          ...authorsList,
          ...conceptsList,
        ]
          .join(" ")
          .toLowerCase();

        // Ensure the fields are arrays for rendering
        entry.authors = authorsList;
        entry.concepts = conceptsList;
      }

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
      state.entries = await loadEntries();
      countEl.textContent = `${state.entries.length} references`;
      renderSortControls();
      renderList();
    } catch (error) {
      listEl.textContent = "";
      const pList = document.createElement("p");
      pList.textContent = "Unable to load bibliography data.";
      listEl.appendChild(pList);
      countEl.textContent = "0 references";

      detailsEl.textContent = "";
      const h3 = document.createElement("h3");
      h3.className = "sidebar-heading";
      h3.textContent = "Details";
      const pDetails = document.createElement("p");
      pDetails.textContent = error.message;
      detailsEl.appendChild(h3);
      detailsEl.appendChild(pDetails);
      return;
    }

    searchInput.addEventListener(
      "input",
      debounce((event) => {
        state.query = event.target.value.trim();
        if (state.query.length > 1 && typeof window.AffineDriftMetrics?.trackSearch === "function") {
          try {
            window.AffineDriftMetrics.trackSearch(state.query);
          } catch (trackErr) {
            // Tracking failure must never prevent search results from rendering
            console.warn("[bibliography] AffineDriftMetrics.trackSearch failed:", trackErr);
          }
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
      const clearBtn = event.target.closest("#bib-clear-search");
      if (clearBtn) {
        searchInput.value = "";
        state.query = "";
        searchInput.focus();
        renderList();
        return;
      }

      // ⚡ Bolt Optimization: Consolidate multiple .closest() queries into a single call and differentiate with .matches()
      const targetElement = event.target.closest("button[data-details-id], article[data-entry-id]");
      if (!targetElement) return;
      const entryId = targetElement.matches("button[data-details-id]")
        ? targetElement.dataset.detailsId
        : targetElement.dataset.entryId;
      const entry = state.entries.find(
        (item) => item.id === entryId,
      );
      if (!entry) return;
      renderDetails(entry);

      // 🎨 Palette UX: Add focus management so screen readers announce the details pane
      // Make it programmatically focusable but not in the tab sequence
      detailsEl.setAttribute("tabindex", "-1");
      detailsEl.focus({ preventScroll: true });

      // Remove tabindex on blur to keep DOM clean
      detailsEl.addEventListener("blur", () => {
        detailsEl.removeAttribute("tabindex");
      }, { once: true });

      if (typeof window.AffineDriftMetrics?.trackEntryClick === "function") {
        try {
          window.AffineDriftMetrics.trackEntryClick(entry.id, entry.title);
        } catch (trackErr) {
          console.warn("[bibliography] AffineDriftMetrics.trackEntryClick failed:", trackErr);
        }
      }
    });
  };

  init();
})();
