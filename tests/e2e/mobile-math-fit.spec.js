const { test, expect } = require('@playwright/test');

/**
 * Mobile math fit and 12px type floor (#5326).
 *
 * At a 390x844 phone viewport, theory-part1's near-fit display equations must
 * not need horizontal scrolling, and no visible non-math text may render under
 * 12px. Truly wide equations elsewhere keep their scroll container.
 */
test.describe('Mobile math fit and type floor (#5326)', () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });

  const MIN_TEXT_PX = 12;

  test('theory-part1 display equations fit and UI text is at least 12px', async ({ page }) => {
    await page.goto('/articles/theory-part1.html', { waitUntil: 'networkidle' });
    // MathJax typesets lazily, so bring every equation into view once.
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 400) {
        window.scrollTo(0, y);
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
      window.scrollTo(0, 0);
    });
    await page.waitForFunction(() => document.documentElement.dataset.adMathReady === 'true');
    await page.waitForFunction(
      () => document.querySelectorAll('mjx-container[display="true"]').length > 0,
    );

    const report = await page.evaluate((minPx) => {
      const scrolls = (el) => el.scrollWidth > el.clientWidth + 1;
      const overflowing = [...document.querySelectorAll('mjx-container[display="true"]')]
        .filter((eq) => scrolls(eq) || scrolls(eq.closest('.math.display') || eq))
        .map((eq) => `${eq.scrollWidth}/${eq.clientWidth}`);
      const smallText = [];
      for (const el of document.querySelectorAll('body *')) {
        if (el.closest('mjx-container') || !el.offsetParent) continue;
        const ownText = [...el.childNodes].some(
          (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
        );
        const size = parseFloat(getComputedStyle(el).fontSize);
        if (ownText && size < minPx) smallText.push(`${el.tagName}.${el.className}@${size}`);
      }
      return { overflowing, smallText };
    }, MIN_TEXT_PX);

    expect(report.overflowing, 'display equations needing horizontal scroll').toEqual([]);
    expect(report.smallText, 'visible text under 12px').toEqual([]);
  });
});
