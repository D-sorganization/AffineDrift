const DEFAULT_DOCUMENT_ATTEMPTS = 1;
const DEFAULT_DOCUMENT_RETRY_DELAY_MS = 500;
const RETRIABLE_DOCUMENT_STATUSES = new Set([500, 502, 503, 504]);

/** Return whether a document status is eligible for the bounded transient policy. */
function isRetriableDocumentStatus(status) {
  return RETRIABLE_DOCUMENT_STATUSES.has(status);
}

function assertNavigationRetryContract(options) {
  if (!options?.page || typeof options.page.goto !== 'function') {
    throw new TypeError('page must provide goto()');
  }
  if (typeof options.targetUrl !== 'string' || options.targetUrl.length === 0) {
    throw new TypeError('targetUrl must be a non-empty string');
  }
  const maxAttempts = options.maxAttempts ?? DEFAULT_DOCUMENT_ATTEMPTS;
  const retryDelayMs = options.retryDelayMs ?? DEFAULT_DOCUMENT_RETRY_DELAY_MS;
  if (!Number.isInteger(maxAttempts) || maxAttempts < 1) {
    throw new TypeError('maxAttempts must be a positive integer');
  }
  if (!Number.isInteger(retryDelayMs) || retryDelayMs < 0) {
    throw new TypeError('retryDelayMs must be a non-negative integer');
  }
  return { maxAttempts, retryDelayMs };
}

function navigationOutcome(response, attempt, maxAttempts) {
  const status = response?.status() ?? null;
  if (response?.ok()) return { status, outcome: 'success' };
  if (!isRetriableDocumentStatus(status)) return { status, outcome: 'non-retriable' };
  return { status, outcome: attempt < maxAttempts ? 'retry' : 'exhausted' };
}

function waitForRetry(delayMs) {
  return new Promise((resolve) => setTimeout(resolve, delayMs));
}

/**
 * Navigate to one document with bounded, recorded retries for transient 5xx responses.
 *
 * The returned response is always the terminal attempt. Navigation exceptions and
 * non-retriable responses fail closed without retrying.
 */
async function navigateDocumentWithRetries(options) {
  const { maxAttempts, retryDelayMs } = assertNavigationRetryContract(options);
  const wait = options.wait ?? waitForRetry;
  const resetAttemptEvidence = options.resetAttemptEvidence ?? (() => undefined);
  const reportRetry = options.reportRetry ?? console.warn;
  const attempts = [];
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    resetAttemptEvidence();
    let response;
    try {
      response = await options.page.goto(options.targetUrl, {
        waitUntil: 'domcontentloaded',
        timeout: 60000,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      attempts.push({
        attempt,
        status: null,
        outcome: 'navigation-error',
        error: message,
      });
      return { response: null, navigationError: message, attempts };
    }
    const result = navigationOutcome(response, attempt, maxAttempts);
    attempts.push({ attempt, ...result });
    if (result.outcome !== 'retry') return { response, navigationError: null, attempts };
    reportRetry(
      `Transient document response ${result.status} for ${options.targetUrl}; ` +
        `retrying ${attempt + 1}/${maxAttempts}.`,
    );
    await wait(retryDelayMs);
  }
  throw new Error('navigation retry loop exhausted without a terminal result');
}

/** Summarize per-cell navigation evidence for top-level release reporting. */
function summarizeNavigationAttempts(results) {
  if (!Array.isArray(results)) throw new TypeError('results must be an array');
  let navigationAttemptCount = 0;
  let retriedEvidenceCount = 0;
  let transientResponseCount = 0;
  let exhaustedRetryCount = 0;
  for (const result of results) {
    const attempts = result.navigation_attempts ?? [];
    if (!Array.isArray(attempts)) throw new TypeError('navigation_attempts must be an array');
    navigationAttemptCount += attempts.length;
    if (attempts.length > 1) retriedEvidenceCount += 1;
    for (const attempt of attempts) {
      if (isRetriableDocumentStatus(attempt.status)) transientResponseCount += 1;
      if (attempt.outcome === 'exhausted') exhaustedRetryCount += 1;
    }
  }
  return {
    navigation_attempt_count: navigationAttemptCount,
    retried_evidence_count: retriedEvidenceCount,
    transient_response_count: transientResponseCount,
    exhausted_retry_count: exhaustedRetryCount,
  };
}

module.exports = {
  isRetriableDocumentStatus,
  navigateDocumentWithRetries,
  summarizeNavigationAttempts,
};
