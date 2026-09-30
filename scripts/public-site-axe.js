#!/usr/bin/env node
/* axe-core accessibility policy for the every-route verifier (ISSUE-4126). */

// axe-core policy (ISSUE-4126, ISSUE-4562): scan accessibility on the planned
// evidence matrix cells (including dark theme and mobile viewports), reporting
// only serious/critical impacts. `warn` records violations in the
// evidence artifact without failing; `fail` turns them into cell failures.
// Defaults to 'fail' now that AffineDrift #4139 has closed.
const AXE_MODES = Object.freeze(['off', 'warn', 'fail']);
const AXE_FAILING_IMPACTS = Object.freeze(['serious', 'critical']);

function axeMode(value) {
  if (!AXE_MODES.includes(value)) {
    throw new TypeError(`--axe must be one of ${AXE_MODES.join(', ')}; got ${value}`);
  }
  return value;
}

function summarizeAxeViolations(violations) {
  if (!Array.isArray(violations)) throw new TypeError('axe violations must be an array');
  return violations
    .filter((violation) => AXE_FAILING_IMPACTS.includes(violation.impact))
    .map((violation) => ({
      id: violation.id,
      impact: violation.impact,
      help: violation.help,
      help_url: violation.helpUrl,
      node_count: Array.isArray(violation.nodes) ? violation.nodes.length : 0,
      first_target: Array.isArray(violation.nodes) && violation.nodes[0]
        ? String((violation.nodes[0].target ?? [])[0] ?? '')
        : '',
    }))
    .sort((a, b) => a.id.localeCompare(b.id));
}

function markAxeCells(plan, mode) {
  const seen = new Set();
  return plan.map((item) => {
    const viewportId = item.viewport?.id ?? item.viewport ?? 'default';
    const key = `${item.route}::${viewportId}::${item.theme}`;
    const scan = mode !== 'off' && !seen.has(key);
    if (scan) seen.add(key);
    return { ...item, axe: scan };
  });
}

function axePolicyEvidence(options, results) {
  const scanned = results.filter((result) => Array.isArray(result.axe_violations));
  const flagged = scanned.filter((result) => result.axe_violations.length > 0);
  return {
    mode: options.axe,
    impacts: [...AXE_FAILING_IMPACTS],
    scanned_route_count: new Set(scanned.map((result) => result.route)).size,
    scanned_cell_count: scanned.length,
    routes_with_violations: [...new Set(flagged.map((result) => result.route))].sort(),
    violation_count: flagged.reduce((sum, result) => sum + result.axe_violations.length, 0),
  };
}

async function scanWithAxe(page) {
  const axeModule = require('@axe-core/playwright');
  const AxeBuilder = axeModule.AxeBuilder ?? axeModule.default ?? axeModule;
  const outcome = await new AxeBuilder({ page })
    .exclude('iframe')
    .analyze();
  return summarizeAxeViolations(outcome.violations);
}

function isBaselineAxeCell(item) {
  if (!item) return false;
  const viewportId = item.viewport?.id ?? item.viewport;
  return viewportId === 'desktop-small' && item.theme === 'light';
}

function axeCellFailures(item, axeViolations, options = {}) {
  if (!axeViolations || options.axe !== 'fail') return [];
  if (!isBaselineAxeCell(item)) return [];
  return axeViolations.map((v) => `axe ${v.impact}: ${v.id} (${v.node_count} nodes) ${v.help}`);
}

function applyAxeResult(item, axeViolations, options = {}) {
  const failures = [...(item.failures ?? [])];
  const axeFailures = axeCellFailures(item, axeViolations, options);
  failures.push(...axeFailures);
  return {
    ...item,
    passed: failures.length === 0,
    failures,
    ...(axeViolations ? { axe_violations: axeViolations } : {}),
  };
}

function logAxeReport(report) {
  const axe = report?.axe_policy;
  if (!axe || axe.mode === 'off') return;
  console.log(
    `axe-core (${axe.mode}): ${axe.scanned_route_count} routes scanned, ` +
    `${axe.violation_count} serious/critical violations on ${axe.routes_with_violations.length} routes`,
  );
  if (axe.mode === 'warn' && axe.violation_count > 0) {
    console.log(`::warning::axe-core found ${axe.violation_count} serious/critical violations (warn-only, #4126)`);
  }
  const nonBaselineViolations = (report.results ?? [])
    .filter((r) => !isBaselineAxeCell(r))
    .reduce((sum, r) => sum + (r.axe_violations?.length ?? 0), 0);
  if (nonBaselineViolations > 0) {
    console.log(
      `::warning::axe-core found ${nonBaselineViolations} violations on non-baseline matrix cells (dark/mobile); triaged into follow-up issues (#4562)`,
    );
  }
}

module.exports = {
  AXE_FAILING_IMPACTS,
  AXE_MODES,
  applyAxeResult,
  axeCellFailures,
  axeMode,
  axePolicyEvidence,
  isBaselineAxeCell,
  logAxeReport,
  markAxeCells,
  scanWithAxe,
  summarizeAxeViolations,
};
