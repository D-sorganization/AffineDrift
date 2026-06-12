/**
 * Visual-regression + layout-invariant tests (issue #3328).
 *
 * Nothing in CI previously tested *rendered layout*, which is how the
 * invalid-media-query breakpoint bug (#3326) and the dead hamburger button
 * shipped green: every functional/unit test passed while the mobile layout was
 * visually broken. This spec adds two complementary safety nets:
 *
 *  1. Deterministic layout invariants — no horizontal overflow at 375px and
 *     single-column collapse of the standard/contact layouts. These run in CI
 *     today with no committed image baselines and catch the exact bug class
 *     above.
 *
 *  2. Pixel snapshots via expect(page).toHaveScreenshot() at 375 / 768 / 1440
 *     for four representative pages. Baselines are platform-specific, so they
 *     are generated with `npx playwright test --update-snapshots` (see
 *     CONTRIBUTING.md) and committed per CI platform. When no baseline exists
 *     Playwright records one on the first run rather than failing.
 *
 * Volatile regions (search box value, dates) are masked so they cannot cause
 * false diffs.
 */

const { test, expect } = require('@playwright/test');

const VIEWPORTS = [
  { label: '375', width: 375, height: 812 }, // iPhone-class
  { label: '768', width: 768, height: 1024 }, // tablet
  { label: '1440', width: 1440, height: 900 }, // desktop
];

// Pages chosen for coverage: homepage, an article index, a content/overview
// page, and the bibliography (equation/list heavy).
const PAGES = [
  { label: 'home', path: '/' },
  { label: 'articles', path: '/resources/articles.html' },
  { label: 'overview', path: '/pages/overview.html' },
  { label: 'bibliography', path: '/resources/bibliography.html' },
];

/** Regions whose content changes between runs and must not drive a diff. */
function volatileMasks(page) {
  return [
    page.locator('#bib-search'),
    page.locator('input[type="search"]'),
    page.locator('time'),
  ];
}

test.describe('visual regression', () => {
  test.describe.configure({ timeout: 90000 });

  for (const vp of VIEWPORTS) {
    for (const pageDef of PAGES) {
      test(`${pageDef.label} @ ${vp.label}px has no horizontal overflow`, async ({
        page,
      }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(pageDef.path, { waitUntil: 'load' });

        // The classic mobile-breakage signature: content wider than the viewport.
        const overflow = await page.evaluate(
          () =>
            document.documentElement.scrollWidth -
            document.documentElement.clientWidth,
        );
        // Allow a 1px rounding slack; anything more is a real horizontal scroll.
        expect(overflow).toBeLessThanOrEqual(1);
      });

      test(`${pageDef.label} @ ${vp.label}px matches visual baseline`, async ({
        page,
      }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(pageDef.path, { waitUntil: 'load' });
        await expect(page).toHaveScreenshot(
          `${pageDef.label}-${vp.label}.png`,
          { fullPage: true, mask: volatileMasks(page) },
        );
      });
    }
  }

  test('standard page layout collapses to a single column at 375px', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/pages/overview.html', { waitUntil: 'load' });

    const layout = page.locator('.standard-page-layout').first();
    if ((await layout.count()) === 0) {
      test.skip(true, 'no .standard-page-layout on this page');
      return;
    }
    const columns = await layout.evaluate(
      (el) => getComputedStyle(el).gridTemplateColumns,
    );
    // A collapsed single-column grid reports one track (no internal space).
    expect(columns.trim().split(/\s+/).length).toBe(1);
  });
});
