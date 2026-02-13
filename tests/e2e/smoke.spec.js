const { test, expect } = require("@playwright/test");

test.describe("PR Smoke", () => {
  test("homepage renders and has core structure", async ({ page }) => {
    const response = await page.goto("/", { waitUntil: "domcontentloaded" });
    expect(response).toBeTruthy();
    expect(response.ok()).toBeTruthy();

    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("a").first()).toBeVisible();
  });

  test("key public pages return success", async ({ page }) => {
    for (const route of ["/", "/articles.html", "/bibliography.html"]) {
      const response = await page.goto(route, { waitUntil: "domcontentloaded" });
      expect(response).toBeTruthy();
      expect(response.ok()).toBeTruthy();
    }
  });
});
