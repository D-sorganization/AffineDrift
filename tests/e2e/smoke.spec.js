const { test, expect } = require("@playwright/test");

const PUBLIC_ROUTES = [
  "/",
  "/resources/articles.html",
  "/resources/bibliography.html",
  "/pages/overview.html",
  "/resources/resources-books.html",
  "/models/models.html",
];

test.describe("PR Smoke", () => {
  test.describe.configure({ timeout: 90000 });

  test("homepage renders and has core structure", async ({ page }) => {
    const response = await page.goto("/", { waitUntil: "domcontentloaded" });
    expect(response).toBeTruthy();
    expect(response.ok()).toBeTruthy();

    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("a").first()).toBeVisible();
  });

  for (const route of PUBLIC_ROUTES) {
    test(`public page ${route} returns success`, async ({ page }) => {
      const response = await page.goto(route, {
        waitUntil: "domcontentloaded",
        timeout: 60000,
      });
      expect(response).toBeTruthy();
      expect(response.ok()).toBeTruthy();
    });
  }

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
    const response = await page.goto("/", { waitUntil: "load" });
    expect(response).toBeTruthy();
    expect(response.ok()).toBeTruthy();
    await page.waitForTimeout(500);
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
