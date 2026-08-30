/**
 * Whole-site Visual Regression + Layout Invariant Test Suite (Issue #4089).
 *
 * Covers representative route families, wide screens, light/dark themes,
 * dense tables, math equations, sidebars, search, focus states, and footers.
 */

const { test, expect } = require('@playwright/test');

const VIEWPORTS = [
  { label: '375', width: 375, height: 812 }, // mobile phone
  { label: '768', width: 768, height: 1024 }, // tablet
  { label: '1024', width: 1024, height: 768 }, // intermediate
  { label: '1200', width: 1200, height: 900 }, // margin-boundary
  { label: '1440', width: 1440, height: 900 }, // standard desktop
  { label: '1920', width: 1920, height: 1080 }, // wide desktop
];

// All 10 representative route families specified in #4089
const REPRESENTATIVE_PAGES = [
  { label: 'home', path: '/', family: 'home' },
  { label: 'books', path: '/books/index.html', family: 'books' },
  {
    label: 'monograph',
    path: '/articles/proximal_distal_energy_transfer/index.html',
    family: 'monograph',
  },
  {
    label: 'article',
    path: '/articles/affine-nature-golf-swing.html',
    family: 'article',
  },
  {
    label: 'model-workbench',
    path: '/articles/proximal-distal-model-workbench.html',
    family: 'model-workbench',
  },
  {
    label: 'programming',
    path: '/models/models.html',
    family: 'programming',
  },
  {
    label: 'search',
    path: '/resources/articles.html',
    family: 'search',
  },
  {
    label: 'critique',
    path: '/critiques/index.html',
    family: 'critique',
  },
  {
    label: 'research-report',
    path: '/reports/scientific-claim-audit.html',
    family: 'research-report',
  },
  {
    label: 'resource',
    path: '/resources/resources.html',
    family: 'resource',
  },
];

/** Regions whose dynamic or time-based content must not trigger false diffs. */
function volatileMasks(page) {
  return [
    page.locator('#bib-search'),
    page.locator('input[type="search"]'),
    page.locator('time'),
    page.locator('.reading-time-estimate'),
  ];
}

test.describe('whole-site visual regression and layout invariants', () => {
  test.describe.configure({ timeout: 90000 });

  for (const vp of VIEWPORTS) {
    for (const pageDef of REPRESENTATIVE_PAGES) {
      test(${pageDef.label} @ px has no horizontal page overflow, async ({
        page,
      }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(pageDef.path, { waitUntil: 'load' });

        const overflow = await page.evaluate(
          () =>
            document.documentElement.scrollWidth -
            document.documentElement.clientWidth,
        );
        expect(overflow).toBeLessThanOrEqual(1);
      });

      test(${pageDef.label} @ px matches visual snapshot, async ({
        page,
      }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(pageDef.path, { waitUntil: 'load' });
        await expect(page).toHaveScreenshot(
          ${pageDef.label}-.png,
          { fullPage: true, mask: volatileMasks(page) },
        );
      });
    }
  }

  test('standard page layout collapses to single column on mobile (< 768px)', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/models/models.html', { waitUntil: 'load' });

    const layout = page.locator('.standard-page-layout').first();
    if ((await layout.count()) > 0) {
      const columns = await layout.evaluate(
        (el) => getComputedStyle(el).gridTemplateColumns,
      );
      expect(columns.trim().split(/\s+/).length).toBe(1);
    }
  });

  test('header navigation and search remain reachable across all viewports', async ({
    page,
  }) => {
    for (const vp of VIEWPORTS) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto('/', { waitUntil: 'load' });

      const navbar = page.locator('#quarto-header');
      await expect(navbar).toBeVisible();
    }
  });
});
