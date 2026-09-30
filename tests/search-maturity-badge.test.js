window.__AFFINEDRIFT_SEARCH_MATURITY_BADGE_NO_AUTO_INIT__ = true;

const {
  normalizeHref,
  enhanceResults,
  init,
} = require("../js/search-maturity-badge.js");

function buildResultItem(href) {
  const doc = document.createElement("div");
  doc.className = "search-result-doc search-item";
  doc.innerHTML = `
    <a class="search-result-link" href="${href}">
      <div class="search-result-container">
        <div class="search-result-title-container">
          <p class="search-result-title">Zero-Torque Counterfactual (ZTCF)</p>
        </div>
        <div class="search-result-text-container">
          <p class="search-result-text">Some matched snippet</p>
        </div>
      </div>
    </a>
  `;
  return doc;
}

describe("search-maturity-badge", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
  });

  describe("normalizeHref", () => {
    test("strips leading slash from an absolute href", () => {
      expect(normalizeHref("/articles/zero-torque-counterfactual.html")).toBe(
        "articles/zero-torque-counterfactual.html",
      );
    });

    test("resolves a relative href against the current page", () => {
      window.history.pushState({}, "", "/books/index.html");
      expect(normalizeHref("../articles/zero-torque-counterfactual.html")).toBe(
        "articles/zero-torque-counterfactual.html",
      );
    });

    test("drops query strings and fragments", () => {
      expect(
        normalizeHref("/articles/zero-torque-counterfactual.html?x=1#sec-ZTCF"),
      ).toBe("articles/zero-torque-counterfactual.html");
    });

    test("returns an empty string for the site root", () => {
      expect(normalizeHref("/")).toBe("");
    });
  });

  describe("enhanceResults", () => {
    test("adds a maturity badge to a matching result once", () => {
      const container = buildResultItem(
        "/articles/zero-torque-counterfactual.html",
      );
      document.body.appendChild(container);

      const maturityIndex = {
        "articles/zero-torque-counterfactual.html": {
          label: "Reviewed",
          variant: "reviewed",
        },
      };

      enhanceResults(document, maturityIndex);

      const badge = container.querySelector(".badge--maturity");
      expect(badge).not.toBeNull();
      expect(badge.textContent).toBe("Reviewed");
      expect(badge.className).toBe("badge badge--maturity badge--reviewed");

      // Running again (e.g. on the next mutation) must not duplicate it.
      enhanceResults(document, maturityIndex);
      expect(container.querySelectorAll(".badge--maturity")).toHaveLength(1);
    });

    test("leaves results with no maturity entry untouched", () => {
      const container = buildResultItem("/articles/unrelated.html");
      document.body.appendChild(container);

      enhanceResults(document, {
        "articles/zero-torque-counterfactual.html": {
          label: "Reviewed",
          variant: "reviewed",
        },
      });

      expect(container.querySelector(".badge--maturity")).toBeNull();
    });

    test("does nothing when the maturity index is empty", () => {
      const container = buildResultItem(
        "/articles/zero-torque-counterfactual.html",
      );
      document.body.appendChild(container);

      expect(() => enhanceResults(document, {})).not.toThrow();
      expect(container.querySelector(".badge--maturity")).toBeNull();
    });
  });

  describe("init", () => {
    test("fetches the maturity index and enhances existing results", async () => {
      const container = buildResultItem(
        "/articles/zero-torque-counterfactual.html",
      );
      document.body.appendChild(container);

      const maturityIndex = {
        "articles/zero-torque-counterfactual.html": {
          label: "Reviewed",
          variant: "reviewed",
        },
      };
      const fetchMock = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(maturityIndex),
      });

      const started = init({ fetch: fetchMock });
      expect(started).toBe(true);
      expect(fetchMock).toHaveBeenCalledWith("/search-maturity.json");

      // Flush the fetch/json promise chain (a macrotask tick reliably
      // drains it regardless of how many microtasks it's chained through).
      await new Promise((resolve) => setTimeout(resolve, 0));

      const badge = container.querySelector(".badge--maturity");
      expect(badge).not.toBeNull();
      expect(badge.textContent).toBe("Reviewed");
    });

    test("returns false and does not throw when fetch is unavailable", () => {
      expect(init({ fetch: undefined })).toBe(false);
    });
  });
});
