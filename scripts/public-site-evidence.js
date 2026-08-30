/* Deterministic screenshot evidence and approved-baseline contracts (SITE-UX). */

const crypto = require('crypto');
const path = require('path');
const Ajv2020 = require('ajv/dist/2020');
const addFormats = require('ajv-formats');
const baselineSchema = require('../schemas/public-site-screenshot-baseline-v1.schema.json');

const EVIDENCE_SCHEMA = 'affinedrift/public-site-screenshot-evidence/v1';
const BASELINE_SCHEMA = 'affinedrift/public-site-screenshot-baseline/v1';
const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);
const validateBaselineSchema = ajv.compile(baselineSchema);

function decodePngDimensions(bytes) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (
    !Buffer.isBuffer(bytes) ||
    bytes.length < 24 ||
    !bytes.subarray(0, 8).equals(signature) ||
    bytes.toString('ascii', 12, 16) !== 'IHDR'
  ) {
    throw new TypeError('screenshot bytes must contain a PNG IHDR header');
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width < 1 || height < 1)
    throw new TypeError('PNG dimensions must be positive');
  return { width, height };
}

function screenshotEvidence({
  item,
  screenshotPath,
  screenshotBytes,
  sourceRevision,
  browser,
}) {
  if (!Buffer.isBuffer(screenshotBytes) || screenshotBytes.length === 0) {
    throw new TypeError('screenshot bytes must be a non-empty Buffer');
  }
  if (!sourceRevision) throw new TypeError('source revision is required');
  if (!browser?.name || !browser?.version) {
    throw new TypeError('browser name and version are required');
  }
  const dimensions = decodePngDimensions(screenshotBytes);
  if (
    dimensions.width !== item.viewport.width ||
    dimensions.height !== item.viewport.height
  ) {
    throw new TypeError(
      `screenshot dimensions ${dimensions.width}x${dimensions.height} do not match ` +
        `${item.viewport.width}x${item.viewport.height}`,
    );
  }
  return {
    schema_version: EVIDENCE_SCHEMA,
    source_revision: sourceRevision,
    route: item.route,
    route_family: item.routeFamily ?? null,
    scenario_id: item.scenarioId ?? null,
    page_kind: item.pageKind,
    viewport: { ...item.viewport },
    theme: item.theme,
    browser: { ...browser },
    screenshot: {
      path: screenshotPath.split(path.sep).join('/'),
      width: dimensions.width,
      height: dimensions.height,
      byte_count: screenshotBytes.length,
      sha256: crypto.createHash('sha256').update(screenshotBytes).digest('hex'),
    },
  };
}

function captureKey(capture) {
  return [
    capture.route,
    capture.scenario_id,
    capture.viewport.id,
    capture.theme,
  ].join('|');
}

function buildBaselineCandidate(report) {
  const captures = report.results
    .filter((result) => result.screenshot)
    .map((result) => result.screenshot)
    .sort((left, right) => captureKey(left).localeCompare(captureKey(right)));
  return {
    schema_version: BASELINE_SCHEMA,
    status: 'candidate',
    approval: null,
    source_revision: report.source_revision,
    browser: { ...report.browser },
    capture_count: captures.length,
    captures: captures.map((capture) => ({
      key: captureKey(capture),
      route: capture.route,
      route_family: capture.route_family,
      scenario_id: capture.scenario_id,
      viewport: { ...capture.viewport },
      theme: capture.theme,
      width: capture.screenshot.width,
      height: capture.screenshot.height,
      sha256: capture.screenshot.sha256,
    })),
  };
}

function assertApprovedBaseline(baseline) {
  if (!validateBaselineSchema(baseline)) {
    const details = validateBaselineSchema.errors
      .map((error) => `${error.instancePath || '/'} ${error.message}`)
      .join('; ');
    throw new TypeError(`visual baseline schema invalid: ${details}`);
  }
  if (baseline.status !== 'approved') {
    throw new TypeError('visual baseline must be an approved v1 baseline');
  }
  if (baseline.capture_count !== baseline.captures.length) {
    throw new TypeError(
      'visual baseline capture_count must equal captures length',
    );
  }
  const keys = new Set();
  for (const capture of baseline.captures) {
    const derivedKey = captureKey(capture);
    if (capture.key !== derivedKey) {
      throw new TypeError(
        `visual baseline capture key does not match its dimensions: ${capture.key}`,
      );
    }
    if (keys.has(capture.key)) {
      throw new TypeError(
        `visual baseline contains duplicate capture key: ${capture.key}`,
      );
    }
    keys.add(capture.key);
  }
}

function compareScreenshotBaseline(report, baseline) {
  assertApprovedBaseline(baseline);
  if (
    baseline.browser?.name !== report.browser?.name ||
    baseline.browser?.version !== report.browser?.version
  ) {
    throw new TypeError(
      'visual baseline browser does not match the current renderer',
    );
  }
  const expected = new Map(
    baseline.captures.map((capture) => [capture.key, capture]),
  );
  const actual = report.results
    .filter((result) => result.screenshot)
    .map((result) => result.screenshot);
  const comparisons = actual.map((capture) => {
    const key = captureKey(capture);
    const expectedCapture = expected.get(key);
    const passed =
      Boolean(expectedCapture) &&
      expectedCapture.sha256 === capture.screenshot.sha256 &&
      expectedCapture.width === capture.screenshot.width &&
      expectedCapture.height === capture.screenshot.height;
    expected.delete(key);
    return {
      key,
      passed,
      actual_sha256: capture.screenshot.sha256,
      expected_sha256: expectedCapture?.sha256 ?? null,
      threshold: { kind: 'sha256-exact', max_diff_ratio: 0 },
    };
  });
  const failures = comparisons.filter((comparison) => !comparison.passed);
  for (const key of expected.keys())
    failures.push({ key, passed: false, missing: 'actual' });
  return {
    passed: failures.length === 0 && actual.length === baseline.capture_count,
    baseline_revision: baseline.source_revision,
    comparison_count: comparisons.length,
    failures,
    comparisons,
  };
}

module.exports = {
  BASELINE_SCHEMA,
  EVIDENCE_SCHEMA,
  buildBaselineCandidate,
  compareScreenshotBaseline,
  decodePngDimensions,
  screenshotEvidence,
};
