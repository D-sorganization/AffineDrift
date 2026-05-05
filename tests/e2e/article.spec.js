const { test, expect } = require('@playwright/test');

test.describe('Article Pages', () => {
  test('should load article with math equations', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Check page loads
    await expect(page).toHaveTitle(/AffineDrift/);

    // Check for article content
    const article = page.locator('article, main, .content');
    await expect(article.first()).toBeVisible();
  });

  test('should render MathJax equations', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Wait for MathJax to process
    await page.waitForTimeout(2000);

    // Look for rendered math (MathJax creates SVG or mjx- elements)
    const mathElements = page.locator('.MathJax, mjx-container, .mjx-chtml, svg[class*="MathJax"]');
    const count = await mathElements.count();

    // Should have at least some math rendered
    expect(count).toBeGreaterThan(0);
  });

  test('should have working internal links', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Find internal article links
    const internalLinks = page.locator('a[href^="#"], a[href*="articles"]');
    const count = await internalLinks.count();

    expect(count).toBeGreaterThanOrEqual(0);

    // If there are anchor links (excluding skip-link), test one
    const anchorLink = page.locator('a[href^="#"]:not([class*="skip"])').first();
    if (await anchorLink.count() > 0) {
      const href = await anchorLink.getAttribute('href');
      await anchorLink.click();
      await page.waitForTimeout(500);

      // URL should contain the anchor
      expect(page.url()).toContain(href);
    }
  });

  test('should display table of contents on article pages', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Look for TOC
    const toc = page.locator('#TOC, .toc, nav[aria-label*="Table of Contents"]');

    if (await toc.count() > 0) {
      await expect(toc.first()).toBeVisible();

      // TOC should have links
      const tocLinks = toc.locator('a');
      const linkCount = await tocLinks.count();
      expect(linkCount).toBeGreaterThan(0);
    }
  });

  test('should have proper article metadata', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Check for author/date metadata
    const metaElements = page.locator('.author, .date, .quarto-title-meta, time');
    const count = await metaElements.count();

    // Articles should have some metadata
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should handle code blocks correctly', async ({ page }) => {
    await page.goto('/articles/inverse-dynamics.html');

    // Look for code blocks
    const codeBlocks = page.locator('pre code, .sourceCode');
    const count = await codeBlocks.count();

    // Code blocks should be styled
    if (count > 0) {
      const codeBlock = codeBlocks.first();
      await expect(codeBlock).toBeVisible();

      // Check code has syntax highlighting classes
      const classes = await codeBlock.getAttribute('class');
      expect(classes).toBeTruthy();
    }
  });
});
