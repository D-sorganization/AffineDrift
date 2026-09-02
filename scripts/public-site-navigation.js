const RETRYABLE_STATUS_CODES = new Set([502, 503, 504]);

function assertNavigationContract(page, targetUrl, options) {
  if (!page || typeof page.goto !== 'function') {
    throw new TypeError('page must provide goto()');
  }
  if (typeof targetUrl !== 'string' || !targetUrl) {
    throw new TypeError(`targetUrl must be a non-empty string, got ${targetUrl}`);
  }
  const maxRetries = options.maxRetries ?? 0;
  const baseDelayMs = options.baseDelayMs ?? 500;
  if (!Number.isInteger(maxRetries) || maxRetries < 0) {
    throw new TypeError(`maxRetries must be a non-negative integer, got ${maxRetries}`);
  }
  if (typeof baseDelayMs !== 'number' || baseDelayMs < 0) {
    throw new TypeError(`baseDelayMs must be a non-negative number, got ${baseDelayMs}`);
  }
  return { maxRetries, baseDelayMs };
}

function retryDelay(baseDelayMs, attempt) {
  return baseDelayMs * Math.pow(2, attempt - 1);
}

/** Navigate with explicit, bounded retries for terminal-document HTTP responses. */
async function navigateWithRetry(page, targetUrl, options = {}) {
  const { maxRetries, baseDelayMs } = assertNavigationContract(page, targetUrl, options);
  const sleepFn = options.sleepFn ?? ((ms) => new Promise((resolve) => setTimeout(resolve, ms)));
  const logger = options.logger ?? console.log;
  const resetAttemptEvidence = options.resetAttemptEvidence ?? (() => undefined);
  const timeout = options.timeout ?? 60000;
  const waitUntil = options.waitUntil ?? 'domcontentloaded';
  const attempts = [];
  let response = null;
  for (let attempt = 1; attempt <= maxRetries + 1; attempt += 1) {
    resetAttemptEvidence();
    try {
      response = await page.goto(targetUrl, { waitUntil, timeout });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      attempts.push({ attempt, status: null, error: message });
      return { response: null, error: message, attempts, retried: attempt > 1 };
    }
    const status = response?.status() ?? null;
    attempts.push({ attempt, status, error: null });
    if (!RETRYABLE_STATUS_CODES.has(status) || attempt > maxRetries) {
      return { response, error: null, attempts, retried: attempt > 1 };
    }
    const delayMs = retryDelay(baseDelayMs, attempt);
    if (process.env.AFFINEDRIFT_VERIFY_VERBOSE === '1' || options.verbose) {
      logger(
        `Transient HTTP ${status} on ${targetUrl} (attempt ${attempt}/${maxRetries + 1}); ` +
        `retrying in ${delayMs}ms...`,
      );
    }
    await sleepFn(delayMs);
  }
  throw new Error('navigation retry loop exhausted without a terminal result');
}

/** Summarize attempt evidence without changing any evidence-cell outcome. */
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
      if (RETRYABLE_STATUS_CODES.has(attempt.status)) transientResponseCount += 1;
    }
    const terminal = attempts[attempts.length - 1];
    if (attempts.length > 1 && RETRYABLE_STATUS_CODES.has(terminal?.status)) {
      exhaustedRetryCount += 1;
    }
  }
  return {
    navigation_attempt_count: navigationAttemptCount,
    retried_evidence_count: retriedEvidenceCount,
    transient_response_count: transientResponseCount,
    exhausted_retry_count: exhaustedRetryCount,
  };
}

/** Describe the configured retry contract inside the verification artifact. */
function navigationRetryPolicyEvidence(options) {
  const maxRetries = options.documentRetries ?? 0;
  const baseDelayMs = options.documentRetryDelayMs ?? 500;
  if (!Number.isInteger(maxRetries) || maxRetries < 0) {
    throw new TypeError('documentRetries must be a non-negative integer');
  }
  if (!Number.isInteger(baseDelayMs) || baseDelayMs < 0) {
    throw new TypeError('documentRetryDelayMs must be a non-negative integer');
  }
  return {
    max_retries: maxRetries,
    maximum_attempts: maxRetries + 1,
    base_delay_ms: baseDelayMs,
    backoff: 'exponential',
    retryable_status_codes: [...RETRYABLE_STATUS_CODES].sort((left, right) => left - right),
  };
}

module.exports = {
  navigateWithRetry,
  navigationRetryPolicyEvidence,
  RETRYABLE_STATUS_CODES,
  summarizeNavigationAttempts,
};
