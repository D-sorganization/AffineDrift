const { test, expect } = require("@playwright/test");

const NAVBAR_LOGO_PATH = "/logo/logo-navbar.png";
const NAVBAR_LOGO_RESPONSE_BUDGET_BYTES = 50 * 1024;

test.describe("Homepage", () => {
  test("should load successfully", async ({ page }) => {
    await page.goto("/");

    // Check page title
    await expect(page).toHaveTitle(/AffineDrift/);

    // Check rendered home heading exists; Quarto's generated title block is hidden.
    await expect(page.locator(".home-hero h1")).toBeVisible();
  });

  test("should have working navigation", async ({ page }) => {
    await page.goto("/");

    // Check navbar exists
    const navbar = page.locator("nav.navbar, .quarto-navbar");
    await expect(navbar).toBeVisible();

    // Check for navigation links
    const navLinks = page.locator("nav a, .navbar a");
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test("should have accessible logo", async ({ page }) => {
    const logoResponsePromise = page.waitForResponse((response) => {
      return new URL(response.url()).pathname === NAVBAR_LOGO_PATH;
    });

    await page.goto("/");

    // Check logo has alt text
    const logo = page
      .locator('img[alt*="AffineDrift"], img[alt*="Logo"]')
      .first();
    if ((await logo.count()) > 0) {
      await expect(logo).toHaveAttribute("alt");
      await expect(logo).toHaveAttribute("src", /logo-navbar\.png/);
    }

    const logoResponse = await logoResponsePromise;
    const contentLength = logoResponse.headers()["content-length"];
    const responseSize = contentLength
      ? Number(contentLength)
      : (await logoResponse.body()).length;
    expect(responseSize).toBeLessThan(NAVBAR_LOGO_RESPONSE_BUDGET_BYTES);
  });

  test("should render desktop home layout as a three-column grid", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const layout = page.locator(".home-layout-3col");
    await expect(layout).toBeVisible();
    await expect(page.locator(".home-hero")).toBeVisible();
    await expect(page.locator(".home-toc")).toBeVisible();

    const layoutState = await page.evaluate(() => {
      const homeLayout = document.querySelector(".home-layout-3col");
      const sidebar = document.querySelector(".home-sidebar");
      const hero = document.querySelector(".home-hero");
      const toc = document.querySelector(".home-toc");
      const codeBlocks = Array.from(document.querySelectorAll("pre code"));

      const rectFor = (element) => {
        const rect = element.getBoundingClientRect();
        return {
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          top: Math.round(rect.top),
          width: Math.round(rect.width),
        };
      };

      return {
        display: getComputedStyle(homeLayout).display,
        sidebar: rectFor(sidebar),
        hero: rectFor(hero),
        toc: rectFor(toc),
        escapedLayout: codeBlocks.some((block) =>
          block.textContent.includes('<aside class="home-sidebar"'),
        ),
        scrollWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
      };
    });

    expect(layoutState.display).toBe("grid");
    expect(layoutState.escapedLayout).toBe(false);
    expect(layoutState.sidebar.right).toBeLessThan(layoutState.hero.left);
    expect(layoutState.hero.right).toBeLessThan(layoutState.toc.left);
    expect(layoutState.scrollWidth).toBeLessThanOrEqual(
      layoutState.viewportWidth,
    );
  });

  test("should be mobile responsive", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    // Check page loads on mobile
    await expect(page.locator("body")).toBeVisible();

    // Check content is not overflowing
    const body = await page.locator("body").boundingBox();
    expect(body.width).toBeLessThanOrEqual(375);
  });

  test("should toggle mobile sidebar sections", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    const readToggle = page
      .locator(".sidebar-section-toggle")
      .filter({ hasText: "Read" });
    const readSection = page.locator("#read-section");

    await expect(readToggle).toBeVisible();
    await expect(readToggle).toHaveAttribute("aria-expanded", "true");
    await expect(readSection).toHaveClass(/show/);

    await readToggle.click();
    await expect(readToggle).toHaveAttribute("aria-expanded", "false");
    await expect(readSection).not.toHaveClass(/show/);

    await readToggle.click();
    await expect(readToggle).toHaveAttribute("aria-expanded", "true");
    await expect(readSection).toHaveClass(/show/);
  });

  test("should have no console errors", async ({ page }) => {
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Allow some common non-critical errors
    const criticalErrors = errors.filter(
      (error) => !error.includes("favicon") && !error.includes("ServiceWorker"),
    );

    expect(criticalErrors).toHaveLength(0);
  });
});
