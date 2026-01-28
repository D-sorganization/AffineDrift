/**
 * AffineDrift - Lightweight Privacy-Friendly Metrics
 * Tracks usage patterns locally and displays statistics
 * No external services - all data stays in localStorage
 */

(function () {
  "use strict";

  const STORAGE_KEY = "affinedrift_metrics";
  const SESSION_KEY = "affinedrift_session";

  // Initialize metrics storage
  function getMetrics() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : initializeMetrics();
    } catch {
      return initializeMetrics();
    }
  }

  function initializeMetrics() {
    return {
      version: 1,
      firstVisit: new Date().toISOString(),
      totalPageViews: 0,
      totalSearches: 0,
      totalBibClicks: 0,
      searchTerms: {},
      popularEntries: {},
      pageViews: {},
      conceptClicks: {},
      sessions: 0,
      lastVisit: null,
    };
  }

  function saveMetrics(metrics) {
    try {
      metrics.lastVisit = new Date().toISOString();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(metrics));
    } catch {
      // Storage full or disabled - fail silently
    }
  }

  // Session management
  function initSession() {
    const sessionData = sessionStorage.getItem(SESSION_KEY);
    if (!sessionData) {
      const metrics = getMetrics();
      metrics.sessions++;
      saveMetrics(metrics);
      sessionStorage.setItem(
        SESSION_KEY,
        JSON.stringify({
          start: new Date().toISOString(),
          pageViews: 0,
        })
      );
    }
  }

  // Track page view
  function trackPageView() {
    const metrics = getMetrics();
    const path = window.location.pathname;

    metrics.totalPageViews++;
    metrics.pageViews[path] = (metrics.pageViews[path] || 0) + 1;

    saveMetrics(metrics);
  }

  // Track bibliography search
  function trackSearch(term) {
    if (!term || term.length < 2) return;

    const metrics = getMetrics();
    const normalizedTerm = term.toLowerCase().trim();

    if (!normalizedTerm) return;

    metrics.totalSearches++;
    metrics.searchTerms[normalizedTerm] =
      (metrics.searchTerms[normalizedTerm] || 0) + 1;

    saveMetrics(metrics);
  }

  // Track bibliography entry click
  function trackEntryClick(entryId, entryTitle) {
    const metrics = getMetrics();

    metrics.totalBibClicks++;
    metrics.popularEntries[entryId] = {
      count: (metrics.popularEntries[entryId]?.count || 0) + 1,
      title: entryTitle,
      lastClick: new Date().toISOString(),
    };

    saveMetrics(metrics);
  }

  // Track concept tag click
  function trackConceptClick(concept) {
    const metrics = getMetrics();
    metrics.conceptClicks[concept] = (metrics.conceptClicks[concept] || 0) + 1;
    saveMetrics(metrics);
  }

  // Get statistics for display
  function getStatistics() {
    const metrics = getMetrics();

    // Top search terms
    const topSearches = Object.entries(metrics.searchTerms)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    // Top entries
    const topEntries = Object.entries(metrics.popularEntries)
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 10)
      .map(([id, data]) => ({ id, ...data }));

    // Top concepts
    const topConcepts = Object.entries(metrics.conceptClicks)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    // Top pages
    const topPages = Object.entries(metrics.pageViews)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    return {
      summary: {
        totalPageViews: metrics.totalPageViews,
        totalSearches: metrics.totalSearches,
        totalBibClicks: metrics.totalBibClicks,
        totalSessions: metrics.sessions,
        firstVisit: metrics.firstVisit,
        lastVisit: metrics.lastVisit,
      },
      topSearches,
      topEntries,
      topConcepts,
      topPages,
    };
  }

  // Render statistics widget
  function renderStatsWidget(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const stats = getStatistics();

    const html = `
      <div class="metrics-widget">
        <h4 class="metrics-heading">Your Usage Statistics</h4>

        <div class="metrics-summary">
          <div class="metric-card">
            <span class="metric-value">${stats.summary.totalPageViews}</span>
            <span class="metric-label">Page Views</span>
          </div>
          <div class="metric-card">
            <span class="metric-value">${stats.summary.totalSearches}</span>
            <span class="metric-label">Searches</span>
          </div>
          <div class="metric-card">
            <span class="metric-value">${stats.summary.totalBibClicks}</span>
            <span class="metric-label">References Viewed</span>
          </div>
          <div class="metric-card">
            <span class="metric-value">${stats.summary.totalSessions}</span>
            <span class="metric-label">Sessions</span>
          </div>
        </div>

        ${
          stats.topSearches.length > 0
            ? `
          <div class="metrics-section">
            <h5>Your Top Searches</h5>
            <div class="metrics-list">
              ${stats.topSearches
                .map(
                  ([term, count]) => `
                <div class="metrics-item">
                  <span class="item-name">${escapeHtml(term)}</span>
                  <span class="item-count">${count}</span>
                </div>
              `
                )
                .join("")}
            </div>
          </div>
        `
            : ""
        }

        ${
          stats.topEntries.length > 0
            ? `
          <div class="metrics-section">
            <h5>Most Viewed References</h5>
            <div class="metrics-list">
              ${stats.topEntries
                .map(
                  (entry) => `
                <div class="metrics-item">
                  <span class="item-name" title="${escapeHtml(entry.title)}">${truncate(entry.title, 40)}</span>
                  <span class="item-count">${entry.count}</span>
                </div>
              `
                )
                .join("")}
            </div>
          </div>
        `
            : ""
        }

        ${
          stats.topConcepts.length > 0
            ? `
          <div class="metrics-section">
            <h5>Popular Concepts</h5>
            <div class="concept-cloud">
              ${stats.topConcepts
                .map(
                  ([concept, count]) => `
                <span class="concept-tag" style="font-size: ${Math.min(1 + count * 0.1, 1.5)}rem">${escapeHtml(concept)}</span>
              `
                )
                .join("")}
            </div>
          </div>
        `
            : ""
        }

        <div class="metrics-footer">
          <small>Data stored locally in your browser. <button onclick="AffineDriftMetrics.clearData()" class="clear-btn">Clear data</button></small>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // Helper functions
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function truncate(str, len) {
    return str.length > len ? str.substring(0, len) + "..." : str;
  }

  // Clear all metrics data
  function clearData() {
    localStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(SESSION_KEY);
    // Refresh any displayed widgets
    const widget = document.getElementById("metrics-widget");
    if (widget) renderStatsWidget("metrics-widget");
  }

  // Initialize on page load
  function init() {
    initSession();
    trackPageView();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose public API
  window.AffineDriftMetrics = {
    trackSearch,
    trackEntryClick,
    trackConceptClick,
    getStatistics,
    renderStatsWidget,
    clearData,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      initializeMetrics,
      getMetrics,
      saveMetrics,
      trackPageView,
      trackSearch,
      trackEntryClick,
      trackConceptClick,
      getStatistics,
      clearData,
      escapeHtml,
      truncate
    };
  }
})();
