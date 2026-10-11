const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

// Exercise the supported reduced-motion mode so offscreen reveal transitions
// cannot distort contrast scans or full-page screenshots.
test.use({ reducedMotion: 'reduce' });

// Navigation pages should not embed the 995-entry scholarly bibliography.
// These document-byte limits supplement, never replace, runtime budgets.
const DOCUMENT_BUDGETS = {
  '/index.html': 100000,
  '/pages/start-here.html': 100000,
  '/pages/how-to-read.html': 120000,
  '/resources/articles.html': 180000,
};

for (const [route, limit] of Object.entries(DOCUMENT_BUDGETS)) {
  test(`navigation document stays focused: ${route}`, async ({ page }) => {
    const response = await page.goto(route);
    expect(response.ok()).toBeTruthy();
    expect((await response.body()).length).toBeLessThan(limit);
    await expect(page.locator('meta[name="citation_reference"]')).toHaveCount(0);
    await expect(page.locator('#quarto-header')).toBeVisible();
  });
}

test('home has one primary action, unique featured books, and working navigation', async ({ page }) => {
  await page.goto('/');
  const actions = page.locator('.home-hero__actions a');
  await expect(actions).toHaveCount(1);
  await expect(page.getByRole('heading', { name: /^Featured Reading/ })).toBeVisible();
  await expect(page.locator('main a[href*="The_Physics_of_Golf/quarto/"]')).toHaveCount(1);
  await actions.click();
  await expect(page).toHaveURL(/pages\/start-here.html$/);
});

test('three goal paths and specialist paths resolve to real destinations', async ({ page }) => {
  await page.goto('/pages/start-here.html');
  const choices = page.locator('#choose-your-path .resource-card');
  await expect(choices).toHaveCount(3);
  const links = page.locator('#choose-your-path a[href*="on-ramp-paths.html"]');
  const targets = await links.evaluateAll(nodes => nodes.map(node => node.href));
  for (const target of targets) {
    const response = await page.request.get(target);
    expect(response.ok()).toBeTruthy();
    await page.goto(target);
    const anchor = new URL(target).hash;
    if (anchor) await expect(page.locator(anchor)).toBeVisible();
  }
});

test('article metadata preserves claim limits and links readable prerequisites', async ({ page }) => {
  await page.goto('/articles/theory-part1.html');
  const prerequisite = page.locator('.page-header-item--prerequisites a');
  await expect(prerequisite).toHaveText('How to Read This Site');
  await expect(page.locator('.page-header-item--published')).toHaveCount(0);
  await expect(page.locator('#title-block-header .date').first()).toHaveText('Publication date not verified');
  await expect(page.getByRole('heading', { name: /^What This Page Does Not Establish/ })).toBeVisible();
  await expect(page.locator('.callout-title-container', { hasText: 'Governed Critiques for This Page' })).toBeVisible();
  await prerequisite.click();
  await expect(page).toHaveURL(/pages\/how-to-read.html$/);
});

for (const route of ['/index.html', '/pages/start-here.html', '/articles/theory-part1.html']) {
  test(`reading layout is accessible without horizontal overflow: ${route}`, async ({ page }) => {
    await page.goto(route);
    const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(result.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Skip to main content', exact: true })).toBeFocused();
    await page.screenshot({ path: test.info().outputPath('reading-layout.png'), fullPage: true });
  });
}
