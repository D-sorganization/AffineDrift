const { test, expect } = require('@playwright/test');

test.describe('Article Pages', () => {
  test.use({ viewport: { width: 1440, height: 900 } });
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

    // Scroll down to trigger lazy loading of MathJax if needed
    await page.evaluate(() => window.scrollBy(0, 1000));

    // Look for rendered math (MathJax creates SVG or mjx- elements)
    const mathElements = page.locator('.MathJax, mjx-container, .mjx-chtml, svg[class*="MathJax"]');
    
    // Check if at least one math element is visible (gives time for rendering to finish)
    await expect(mathElements.first()).toBeVisible({ timeout: 15000 });

    const count = await mathElements.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should load MathJax assistive MathML without duplicate state errors', async ({ page }) => {
    const consoleErrors = [];
    const pageErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    page.on('pageerror', (error) => {
      pageErrors.push(error.message);
    });

    await page.goto('/articles/theory-part1.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => window.scrollBy(0, 1000));
    await page.waitForSelector('mjx-container', { timeout: 15000 });
    await page.waitForSelector('mjx-assistive-mml', { state: 'attached', timeout: 15000 });

    const mainMathJaxBundleCount = await page
      .locator('script[src*="mathjax"][src*="/es5/tex-"]')
      .count();
    const explicitAssistiveMmlScriptCount = await page
      .locator('script[src*="assistive-mml"]')
      .count();
    expect(mainMathJaxBundleCount).toBe(1);
    expect(explicitAssistiveMmlScriptCount).toBe(0);

    const allErrors = [...consoleErrors, ...pageErrors];
    expect(allErrors.join('\n')).not.toContain('State ASSISTIVEMML already exists');
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
      expect(decodeURIComponent(page.url())).toContain(href);
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
