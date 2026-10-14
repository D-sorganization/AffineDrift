/** Bounded evidence reload when first-party subresources return transient 5xx. */

const { navigateWithRetry, retryDelay } = require('./public-site-navigation.js');
const {
  failuresAreOnlyRetriableSubresourceNoise,
  isActionablePageError,
} = require('./public-site-browser-noise.js');

function sleepMs(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
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
      if (process.env.AFFINEDRIFT_VERIFY_VERBOSE === '1') {
        console.log(
          `Transient subresource load on ${item.route} (${item.viewport.id}, ${item.theme}); ` +
          `retrying evidence in ${delayMs}ms (attempt ${evidenceAttempt}/${maxEvidenceAttempts})...`,
        );
      }
      await sleepMs(delayMs);
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
    if (!failuresAreOnlyRetriableSubresourceNoise(failures)) break;
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
};
