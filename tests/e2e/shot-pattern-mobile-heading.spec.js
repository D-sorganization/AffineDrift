const { test, expect } = require('@playwright/test');

test('shot-pattern mobile title keeps words intact without a source control', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/articles/shot-pattern-analysis.html');

  const title = page.locator('#title-block-header h1.title');
  await expect(title).toBeVisible();
  await page.evaluate(async () => { await document.fonts.ready; });

  const splitWords = await title.evaluate((heading) => {
    const text = heading.firstChild;
    return ['Dispersion', 'Conditional'].filter((word) => {
      const start = text.textContent.indexOf(word);
      const range = document.createRange();
      range.setStart(text, start);
      range.setEnd(text, start + word.length);
      return range.getClientRects().length !== 1;
    });
  });

  expect(splitWords).toEqual([]);
  await expect(page.locator('#quarto-code-tools-source')).toHaveCount(0);
});
