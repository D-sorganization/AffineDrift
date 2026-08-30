#!/usr/bin/env node
/* Governed representative visual evidence layered over the exhaustive verifier. */

const fs = require("fs");
const path = require("path");
const { runVerification, screenshotName } = require("./verify-public-site.js");
const {
  buildBaselineCandidate,
  compareScreenshotBaseline,
  screenshotEvidence,
} = require("./public-site-evidence.js");

function parseArgs(argv) {
  const options = {
    baseUrl: "http://localhost:8000",
    manifestPath: "docs/public-site-manifest.json",
    outputPath: "artifacts/public-site-verification/visual-results.json",
    screenshotDir: "artifacts/public-site-verification/screenshots",
    candidateBaselinePath: undefined,
    baselinePath: undefined,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const value = () => {
      index += 1;
      if (index >= argv.length) throw new TypeError(`${arg} requires a value`);
      return argv[index];
    };
    if (arg === "--base-url") options.baseUrl = value();
    else if (arg === "--manifest") options.manifestPath = value();
    else if (arg === "--output") options.outputPath = value();
    else if (arg === "--screenshot-dir") options.screenshotDir = value();
    else if (arg === "--candidate-baseline")
      options.candidateBaselinePath = value();
    else if (arg === "--baseline") options.baselinePath = value();
    else throw new TypeError(`unknown argument: ${arg}`);
  }
  return options;
}

function assertRepresentativeContract(manifest) {
  const contract = manifest?.verification?.representative;
  if (
    !contract ||
    !Array.isArray(contract.routes) ||
    contract.routes.length === 0
  ) {
    throw new TypeError("representative route contract is missing");
  }
  const families = contract.routes.map((record) => record.family);
  const routes = contract.routes.map((record) => record.route);
  if (
    families.some((family) => typeof family !== "string" || !family.trim()) ||
    new Set(families).size !== families.length
  ) {
    throw new TypeError(
      "representative family identities must be unique and non-empty",
    );
  }
  if (new Set(routes).size !== routes.length) {
    throw new TypeError("representative routes must be unique");
  }
  if (contract.routes.some((record) => !record.scenario?.trim())) {
    throw new TypeError("representative capture scenario is required");
  }
  const availableRoutes = new Set(manifest.pages.map((page) => page.route));
  const missing = routes.filter((route) => !availableRoutes.has(route));
  if (missing.length) {
    throw new TypeError(
      `representative route is absent from page inventory: ${missing[0]}`,
    );
  }
  return contract;
}

function representativeManifest(manifest) {
  const contract = assertRepresentativeContract(manifest);
  const routes = new Set(contract.routes.map((record) => record.route));
  const pages = manifest.pages.filter((page) => routes.has(page.route));
  return {
    ...manifest,
    page_count: pages.length,
    pages,
    verification: {
      ...manifest.verification,
      every_page: {
        viewports: [...contract.viewports],
        themes: [...contract.themes],
      },
    },
  };
}

const SUPPLEMENTAL_SCENARIO_IDS = new Set([
  "footer",
  "dense-content",
  "keyboard-focus",
  "reduced-motion",
  "print",
  "no-javascript",
]);

