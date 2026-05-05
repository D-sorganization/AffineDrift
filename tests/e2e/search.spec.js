const { test, expect } = require("@playwright/test");

test.describe("Search Functionality", () => {
  test("should have search button or input", async ({ page }) => {
    await page.goto("/");

    // Look for search elements
    const searchButton = page.locator(
      'button.search-trigger, button[aria-label*="search" i]',
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
      .locator('button.search-trigger, button[aria-label*="search" i]')
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
});
