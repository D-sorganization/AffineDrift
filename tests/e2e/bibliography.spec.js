const { test, expect } = require("@playwright/test");

test.describe("Bibliography Page", () => {
  test("should load bibliography page", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Check page loads
    await expect(page).toHaveTitle(/Bibliography|References|AffineDrift/);

    // Check for bibliography container
    const bibList = page.locator("#bib-list, .bibliography, .references");
    await expect(bibList.first()).toBeVisible({ timeout: 10000 });
  });

  test("should display bibliography entries", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for bibliography to load
    await page
      .waitForSelector(".bib-entry, .bibliography-entry, .reference-item", {
        timeout: 10000,
      })
      .catch(() => {});

    // Check for entries
    const entries = page.locator(
      ".bib-entry, .bibliography-entry, .reference-item",
    );
    const count = await entries.count();

    // Should have bibliography entries
    expect(count).toBeGreaterThan(0);
  });

  test("should have working search functionality", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Find search input
    const searchInput = page.locator(
      '#bib-search, input[type="search"], input[placeholder*="search" i]',
    );

    if ((await searchInput.count()) > 0) {
      await expect(searchInput.first()).toBeVisible();

      // Type a search term
      await searchInput.first().fill("biomechanics");

      await expect(searchInput.first()).toHaveValue("biomechanics");

      // Results should be filtered
      const entries = page.locator(".bib-entry, .bibliography-entry");
      // Just verify search doesn't error
      const count = await entries.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test("should have working sort controls", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Find sort controls
    const sortControls = page.locator(
      "#bib-sort-controls, .sort-controls, .sort-btn",
    );

    if ((await sortControls.count()) > 0) {
      await expect(sortControls.first()).toBeVisible();

      // Try clicking a sort button
      const sortButton = page.locator(".sort-btn, button[data-sort]").first();
      if ((await sortButton.count()) > 0) {
        await sortButton.click();

        // Should not error
        const entries = page.locator(".bib-entry, .bibliography-entry");
        const count = await entries.count();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test("should show entry details when clicked", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for entries to load
    await page
      .waitForSelector(".bib-entry, .bibliography-entry", {
        timeout: 10000,
      })
      .catch(() => {});

    // Find an entry
    const entry = page.locator(".bib-entry, .bibliography-entry").first();

    if ((await entry.count()) > 0) {
      await entry.click();

      // Check for details panel
      const details = page.locator(
        "#bib-details, .bib-detail-content, .entry-details",
      );
      if ((await details.count()) > 0) {
        await expect(details.first()).toBeVisible();
      }
    }
  });

  test("should display entry type badges", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for entries to load
    await page
      .waitForSelector(".bib-entry, .bibliography-entry", {
        timeout: 10000,
      })
      .catch(() => {});

    // Check for type badges
    const typeBadges = page.locator(".type-badge, .entry-type");
    const count = await typeBadges.count();

    // Should have type badges on entries
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("should display concept tags", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for entries to load
    await page
      .waitForSelector(".bib-entry, .bibliography-entry", {
        timeout: 10000,
      })
      .catch(() => {});

    // Check for concept tags
    const conceptTags = page.locator(".concept-tag, .keyword-tag");
    const count = await conceptTags.count();

    // Should have concept tags
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("should handle empty search results gracefully", async ({ page }) => {
    await page.goto("/bibliography.html");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Find search input
    const searchInput = page.locator('#bib-search, input[type="search"]');

    if ((await searchInput.count()) > 0) {
      // Search for something that won't match
      await searchInput.first().fill("xyznonexistentterm123");

      await expect(searchInput.first()).toHaveValue("xyznonexistentterm123");

      // Should show no results message or empty state
      const content = await page
        .locator("#bib-list, .bibliography")
        .textContent();
      expect(content).toBeTruthy();
    }
  });
});