function supplementalScenarioPlan(manifest) {
  const core = assertRepresentativeContract(manifest);
  const scenarios = manifest?.verification?.supplemental?.scenarios;
  if (!Array.isArray(scenarios) || scenarios.length === 0) {
    throw new TypeError("supplemental scenario contract is missing");
  }
  const ids = scenarios.map((record) => record.id);
  if (
    ids.some((id) => !SUPPLEMENTAL_SCENARIO_IDS.has(id)) ||
    new Set(ids).size !== ids.length
  ) {
    throw new TypeError(
      "supplemental scenario ids must be unique and supported",
    );
  }
  const pages = new Map(manifest.pages.map((page) => [page.route, page]));
  const viewports = new Map(
    manifest.verification.viewports.map((viewport) => [viewport.id, viewport]),
  );
  const themes = new Set(manifest.verification.themes);
  const families = new Set(core.routes.map((record) => record.family));
  const plan = [];
  for (const record of scenarios) {
    const page = pages.get(record.route);
    if (!page) {
      throw new TypeError(
        `supplemental route is absent from page inventory: ${record.route}`,
      );
    }
    if (!families.has(record.family)) {
      throw new TypeError(
        `supplemental route family is unsupported: ${record.family}`,
      );
    }
    if (!Array.isArray(record.viewports) || record.viewports.length === 0) {
      throw new TypeError(`supplemental viewport list is empty: ${record.id}`);
    }
    if (!Array.isArray(record.themes) || record.themes.length === 0) {
      throw new TypeError(`supplemental theme list is empty: ${record.id}`);
    }
    for (const viewportId of record.viewports) {
      const viewport = viewports.get(viewportId);
      if (!viewport) {
        throw new TypeError(`unsupported supplemental viewport: ${viewportId}`);
      }
      for (const theme of record.themes) {
        if (!themes.has(theme)) {
          throw new TypeError(`unsupported supplemental theme: ${theme}`);
        }
        plan.push({
          route: record.route,
          routeFamily: record.family,
          scenarioId: record.id,
          pageKind: page.page_kind,
          viewport: { ...viewport },
          theme,
        });
      }
    }
  }
  return plan;
}

function scenarioScreenshotName(route, scenarioId, viewportId, theme) {
  const coreName = screenshotName(route, viewportId, theme);
  return coreName.replace(
    `__${viewportId}__${theme}.png`,
    `__${scenarioId}__${viewportId}__${theme}.png`,
  );
}

async function captureSearch(page, targetUrl, screenshotPath) {
  await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.evaluate(() => document.fonts?.ready);
  await page.locator("#quarto-search button").click();
  const input = page.locator(".aa-DetachedContainer .aa-Input");
  await input.waitFor({ state: "visible" });
  await input.fill("proximal distal");
  const results = page.locator(".aa-DetachedContainer .aa-Item");
  await results.first().waitFor({ state: "visible" });
  const resultText = (await results.allTextContents()).join(" ");
  if (!/proximal.{0,30}distal|distal.{0,30}proximal/i.test(resultText)) {
    throw new Error("site search did not return a proximal-distal result");
  }
  await page.screenshot({
    path: screenshotPath,
    animations: "disabled",
    fullPage: false,
  });
  return { query: "proximal distal", result_count: await results.count() };
}

async function settleScenarioPage(page) {
  await page.evaluate(() => document.fonts?.ready);
  await page.evaluate(
    () =>
      new Promise((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(resolve));
      }),
  );
}

async function inspectFooter(page) {
  const footer = page
    .locator("footer.footer, footer.page-footer, footer")
    .last();
  await footer.waitFor({ state: "visible" });
  await footer.scrollIntoViewIfNeeded();
  return footer.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    const text = element.textContent.replace(/\s+/g, " ").trim();
    const links = [...element.querySelectorAll("a")]
      .filter((link) => link.getClientRects().length > 0)
      .map((link) => ({
        href: link.href,
        name: (link.getAttribute("aria-label") || link.textContent).trim(),
      }));
    return {
      text,
      links,
      visible: rect.width > 0 && rect.height > 0,
      pageOverflow: Math.max(
        0,
        document.documentElement.scrollWidth - window.innerWidth,
      ),
    };
  });
}

