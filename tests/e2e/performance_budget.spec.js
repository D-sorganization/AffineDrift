const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const configPath = path.resolve(__dirname, '../../config/runtime_performance_budget.json');
const budgetConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));

test.describe('Runtime Performance Budgets (WEB-10.1 / #4570)', () => {
  test.describe.configure({ timeout: 60000 });

  for (const [route, budget] of Object.entries(budgetConfig.routes)) {
    test(`route ${route} meets runtime performance budget`, async ({ page }) => {
      let transferBytes = 0;

      // Track transfer bytes across all network responses for this navigation
      page.on('response', async (response) => {
        try {
          const headers = response.headers();
          if (headers['content-length']) {
            transferBytes += parseInt(headers['content-length'], 10);
          } else {
            const body = await response.body();
            transferBytes += body.length;
          }
        } catch {
          // Ignore aborted or cross-origin requests
        }
      });

      // Inject PerformanceObservers before the document starts loading
      await page.addInitScript(() => {
        window.__runtimePerfMetrics = {
          lcp: 0,
          cls: 0,
          tbt: 0,
        };

        // Largest Contentful Paint (LCP)
        try {
          const lcpObserver = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            if (entries.length > 0) {
              const lastEntry = entries[entries.length - 1];
              window.__runtimePerfMetrics.lcp =
                lastEntry.renderTime || lastEntry.loadTime || lastEntry.startTime || 0;
            }
          });
          lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {
          // PerformanceObserver type not supported in older engines
        }

        // Cumulative Layout Shift (CLS)
        try {
          const clsObserver = new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
              if (!entry.hadRecentInput) {
                window.__runtimePerfMetrics.cls += entry.value;
              }
            }
          });
          clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
          // Ignore
        }

        // Long Tasks -> Total Blocking Time (TBT)
        try {
          const longTaskObserver = new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
              if (entry.duration > 50) {
                window.__runtimePerfMetrics.tbt += entry.duration - 50;
              }
            }
          });
          longTaskObserver.observe({ type: 'longtask', buffered: true });
        } catch (e) {
          // Ignore
        }
      });

      // Navigate to route and wait for DOM content loaded
      const response = await page.goto(route, {
        waitUntil: 'domcontentloaded',
        timeout: 45000,
      });
      expect(response).toBeTruthy();
      expect(response.ok()).toBeTruthy();

      // Allow paint observer callbacks and any async MathJax/assets to settle
      await page.waitForTimeout(300);

      const metrics = await page.evaluate(() => {
        const perf = window.__runtimePerfMetrics || { lcp: 0, cls: 0, tbt: 0 };
        // Fallback for LCP if observer didn't fire
        if (!perf.lcp) {
          const navEntries = performance.getEntriesByType('navigation');
          if (navEntries.length > 0) {
            perf.lcp = navEntries[0].domContentLoadedEventEnd || navEntries[0].responseEnd || 0;
          }
        }
        // Fallback/additional resource bytes calculation
        let resourceBytes = 0;
        const resources = performance.getEntriesByType('resource');
        for (const res of resources) {
          resourceBytes += res.transferSize || res.encodedBodySize || 0;
        }
        return {
          lcp: perf.lcp,
          cls: perf.cls,
          tbt: perf.tbt,
          resourceBytes,
        };
      });

      const totalTransfer = Math.max(transferBytes, metrics.resourceBytes);

      // Verify each runtime metric against the committed budget
      expect(
        metrics.lcp,
        `Route ${route} LCP of ${metrics.lcp.toFixed(1)}ms exceeded budget limit of ${budget.max_lcp_ms}ms`
      ).toBeLessThanOrEqual(budget.max_lcp_ms);

      expect(
        metrics.cls,
        `Route ${route} CLS of ${metrics.cls.toFixed(3)} exceeded budget limit of ${budget.max_cls}`
      ).toBeLessThanOrEqual(budget.max_cls);

      expect(
        metrics.tbt,
        `Route ${route} TBT of ${metrics.tbt.toFixed(1)}ms exceeded budget limit of ${budget.max_tbt_ms}ms`
      ).toBeLessThanOrEqual(budget.max_tbt_ms);

      if (totalTransfer > 0) {
        expect(
          totalTransfer,
          `Route ${route} transfer bytes of ${totalTransfer} exceeded budget limit of ${budget.max_transfer_bytes}`
        ).toBeLessThanOrEqual(budget.max_transfer_bytes);
      }
    });
  }
});
