const { test, expect } = require('@playwright/test');

test.describe('Offline Mode (Service Worker)', () => {
  test('should serve cached homepage when offline', async ({ page, context }) => {
    // 1. Online: Navigate to homepage to trigger SW install
    await page.goto('/');
    await expect(page).toHaveTitle(/AffineDrift/);

    // Wait a bit for SW to install and cache
    await page.waitForTimeout(3000);

    // 2. Go Offline
    await context.setOffline(true);

    // 3. Reload homepage
    await page.reload();
    await expect(page).toHaveTitle(/AffineDrift/);

    // Check we are actually offline by checking navigator
    const isOnline = await page.evaluate(() => navigator.onLine);
    expect(isOnline).toBe(false);
  });

  test('should serve offline page for non-cached resources', async ({ page, context }) => {
    // 1. Online: Navigate to homepage
    await page.goto('/');
    await page.waitForTimeout(3000); // Wait for SW

    // 2. Go Offline
    await context.setOffline(true);

    // 3. Navigate to a non-cached page
    // Using a timestamp to ensure unique URL that isn't cached
    const uniqueUrl = `/non-existent-page-${Date.now()}.html`;
    await page.goto(uniqueUrl);

    // 4. Verify offline page content
    // offline.html usually has specific text
    const heading = page.locator('h1, h2');
    await expect(heading).toContainText(/Offline/i);

    // Or check specific text from offline.html if we know it
    // Let's assume it mentions "Offline"
  });
});
