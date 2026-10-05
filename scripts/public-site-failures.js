/** Formats failed public-site evidence items as job-log lines (#4924). */

const MAX_FAILURE_ANNOTATIONS = 20;
const MAX_CONSOLE_REASONS_SHOWN = 5;
const MAX_REASON_LENGTH = 300;

function truncateReason(text) {
  const flat = String(text).replace(/\s+/g, ' ').trim();
  return flat.length > MAX_REASON_LENGTH ? `${flat.slice(0, MAX_REASON_LENGTH)}...` : flat;
}

/**
 * Render failed evidence items as job-log lines (#4924). Diagnostic output
 * only: never alters pass/fail. Per failing item: a detail block plus one
 * `::error` annotation, capped at `limit` items with an omitted-count line.
 */
function formatFailures(results, limit = MAX_FAILURE_ANNOTATIONS) {
  const failed = results.filter((result) => !result.passed);
  const lines = [];
  for (const result of failed.slice(0, limit)) {
    const label = `${result.route} (${result.viewport?.id ?? '?'}/${result.theme ?? '?'})`;
    const reasons = result.failures ?? [];
    // Cap console errors by position so repeated identical messages count.
    let consoleSeen = 0;
    const shown = reasons.filter((r) => !r.startsWith('console:') || ++consoleSeen <= MAX_CONSOLE_REASONS_SHOWN);
    const hiddenConsole = Math.max(0, consoleSeen - MAX_CONSOLE_REASONS_SHOWN);
    lines.push(`FAILED ${label}${result.status != null ? ` status=${result.status}` : ''}`);
    for (const reason of shown) lines.push(`  - ${truncateReason(reason)}`);
    if (hiddenConsole > 0) lines.push(`  - ... ${hiddenConsole} more console errors`);
    const summary = truncateReason(shown.join('; ') || 'no failure reason recorded');
    lines.push(`::error title=Public site verification::${label}: ${summary}`);
  }
  if (failed.length > limit) {
    lines.push(`... ${failed.length - limit} more failed items omitted (see the uploaded report artifact)`);
  }
  return lines;
}

module.exports = {
  formatFailures,
};