async function inspectDenseContent(page) {
  const dense = page
    .locator("main table, main pre, main mjx-container, main .math")
    .first();
  await dense.waitFor({ state: "visible" });
  await dense.scrollIntoViewIfNeeded();
  return dense.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    const parentStyle = element.parentElement
      ? getComputedStyle(element.parentElement)
      : null;
    const viewportOverflow = Math.max(
      0,
      document.documentElement.scrollWidth - window.innerWidth,
    );
    const protectedOverflow =
      element.scrollWidth <= element.clientWidth + 1 ||
      ["auto", "scroll"].includes(parentStyle?.overflowX);
    const longCellWidths = [...element.querySelectorAll("th, td")]
      .filter(
        (cell) => cell.textContent.replace(/\s+/g, " ").trim().length >= 20,
      )
      .map((cell) => cell.getBoundingClientRect().width);
    return {
      kind: element.tagName.toLowerCase(),
      width: rect.width,
      viewportOverflow,
      protectedOverflow,
      minimumLongCellWidth: longCellWidths.length
        ? Math.min(...longCellWidths)
        : null,
    };
  });
}

async function inspectKeyboardFocus(page) {
  for (let attempt = 0; attempt < 12; attempt += 1) {
    await page.keyboard.press("Tab");
    const inspection = await page.evaluate(() => {
      const active = document.activeElement;
      if (!(active instanceof HTMLElement)) return null;
      const rect = active.getBoundingClientRect();
      const style = getComputedStyle(active);
      const name = (
        active.getAttribute("aria-label") ||
        active.getAttribute("title") ||
        active.querySelector("img")?.getAttribute("alt") ||
        active.textContent ||
        ""
      )
        .replace(/\s+/g, " ")
        .trim();
      return {
        tag: active.tagName.toLowerCase(),
        name,
        focusVisible: active.matches(":focus-visible"),
        outlineStyle: style.outlineStyle,
        outlineWidth: style.outlineWidth,
        inViewport:
          rect.width > 0 &&
          rect.height > 0 &&
          rect.right > 0 &&
          rect.bottom > 0 &&
          rect.left < window.innerWidth &&
          rect.top < window.innerHeight,
      };
    });
    if (inspection?.focusVisible && inspection.inViewport) return inspection;
  }
  throw new Error("keyboard traversal did not reach a visible focus target");
}

async function inspectReducedMotion(page) {
  return page.evaluate(() => {
    const seconds = (value) =>
      value.split(",").reduce((maximum, token) => {
        const trimmed = token.trim();
        const numeric = Number.parseFloat(trimmed) || 0;
        const duration = trimmed.endsWith("ms") ? numeric / 1000 : numeric;
        return Math.max(maximum, duration);
      }, 0);
    const violations = [...document.querySelectorAll("body *")]
      .filter((element) => element.getClientRects().length > 0)
      .map((element) => {
        const style = getComputedStyle(element);
        return {
          tag: element.tagName.toLowerCase(),
          animation: seconds(style.animationDuration),
          transition: seconds(style.transitionDuration),
        };
      })
      .filter((record) => record.animation > 0.001 || record.transition > 0.001)
      .slice(0, 10);
    return {
      mediaMatches: matchMedia("(prefers-reduced-motion: reduce)").matches,
      scrollBehavior: getComputedStyle(document.documentElement).scrollBehavior,
      violations,
    };
  });
}

async function inspectPrint(page) {
  return page.evaluate(() => {
    const visible = (selector) =>
      [...document.querySelectorAll(selector)].some(
        (element) =>
          getComputedStyle(element).display !== "none" &&
          element.getClientRects().length,
      );
    const main = document.querySelector(
      "#quarto-document-content, main.content, main",
    );
    const rect = main?.getBoundingClientRect();
    const title = document.querySelector("#title-block-header h1, main h1");
    const titleRect = title?.getBoundingClientRect();
    const titleBlock = document.querySelector("#title-block-header");
    const titleBlockStyle = titleBlock ? getComputedStyle(titleBlock) : null;
    const readingTime = document.querySelector(
      "#title-block-header .reading-time-estimate",
    );
    const citation = document.querySelector('a[role="doc-biblioref"]');
    return {
      printMediaMatches: matchMedia("print").matches,
      fixedChromeVisible: visible(
        "#quarto-header, .left-sidebar, .right-sidebar",
      ),
      mainVisible: Boolean(rect && rect.width > 0 && rect.height > 0),
      titleVisible: Boolean(
        titleRect && titleRect.width > 0 && titleRect.height > 0,
      ),
      titleBackground: titleBlockStyle?.backgroundColor ?? null,
      titleColor: title ? getComputedStyle(title).color : null,
      readingTimeColor: readingTime
        ? getComputedStyle(readingTime).color
        : null,
      citationAfterContent: citation
        ? getComputedStyle(citation, "::after").content
        : "none",
      pageOverflow: Math.max(
        0,
        document.documentElement.scrollWidth - window.innerWidth,
      ),
    };
  });
}

