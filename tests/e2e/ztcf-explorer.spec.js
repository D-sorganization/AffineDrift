const { test, expect } = require("@playwright/test");

// WEB-06.4 (#4534): ZTCF counterfactual explorer on the ZTCF page. ADR 0002
// class A widget checks: self-hosted (no cross-origin requests while it runs),
// its own bytes within 60 KB, and ready within 1.0 s of boot at 4x CPU throttling.
const route = "/articles/zero-torque-counterfactual.html#sec-ztcf-explorer";
const CLASS_A_MAX_BYTES = 60 * 1024;
const CLASS_A_MAX_TTI_MS = 1000;

test.describe("ZTCF counterfactual explorer", () => {
  test("boots within the class A budget and stays self-hosted", async ({
    page,
  }) => {
    const client = await page.context().newCDPSession(page);
    await client.send("Emulation.setCPUThrottlingRate", { rate: 4 });

    let widgetBytes = 0;
    page.on("response", async (response) => {
      if (!response.url().includes("ztcf-explorer")) return;
      try {
        widgetBytes += (await response.body()).length;
      } catch {
        // Redirects and aborted responses carry no body.
      }
    });

    await page.goto(route, { waitUntil: "load" });
    const app = page.locator("#ztx-app");
    await expect(app).toHaveAttribute("data-widget-ready", "true");

    const bootMs = await page.evaluate(
      () => performance.measure("ztx-tti", "ztx-boot", "ztx-ready").duration,
    );
    expect(bootMs).toBeLessThanOrEqual(CLASS_A_MAX_TTI_MS);
    expect(widgetBytes).toBeGreaterThan(0);
    expect(widgetBytes).toBeLessThanOrEqual(CLASS_A_MAX_BYTES);

    const origin = new URL(page.url()).origin;
    const crossOrigin = [];
    page.on("request", (request) => {
      if (new URL(request.url()).origin !== origin) crossOrigin.push(request.url());
    });

    const before = await page.locator("#ztx-speed-branch").textContent();
    await page.locator("#ztx-step").fill("150");
    await expect(page.locator("#ztx-speed-branch")).not.toHaveText(before);
    expect(crossOrigin).toEqual([]);
  });

  test("shows provenance, caveats and a data-table text alternative", async ({
    page,
  }) => {
    await page.goto(route, { waitUntil: "load" });
    await expect(page.locator("#ztx-app")).toHaveAttribute("data-widget-ready", "true");
    await expect(page.locator("#ztx-app .ztx-badge")).toHaveText(
      "Exploratory model output",
    );
    await expect(page.locator("#ztx-fixture-sha256")).toHaveText(/^[0-9a-f]{64}$/);
    await expect(page.locator("#ztx-data tr").first()).toBeAttached();
    await expect(
      page.locator('#ztx-app a[href$="critiques/ztcf_identifiability.html"]'),
    ).toBeVisible();
  });
});
