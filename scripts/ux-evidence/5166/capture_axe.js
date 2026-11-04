#!/usr/bin/env node
/** One-off axe scan for #5166 closeout evidence (live public pages). */
const { chromium } = require("playwright");
const AxeBuilder = require("@axe-core/playwright").default;

const PAGES = [
  { name: "Home", path: "/" },
  { name: "Theory Part 1", path: "/articles/theory-part1.html" },
  {
    name: "Physics of Golf ch03",
    path: "/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html",
  },
];

const VIEWPORTS = [
  { label: "375×812", width: 375, height: 812 },
  { label: "1440×900", width: 1440, height: 900 },
];

async function main() {
  const base = "https://www.affinedrift.com";
  const browser = await chromium.launch({ headless: true });
  const rows = [];
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    for (const entry of PAGES) {
      await page.goto(`${base}${entry.path}`, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze();
      rows.push({
        page: entry.name,
        viewport: viewport.label,
        passes: result.passes.length,
        violations: result.violations.length,
      });
    }
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(rows, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
