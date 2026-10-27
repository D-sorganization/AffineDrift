const { test, expect } = require('@playwright/test');

const MOBILE_VIEWPORT = { width: 375, height: 812 };
const DESKTOP_VIEWPORT = { width: 1440, height: 900 };
/** Removing column-gap restores ~322px at 375px (design review #5173). */
const MIN_MOBILE_ARTICLE_COLUMN_PX = 320;
/** ~68ch body measure at 1440px (design review: prose ~772px after slice 1). */
const MAX_PROSE_PARAGRAPH_PX = 780;

const ARTICLE_ROUTES = [
  '/articles/theory-part1.html',
  '/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html',
];

async function waitForStableLayout(page) {
  await page.waitForLoadState('load');
  await page.evaluate(() => document.fonts.ready).catch(() => undefined);
}

async function waitForArticleMath(page) {
  await waitForStableLayout(page);
  await page
    .waitForSelector('mjx-container', { timeout: 20000 })
    .catch(() => undefined);
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
      await waitForStableLayout(page);
      const width = await measureMainColumnWidth(page);
      expect(width).toBeGreaterThanOrEqual(MIN_MOBILE_ARTICLE_COLUMN_PX);
      await assertNoHorizontalOverflow(page);
    });
  }

  test('home has no horizontal overflow at mobile width', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'load' });
    await waitForStableLayout(page);
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
        await waitForStableLayout(page);
        await assertNoHorizontalOverflow(page);
      });
    }
  }
});

test.describe('Article desktop measure and chrome (#5164)', () => {
  test.use({ viewport: DESKTOP_VIEWPORT });

  test('theory part 1 prose and sidebars stay separated', async ({ page }) => {
    await page.goto('/articles/theory-part1.html', { waitUntil: 'load' });
    await waitForArticleMath(page);

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
    await waitForStableLayout(page);

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
    expect(parseFloat(sectionStyles.opacity)).toBeGreaterThanOrEqual(0.99);
    expect(sectionStyles.transform === 'none' || sectionStyles.transform === '').toBeTruthy();
    expect(sectionStyles.inlineTransform).not.toContain('translateY');
    expect(sectionStyles.inlineOpacity).not.toBe('0');
  });

  test('page container does not apply layout-shifting inline min-height (#5211)', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/articles/theory-part1.html', { waitUntil: 'load' });
    await waitForStableLayout(page);

    const containerStyle = await page.evaluate(() => {
      const container = document.getElementById('quarto-content');
      if (!container) {
        return null;
      }
      return {
        inlineMinHeight: container.style.minHeight,
        computedMinHeight: getComputedStyle(container).minHeight,
      };
    });

    expect(containerStyle).toBeTruthy();
    // Inline min-height should either be empty or overridden to avoid CLS
    expect(
      !containerStyle.inlineMinHeight ||
        containerStyle.inlineMinHeight === 'auto' ||
        containerStyle.computedMinHeight === '0px'
    ).toBe(true);
  });
});

test.describe('Programming companion catalog (#5164 round 2)', () => {
  const route = '/models/programming/programs.html';

  test('catalog page keeps title, gutters, and no page-level overflow at 375px', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(route, { waitUntil: 'load' });
    await waitForStableLayout(page);

    await expect(page.locator('#title-block-header')).toBeVisible();
    await expect(page.locator('#title-block-header h1.title')).toBeVisible();

    const layout = await page.evaluate(() => {
      const main = document.querySelector('main#quarto-document-content');
      const rect = main ? main.getBoundingClientRect() : null;
      return {
        mainLeft: rect ? rect.left : 0,
        pageLayoutFull: document
          .getElementById('quarto-content')
          ?.classList.contains('page-layout-full'),
        overflows: document.documentElement.scrollWidth > window.innerWidth,
      };
    });

    expect(layout.pageLayoutFull).toBe(false);
    expect(layout.mainLeft).toBeGreaterThan(0);
    expect(layout.overflows).toBe(false);
  });

  test('catalog page shows margin TOC at 1440px', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(route, { waitUntil: 'load' });
    await waitForStableLayout(page);

    await expect(page.locator('#quarto-margin-sidebar')).toBeVisible();
    await expect(page.locator('#title-block-header h1.title')).toBeVisible();
  });
});
