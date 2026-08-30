#!/usr/bin/env node
/* Manifest-driven rendered-site verification and screenshot evidence (WEB-D). */

const fs = require('fs');
const path = require('path');
const {
  navigateWithRetry,
  navigationRetryPolicyEvidence,
  RETRYABLE_STATUS_CODES,
  summarizeNavigationAttempts,
} = require('./public-site-navigation.js');

const SCHEMA_VERSION = 'affinedrift/public-site-manifest/v1';

function assertManifest(manifest) {
  if (!manifest || manifest.schema_version !== SCHEMA_VERSION) {
    throw new TypeError(`manifest must use ${SCHEMA_VERSION}`);
  }
  if (!Array.isArray(manifest.pages) || manifest.pages.length === 0) {
    throw new TypeError('manifest pages must be a non-empty array');
  }
  if (manifest.page_count !== manifest.pages.length) {
    throw new TypeError(
      `manifest page_count ${manifest.page_count} does not match ${manifest.pages.length}`,
    );
  }
  const routes = manifest.pages.map((page) => page.route);
  if (new Set(routes).size !== routes.length) {
    throw new TypeError('manifest contains a duplicate route');
  }
  if (!manifest.verification || !Array.isArray(manifest.verification.viewports)) {
    throw new TypeError('manifest verification viewport contract is missing');
  }
  return manifest;
}

function selectedValues(available, requested, label) {
  const values = requested ?? available;
  for (const value of values) {
    if (!available.includes(value)) {
      throw new TypeError(`unsupported ${label}: ${value}`);
    }
  }
  return values;
}

function buildEvidencePlan(manifest, options = {}) {
  assertManifest(manifest);
  const viewportById = new Map(
    manifest.verification.viewports.map((viewport) => [viewport.id, viewport]),
  );
  const defaultViewportIds = manifest.verification.every_page.viewports;
  const defaultThemes = manifest.verification.every_page.themes;
  const viewportIds = selectedValues(
    [...viewportById.keys()],
    options.viewportIds ?? defaultViewportIds,
    'viewport',
  );
  const themes = selectedValues(defaultThemes, options.themes, 'theme');
  const availableRoutes = manifest.pages.map((page) => page.route);
  const routes = selectedValues(availableRoutes, options.routes, 'route');
  const routeSet = new Set(routes);
  const plan = [];
  for (const page of manifest.pages.filter((candidate) => routeSet.has(candidate.route))) {
    for (const viewportId of viewportIds) {
      const viewport = viewportById.get(viewportId);
      if (!viewport) throw new TypeError(`viewport definition missing: ${viewportId}`);
      for (const theme of themes) {
        plan.push({
          route: page.route,
          pageKind: page.page_kind,
          viewport: { ...viewport },
          theme,
        });
      }
    }
  }
  return plan;
}

function screenshotName(route, viewportId, theme) {
  const withoutExtension = route.replace(/\.html$/i, '');
  const routeSlug = withoutExtension === '/'
    ? 'home'
    : withoutExtension
      .replace(/^\/+|\/+$/g, '')
      .split('/')
      .map((segment) => segment
        .replace(/[^a-zA-Z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
        .toLowerCase())
      .join('__');
  return `${routeSlug}__${viewportId}__${theme}.png`;
}

function screenshotOptions() {
  return { animations: 'disabled', fullPage: false };
}

function canonicalPathMatches(canonicalPath, route) {
  if (canonicalPath === route) return true;
  if (!route.endsWith('/index.html')) return false;
  return canonicalPath === route.slice(0, -'index.html'.length);
}

function boundedInteger(value, label) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 0) {
    throw new TypeError(`${label} must be a non-negative integer`);
  }
  return parsed;
}

