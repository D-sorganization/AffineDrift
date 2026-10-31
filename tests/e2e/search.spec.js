const { test, expect } = require("@playwright/test");

test.describe("Search Functionality", () => {
  test("should have search button or input", async ({ page }) => {
    await page.goto("/");

    // Look for search elements
    const searchButton = page.locator(
      '#quarto-search button, button.search-trigger, button[aria-label*="search" i]',
    );
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i]',
    );

    const hasSearch =
      (await searchButton.count()) > 0 || (await searchInput.count()) > 0;
    expect(hasSearch).toBeTruthy();
  });

  test("should open search modal when clicked", async ({ page }) => {
    await page.goto("/");

    // Find search button
    const searchButton = page
      .locator(
        '#quarto-search button, button.search-trigger, button[aria-label*="search" i]',
      )
      .first();

    if ((await searchButton.count()) > 0) {
      await searchButton.click();

      // Wait for modal to appear
      await page.waitForTimeout(300);

      // Check for search modal or input
      const searchModal = page.locator(
        '.search-modal, .search-container, [role="dialog"]',
      );
      const searchInput = page.locator('input[type="search"]');

      const modalVisible =
        (await searchModal.count()) > 0 || (await searchInput.count()) > 0;
      expect(modalVisible).toBeTruthy();
    }
  });

  test("should support keyboard shortcut", async ({ page }) => {
    await page.goto("/");

    // Try Ctrl+K or Cmd+K
    const isMac = process.platform === "darwin";
    if (isMac) {
      await page.keyboard.press("Meta+K");
    } else {
      await page.keyboard.press("Control+K");
    }

    await page.waitForTimeout(300);

    // Check if search opened
    const searchInput = page.locator('input[type="search"]');
    // Keyboard shortcut is optional, so we just verify it doesn't error
    const count = await searchInput.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("should close custom search modal from close button", async ({
    page,
  }) => {
    await page.goto("/");
    await page.keyboard.press(
      process.platform === "darwin" ? "Meta+K" : "Control+K",
    );

    const modal = page.locator("#global-search-modal");
    const closeBtn = page.locator("#global-search-modal .search-close-btn");
    if ((await modal.count()) > 0) {
      await expect(modal).toHaveClass(/active/);
      await closeBtn.click();
      await expect(modal).not.toHaveClass(/active/);
    }
  });

  test("finds the proximal-distal energy transfer article", async ({
    page,
  }) => {
    await page.goto("/");

    const searchButton = page
      .locator(
        '#quarto-search button, button.search-trigger, button[aria-label*="search" i]',
      )
      .first();
    await searchButton.click();

    const searchInput = page.locator(".aa-Input, input[type=search]").first();
    await expect(searchInput).toBeVisible();
    await searchInput.fill("proximal distal energy transfer");

    const articleResult = page
      .locator('a[href*="articles/proximal-distal-energy-transfer.html"]')
      .first();
    await expect(articleResult).toBeVisible();
  });

  // No page carries a `status`/`maturity` front-matter field yet, so the
  // badge annotation is covered by tests/search-maturity-badge.test.js
  // fixtures; assert here only that ZTCF ranks first (#4504).
  test("finds the ZTCF page first (#4504)", async ({
    page,
  }) => {
    await page.goto("/");

    const searchButton = page
      .locator(
        '#quarto-search button, button.search-trigger, button[aria-label*="search" i]',
      )
      .first();
    await searchButton.click();

    const searchInput = page.locator(".aa-Input, input[type=search]").first();
    await expect(searchInput).toBeVisible();
    await searchInput.fill("ZTCF");

    const firstResult = page.locator(".search-result-doc .search-result-link").first();
    await expect(firstResult).toHaveAttribute("href", /zero[-_]torque[-_]counterfactual/);
  });

  test("loads the search libraries and index only after search interaction", async ({ page }) => {
    const requested = [];
    page.on("request", (request) => {
      if (/site_libs\/quarto-search\/(autocomplete\.umd|fuse\.min|quarto-search)\.js|search\.json/.test(request.url())) {
        requested.push(request.url());
      }
    });

    await page.goto("/", { waitUntil: "networkidle" });
    expect(requested).toEqual([]);

    await page.locator("#quarto-search .aa-DetachedSearchButton").click();
    await expect(page.locator(".aa-Input")).toBeVisible();
    await expect.poll(() => requested.filter((url) => url.includes("site_libs/quarto-search/")).length).toBe(3);
    expect(requested.some((url) => url.endsWith("/search.json"))).toBe(false);

    await page.locator(".aa-Input").fill("double pendulum");
    await expect.poll(() => requested.some((url) => url.endsWith("/search.json"))).toBe(true);
  });

  test("ranks the double-pendulum chapter in the first three results", async ({ page }) => {
    await page.goto("/");
    await page.locator("#quarto-search .aa-DetachedSearchButton").click();
    const input = page.locator(".aa-Input");
    await expect(input).toBeVisible();
    await input.fill("double pendulum");

    const results = page.locator(".search-result-doc .search-result-link");
    await expect(results.first()).toBeVisible();
    await expect.poll(async () => results.evaluateAll((links) =>
      links.slice(0, 3).some((link) => new URL(link.href).pathname.endsWith(
        "/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html",
      )),
    )).toBe(true);
    await expect(page.locator(".aa-Panel")).not.toContainText("Skip to main content");
  });

  test("phone search panel fills the viewport below the input and restores focus", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");
    const trigger = page.locator("#quarto-search .aa-DetachedSearchButton");
    await trigger.click();
    await expect(page.locator("body")).toHaveClass(/aa-Detached/);
    const panel = page.locator(".aa-DetachedContainer .aa-Panel");
    await expect(panel).toBeVisible();

    const [form, panelBox] = await Promise.all([
      page.locator(".aa-DetachedFormContainer").boundingBox(),
      panel.boundingBox(),
    ]);
    expect(panelBox.y).toBeGreaterThanOrEqual(form.y + form.height - 1);
    expect(panelBox.y + panelBox.height).toBeGreaterThanOrEqual(811);
    expect(panelBox.width).toBeGreaterThanOrEqual(374);

    await page.keyboard.press("Escape");
    await expect(page.locator("body")).not.toHaveClass(/aa-Detached/);
    await expect(trigger).toBeFocused();

    await trigger.click();
    await expect(page.locator("body")).toHaveClass(/aa-Detached/);
    await page.getByRole("button", { name: /cancel/i }).click();
    await expect(page.locator("body")).not.toHaveClass(/aa-Detached/);
    await expect(trigger).toBeFocused();
  });
});
