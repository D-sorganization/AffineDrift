const { test, expect } = require("@playwright/test");

const route = "/articles/proximal-distal-energy-transfer.html#sec-advanced-bridge";

test.describe("advanced proximal-distal bridge", () => {
  for (const viewport of [
    { label: "mobile", width: 375, height: 812 },
    { label: "desktop", width: 1440, height: 900 },
  ]) {
    test(`${viewport.label} layout exposes the bridge without overflow`, async ({
      page,
    }) => {
      await page.setViewportSize(viewport);
      await page.goto(route, { waitUntil: "load" });

      await expect(
        page.getByRole("heading", {
          name: "Reference Frames, Biological Redundancy, and Engine Roles",
        }),
      ).toBeVisible();
      const section = page.locator("#sec-advanced-bridge");
      const figures = section.locator("img");
      expect(await figures.count()).toBeGreaterThanOrEqual(5);
      for (const figure of await figures.all()) {
        await expect(figure).toBeVisible();
        const size = await figure.evaluate((image) => ({
          naturalWidth: image.naturalWidth,
          naturalHeight: image.naturalHeight,
        }));
        expect(size.naturalWidth).toBeGreaterThan(0);
        expect(size.naturalHeight).toBeGreaterThan(0);
      }
      const bridgeOverflow = await section.evaluate(
        (element) => element.scrollWidth - element.clientWidth,
      );
      expect(bridgeOverflow).toBeLessThanOrEqual(1);
    });
  }
});
