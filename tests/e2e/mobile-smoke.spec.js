const { test, expect } = require('@playwright/test');
const audit = require('../../config/mobile-layout-audit-routes.json');

/**
 * Phone-viewport smoke test (#5316) over the phone layout audit manifest (#5313).
 *
 * Routes and viewports come from config/mobile-layout-audit-routes.json, so the
 * audit set has one source; config/lighthouserc.json must list the same routes
 * (tests/test_mobile_layout_audit_config.py checks both). Runs under the chromium
 * project with touch, so the e2e-tests job picks it up without a new project or job.
 * Touch-target size (#5314) and full-layout side padding (#5323) are covered by
 * their own specs.
 */
for (const { label, width, height } of audit.viewports) {
  test.describe(`Mobile smoke at ${width}x${height} ${label} (#5316, #5313)`, () => {
    test.use({ viewport: { width, height }, isMobile: true, hasTouch: true });
    test.describe.configure({ timeout: 90000 });

    for (const route of audit.routes) {
      test(`${route} renders for phones without horizontal scroll`, async ({ page }) => {
        const response = await page.goto(route, {
          waitUntil: 'load',
          timeout: 60000,
        });
        expect(response && response.ok()).toBeTruthy();
        await expect(page.locator('body')).toBeVisible();

        const viewportMeta = await page.locator('meta[name="viewport"]').getAttribute('content');
        expect(viewportMeta).toContain('width=device-width');

        const overflow = await page.evaluate(() => ({
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
        }));
        expect(overflow.scrollWidth, 'page scrolls horizontally').toBeLessThanOrEqual(
          overflow.innerWidth,
        );
      });

      test(`${route} collapses the navbar behind a working toggle`, async ({ page }) => {
        await page.goto(route, { waitUntil: 'load', timeout: 60000 });
        const toggle = page.locator('.navbar-toggler').first();
        const menu = page.locator('#navbarCollapse');
        await expect(toggle).toBeVisible();
        await expect(menu).toBeHidden();

        await toggle.tap();
        await expect(menu).toBeVisible();
      });
    }
  });
}
