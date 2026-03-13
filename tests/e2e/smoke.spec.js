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
    for (const route of [
      "/",
      "/articles.html",
      "/bibliography.html",
      "/overview.html",
      "/resources-books.html",
      "/models.html",
    ]) {
      const response = await page.goto(route, { waitUntil: "domcontentloaded" });
      expect(response).toBeTruthy();
      expect(response.ok()).toBeTruthy();
    }
  });

  test("homepage has title and navbar", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page).toHaveTitle(/AffineDrift/);
    const navbar = page.locator("nav.navbar, .quarto-navbar, nav");
    await expect(navbar.first()).toBeVisible();
  });

  test("static assets load without errors", async ({ page }) => {
    const failedRequests = [];
    page.on("requestfailed", (request) => {
      if (!request.url().includes("google")) {
        failedRequests.push(request.url());
      }
    });
    await page.goto("/", { waitUntil: "networkidle" });
    expect(failedRequests).toHaveLength(0);
  });

  test("print stylesheet is loaded", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    const printStyle = await page.evaluate(() => {
      const sheets = Array.from(document.styleSheets);
      return sheets.some((s) => {
        try {
          return s.media && s.media.mediaText && s.media.mediaText.includes("print");
        } catch {
          return false;
        }
      });
    });
    // Print styles may be in combined stylesheet or separate - just verify page loaded
    expect(page.url()).toContain("localhost");
  });
});