function parseArgs(argv) {
  const options = {
    baseUrl: 'http://localhost:8000',
    manifestPath: 'docs/public-site-manifest.json',
    outputPath: 'artifacts/public-site-verification/results.json',
    screenshotDir: 'artifacts/public-site-verification/screenshots',
    screenshots: false,
    viewportIds: undefined,
    themes: undefined,
    routes: undefined,
    documentRetries: 0,
    documentRetryDelayMs: 500,
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
    else if (arg === '--viewports') options.viewportIds = value().split(',').filter(Boolean);
    else if (arg === '--themes') options.themes = value().split(',').filter(Boolean);
    else if (arg === '--routes') options.routes = value().split(',').filter(Boolean);
    else if (arg === '--document-retries') {
      options.documentRetries = boundedInteger(value(), 'document retries');
    } else if (arg === '--document-retry-delay-ms') {
      options.documentRetryDelayMs = boundedInteger(value(), 'document retry delay');
    }
    else if (arg === '--screenshots') options.screenshots = true;
    else throw new TypeError(`unknown argument: ${arg}`);
  }
  return options;
}

function fixedElementCanObscureHeading(style) {
  const zIndex = Number.parseInt(style.zIndex, 10);
  return style.pointerEvents !== 'none' && (Number.isNaN(zIndex) || zIndex >= 0);
}

function isActionableConsoleError(message) {
  return !message.includes('Permissions policy violation: compute-pressure');
}

function headingBeginsWithinViewport(rect, viewport) {
  return Boolean(
    rect &&
    rect.width > 0 &&
    rect.height > 0 &&
    rect.top < viewport.height &&
    rect.bottom > 0 &&
    rect.left < viewport.width &&
    rect.right > 0
  );
}