async function inspectNoJavaScript(page) {
  return page.evaluate(() => {
    const visible = (element) => element && element.getClientRects().length > 0;
    const headings = [...document.querySelectorAll("h1")]
      .filter(visible)
      .map((heading) => heading.textContent.replace(/\s+/g, " ").trim());
    const namedLinks = [...document.querySelectorAll("nav a, .navbar a")]
      .filter(visible)
      .map((link) =>
        (link.getAttribute("aria-label") || link.textContent).trim(),
      )
      .filter(Boolean);
    return {
      headings,
      namedLinkCount: namedLinks.length,
      pageOverflow: Math.max(
        0,
        document.documentElement.scrollWidth - window.innerWidth,
      ),
    };
  });
}

function scenarioFailures(scenarioId, inspection) {
  if (scenarioId === "footer") {
    return [
      !inspection.visible && "footer is not visible",
      inspection.links.length < 3 && "footer companion links are missing",
      !/AffineDrift/i.test(inspection.text) &&
        "footer publication identity is missing",
      !inspection.links.some((link) => /UpstreamDrift/.test(link.name)) &&
        "footer executable-companion link is missing",
      inspection.links.some((link) => !link.name) &&
        "footer link lacks an accessible name",
      inspection.pageOverflow > 1 &&
        `footer causes ${inspection.pageOverflow}px page overflow`,
    ].filter(Boolean);
  }
  if (scenarioId === "dense-content") {
    return [
      !inspection.protectedOverflow &&
        "dense content has unbounded horizontal overflow",
      inspection.minimumLongCellWidth !== null &&
        inspection.minimumLongCellWidth < 80 &&
        `dense table collapses long cells to ${inspection.minimumLongCellWidth}px`,
      inspection.viewportOverflow > 1 &&
        `dense-content page has ${inspection.viewportOverflow}px page overflow`,
    ].filter(Boolean);
  }
  if (scenarioId === "keyboard-focus") {
    return [
      !inspection.name && "focused control lacks an accessible name",
      inspection.outlineStyle === "none" &&
        "focused control has no visible outline",
      Number.parseFloat(inspection.outlineWidth) < 2 &&
        "focus outline is too thin",
    ].filter(Boolean);
  }
  if (scenarioId === "reduced-motion") {
    return [
      !inspection.mediaMatches && "reduced-motion media query does not match",
      inspection.scrollBehavior !== "auto" &&
        "reduced motion does not disable smooth scrolling",
      inspection.violations.length &&
        `${inspection.violations.length} visible elements retain motion durations`,
    ].filter(Boolean);
  }
  if (scenarioId === "print") {
    return [
      !inspection.printMediaMatches && "print media query does not match",
      inspection.fixedChromeVisible &&
        "fixed navigation remains visible in print",
      !inspection.mainVisible && "main content is hidden in print",
      !inspection.titleVisible && "document title is hidden in print",
      inspection.titleBackground !== "rgb(255, 255, 255)" &&
        `print title background is ${inspection.titleBackground}`,
      inspection.titleColor !== "rgb(0, 0, 0)" &&
        `print title color is ${inspection.titleColor}`,
      inspection.readingTimeColor &&
        inspection.readingTimeColor !== "rgb(0, 0, 0)" &&
        `print reading-time color is ${inspection.readingTimeColor}`,
      inspection.citationAfterContent !== "none" &&
        "internal citation URLs are expanded in print",
      inspection.pageOverflow > 1 &&
        `print page has ${inspection.pageOverflow}px overflow`,
    ].filter(Boolean);
  }
  return [
    inspection.headings.length !== 1 &&
      `no-JavaScript page exposes ${inspection.headings.length} visible H1 elements`,
    inspection.namedLinkCount === 0 &&
      "no-JavaScript navigation has no named links",
    inspection.pageOverflow > 1 &&
      `no-JavaScript page has ${inspection.pageOverflow}px overflow`,
  ].filter(Boolean);
}

