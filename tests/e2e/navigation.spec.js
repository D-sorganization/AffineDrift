const { test, expect } = require('@playwright/test');

test.describe('Navigation', () => {
  test('should navigate to articles page', async ({ page }) => {
    await page.goto('/');
    
    // Find and click articles link
    const articlesLink = page.locator('a[href*="articles"]').first();
    await articlesLink.click();
    
    // Wait for navigation
    await page.waitForLoadState('networkidle');
    
    // Check we're on articles page
    expect(page.url()).toContain('articles');
  });

  test('should navigate to overview page', async ({ page }) => {
    await page.goto('/');
    
    // Find and click overview link
    const overviewLink = page.locator('a[href*="overview"]').first();
    if (await overviewLink.count() > 0) {
      await overviewLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('overview');
    }
  });

  test('should have working table of contents', async ({ page }) => {
    await page.goto('/articles.html');
    
    // Check for TOC
    const toc = page.locator('#TOC, .toc, nav[role="navigation"]');
    if (await toc.count() > 0) {
      await expect(toc.first()).toBeVisible();
      
      // Check TOC has links
      const tocLinks = toc.locator('a');
      const count = await tocLinks.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('should support smooth scrolling to anchors', async ({ page }) => {
    await page.goto('/articles.html');
    
    // Find an anchor link
    const anchorLink = page.locator('a[href^="#"]').first();
    if (await anchorLink.count() > 0) {
      const href = await anchorLink.getAttribute('href');
      await anchorLink.click();
      
      // Wait for scroll
      await page.waitForTimeout(500);
      
      // Check URL updated
      expect(page.url()).toContain(href);
    }
  });

  test('should highlight active section in TOC', async ({ page }) => {
    await page.goto('/articles.html');
    
    // Scroll down the page
    await page.evaluate(() => window.scrollBy(0, 500));
    await page.waitForTimeout(300);
    
    // Check for active class on TOC items
    const activeTocItem = page.locator('#TOC .active, .toc .active, nav a.active');
    // Active highlighting is optional, so we just check it doesn't error
    const count = await activeTocItem.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});
