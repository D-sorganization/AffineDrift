const {
  buildBaselineCandidate,
  compareScreenshotBaseline,
  decodePngDimensions,
  screenshotEvidence,
} = require('../scripts/public-site-evidence.js');
const {
  assertRepresentativeContract,
  representativeManifest,
} = require('../scripts/verify-public-site-visual.js');

function pngHeader(width, height) {
  const header = Buffer.alloc(24);
  Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]).copy(header);
  header.writeUInt32BE(13, 8);
  header.write('IHDR', 12, 'ascii');
  header.writeUInt32BE(width, 16);
  header.writeUInt32BE(height, 20);
  return header;
}

function fixtureManifest() {
  const families = [
    'home',
    'books',
    'monograph',
    'article',
    'model-workbench',
    'programming',
    'search',
    'critique',
    'research-report',
    'resource',
  ];
  const viewports = [
    { id: 'mobile', width: 390, height: 844 },
    { id: 'tablet', width: 768, height: 1024 },
    { id: 'intermediate', width: 1024, height: 768 },
    { id: 'margin-boundary', width: 1200, height: 900 },
    { id: 'margin-reentry', width: 1280, height: 900 },
    { id: 'desktop-small', width: 1366, height: 768 },
    { id: 'desktop-wide', width: 1920, height: 1080 },
  ];
  return {
    schema_version: 'affinedrift/public-site-manifest/v1',
    source_revision: 'abc123',
    page_count: families.length,
    pages: families.map((family) => ({
      route: `/${family}.html`,
      page_kind: 'hub',
    })),
    verification: {
      themes: ['light', 'dark'],
      viewports,
      every_page: { viewports: ['mobile'], themes: ['light', 'dark'] },
      representative: {
        routes: families.map((family) => ({
          family,
          route: `/${family}.html`,
          scenario: family === 'search' ? 'site-search' : 'fold',
        })),
        viewports: viewports.map((viewport) => viewport.id),
        themes: ['light', 'dark'],
      },
    },
  };
}

function fixtureEvidenceReport() {
  const item = {
    route: '/article.html',
    routeFamily: 'article',
    scenarioId: 'fold',
    pageKind: 'article',
    viewport: { id: 'tablet', width: 768, height: 1024 },
    theme: 'dark',
  };
  const browser = { name: 'chromium', version: '1.2.3' };
  return {
    source_revision: 'abc123',
    browser,
    results: [
      {
        ...item,
        screenshot: screenshotEvidence({
          item,
          screenshotPath: 'artifacts/example.png',
          screenshotBytes: pngHeader(768, 1024),
          sourceRevision: 'abc123',
          browser,
        }),
      },
    ],
  };
}

describe('public-site visual evidence contracts (SITE-UX)', () => {
  test('governs exactly ten families across a 140-cell core matrix', () => {
    const manifest = fixtureManifest();
    const contract = assertRepresentativeContract(manifest);
    const bounded = representativeManifest(manifest);

    expect(contract.routes).toHaveLength(10);
    expect(
      contract.routes.length *
        contract.viewports.length *
        contract.themes.length,
    ).toBe(140);
    expect(bounded.page_count).toBe(10);
    expect(bounded.verification.every_page.viewports).toEqual(
      contract.viewports,
    );
  });

  test('fails closed for duplicate families, missing routes, and absent scenarios', () => {
    const duplicate = fixtureManifest();
    duplicate.verification.representative.routes[1].family = 'home';
    expect(() => assertRepresentativeContract(duplicate)).toThrow(/family/);

    const missing = fixtureManifest();
    missing.verification.representative.routes[0].route = '/missing.html';
    expect(() => assertRepresentativeContract(missing)).toThrow(
      /page inventory/,
    );

    const scenario = fixtureManifest();
    delete scenario.verification.representative.routes[0].scenario;
    expect(() => assertRepresentativeContract(scenario)).toThrow(/scenario/);
  });

  test('rejects arbitrary bytes and decodes actual PNG dimensions', () => {
    expect(() => decodePngDimensions(Buffer.from('not a png'))).toThrow(/PNG/);
    expect(decodePngDimensions(pngHeader(768, 1024))).toEqual({
      width: 768,
      height: 1024,
    });
  });

  test('binds evidence to route, scenario, renderer, dimensions, and SHA-256', () => {
    const report = fixtureEvidenceReport();
    const evidence = report.results[0].screenshot;

    expect(evidence.route_family).toBe('article');
    expect(evidence.scenario_id).toBe('fold');
    expect(evidence.screenshot).toMatchObject({
      width: 768,
      height: 1024,
      byte_count: 24,
    });
    expect(evidence.screenshot.sha256).toMatch(/^[a-f0-9]{64}$/);
  });

  test('requires explicit approval and fails changed, missing, or incompatible baselines', () => {
    const report = fixtureEvidenceReport();
    const candidate = buildBaselineCandidate(report);
    expect(() => compareScreenshotBaseline(report, candidate)).toThrow(
      /approved/,
    );

    const approved = {
      ...candidate,
      status: 'approved',
      approval: {
        reviewed_by: 'independent-reviewer',
        reviewed_at: '2026-08-30T00:00:00Z',
        pull_request: 'https://github.com/D-sorganization/AffineDrift/pull/1',
      },
    };
    expect(compareScreenshotBaseline(report, approved).passed).toBe(true);

    const changed = JSON.parse(JSON.stringify(approved));
    changed.captures[0].sha256 = '0'.repeat(64);
    expect(compareScreenshotBaseline(report, changed).passed).toBe(false);

    const missing = JSON.parse(JSON.stringify(report));
    missing.results = [];
    expect(compareScreenshotBaseline(missing, approved).passed).toBe(false);

    const incompatible = JSON.parse(JSON.stringify(approved));
    incompatible.browser.version = '9.9.9';
    expect(() => compareScreenshotBaseline(report, incompatible)).toThrow(
      /browser/,
    );
  });

  test('rejects malformed approval metadata, count mismatches, and duplicate keys', () => {
    const report = fixtureEvidenceReport();
    const approved = {
      ...buildBaselineCandidate(report),
      status: 'approved',
      approval: {
        reviewed_by: 'independent-reviewer',
        reviewed_at: '2026-08-30T00:00:00Z',
        pull_request: 'https://github.com/D-sorganization/AffineDrift/pull/1',
      },
    };

    const missingTimestamp = JSON.parse(JSON.stringify(approved));
    delete missingTimestamp.approval.reviewed_at;
    expect(() => compareScreenshotBaseline(report, missingTimestamp)).toThrow(
      /baseline schema/,
    );

    const invalidTimestamp = JSON.parse(JSON.stringify(approved));
    invalidTimestamp.approval.reviewed_at = 'yesterday';
    expect(() => compareScreenshotBaseline(report, invalidTimestamp)).toThrow(
      /baseline schema/,
    );

    const invalidPullRequest = JSON.parse(JSON.stringify(approved));
    invalidPullRequest.approval.pull_request = 'not-a-url';
    expect(() => compareScreenshotBaseline(report, invalidPullRequest)).toThrow(
      /baseline schema/,
    );

    const countMismatch = JSON.parse(JSON.stringify(approved));
    countMismatch.capture_count = 2;
    expect(() => compareScreenshotBaseline(report, countMismatch)).toThrow(
      /capture_count/,
    );

    const duplicateKey = JSON.parse(JSON.stringify(approved));
    duplicateKey.captures.push({ ...duplicateKey.captures[0] });
    duplicateKey.capture_count = 2;
    expect(() => compareScreenshotBaseline(report, duplicateKey)).toThrow(
      /duplicate capture key/,
    );
  });
});
