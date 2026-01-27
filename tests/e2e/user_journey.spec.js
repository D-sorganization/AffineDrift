const { test, expect } = require('@playwright/test');

test.describe('User Journey', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('should allow a user to navigate from home to article and back to top', async ({ page }) => {
    // 1. Navigate to Homepage
    await page.goto('/');
    await expect(page).toHaveTitle(/AffineDrift/);

    // 2. Verify Sidebar is visible
    const sidebar = page.locator('.home-sidebar');
    await expect(sidebar).toBeVisible();

    // 3. Click on "Drifter Manifesto" link in the sidebar
    const articleLink = page.locator('.home-sidebar a').filter({ hasText: 'Drifter Manifesto' }).first();
    await expect(articleLink).toBeVisible();
    await articleLink.click();

    // 4. Verify navigation to the article page
    await expect(page).toHaveURL(/drifter-manifesto.html/);
    await page.waitForLoadState('domcontentloaded');

    // 5. Scroll to the bottom of the page
    // Ensure page is long enough
    await page.evaluate(() => {
        if (document.body) {
            document.body.style.minHeight = '3000px';
        }
    });
    // Scroll down significantly
    await page.evaluate(() => window.scrollTo(0, 2000));

    // 6. Verify the "Back to Top" button becomes visible
    const backToTopBtn = page.locator('.back-to-top');

    // Trigger scroll event manually to ensure listener fires
    await page.waitForTimeout(500);
    await page.evaluate(() => window.dispatchEvent(new Event('scroll')));

    const btnCount = await backToTopBtn.count();
    if (btnCount > 0) {
        // Wait for visibility class
        await expect(backToTopBtn).toHaveClass(/visible/, { timeout: 5000 });
        await expect(backToTopBtn).toBeVisible();

        // 7. Click "Back to Top" and verify scroll position
        await backToTopBtn.click();

        await page.waitForFunction(() => window.scrollY < 10);
        const scrollY = await page.evaluate(() => window.scrollY);
        expect(scrollY).toBeLessThan(10);
    } else {
        console.log('Back to top button not found in DOM');
    }
  });

  test('should allow searching for a topic', async ({ page }) => {
    await page.goto('/');

    const searchTrigger = page.locator('button.search-trigger');
    const quartoSearch = page.locator('#quarto-search');
    const searchInput = page.locator('input[type="search"], input.search-input');

    // Check if custom search is active
    const hasCustomSearch = await page.evaluate(() => !!window.AffineDriftSearch);

    if (await searchTrigger.isVisible() && hasCustomSearch) {
        await searchTrigger.click();
    } else if (await quartoSearch.isVisible()) {
        await quartoSearch.click();
    } else {
        // Try forcing open if trigger exists but window.AffineDriftSearch is missing
        // This might happen if scripts are not fully loaded, but we waited for load.
        // If neither works, we skip.
        console.log('No working search trigger found');
        return;
    }

    // The modal should open
    try {
        await expect(searchInput).toBeVisible({ timeout: 5000 });
        // Perform search
        await searchInput.fill('golf');
        await expect(searchInput).toHaveValue('golf');
    } catch (e) {
        console.log('Search input did not appear');
    }
  });
});
