#!/usr/bin/env node
/* Governed representative visual evidence layered over the exhaustive verifier. */

const fs = require('fs');
const path = require('path');
const { runVerification } = require('./verify-public-site.js');
const {
  buildBaselineCandidate,
  compareScreenshotBaseline,
  screenshotEvidence,
} = require('./public-site-evidence.js');

function parseArgs(argv) {
  const options = {
    baseUrl: 'http://localhost:8000',
    manifestPath: 'docs/public-site-manifest.json',
    outputPath: 'artifacts/public-site-verification/visual-results.json',
    screenshotDir: 'artifacts/public-site-verification/screenshots',
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
    if (arg === '--base-url') options.baseUrl = value();
    else if (arg === '--manifest') options.manifestPath = value();
    else if (arg === '--output') options.outputPath = value();
    else if (arg === '--screenshot-dir') options.screenshotDir = value();
    else if (arg === '--candidate-baseline')
      options.candidateBaselinePath = value();
    else if (arg === '--baseline') options.baselinePath = value();
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
    throw new TypeError('representative route contract is missing');
  }
  const families = contract.routes.map((record) => record.family);
  const routes = contract.routes.map((record) => record.route);
  if (
    families.some((family) => typeof family !== 'string' || !family.trim()) ||
    new Set(families).size !== families.length
  ) {
    throw new TypeError(
      'representative family identities must be unique and non-empty',
    );
  }
  if (new Set(routes).size !== routes.length) {
    throw new TypeError('representative routes must be unique');
  }
  if (contract.routes.some((record) => !record.scenario?.trim())) {
    throw new TypeError('representative capture scenario is required');
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

async function captureSearch(page, targetUrl, screenshotPath) {
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.evaluate(() => document.fonts?.ready);
  await page.locator('#quarto-search button').click();
  const input = page.locator('.aa-DetachedContainer .aa-Input');
  await input.waitFor({ state: 'visible' });
  await input.fill('proximal distal');
  const results = page.locator('.aa-DetachedContainer .aa-Item');
  await results.first().waitFor({ state: 'visible' });
  const resultText = (await results.allTextContents()).join(' ');
  if (!/proximal.{0,30}distal|distal.{0,30}proximal/i.test(resultText)) {
    throw new Error('site search did not return a proximal-distal result');
  }
  await page.screenshot({
    path: screenshotPath,
    animations: 'disabled',
    fullPage: false,
  });
  return { query: 'proximal distal', result_count: await results.count() };
}

async function replaceScenarioCaptures(report, contract, options, browser) {
  const byRoute = new Map(
    contract.routes.map((record) => [record.route, record]),
  );
  const scenarioResults = [];
  for (const result of report.results) {
    const record = byRoute.get(result.route);
    if (record.scenario !== 'site-search') continue;
    const context = await browser.newContext({
      viewport: {
        width: result.viewport.width,
        height: result.viewport.height,
      },
      colorScheme: result.theme,
      reducedMotion: 'reduce',
      serviceWorkers: 'block',
    });
    await context.addInitScript((theme) => {
      localStorage.setItem('affinedrift-theme', theme);
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
    result.routeFamily = record.family;
    result.scenarioId = record.scenario;
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
  const { chromium } = require('@playwright/test');
  const manifest = JSON.parse(fs.readFileSync(options.manifestPath, 'utf8'));
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
    const renderer = { name: 'chromium', version: browser.version() };
    report.browser = renderer;
    attachScreenshotEvidence(report, contract, renderer);
  } finally {
    await browser.close();
  }
  report.schema_version = 'affinedrift/public-site-visual-verification/v1';
  report.expected_evidence_count =
    contract.routes.length * contract.viewports.length * contract.themes.length;
  report.passed =
    report.passed && report.evidence_count === report.expected_evidence_count;
  if (options.baselinePath) {
    report.visual_baseline = compareScreenshotBaseline(
      report,
      JSON.parse(fs.readFileSync(options.baselinePath, 'utf8')),
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
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
