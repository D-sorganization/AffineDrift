#!/usr/bin/env node
/* axe-core accessibility policy for the every-route verifier (ISSUE-4126). */

// axe-core policy (ISSUE-4126): one scan per route on the first evidence cell,
// reporting only serious/critical impacts. `warn` records violations in the
// evidence artifact without failing; `fail` turns them into cell failures.
// TODO(2026-09-03, #4139): default to 'fail' once AffineDrift #4139 (the
// violations this scan found) is closed. tests/e2e contrast test stays as-is.
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
    const scan = mode !== 'off' && !seen.has(item.route);
    if (scan) seen.add(item.route);
    return { ...item, axe: scan };
  });
}

function axePolicyEvidence(options, results) {
  const scanned = results.filter((result) => Array.isArray(result.axe_violations));
  const flagged = scanned.filter((result) => result.axe_violations.length > 0);
  return {
    mode: options.axe,
    impacts: [...AXE_FAILING_IMPACTS],
    scanned_route_count: scanned.length,
    routes_with_violations: flagged.map((result) => result.route).sort(),
    violation_count: flagged.reduce((sum, result) => sum + result.axe_violations.length, 0),
  };
}

async function scanWithAxe(page) {
  const axeModule = require('@axe-core/playwright');
  const AxeBuilder = axeModule.AxeBuilder ?? axeModule.default ?? axeModule;
  const outcome = await new AxeBuilder({ page }).analyze();
  return summarizeAxeViolations(outcome.violations);
}

module.exports = {
  AXE_FAILING_IMPACTS,
  AXE_MODES,
  axeMode,
  axePolicyEvidence,
  markAxeCells,
  scanWithAxe,
  summarizeAxeViolations,
};
