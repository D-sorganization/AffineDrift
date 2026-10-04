const { test, expect } = require('@playwright/test');

test.use({ serviceWorkers: 'block' });

test('Volume II retains the three distinct singularity definitions', async ({ page }) => {
  await page.goto('/articles/The_Geometry_of_Motion/quarto/volume2.html', {
    waitUntil: 'domcontentloaded',
  });
  const paragraph = page
    .locator('main p')
    .filter({ hasText: 'There are three distinct concerns.' });
  await expect(paragraph).toHaveCount(1);
  await expect(paragraph).toContainText(
    'A coordinate singularity is a failure of a representation.',
  );
  await expect(paragraph).toContainText(
    'A mechanical singularity may align actual gimbal axes',
  );
  await expect(paragraph).toContainText('A task singularity is a rank loss');
});

test('Volume II preserves the directional qualification of amplification', async ({ page }) => {
  await page.goto('/articles/The_Geometry_of_Motion/quarto/volume2.html', {
    waitUntil: 'domcontentloaded',
  });
  const paragraph = page
    .locator('main p')
    .filter({ hasText: 'A value above one means' });
  await expect(paragraph).toHaveCount(1);
  await expect(paragraph).toContainText(
    'some initial direction is amplified, not all directions.',
  );
});

test('Volume II keeps the transient matrix example within the text column', async ({ page }) => {
  await page.goto('/articles/The_Geometry_of_Motion/quarto/volume2.html');
  const equation = page.locator('#eq-orbital_transient_growth');
  await equation.scrollIntoViewIfNeeded();
  const math = equation.locator('mjx-math');
  await expect(math).toBeVisible();
  const dimensions = await equation.evaluate(el => ({
    column: el.getBoundingClientRect().width,
    math: el.querySelector('mjx-math').getBoundingClientRect().width,
  }));
  expect(dimensions.math).toBeLessThanOrEqual(dimensions.column + 1);
});
