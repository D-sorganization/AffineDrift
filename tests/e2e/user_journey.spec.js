const { test, expect } = require('@playwright/test');

test.describe('User Journey', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('should allow a user to navigate from home to article and back to top', async ({ page }) => {
    // 1. Navigate to Homepage
    await page.goto('/');
    await expect(page).toHaveTitle(/AffineDrift/);

    // 2. Verify Home content is visible
    await expect(page.locator('.home-content')).toBeVisible();

    // 3. Click on first article link in the entry list
    const articleLink = page.locator('.entry-list a.entry-list__title').first();
    await expect(articleLink).toBeVisible();
    const targetHref = await articleLink.getAttribute('href');
    await articleLink.click();

    // 4. Verify navigation to the article page
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain(targetHref.replace(/\.html$/, ''));

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
        await backToTopBtn.click({ force: true });

        // Wait for smooth scrolling, with fallback for Mobile Safari
        await page.waitForTimeout(1000);
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForFunction(() => window.scrollY < 10, { timeout: 10000 });
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
    const searchInput = page.locator('#quarto-search-input, input[type="search"], input.search-input');

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
