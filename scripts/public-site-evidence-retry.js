/** Bounded evidence reload when first-party subresources return transient 5xx. */

const {
  RETRYABLE_STATUS_CODES,
  navigateWithRetry,
  retryDelay,
} = require('./public-site-navigation.js');
const {
  failuresAreOnlyRetriableSubresourceNoise,
  hasTransientSubresourceFailure,
  isActionableConsoleError,
  isActionablePageError,
} = require('./public-site-browser-noise.js');

function sleepMs(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createPageListeners(page, options) {
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const transientResponses = [];
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
  const onResponse = (response) => {
    try {
      const status = typeof response.status === 'function' ? response.status() : response.status;
      if (RETRYABLE_STATUS_CODES.has(status)) {
        const url = typeof response.url === 'function' ? response.url() : response.url;
        transientResponses.push({ url, status });
      }
    } catch {}
  };
  page.on('console', onConsole);
  page.on('pageerror', onPageError);
  page.on('requestfailed', onRequestFailed);
  page.on('response', onResponse);
  return {
    consoleErrors,
    pageErrors,
    failedRequests,
    transientResponses,
    onConsole,
    onPageError,
    onRequestFailed,
    onResponse,
    resetAttemptEvidence: () => {
      consoleErrors.length = 0;
      pageErrors.length = 0;
      failedRequests.length = 0;
      transientResponses.length = 0;
    },
    detach: () => {
      page.off('console', onConsole);
      page.off('pageerror', onPageError);
      page.off('requestfailed', onRequestFailed);
      page.off('response', onResponse);
    },
  };
}

function isRemoteBaseUrl(baseUrl) {
  if (!baseUrl || typeof baseUrl !== 'string') return false;
  try {
    const parsed = new URL(baseUrl);
    const host = parsed.hostname.toLowerCase();
    return (
      host !== 'localhost' &&
      host !== '127.0.0.1' &&
      host !== '0.0.0.0' &&
      host !== '::1' &&
      !host.endsWith('.local')
    );
  } catch {
    return false;
  }
}

function shouldRetryEvidenceAttempt(failures, listeners = {}, options = {}) {
  if (!Array.isArray(failures) || failures.length === 0) return false;
  if (hasTransientSubresourceFailure(failures, listeners)) return true;
  if (isRemoteBaseUrl(options.baseUrl)) return true;
  return false;
}

async function collectEvidenceAttempt(page, item, options, listeners, pageVerification) {
  const {
    waitForSettledPage,
    inspectRenderedPage,
    canonicalPathMatches,
  } = pageVerification;
  const { resetAttemptEvidence } = listeners;
  const targetUrl = new URL(item.route, options.baseUrl).href;
  let response = null;
  let inspection = { failures: ['page inspection did not run'] };
  let navigationError = null;
  let navigationAttempts = [];
  let navigationRetried = false;
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

    await waitForSettledPage(page);
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
  failures.push(...listeners.consoleErrors.map((error) => `console: ${error}`));
  failures.push(...listeners.pageErrors.filter(isActionablePageError).map((error) => `pageerror: ${error}`));
  failures.push(...listeners.failedRequests.map((error) => `requestfailed: ${error}`));
  for (const resp of listeners.transientResponses ?? []) {
    failures.push(`response: subresource HTTP ${resp.status} on ${resp.url}`);
  }

  return {
    failures,
    response,
    inspection,
    navigationError,
    navigationAttempts,
    navigationRetried,
  };
}

async function collectEvidenceWithSubresourceRetries(page, item, options, listeners, pageVerification) {
  const maxEvidenceAttempts = options.documentRetries + 1;
  const sleepFn = options.sleepFn ?? sleepMs;
  let evidenceAttemptCount = 0;
  let subresourceRetried = false;
  let response = null;
  let inspection = { failures: ['page inspection did not run'] };
  let navigationError = null;
  let navigationAttempts = [];
  let navigationRetried = false;
  let failures = [];
  for (let evidenceAttempt = 1; evidenceAttempt <= maxEvidenceAttempts; evidenceAttempt += 1) {
    if (evidenceAttempt > 1) {
      subresourceRetried = true;
      const delayMs = retryDelay(options.documentRetryDelayMs, evidenceAttempt - 1);
      if (process.env.AFFINEDRIFT_VERIFY_VERBOSE === '1' || options.verbose) {
        console.log(
          `Transient subresource load on ${item.route} (${item.viewport.id}, ${item.theme}); ` +
          `retrying evidence in ${delayMs}ms (attempt ${evidenceAttempt}/${maxEvidenceAttempts})...`,
        );
      }
      await sleepFn(delayMs);
      listeners.resetAttemptEvidence();
    }
    const attempt = await collectEvidenceAttempt(page, item, options, listeners, pageVerification);
    evidenceAttemptCount = evidenceAttempt;
    response = attempt.response;
    inspection = attempt.inspection;
    navigationError = attempt.navigationError;
    navigationAttempts = navigationAttempts.concat(attempt.navigationAttempts);
    navigationRetried = navigationRetried || attempt.navigationRetried;
    failures = attempt.failures;
    if (failures.length === 0) break;
    if (options.documentRetries === 0) break;
    if (!shouldRetryEvidenceAttempt(failures, listeners, options)) break;
    if (evidenceAttempt === maxEvidenceAttempts) break;
  }
  return {
    evidenceAttemptCount,
    subresourceRetried,
    response,
    inspection,
    navigationError,
    navigationAttempts,
    navigationRetried,
    failures,
  };
}

module.exports = {
  collectEvidenceWithSubresourceRetries,
  createPageListeners,
  isRemoteBaseUrl,
  shouldRetryEvidenceAttempt,
};
