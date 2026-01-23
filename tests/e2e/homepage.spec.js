const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test('should load successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/AffineDrift/);
    
    // Check main heading exists
    const heading = page.locator('h1, h2').first();
    await expect(heading).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await page.goto('/');
    
    // Check navbar exists
    const navbar = page.locator('nav.navbar, .quarto-navbar');
    await expect(navbar).toBeVisible();
    
    // Check for navigation links
    const navLinks = page.locator('nav a, .navbar a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should have accessible logo', async ({ page }) => {
    await page.goto('/');
    
    // Check logo has alt text
    const logo = page.locator('img[alt*="AffineDrift"], img[alt*="Logo"]').first();
    if (await logo.count() > 0) {
      await expect(logo).toHaveAttribute('alt');
    }
  });

  test('should be mobile responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check page loads on mobile
    await expect(page.locator('body')).toBeVisible();
    
    // Check content is not overflowing
    const body = await page.locator('body').boundingBox();
    expect(body.width).toBeLessThanOrEqual(375);
  });

  test('should have no console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Allow some common non-critical errors
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('ServiceWorker')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });
});