async function inspectRenderedPage(page, item) {
  const inspection = await page.evaluate(({ route, pageKind, viewportId, expectedTheme }) => {
    const isVisible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        Number(style.opacity) !== 0 &&
        rect.width > 0 &&
        rect.height > 0
      );
    };
    const normalize = (value) => (value ?? '').trim().replace(/\s+/g, ' ');
    const failures = [];
    const main = document.querySelector('#quarto-document-content, main.content, main');
    const visibleH1s = [...document.querySelectorAll('main h1')].filter(isVisible);
    if (visibleH1s.length !== 1) {
      failures.push(`visible H1 count is ${visibleH1s.length}`);
    } else if (!normalize(visibleH1s[0].textContent)) {
      failures.push('visible H1 is empty');
    }
    if (!main || normalize(main.textContent).length < 20) {
      failures.push('main content is missing or empty');
    }
    const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    if (overflow > 1) failures.push(`horizontal overflow is ${overflow}px`);
    const overflowElements = overflow > 1
      ? [...document.body.querySelectorAll('*')]
        .filter(isVisible)
        .map((element) => {
          const rect = element.getBoundingClientRect();
          return { element, rect };
        })
        .filter(({ rect }) => rect.left < -1 || rect.right > window.innerWidth + 1)
        .slice(0, 8)
        .map(({ element, rect }) => {
          const style = getComputedStyle(element);
          const parent = element.parentElement;
          return {
            selector: `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ''}${
              [...element.classList].slice(0, 3).map((name) => `.${name}`).join('')
            }`,
            parent: parent
              ? `${parent.tagName.toLowerCase()}${parent.id ? `#${parent.id}` : ''}${
                [...parent.classList].slice(0, 3).map((name) => `.${name}`).join('')
              }`
              : null,
            left: Math.round(rect.left),
            right: Math.round(rect.right),
            width: Math.round(rect.width),
            whiteSpace: style.whiteSpace,
            overflowWrap: style.overflowWrap,
            wordBreak: style.wordBreak,
          };
        })
      : [];
    if (!normalize(document.title)) failures.push('document title is empty');

    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (!canonical) {
      failures.push('canonical URL is missing');
    }

    const navbar = document.querySelector('#quarto-header nav, nav.navbar, nav');
    if (!navbar || !isVisible(navbar)) failures.push('primary navigation is not visible');
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const bootstrapTheme = document.documentElement.getAttribute('data-bs-theme');
    if (currentTheme !== expectedTheme || bootstrapTheme !== expectedTheme) {
      failures.push(`theme state is ${currentTheme}/${bootstrapTheme}, expected ${expectedTheme}`);
    }

    const titleBlock = document.querySelector('#title-block-header');
    if (titleBlock && isVisible(titleBlock) && viewportId !== 'mobile') {
      const title = titleBlock.querySelector('h1');
      const titleRect = title?.getBoundingClientRect();
      const blockRect = titleBlock.getBoundingClientRect();
      if (getComputedStyle(titleBlock).display === 'flex') {
        failures.push('title block uses the collapsing horizontal flex layout');
      }
      if (titleRect && blockRect.width > 0 && titleRect.width / blockRect.width < 0.7) {
        failures.push(
          `title occupies only ${Math.round((titleRect.width / blockRect.width) * 100)}% of title block`,
        );
      }
    }

    const visibleHeadings = [...document.querySelectorAll('main h1, main h2, main h3, main h4')]
      .filter(isVisible);
    for (let index = 1; index < visibleHeadings.length; index += 1) {
      const previous = Number(visibleHeadings[index - 1].tagName.slice(1));
      const current = Number(visibleHeadings[index].tagName.slice(1));
      if (current - previous > 1) {
        failures.push(
          `heading rank skips from ${visibleHeadings[index - 1].tagName} to ${visibleHeadings[index].tagName}`,
        );
        break;
      }
    }

    const missingAlt = [...document.querySelectorAll('main img:not([alt])')].filter(isVisible);
    if (missingAlt.length) failures.push(`${missingAlt.length} visible images lack alt attributes`);
    const visiblePendingMath = [...document.querySelectorAll('main .math')].filter((element) => {
      if (!isVisible(element) || element.querySelector('mjx-container')) return false;
      const rect = element.getBoundingClientRect();
      return rect.bottom > 0 && rect.top < window.innerHeight &&
        rect.right > 0 && rect.left < window.innerWidth;
    });
    if (visiblePendingMath.length) {
      failures.push(`${visiblePendingMath.length} visible equations remain untypeset`);
    }
    const visibleRawMath = [...document.querySelectorAll('main .math-showcase')].filter((element) => {
      if (!isVisible(element) || !element.textContent.includes('$$')) return false;
      const rect = element.getBoundingClientRect();
      return rect.bottom > 0 && rect.top < window.innerHeight &&
        rect.right > 0 && rect.left < window.innerWidth;
    });
    if (visibleRawMath.length) failures.push('visible display math remains untypeset');
    const unnamedButtons = [...document.querySelectorAll('button')].filter(
      (button) => isVisible(button) && !normalize(button.textContent) &&
        !normalize(button.getAttribute('aria-label')) && !normalize(button.getAttribute('title')),
    );
    if (unnamedButtons.length) failures.push(`${unnamedButtons.length} visible buttons lack names`);

    const notesToggle = document.querySelector('#ad-notes-workspace-toggle');
    const shouldHaveNotes = ['article', 'textbook', 'book'].includes(pageKind);
    if (shouldHaveNotes !== Boolean(notesToggle)) {
      failures.push(`reader notes availability does not match ${pageKind} page contract`);
    }

    if (pageKind === 'book' && viewportId === 'desktop') {
      if (route === '/books/index.html') {
        const hub = document.querySelector('.book-hub');
        const grid = document.querySelector('.resource-grid--long-form');
        const cards = grid ? [...grid.querySelectorAll('.resource-card')].filter(isVisible) : [];
        const cardRows = new Set(cards.map((card) => Math.round(card.getBoundingClientRect().top)));
        if (!hub || !isVisible(hub) || !grid || !isVisible(grid) || cards.length < 3) {
          failures.push('Books hub long-form library is incomplete or not visible');
        } else if (cardRows.size !== 1) {
          failures.push('Books hub long-form library does not share one desktop row');
        }
      } else {
        const sidebar = document.querySelector('#quarto-sidebar');
        if (!sidebar || !isVisible(sidebar)) {
          failures.push('Books navigation sidebar is not visible');
        }
      }
    }

    if (visibleH1s.length === 1) {
      const headingRect = visibleH1s[0].getBoundingClientRect();
      const fixedElements = [...document.body.querySelectorAll('*')].filter((element) => {
        const style = getComputedStyle(element);
        const zIndex = Number.parseInt(style.zIndex, 10);
        const canObscure = style.pointerEvents !== 'none' &&
          (Number.isNaN(zIndex) || zIndex >= 0);
        if (!isVisible(element) || style.position !== 'fixed' || !canObscure) return false;
        if (element.matches('.reading-progress')) return false;
        const rect = element.getBoundingClientRect();
        if (element.matches('#quarto-header') && rect.bottom - headingRect.top <= 3) {
          return false;
        }
        return !(
          rect.right <= headingRect.left || rect.left >= headingRect.right ||
          rect.bottom <= headingRect.top || rect.top >= headingRect.bottom
        );
      });
      if (fixedElements.length) failures.push('fixed utility chrome overlaps the primary heading');
    }

    return {
      failures,
      visibleH1s: visibleH1s.map((heading) => normalize(heading.textContent)),
      primaryHeadingRect: visibleH1s.length === 1
        ? (() => {
          const rect = visibleH1s[0].getBoundingClientRect();
          return {
            left: rect.left,
            right: rect.right,
            top: rect.top,
            bottom: rect.bottom,
            width: rect.width,
            height: rect.height,
          };
        })()
        : null,
      overflow,
      overflowElements,
      mainTextLength: main ? normalize(main.textContent).length : 0,
      canonical,
    };
  }, {
    route: item.route,
    pageKind: item.pageKind,
    viewportId: item.viewport.id,
    expectedTheme: item.theme,
  });
  if (
    inspection.primaryHeadingRect &&
    !headingBeginsWithinViewport(inspection.primaryHeadingRect, item.viewport)
  ) {
    inspection.failures.push('primary heading does not begin within the first viewport');
  }
  return inspection;
}

async function waitForVisibleMath(page) {
  await page.waitForFunction(() => {
    const visiblePendingMath = [...document.querySelectorAll('.math')].some((element) => {
      if (element.querySelector('mjx-container')) return false;
      const rect = element.getBoundingClientRect();
      return rect.bottom > 0 && rect.top < window.innerHeight &&
        rect.right > 0 && rect.left < window.innerWidth;
    });
    const visibleRawMath = [...document.querySelectorAll('.math-showcase')].some((element) => {
      const rect = element.getBoundingClientRect();
      return element.textContent.includes('$$') &&
        rect.bottom > 0 && rect.top < window.innerHeight &&
        rect.right > 0 && rect.left < window.innerWidth;
    });
    return !visiblePendingMath && !visibleRawMath;
  }, { timeout: 5000 });
}

async function verifyItem(page, item, options) {
  if (process.env.AFFINEDRIFT_VERIFY_VERBOSE === '1') {
    console.log(`Verifying ${item.route} (${item.viewport.id}, ${item.theme})`);
  }
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const onConsole = (message) => {
    if (message.type() === 'error' && isActionableConsoleError(message.text())) {
      consoleErrors.push(message.text());
    }
  };
  const onPageError = (error) => pageErrors.push(error.message);
  const onRequestFailed = (request) => {
    const target = new URL(request.url());
    const isRequiredMathRuntime = target.href.startsWith(
      'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/',
    );
    if (target.origin === new URL(options.baseUrl).origin || isRequiredMathRuntime) {
      failedRequests.push(`${target.pathname}: ${request.failure()?.errorText ?? 'failed'}`);
    }
  };
  page.on('console', onConsole);
  page.on('pageerror', onPageError);
  page.on('requestfailed', onRequestFailed);

  const targetUrl = new URL(item.route, options.baseUrl).href;
  let response = null;
  let inspection = { failures: ['page inspection did not run'] };
  let navigationError = null;
  let navigationAttempts = [];
  let navigationRetried = false;
  const resetAttemptEvidence = () => {
    consoleErrors.length = 0;
    pageErrors.length = 0;
    failedRequests.length = 0;
  };
  try {
    const navResult = await navigateWithRetry(page, targetUrl, {
      timeout: 60000,
      waitUntil: 'domcontentloaded',
      maxRetries: options.documentRetries,
      baseDelayMs: options.documentRetryDelayMs,
      resetAttemptEvidence,
    });
    response = navResult.response;
    navigationAttempts = navResult.attempts;
    navigationRetried = navResult.retried;
    if (navResult.error) {
      throw new Error(navResult.error);
    }

    await page.evaluate(() => document.fonts?.ready);
    // The gated MathJax request is injected after DOMContentLoaded. Wait for
    // its explicit post-typeset contract before checking the visible fold.
    await page.waitForFunction(() => {
      const gate = window.AffineDriftMathJax;
      if (!gate) {
        const mainText = document.querySelector('main')?.textContent ?? '';
        return !document.querySelector('.math') && !mainText.includes('$$');
      }
      return !gate.hasMath() || typeof window.MathJax?.typeset === 'function';
    }, { timeout: 20000 });
    await waitForVisibleMath(page);
    await page.evaluate(() => new Promise((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(resolve));
    }));
    await waitForVisibleMath(page);
    await page.waitForFunction(() => {
      const header = document.querySelector('#quarto-header.fixed-top');
      if (!header) return true;
      const bodyPadding = Number.parseFloat(getComputedStyle(document.body).paddingTop);
      return bodyPadding + 3 >= header.getBoundingClientRect().height;
    }, { timeout: 5000 });
    // The shipped UI deliberately defers table/code wrappers to an idle task.
    // Inspect the settled public page, not the transient pre-enhancement DOM.
    await page.waitForFunction(() => {
      const main = document.querySelector('#quarto-document-content, main.content, main');
      if (!main) return true;
      const tablesReady = [...main.querySelectorAll('table')].every((table) => {
        const parent = table.parentElement;
        return parent?.classList.contains('table-wrapper') ||
          getComputedStyle(parent).overflowX === 'auto';
      });
      const codeReady = [...main.querySelectorAll('pre')].every((pre) => {
        const parent = pre.parentElement;
        return parent?.classList.contains('code-wrapper') ||
          parent?.classList.contains('sourceCode') ||
          getComputedStyle(pre).overflowX === 'auto' ||
          getComputedStyle(parent).overflowX === 'auto';
      });
      return tablesReady && codeReady;
    }, { timeout: 5000 });
    inspection = await inspectRenderedPage(page, item);
  } catch (error) {
    navigationError = error.message;
  }

  const failures = [...inspection.failures];
  if (navigationError) failures.push(`inspection: ${navigationError}`);
  if (inspection.canonical) {
    const canonicalPath = new URL(inspection.canonical).pathname;
    if (!canonicalPathMatches(canonicalPath, item.route)) {
      failures.push(`canonical path ${canonicalPath} does not match ${item.route}`);
    }
  }
  if (!response || !response.ok()) {
    failures.push(`document response failed: ${response?.status() ?? navigationError ?? 'no response'}`);
  }
  failures.push(...consoleErrors.map((error) => `console: ${error}`));
  failures.push(...pageErrors.map((error) => `pageerror: ${error}`));
  failures.push(...failedRequests.map((error) => `requestfailed: ${error}`));

  let screenshot = null;
  if (options.screenshots && !navigationError) {
    await page.evaluate(async () => {
      const visibleImages = [...document.images].filter((image) => {
        const rect = image.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < window.innerHeight &&
          rect.right > 0 && rect.left < window.innerWidth;
      });
      await Promise.all(visibleImages.map((image) => image.decode().catch(() => undefined)));
    });
    fs.mkdirSync(options.screenshotDir, { recursive: true });
    screenshot = path.join(
      options.screenshotDir,
      screenshotName(item.route, item.viewport.id, item.theme),
    );
    await page.screenshot({ path: screenshot, ...screenshotOptions() });
  }

  page.off('console', onConsole);
  page.off('pageerror', onPageError);
  page.off('requestfailed', onRequestFailed);
  return {
    ...item,
    status: response?.status() ?? null,
    passed: failures.length === 0,
    failures,
    screenshot,
    inspection,
    navigation_attempts: navigationAttempts,
    navigation_retried: navigationRetried,
  };
}

async function verifyGroup(browser, items, options) {
  const first = items[0];
  const context = await browser.newContext({
    viewport: { width: first.viewport.width, height: first.viewport.height },
    colorScheme: first.theme,
    reducedMotion: 'reduce',
    // Verify the exact rendered artifact. PWA caching has its own tests and
    // must not substitute a previous build's CSS/JS during a release gate.
    serviceWorkers: 'block',
  });
  await context.addInitScript((theme) => {
    localStorage.setItem('affinedrift-theme', theme);
  }, first.theme);

  let nextIndex = 0;
  let completedCount = 0;
  const results = [];
  const workerCount = Math.min(4, items.length);
  await Promise.all(
    Array.from({ length: workerCount }, async () => {
      const page = await context.newPage();
      while (nextIndex < items.length) {
        const index = nextIndex;
        nextIndex += 1;
        results[index] = await verifyItem(page, items[index], options);
        completedCount += 1;
        if (completedCount % 25 === 0 || completedCount === items.length) {
          console.log(
            `Verified ${completedCount}/${items.length} ` +
            `(${first.viewport.id}, ${first.theme})`,
          );
        }
      }
      await page.close();
    }),
  );
  await context.close();
  return results;
}

async function runVerification(options) {
  const { chromium } = require('@playwright/test');
  const manifest = assertManifest(
    JSON.parse(fs.readFileSync(options.manifestPath, 'utf8')),
  );
  const plan = buildEvidencePlan(manifest, options);
  const groups = new Map();
  for (const item of plan) {
    const key = `${item.viewport.id}:${item.theme}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }

  const browser = await chromium.launch();
  const results = [];
  try {
    for (const items of groups.values()) {
      results.push(...await verifyGroup(browser, items, options));
    }
  } finally {
    await browser.close();
  }

  const failures = results.filter((result) => !result.passed);
  const report = {
    schema_version: 'affinedrift/public-site-verification/v1',
    base_url: options.baseUrl,
    manifest_page_count: manifest.page_count,
    evidence_count: results.length,
    expected_evidence_count: plan.length,
    passed: failures.length === 0 && results.length === plan.length,
    failure_count: failures.length,
    navigation_retry_policy: navigationRetryPolicyEvidence(options),
    ...summarizeNavigationAttempts(results),
    results,
  };
  fs.mkdirSync(path.dirname(options.outputPath), { recursive: true });
  fs.writeFileSync(options.outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  return report;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const report = await runVerification(options);
  console.log(
    `Public site verification: ${report.evidence_count}/${report.expected_evidence_count} evidence items, ` +
    `${report.failure_count} failed -> ${options.outputPath}`,
  );
  if (!report.passed) process.exitCode = 1;
}

module.exports = {
  assertManifest,
  buildEvidencePlan,
  canonicalPathMatches,
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
  navigateWithRetry,
  navigationRetryPolicyEvidence,
  parseArgs,
  RETRYABLE_STATUS_CODES,
  summarizeNavigationAttempts,
  screenshotOptions,
  screenshotName,
  runVerification,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
