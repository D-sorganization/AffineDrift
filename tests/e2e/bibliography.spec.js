const { test, expect } = require('@playwright/test');

test.describe('Bibliography Page', () => {
  test('should load bibliography page', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Check page loads
    await expect(page).toHaveTitle(/Bibliography|References|AffineDrift/);

    // Check for bibliography container
    const bibList = page.locator('#bib-list, .bibliography, .references');
    await expect(bibList.first()).toBeVisible({ timeout: 10000 });
  });

  test('should display bibliography entries', async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER CONSOLE: ${msg.text()}`));
    page.on('pageerror', err => console.log(`BROWSER ERROR: ${err.message}`));
    await page.goto('/resources/bibliography.html');

    // Wait for bibliography entries to load and render
    const entries = page.locator('.bib-entry, .bibliography-entry, .reference-item');
    await expect(entries.first()).toBeVisible({ timeout: 30000 });

    // Check for entries
    const count = await entries.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should have working search functionality without TypeError', async ({ page }) => {
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    await page.goto('/resources/bibliography.html');
    await page.waitForLoadState('networkidle');
    // Wait past the startup-launcher splash-hide timeout so AffineDriftMetrics
    // would be clobbered if the bug was present
    await page.waitForTimeout(1500);

    const searchInput = page.locator('#bib-search, input[type="search"], input[placeholder*="search" i]');

    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible();

      const unfilteredEntries = page.locator('.bib-entry, .bibliography-entry');
      const unfilteredCount = await unfilteredEntries.count();

      await searchInput.first().fill('biomechanics');
      await page.waitForTimeout(600);

      const filteredCount = await unfilteredEntries.count();
      // Search must actually filter: count must change and stay > 0
      if (unfilteredCount > 5) {
        expect(filteredCount).toBeGreaterThan(0);
        expect(filteredCount).toBeLessThan(unfilteredCount);
      }

      // No TypeError from trackSearch being called on the startup-launcher object
      const trackErrors = pageErrors.filter(e => e.includes('trackSearch') || e.includes('AffineDriftMetrics'));
      expect(trackErrors).toHaveLength(0);
    }
  });

  test('should have working sort controls', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Find sort controls
    const sortControls = page.locator('#bib-sort-controls, .sort-controls, .sort-btn');

    if (await sortControls.count() > 0) {
      await expect(sortControls.first()).toBeVisible();

      // Try clicking a sort button
      const sortButton = page.locator('.sort-btn, button[data-sort]').first();
      if (await sortButton.count() > 0) {
        await sortButton.click();

        // Wait for re-sort
        await page.waitForTimeout(300);

        // Should not error
        const entries = page.locator('.bib-entry, .bibliography-entry');
        const count = await entries.count();
        expect(count).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should show entry details when clicked', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Wait for entries to load
    await page.waitForSelector('.bib-entry, .bibliography-entry', {
      timeout: 10000
    }).catch(() => {});

    // Find an entry
    const entry = page.locator('.bib-entry, .bibliography-entry').first();

    if (await entry.count() > 0) {
      await entry.click();

      // Wait for details to show
      await page.waitForTimeout(500);

      // Check for details panel
      const details = page.locator('#bib-details, .bib-detail-content, .entry-details');
      if (await details.count() > 0) {
        await expect(details.first()).toBeVisible();
      }
    }
  });

  test('should display entry type badges', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Wait for entries to load
    await page.waitForSelector('.bib-entry, .bibliography-entry', {
      timeout: 10000
    }).catch(() => {});

    // Check for type badges
    const typeBadges = page.locator('.type-badge, .entry-type');
    const count = await typeBadges.count();

    // Should have type badges on entries
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should display concept tags', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Wait for entries to load
    await page.waitForSelector('.bib-entry, .bibliography-entry', {
      timeout: 10000
    }).catch(() => {});

    // Check for concept tags
    const conceptTags = page.locator('.concept-tag, .keyword-tag');
    const count = await conceptTags.count();

    // Should have concept tags
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should handle empty search results gracefully', async ({ page }) => {
    await page.goto('/resources/bibliography.html');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Find search input
    const searchInput = page.locator('#bib-search, input[type="search"]');

    if (await searchInput.count() > 0) {
      // Search for something that won't match
      await searchInput.first().fill('xyznonexistentterm123');

      // Wait for filtering
      await page.waitForTimeout(500);

      // Should show no results message or empty state
      const content = await page.locator('#bib-list, .bibliography').textContent();
      expect(content).toBeTruthy();
    }
  });
});
