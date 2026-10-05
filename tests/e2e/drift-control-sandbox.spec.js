const { test, expect } = require("@playwright/test");

// WEB-06.3 (#4533): Drift vs Control sandbox on theory Part 1. ADR 0002 class A
// widget checks: self-hosted (no cross-origin requests while it runs), its own
// bytes within 60 KB, and ready within 1.0 s of boot at 4x CPU throttling.
const route = "/articles/theory-part1.html#drift-control-sandbox";
const CLASS_A_MAX_BYTES = 60 * 1024;
const CLASS_A_MAX_TTI_MS = 1000;

test.describe("drift vs control sandbox", () => {
  test("boots within the class A budget and stays self-hosted", async ({
    page,
  }) => {
    const client = await page.context().newCDPSession(page);
    await client.send("Emulation.setCPUThrottlingRate", { rate: 4 });

    let widgetBytes = 0;
    page.on("response", async (response) => {
      if (!response.url().includes("drift-control-sandbox")) return;
      try {
        widgetBytes += (await response.body()).length;
      } catch {
        // Redirects and aborted responses carry no body.
      }
    });

    await page.goto(route, { waitUntil: "load" });
    const app = page.locator("#dcsb-app");
    await expect(app).toHaveAttribute("data-widget-ready", "true");

    const bootMs = await page.evaluate(
      () => performance.measure("dcsb-tti", "dcsb-boot", "dcsb-ready").duration,
    );
    expect(bootMs).toBeLessThanOrEqual(CLASS_A_MAX_TTI_MS);
    expect(widgetBytes).toBeGreaterThan(0);
    expect(widgetBytes).toBeLessThanOrEqual(CLASS_A_MAX_BYTES);

    const origin = new URL(page.url()).origin;
    const crossOrigin = [];
    page.on("request", (request) => {
      if (new URL(request.url()).origin !== origin) crossOrigin.push(request.url());
    });

    await page.locator("#dcsb-preset").selectOption("shoulder-and-wrist");
    await page.locator("#dcsb-shoulder").focus();
    await page.keyboard.press("ArrowRight");
    await page.locator("#dcsb-play").click();
    await expect
      .poll(async () => Number(await page.locator("#dcsb-time").inputValue()))
      .toBeGreaterThan(0);
    expect(crossOrigin).toEqual([]);
  });

  test("offers a data-table text alternative and the exploratory label", async ({
    page,
  }) => {
    await page.goto(route, { waitUntil: "load" });
    await expect(page.locator("#dcsb-app")).toHaveAttribute("data-widget-ready", "true");
    await expect(page.locator("#dcsb-app .dcsb-badge")).toHaveText(
      "Exploratory model output",
    );
    await expect(page.locator("#dcsb-data tr")).toHaveCount(21);
    await expect(page.locator("#dcsb-status")).toHaveAttribute("data-valid", "true");
  });

  test("zero torque leaves only the drift term", async ({ page }) => {
    await page.goto(route, { waitUntil: "load" });
    await expect(page.locator("#dcsb-app")).toHaveAttribute("data-widget-ready", "true");
    await page.locator("#dcsb-preset").selectOption("zero-torque");
    await page.locator("#dcsb-time").fill("250");
    await expect(page.locator("#dcsb-now-input-1")).toHaveText("0");
    await expect(page.locator("#dcsb-now-input-2")).toHaveText("0");
    await expect(page.locator("#dcsb-now-tip-input")).toHaveText("0");
    await expect(page.locator("#dcsb-now-drift-1")).not.toHaveText("0");
  });
});
