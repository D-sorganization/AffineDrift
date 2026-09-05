const { test, expect } = require('@playwright/test');

test('a long chapter becomes opaque when navigating into its middle', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.route('**/fade-fixture', route => route.fulfill({
    contentType: 'text/html',
    body: `<!doctype html><html><body style="margin:0">
      <div style="height:1800px">Before the chapter</div>
      <section id="chapter" style="height:18000px">
        <h2>A long textbook chapter</h2>
        <div style="height:8000px"></div>
        <section id="worked-example"><h3>A worked example</h3><p>Readable mathematics.</p></section>
      </section>
    </body></html>`,
  }));
  await page.goto('/fade-fixture');
  await page.evaluate(async () => {
    const { initFadeAnimations } = await import('/js/ui-components.js');
    initFadeAnimations();
  });
  await expect(page.locator('#chapter')).toHaveCSS('opacity', '0');
  await page.evaluate(() => { location.hash = 'worked-example'; });

  // Visibility matchers do not detect a transparent ancestor. Check opacity
  // explicitly: this chapter can never fit 10% of its height in the viewport.
  await expect(page.locator('#chapter')).toHaveCSS('opacity', '1');
  await expect(page.locator('#worked-example')).toHaveCSS('opacity', '1');
  await expect(page.locator('#worked-example')).toBeInViewport();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('#chapter')).toHaveCSS('opacity', '1');
  await expect(page.locator('#worked-example')).toHaveCSS('opacity', '1');
});
