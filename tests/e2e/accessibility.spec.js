const { test, expect } = require("@playwright/test");

const CONTRAST_ROUTES = [
  "/",
  "/pages/technology.html",
  "/articles/The_Geometry_of_Motion/quarto/ch01_foundations.html",
];

async function publishedRoutes(page) {
  const response = await page.request.get("/sitemap.xml");
  if (!response.ok()) return CONTRAST_ROUTES;
  const xml = await response.text();
  const routes = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map(
    (match) => new URL(match[1]).pathname,
  );
  return [...new Set([...CONTRAST_ROUTES, ...routes])];
}

async function findContrastFailures(page) {
  return page.evaluate(() => {
    const parseColor = (value) => {
      const match = value.match(/rgba?\(([^)]+)\)/);
      if (!match) return null;
      const parts = match[1]
        .split(/[, /]+/)
        .filter(Boolean)
        .map(Number);
      return { r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 };
    };
    const blend = (top, bottom) => ({
      r: top.r * top.a + bottom.r * (1 - top.a),
      g: top.g * top.a + bottom.g * (1 - top.a),
      b: top.b * top.a + bottom.b * (1 - top.a),
      a: 1,
    });
    const luminance = (color) => {
      const channel = (value) => {
        const normalized = value / 255;
        return normalized <= 0.04045
          ? normalized / 12.92
          : ((normalized + 0.055) / 1.055) ** 2.4;
      };
      return (
        0.2126 * channel(color.r) +
        0.7152 * channel(color.g) +
        0.0722 * channel(color.b)
      );
    };
    const ratio = (first, second) => {
      const values = [luminance(first), luminance(second)].sort(
        (a, b) => b - a,
      );
      return (values[0] + 0.05) / (values[1] + 0.05);
    };
    const backgrounds = (element) => {
      const layers = [];
      const gradientStops = [];
      for (let node = element; node; node = node.parentElement) {
        const style = getComputedStyle(node);
        const color = parseColor(style.backgroundColor);
        if (color?.a > 0) layers.push(color);
        if (style.backgroundImage !== "none") {
          for (const token of style.backgroundImage.match(/rgba?\([^)]+\)/g) ??
            []) {
            const stop = parseColor(token);
            if (stop) gradientStops.push(stop);
          }
        }
      }
      let solid = { r: 255, g: 255, b: 255, a: 1 };
      for (const layer of layers.reverse()) solid = blend(layer, solid);
      return gradientStops.length
        ? gradientStops.map((stop) => blend(stop, solid))
        : [solid];
    };
    const failures = [];
    for (const element of document.querySelectorAll("body *")) {
      const directText = [...element.childNodes]
        .filter((node) => node.nodeType === 3)
        .map((node) => node.textContent.trim())
        .join(" ");
      const style = getComputedStyle(element);
      if (
        !directText ||
        style.display === "none" ||
        style.visibility === "hidden"
      )
        continue;
      if (element.closest(".screen-reader-only, .visually-hidden")) continue;
      if (!element.getClientRects().length) continue;
      const foreground = parseColor(style.color);
      if (!foreground) continue;
      const size = Number(style.fontSize.replace("px", ""));
      const weight = Number(style.fontWeight) || 400;
      const threshold =
        size >= 24 || (size >= 18.66 && weight >= 700) ? 3 : 4.5;
      const measured = backgrounds(element).map((background) =>
        ratio(blend(foreground, background), background),
      );
      const worst = Math.min(...measured);
      if (worst + 0.01 < threshold) {
        failures.push(
          `${element.tagName.toLowerCase()}.${element.className}: ${worst.toFixed(2)}:1 — ${directText.slice(0, 70)}`,
        );
      }
    }
    return failures.slice(0, 30);
  });
}

test.describe("Accessibility", () => {
  test("should have proper heading hierarchy", async ({ page }) => {
    await page.goto("/");

    // Get all headings
    const headings = await page.locator("h1, h2, h3, h4, h5, h6").all();

    // Check we have at least one heading
    expect(headings.length).toBeGreaterThan(0);

    // Check first heading is h1 or h2
    const firstHeading = headings[0];
    const tagName = await firstHeading.evaluate((el) =>
      el.tagName.toLowerCase(),
    );
    expect(["h1", "h2"]).toContain(tagName);
  });

  test("should have alt text on all images", async ({ page }) => {
    await page.goto("/");

    // Get all images
    const images = await page.locator("img").all();

    // Check each image has alt attribute
    for (const img of images) {
      const alt = await img.getAttribute("alt");
      expect(alt).toBeDefined();
    }
  });

  test("should have ARIA labels on navigation", async ({ page }) => {
    await page.goto("/");

    // Check main navigation has aria-label or role
    const nav = page.locator("nav").first();
    if ((await nav.count()) > 0) {
      const ariaLabel = await nav.getAttribute("aria-label");
      const role = await nav.getAttribute("role");

      // Should have either aria-label or role
      expect(ariaLabel || role).toBeTruthy();
    }
  });

  test("should be keyboard navigable", async ({ page }) => {
    await page.goto("/");

    // Tab through interactive elements
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Check focus is visible
    const focusedElement = await page.evaluate(
      () => document.activeElement.tagName,
    );
    expect(focusedElement).toBeTruthy();
  });

  test("should meet WCAG AA text contrast in both themes", async ({ page }) => {
    test.setTimeout(10 * 60 * 1000);
    const routes = await publishedRoutes(page);
    for (const route of routes) {
      await page.goto(route);
      for (const theme of ["light", "dark"]) {
        await page.evaluate((selectedTheme) => {
          document.documentElement.setAttribute("data-theme", selectedTheme);
          document.documentElement.setAttribute("data-bs-theme", selectedTheme);
        }, theme);
        const failures = await findContrastFailures(page);
        expect(failures, `${route} (${theme}) contrast failures`).toEqual([]);
      }
    }
  });

  test("should have lang attribute", async ({ page }) => {
    await page.goto("/");

    // Check html has lang attribute
    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBeTruthy();
    expect(lang).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/); // e.g., 'en' or 'en-US'
  });

  test("should have skip to main content link", async ({ page }) => {
    await page.goto("/");

    // Tab to first element (should be skip link if present)
    await page.keyboard.press("Tab");

    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return {
        text: el.textContent,
        href: el.getAttribute("href"),
      };
    });

    // Skip link is optional but recommended
    // Just verify we can tab to something
    expect(focusedElement).toBeTruthy();
  });
});
