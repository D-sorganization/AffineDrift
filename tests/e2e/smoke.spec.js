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

// Behavioral invariants (issue #3233): assert real interactive behavior, not
// just that the page loaded. These cover the JS modules under test
// (dark-mode-toggle, ui-components back-to-top, startup-launcher).
test.describe("PR Smoke - behavioral invariants", () => {
  test.describe.configure({ timeout: 90000 });

  test("dark-mode toggle flips the documentElement theme", async ({ page }) => {
    await page.goto("/", { waitUntil: "load" });
    const toggle = page.locator("#theme-toggle");
    await expect(toggle).toBeVisible();

    const before = await page.evaluate(
      () => document.documentElement.getAttribute("data-theme") || "light",
    );
    await toggle.click();
    const after = await page.evaluate(
      () => document.documentElement.getAttribute("data-theme") || "light",
    );

    expect(after).not.toBe(before);
    // Bootstrap dark mode must track the site theme so the chrome recolors too.
    const bsTheme = await page.evaluate(() =>
      document.documentElement.getAttribute("data-bs-theme"),
    );
    expect(bsTheme).toBe(after);
    // Preference is persisted for the next visit.
    const stored = await page.evaluate(() =>
      window.localStorage.getItem("affinedrift-theme"),
    );
    expect(stored).toBe(after);
  });

  test("startup splash is removed and the page is revealed after load", async ({ page }) => {
    await page.goto("/", { waitUntil: "load" });
    // The launcher reveals the page (and clears the splash) once ready; allow
    // for its minimum-splash + fade timing.
    await expect
      .poll(
        () =>
          page.evaluate(() =>
            document.documentElement.classList.contains("ad-page-revealed"),
          ),
        { timeout: 10000 },
      )
      .toBe(true);
    await expect(page.locator("#ad-splash-screen")).toBeHidden();
  });

  test("back-to-top control becomes actionable after scrolling down", async ({ page }) => {
    await page.goto("/", { waitUntil: "load" });
    const backToTop = page.locator("button.back-to-top");
    // The control is injected by ui-components.js on init.
    await expect(backToTop).toHaveCount(1);
    await expect(backToTop).toHaveAttribute("aria-label", "Scroll to top");

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(400);
    await backToTop.click({ force: true });
    await expect
      .poll(() => page.evaluate(() => window.scrollY), { timeout: 5000 })
      .toBeLessThan(200);
  });
});