async function runScenario(browser, item, options) {
  const context = await browser.newContext({
    viewport: { width: item.viewport.width, height: item.viewport.height },
    colorScheme: item.theme,
    reducedMotion: "reduce",
    javaScriptEnabled: item.scenarioId !== "no-javascript",
    serviceWorkers: "block",
  });
  if (item.scenarioId !== "no-javascript") {
    await context.addInitScript((theme) => {
      localStorage.setItem("affinedrift-theme", theme);
    }, item.theme);
  }
  const page = await context.newPage();
  const screenshotPath = path.join(
    options.screenshotDir,
    scenarioScreenshotName(
      item.route,
      item.scenarioId,
      item.viewport.id,
      item.theme,
    ),
  );
  const failures = [];
  let inspection = {};
  let response = null;
  try {
    if (item.scenarioId === "print")
      await page.emulateMedia({ media: "print" });
    response = await page.goto(new URL(item.route, options.baseUrl).href, {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    if (item.scenarioId === "no-javascript") await page.waitForTimeout(100);
    else await settleScenarioPage(page);
    if (!response?.ok())
      failures.push(`document response failed: ${response?.status()}`);
    if (item.scenarioId === "footer") inspection = await inspectFooter(page);
    else if (item.scenarioId === "dense-content")
      inspection = await inspectDenseContent(page);
    else if (item.scenarioId === "keyboard-focus")
      inspection = await inspectKeyboardFocus(page);
    else if (item.scenarioId === "reduced-motion")
      inspection = await inspectReducedMotion(page);
    else if (item.scenarioId === "print") inspection = await inspectPrint(page);
    else inspection = await inspectNoJavaScript(page);
    failures.push(...scenarioFailures(item.scenarioId, inspection));
    fs.mkdirSync(options.screenshotDir, { recursive: true });
    await page.screenshot({
      path: screenshotPath,
      animations: "disabled",
      fullPage: false,
    });
  } catch (error) {
    failures.push(`scenario: ${error.message}`);
  } finally {
    await context.close();
  }
  return {
    ...item,
    status: response?.status() ?? null,
    passed: failures.length === 0,
    failures,
    screenshot: screenshotPath,
    inspection,
  };
}

async function runSupplementalScenarios(browser, manifest, options) {
  const plan = supplementalScenarioPlan(manifest);
  const results = [];
  for (const item of plan)
    results.push(await runScenario(browser, item, options));
  return { plan, results };
}

async function replaceScenarioCaptures(report, contract, options, browser) {
  const byRoute = new Map(
    contract.routes.map((record) => [record.route, record]),
  );
  const scenarioResults = [];
  for (const result of report.results) {
    const record = byRoute.get(result.route);
    if (record.scenario !== "site-search") continue;
    const context = await browser.newContext({
      viewport: {
        width: result.viewport.width,
        height: result.viewport.height,
      },
      colorScheme: result.theme,
      reducedMotion: "reduce",
      serviceWorkers: "block",
    });
    await context.addInitScript((theme) => {
      localStorage.setItem("affinedrift-theme", theme);
    }, result.theme);
    const page = await context.newPage();
    try {
      scenarioResults.push(
        await captureSearch(
          page,
          new URL(result.route, options.baseUrl).href,
          result.screenshot,
        ),
      );
    } finally {
      await context.close();
    }
  }
  return scenarioResults;
}

function attachScreenshotEvidence(report, contract, browser) {
  const byRoute = new Map(
    contract.routes.map((record) => [record.route, record]),
  );
  for (const result of report.results) {
    const record = byRoute.get(result.route);
    result.routeFamily ??= record?.family;
    result.scenarioId ??= record?.scenario;
    if (!result.screenshot || !fs.existsSync(result.screenshot)) {
      result.screenshot = null;
      continue;
    }
    result.screenshot = screenshotEvidence({
      item: result,
      screenshotPath: result.screenshot,
      screenshotBytes: fs.readFileSync(result.screenshot),
      sourceRevision: report.source_revision,
      browser,
    });
  }
}

async function runVisualVerification(options) {
  const { chromium } = require("@playwright/test");
  const manifest = JSON.parse(fs.readFileSync(options.manifestPath, "utf8"));
  const contract = assertRepresentativeContract(manifest);
  const boundedManifest = representativeManifest(manifest);
  fs.mkdirSync(path.dirname(options.outputPath), { recursive: true });
  const boundedManifestPath = `${options.outputPath}.manifest.json`;
  const structuralOutputPath = `${options.outputPath}.structural.json`;
  fs.writeFileSync(
    boundedManifestPath,
    `${JSON.stringify(boundedManifest, null, 2)}\n`,
  );

  const report = await runVerification({
    baseUrl: options.baseUrl,
    manifestPath: boundedManifestPath,
    outputPath: structuralOutputPath,
    screenshotDir: options.screenshotDir,
    screenshots: true,
    viewportIds: undefined,
    themes: undefined,
    routes: undefined,
  });
  report.source_revision = manifest.source_revision;
  const browser = await chromium.launch();
  try {
    await replaceScenarioCaptures(report, contract, options, browser);
    const supplemental = await runSupplementalScenarios(
      browser,
      manifest,
      options,
    );
    report.results.push(...supplemental.results);
    const renderer = { name: "chromium", version: browser.version() };
    report.browser = renderer;
    attachScreenshotEvidence(report, contract, renderer);
  } finally {
    await browser.close();
  }
  report.schema_version = "affinedrift/public-site-visual-verification/v1";
  report.evidence_count = report.results.length;
  report.failure_count = report.results.filter(
    (result) => !result.passed,
  ).length;
  report.expected_evidence_count =
    contract.routes.length *
      contract.viewports.length *
      contract.themes.length +
    supplementalScenarioPlan(manifest).length;
  report.passed =
    report.failure_count === 0 &&
    report.evidence_count === report.expected_evidence_count &&
    report.results.every((result) => result.screenshot);
  if (options.baselinePath) {
    report.visual_baseline = compareScreenshotBaseline(
      report,
      JSON.parse(fs.readFileSync(options.baselinePath, "utf8")),
    );
    report.passed = report.passed && report.visual_baseline.passed;
  }
  fs.writeFileSync(options.outputPath, `${JSON.stringify(report, null, 2)}\n`);
  if (options.candidateBaselinePath) {
    fs.mkdirSync(path.dirname(options.candidateBaselinePath), {
      recursive: true,
    });
    fs.writeFileSync(
      options.candidateBaselinePath,
      `${JSON.stringify(buildBaselineCandidate(report), null, 2)}\n`,
    );
  }
  return report;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const report = await runVisualVerification(options);
  console.log(
    `Public site visual verification: ${report.evidence_count}/` +
      `${report.expected_evidence_count}, passed=${report.passed}`,
  );
  if (!report.passed) process.exitCode = 1;
}

module.exports = {
  assertRepresentativeContract,
  parseArgs,
  representativeManifest,
  runVisualVerification,
  scenarioScreenshotName,
  supplementalScenarioPlan,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
