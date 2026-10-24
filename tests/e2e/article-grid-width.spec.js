const { test, expect } = require('@playwright/test');

const MOBILE_VIEWPORT = { width: 375, height: 812 };
/** ~1.5rem gutters each side at 375px with a 17px root (issue #5164). */
const MIN_MOBILE_ARTICLE_COLUMN_PX = 324;

const ARTICLE_ROUTES = [
  '/articles/theory-part1.html',
  '/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html',
];

async function assertNoHorizontalOverflow(page) {
  const overflows = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth
  );
  expect(overflows).toBe(false);
}

async function measureMainColumnWidth(page) {
  const main = page.locator('main#quarto-document-content');
  await expect(main).toBeVisible();
  const box = await main.boundingBox();
  expect(box).toBeTruthy();
  return box.width;
}

test.describe('Article grid width (#5164)', () => {
  test.use({ viewport: MOBILE_VIEWPORT });

  for (const route of ARTICLE_ROUTES) {
    test(`mobile article column is readable: ${route}`, async ({ page }) => {
      await page.goto(route, { waitUntil: 'domcontentloaded' });
      const width = await measureMainColumnWidth(page);
      expect(width).toBeGreaterThanOrEqual(MIN_MOBILE_ARTICLE_COLUMN_PX);
      await assertNoHorizontalOverflow(page);
    });
  }

  test('home has no horizontal overflow at mobile width', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    await assertNoHorizontalOverflow(page);
  });
});

test.describe('Article grid width — responsive overflow (#5164)', () => {
  const viewports = [
    { label: '375', width: 375, height: 812 },
    { label: '768', width: 768, height: 1024 },
    { label: '1440', width: 1440, height: 900 },
  ];

  const routes = ['/', ...ARTICLE_ROUTES];

  for (const viewport of viewports) {
    for (const route of routes) {
      test(`no page-level horizontal scroll at ${viewport.label}px: ${route}`, async ({
        page,
      }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        const path = route === '/' ? '/index.html' : route;
        await page.goto(path, { waitUntil: 'domcontentloaded' });
        await assertNoHorizontalOverflow(page);
      });
    }
  }
});
