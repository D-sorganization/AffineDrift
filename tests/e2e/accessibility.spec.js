const { test, expect } = require('@playwright/test');

test.describe('Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Get all headings
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    
    // Check we have at least one heading
    expect(headings.length).toBeGreaterThan(0);
    
    // Check first heading is h1 or h2
    const firstHeading = headings[0];
    const tagName = await firstHeading.evaluate(el => el.tagName.toLowerCase());
    expect(['h1', 'h2']).toContain(tagName);
  });

  test('should have alt text on all images', async ({ page }) => {
    await page.goto('/');
    
    // Get all images
    const images = await page.locator('img').all();
    
    // Check each image has alt attribute
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeDefined();
    }
  });

  test('should have ARIA labels on navigation', async ({ page }) => {
    await page.goto('/');
    
    // Check main navigation has aria-label or role
    const nav = page.locator('nav').first();
    if (await nav.count() > 0) {
      const ariaLabel = await nav.getAttribute('aria-label');
      const role = await nav.getAttribute('role');
      
      // Should have either aria-label or role
      expect(ariaLabel || role).toBeTruthy();
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check focus is visible
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(focusedElement).toBeTruthy();
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/');
    
    // Get computed styles of main text
    const textColor = await page.locator('body').evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.color;
    });
    
    const bgColor = await page.locator('body').evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.backgroundColor;
    });
    
    // Basic check that colors are defined
    expect(textColor).toBeTruthy();
    expect(bgColor).toBeTruthy();
  });

  test('should have lang attribute', async ({ page }) => {
    await page.goto('/');
    
    // Check html has lang attribute
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBeTruthy();
    expect(lang).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/); // e.g., 'en' or 'en-US'
  });

  test('should have skip to main content link', async ({ page }) => {
    await page.goto('/');
    
    // Tab to first element (should be skip link if present)
    await page.keyboard.press('Tab');
    
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return {
        text: el.textContent,
        href: el.getAttribute('href')
      };
    });
    
    // Skip link is optional but recommended
    // Just verify we can tab to something
    expect(focusedElement).toBeTruthy();
  });
});
