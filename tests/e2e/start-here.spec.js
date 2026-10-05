const { test, expect } = require("@playwright/test");

// WEB-01.1 (#4486): Start Here is one click away from every page's navbar.
// The navbar is site-wide (_quarto.yml, pinned first by
// tests/test_start_here_page.py), so these routes sample each page family:
// home, hub, core article, textbook chapter, critique and model page.
const ROUTES = [
  "/index.html",
  "/pages/glossary.html",
  "/resources/learning-paths.html",
  "/articles/theory-part1.html",
  "/articles/The_Physics_of_Golf/quarto/index.html",
  "/critiques/index.html",
  "/models/models.html",
];

for (const route of ROUTES) {
  test(`Start Here is one navbar click from ${route}`, async ({ page }) => {
    await page.goto(route, { waitUntil: "domcontentloaded" });
    // On narrow screens the navbar first collapses behind its toggler.
    const toggler = page.locator(".navbar-toggler");
    if (await toggler.isVisible()) await toggler.click();
    const link = page.locator("#quarto-header .navbar-nav a.nav-link", {
      hasText: "Start Here",
    });
    await expect(link.first()).toBeVisible();
    await link.first().click();
    await expect(page).toHaveURL(/\/pages\/start-here\.html$/);
    await expect(page.locator("h1")).toHaveText("Start Here");
  });
}

test("Start Here is the home page's primary call to action", async ({ page }) => {
  await page.goto("/");
  const primary = page.locator(".home-hero__actions a.site-button").first();
  await expect(primary).toHaveAttribute("href", "pages/start-here.html");
  await expect(primary).not.toHaveClass(/site-button--ghost/);
});
