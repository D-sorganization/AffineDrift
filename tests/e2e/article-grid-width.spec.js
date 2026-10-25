const { test, expect } = require('@playwright/test');

const MOBILE_VIEWPORT = { width: 375, height: 812 };
const DESKTOP_VIEWPORT = { width: 1440, height: 900 };
/** Removing column-gap restores ~322px at 375px (design review #5173). */
const MIN_MOBILE_ARTICLE_COLUMN_PX = 320;
const MAX_PROSE_PARAGRAPH_PX = 720;

const ARTICLE_ROUTES = [
  '/articles/theory-part1.html',
  '/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html',
];

async function waitForArticleLayout(page) {
  await page.waitForLoadState('load');
  await page
    .waitForFunction(
      () =>
        typeof window.MathJax !== 'undefined' &&
        (window.MathJax.startup?.promise === undefined ||
          window.MathJax.startup?.document?.state?.() >= 6),
      { timeout: 20000 }
    )
    .catch(() => undefined);
  await page.evaluate(async () => {
    if (window.MathJax?.startup?.promise) {
      await window.MathJax.startup.promise;
    }
    await document.fonts.ready;
  });
}

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

function boxesOverlap(a, b) {
  if (!a || !b) {
    return false;
  }
  return a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
}

test.describe('Article grid width (#5164)', () => {
  test.use({ viewport: MOBILE_VIEWPORT });

  for (const route of ARTICLE_ROUTES) {
    test(`mobile article column is readable: ${route}`, async ({ page }) => {
      await page.goto(route, { waitUntil: 'load' });
      await waitForArticleLayout(page);
      const width = await measureMainColumnWidth(page);
      expect(width).toBeGreaterThanOrEqual(MIN_MOBILE_ARTICLE_COLUMN_PX);
      await assertNoHorizontalOverflow(page);
    });
  }

  test('home has no horizontal overflow at mobile width', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'load' });
    await waitForArticleLayout(page);
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
        await page.goto(path, { waitUntil: 'load' });
        await waitForArticleLayout(page);
        await assertNoHorizontalOverflow(page);
      });
    }
  }
});

test.describe('Article desktop measure and chrome (#5164)', () => {
  test.use({ viewport: DESKTOP_VIEWPORT });

  test('theory part 1 prose and sidebars stay separated', async ({ page }) => {
    await page.goto('/articles/theory-part1.html', { waitUntil: 'load' });
    await waitForArticleLayout(page);

    const layout = await page.evaluate(() => {
      const rect = (el) => (el ? el.getBoundingClientRect() : null);
      const main = document.querySelector('main#quarto-document-content');
      const paragraph = main?.querySelector('p');
      return {
        main: rect(main),
        sidebar: rect(document.getElementById('quarto-sidebar')),
        marginToc: rect(document.getElementById('quarto-margin-sidebar')),
        paragraphWidth: paragraph ? paragraph.getBoundingClientRect().width : null,
      };
    });

    expect(layout.paragraphWidth).toBeLessThanOrEqual(MAX_PROSE_PARAGRAPH_PX);
    expect(boxesOverlap(layout.main, layout.sidebar)).toBe(false);
    expect(boxesOverlap(layout.main, layout.marginToc)).toBe(false);
  });
});

test.describe('Article section reveal CLS guard (#5164)', () => {
  test('article sections stay visible without transform shifts', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/articles/theory-part1.html', { waitUntil: 'load' });
    await waitForArticleLayout(page);

    const sectionStyles = await page.evaluate(() => {
      const section = document.querySelector('#quarto-document-content section');
      if (!section) {
        return null;
      }
      const computed = getComputedStyle(section);
      return {
        opacity: computed.opacity,
        transform: computed.transform,
        inlineTransform: section.style.transform,
        inlineOpacity: section.style.opacity,
      };
    });

    expect(sectionStyles).toBeTruthy();
    expect(Number(sectionStyles.opacity)).toBeGreaterThanOrEqual(1);
    expect(sectionStyles.transform === 'none' || sectionStyles.transform === '').toBeTruthy();
    expect(sectionStyles.inlineTransform).not.toContain('translateY');
    expect(sectionStyles.inlineOpacity).not.toBe('0');
  });
});
