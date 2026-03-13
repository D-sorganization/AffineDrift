/**
 * Tests for src/js/metrics.js
 * Testing privacy-friendly local metrics tracking
 */

const {
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
  truncate,
} = require("../js/metrics.js");

describe("Metrics Module", () => {
  const STORAGE_KEY = "affinedrift_metrics";
  const SESSION_KEY = "affinedrift_session";

  beforeEach(() => {
    // Clear storage before each test
    localStorage.clear();
    sessionStorage.clear();
    jest.clearAllMocks();
  });

  describe("initializeMetrics", () => {
    test("should create metrics object with correct structure", () => {
      const metrics = initializeMetrics();

      expect(metrics).toHaveProperty("version", 1);
      expect(metrics).toHaveProperty("firstVisit");
      expect(metrics).toHaveProperty("totalPageViews", 0);
      expect(metrics).toHaveProperty("totalSearches", 0);
      expect(metrics).toHaveProperty("totalBibClicks", 0);
      expect(metrics).toHaveProperty("searchTerms");
      expect(metrics).toHaveProperty("popularEntries");
      expect(metrics).toHaveProperty("pageViews");
      expect(metrics).toHaveProperty("conceptClicks");
      expect(metrics).toHaveProperty("sessions", 0);
      expect(metrics).toHaveProperty("lastVisit", null);
    });

    test("should set firstVisit as ISO date string", () => {
      const metrics = initializeMetrics();
      expect(() => new Date(metrics.firstVisit)).not.toThrow();
    });
  });

  describe("getMetrics", () => {
    test("should return stored metrics if available", () => {
      const storedMetrics = {
        version: 1,
        totalPageViews: 10,
        totalSearches: 5,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(storedMetrics));

      const metrics = getMetrics();
      expect(metrics.totalPageViews).toBe(10);
      expect(metrics.totalSearches).toBe(5);
    });

    test("should return new metrics if nothing stored", () => {
      const metrics = getMetrics();
      expect(metrics.totalPageViews).toBe(0);
      expect(metrics.sessions).toBe(0);
    });

    test("should handle invalid JSON in storage", () => {
      localStorage.setItem(STORAGE_KEY, "invalid json");
      const metrics = getMetrics();
      expect(metrics).toHaveProperty("totalPageViews", 0);
    });
  });

  describe("saveMetrics", () => {
    test("should save metrics to localStorage", () => {
      const metrics = initializeMetrics();
      metrics.totalPageViews = 5;

      saveMetrics(metrics);

      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
      expect(stored.totalPageViews).toBe(5);
    });

    test("should update lastVisit timestamp", () => {
      const metrics = initializeMetrics();
      expect(metrics.lastVisit).toBeNull();

      saveMetrics(metrics);

      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
      expect(stored.lastVisit).not.toBeNull();
      expect(() => new Date(stored.lastVisit)).not.toThrow();
    });
  });

  describe("trackPageView", () => {
    beforeEach(() => {
      window.history.pushState({}, "", "/");
    });

    test("should increment totalPageViews", () => {
      trackPageView();
      const metrics = getMetrics();
      expect(metrics.totalPageViews).toBe(1);
    });

    test("should track page path", () => {
      window.history.pushState({}, "", "/articles/test-article");

      trackPageView();
      const metrics = getMetrics();
      expect(metrics.pageViews["/articles/test-article"]).toBe(1);
    });

    test("should increment count for repeated visits to same page", () => {
      window.history.pushState({}, "", "/test-page");

      trackPageView();
      trackPageView();
      trackPageView();

      const metrics = getMetrics();
      expect(metrics.pageViews["/test-page"]).toBe(3);
    });
  });

  describe("trackSearch", () => {
    test("should increment totalSearches", () => {
      trackSearch("golf swing");
      const metrics = getMetrics();
      expect(metrics.totalSearches).toBe(1);
    });

    test("should store normalized search term", () => {
      trackSearch("  GOLF Swing  ");
      const metrics = getMetrics();
      expect(metrics.searchTerms["golf swing"]).toBe(1);
    });

    test("should increment count for repeated searches", () => {
      trackSearch("biomechanics");
      trackSearch("Biomechanics");
      trackSearch("BIOMECHANICS");

      const metrics = getMetrics();
      expect(metrics.searchTerms["biomechanics"]).toBe(3);
    });

    test("should ignore empty search terms", () => {
      trackSearch("");
      trackSearch("   ");

      const metrics = getMetrics();
      expect(metrics.totalSearches).toBe(0);
    });

    test("should ignore search terms shorter than 2 characters", () => {
      trackSearch("a");

      const metrics = getMetrics();
      expect(metrics.totalSearches).toBe(0);
    });
  });

  describe("trackEntryClick", () => {
    test("should increment totalBibClicks", () => {
      trackEntryClick("entry-1", "Test Entry");
      const metrics = getMetrics();
      expect(metrics.totalBibClicks).toBe(1);
    });

    test("should store entry details", () => {
      trackEntryClick("entry-1", "Test Entry Title");

      const metrics = getMetrics();
      expect(metrics.popularEntries["entry-1"]).toBeDefined();
      expect(metrics.popularEntries["entry-1"].count).toBe(1);
      expect(metrics.popularEntries["entry-1"].title).toBe("Test Entry Title");
      expect(metrics.popularEntries["entry-1"].lastClick).toBeDefined();
    });

    test("should increment count for repeated clicks", () => {
      trackEntryClick("entry-1", "Test Entry");
      trackEntryClick("entry-1", "Test Entry");

      const metrics = getMetrics();
      expect(metrics.popularEntries["entry-1"].count).toBe(2);
    });
  });

  describe("trackConceptClick", () => {
    test("should track concept clicks", () => {
      trackConceptClick("biomechanics");
      const metrics = getMetrics();
      expect(metrics.conceptClicks["biomechanics"]).toBe(1);
    });

    test("should increment count for repeated clicks", () => {
      trackConceptClick("control-theory");
      trackConceptClick("control-theory");
      trackConceptClick("control-theory");

      const metrics = getMetrics();
      expect(metrics.conceptClicks["control-theory"]).toBe(3);
    });
  });

  describe("getStatistics", () => {
    test("should return summary statistics", () => {
      const metrics = initializeMetrics();
      metrics.totalPageViews = 100;
      metrics.totalSearches = 50;
      metrics.totalBibClicks = 25;
      metrics.sessions = 10;
      saveMetrics(metrics);

      const stats = getStatistics();

      expect(stats.summary.totalPageViews).toBe(100);
      expect(stats.summary.totalSearches).toBe(50);
      expect(stats.summary.totalBibClicks).toBe(25);
      expect(stats.summary.totalSessions).toBe(10);
    });

    test("should return top searches sorted by count", () => {
      const metrics = initializeMetrics();
      metrics.searchTerms = {
        biomechanics: 10,
        golf: 5,
        "control theory": 15,
      };
      saveMetrics(metrics);

      const stats = getStatistics();

      expect(stats.topSearches[0][0]).toBe("control theory");
      expect(stats.topSearches[0][1]).toBe(15);
    });

    test("should return top entries sorted by count", () => {
      const metrics = initializeMetrics();
      metrics.popularEntries = {
        "entry-1": { count: 5, title: "Entry 1" },
        "entry-2": { count: 10, title: "Entry 2" },
        "entry-3": { count: 3, title: "Entry 3" },
      };
      saveMetrics(metrics);

      const stats = getStatistics();

      expect(stats.topEntries[0].id).toBe("entry-2");
      expect(stats.topEntries[0].count).toBe(10);
    });

    test("should limit results to top 10", () => {
      const metrics = initializeMetrics();
      // Add 15 search terms
      for (let i = 0; i < 15; i++) {
        metrics.searchTerms[`term-${i}`] = i;
      }
      saveMetrics(metrics);

      const stats = getStatistics();
      expect(stats.topSearches.length).toBeLessThanOrEqual(10);
    });
  });

  describe("clearData", () => {
    test("should clear all metrics data", () => {
      trackPageView();
      trackSearch("test");
      trackEntryClick("entry-1", "Test");

      clearData();

      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
      expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
    });

    test("clear button uses event listener instead of inline handler", () => {
      document.body.innerHTML = '<div id="metrics-widget"></div>';
      trackPageView();
      window.AffineDriftMetrics.renderStatsWidget("metrics-widget");

      const clearBtn = document.querySelector("#metrics-widget .clear-btn");
      expect(clearBtn).toBeTruthy();
      expect(clearBtn.getAttribute("onclick")).toBeNull();

      clearBtn.click();
      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    });
  });

  describe("escapeHtml", () => {
    test("should escape HTML special characters", () => {
      expect(escapeHtml('<script>alert("xss")</script>')).toBe(
        '&lt;script&gt;alert("xss")&lt;/script&gt;',
      );
    });

    test("should handle plain text unchanged", () => {
      expect(escapeHtml("Hello World")).toBe("Hello World");
    });

    test("should escape ampersands", () => {
      expect(escapeHtml("foo & bar")).toBe("foo &amp; bar");
    });
  });

  describe("truncate", () => {
    test("should truncate long strings", () => {
      const longString = "This is a very long string that needs truncation";
      expect(truncate(longString, 20)).toBe("This is a very long ...");
    });

    test("should not truncate short strings", () => {
      const shortString = "Short";
      expect(truncate(shortString, 20)).toBe("Short");
    });

    test("should handle exact length", () => {
      const exactString = "12345";
      expect(truncate(exactString, 5)).toBe("12345");
    });
  });
});
