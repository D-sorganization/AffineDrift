const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const exists = (rel) => fs.existsSync(path.join(ROOT, rel));

const SMOKE_SPEC = 'tests/e2e/mobile-smoke.spec.js';
const LHCI_CONFIG = 'lighthouserc.json';
const NIGHTLY = '.github/workflows/cross-browser-nightly.yml';

/** Body of a top-level job in a workflow file, up to the next top-level job. */
function jobBlock(workflow, jobName) {
  const start = workflow.indexOf(`\n  ${jobName}:\n`);
  if (start === -1) return '';
  const rest = workflow.slice(start + 1);
  const next = rest.slice(1).search(/\n {2}[a-z][a-z0-9-]*:\n/);
  return next === -1 ? rest : rest.slice(0, next + 1);
}

describe('Mobile smoke and Lighthouse mobile baseline in CI (#5316)', () => {
  test('a phone-viewport Playwright smoke spec runs under the chromium project', () => {
    expect(exists(SMOKE_SPEC)).toBe(true);
    const spec = read(SMOKE_SPEC);
    // test.use keeps it inside `--project=chromium`, so e2e-tests runs it as-is.
    expect(spec).toMatch(/test\.use\(\{[^}]*width:\s*390,\s*height:\s*844[^}]*isMobile:\s*true/);
    expect(spec).toMatch(/hasTouch:\s*true/);
    expect(spec).toMatch(/scrollWidth/);
    expect(spec).toMatch(/navbar-toggler/);
  });

  test('the smoke spec and Lighthouse audit the same routes', () => {
    const config = JSON.parse(read(LHCI_CONFIG));
    const urls = config.ci.collect.url.map((url) => new URL(url).pathname);
    const spec = read(SMOKE_SPEC);
    expect(urls.length).toBeGreaterThanOrEqual(5);
    for (const route of urls) expect(spec).toContain(`'${route}'`);
  });

  test('Lighthouse runs as a mobile baseline that warns rather than blocks', () => {
    const { ci } = JSON.parse(read(LHCI_CONFIG));
    expect(ci.collect.settings.formFactor).toBe('mobile');
    const assertions = Object.values(ci.assert.assertions);
    expect(assertions.length).toBeGreaterThan(0);
    for (const [level] of assertions) expect(level).toBe('warn');
    expect(ci.upload.target).toBe('filesystem');
  });

  test('the nightly workflow runs a pinned lhci and keeps its reports', () => {
    const job = jobBlock(read(NIGHTLY), 'lighthouse-mobile');
    expect(job).not.toBe('');
    expect(job).toMatch(/needs:\s*build-site/);
    expect(job).toMatch(/@lhci\/cli@\d+\.\d+\.\d+ autorun/);
    expect(job).toMatch(/name:\s*lighthouse-mobile/);
  });

  test('the baseline never becomes a PR gate', () => {
    expect(read('.github/workflows/ci-standard.yml')).not.toMatch(/lhci|lighthouse/i);
  });
});
