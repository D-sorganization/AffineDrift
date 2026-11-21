# Modified Search Shortcut Evidence

This is one keyboard interaction slice of #5171. Ctrl, Meta, or Alt with a
configured search key must retain the browser/OS command and avoid loading search.
Plain `s` and `/` still start lazy search. The other UX acceptance items remain open.

## Results

The real-loader regression suite first failed six modified-key cases while three
existing behaviors passed. After the one-line guard, all nine cases pass.
A separate Chromium fixture dispatches cancelable DOM `keyup` events through the
actual loader: all six modified combinations were intercepted before and are
untouched after; both plain keys still load search in each version. This checks
the DOM boundary, not the operating system's Save dialog.

All 18 axe scans report zero WCAG A/AA violations. All 12 Lighthouse reports
completed without runtime errors; accessibility, best practices, and SEO each
score 100. Performance varies: home mobile 55 to 58, desktop 93 to 93; Theory
mobile 30 to 30, desktop 79 to 72; Physics chapter mobile 37 to 34, desktop 83 to
78. These single runs do not establish a performance improvement or regression
attributable to the keyboard guard. Several performance targets remain unmet.
Full values, transfer sizes, request counts, and timing units (milliseconds)
are in [metrics.csv](metrics.csv); CLS is unitless and transfer size is bytes.

## Method and Limits

The November 6, 2026 run used Lighthouse 12.6.1 and Chromium from Playwright's
chromium-1248 distribution, on this Windows worker. Each version has one stock
mobile and one stock desktop Lighthouse run per page. These are localhost cached
snapshots, not deployed-site performance claims. Public HTML and first-party
assets were fetched once per URL and shared between versions; their hashes are
in `receipts.json.gz`. The deployed site's commit was not established. External
CDN resources are not frozen by this harness, and their timing/cache behavior
can vary. Only the local loader source changes between versions.

The baseline loader is from commit
`6ee9c59f89624ab6f58f3b566119f9ae829697ed`, SHA-256
`927d661eb5c5d99924a25595d4cf590902e69739fdcfe8cf3413203376705fe8`.
The patched loader SHA-256 is
`7e32176fcdf23dd78bd3348f14cb2708beb749f5297206164f5b94e16158b047`.
Receipts bind both sources and record the raw keyboard results.

Page indices are 0 for `/`, 1 for `/articles/theory-part1.html`, and 2 for
`/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html`.
Full-page screenshots and axe output cover 375x812, 768x1024, and 1440x900
viewports, with reduced motion. Screenshot pairs are not all byte-identical;
they are review evidence, not proof of pixel equality. The capture does not
isolate rendering or font timing variation. No article source was edited or
published by this measurement.

Files use `before|after-page-width.png`, corresponding `-axe.json.gz`, and
`before|after-page-mobile|desktop-lighthouse.json.gz`. Raw reports are JSON
compressed with gzip. `SHA256SUMS` covers all raw reports and screenshots.

## Reproduction

From the repository root, set `AD_TOOL_ROOT` to an installed node_modules with
Lighthouse 12.6.1, puppeteer-core, chrome-launcher, and axe-core. Set
`AD_CHROME_PATH` to Chromium, then run:

```text
node docs/development/search-shortcut-5171/measure.cjs <output-directory>
```

The harness defaults to the baseline commit above; `AD_BASE_REV` can override
it. Use a separate output directory. Fresh public resources may differ from
these recorded snapshots. The server binds only to localhost, uses disposable
browser profiles, and closes when the run finishes.
