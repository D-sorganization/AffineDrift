/* Declarative expansion and validation for supplemental visual scenarios. */

const SUPPLEMENTAL_SCENARIO_IDS = new Set([
  "footer",
  "dense-content",
  "keyboard-focus",
  "reduced-motion",
  "print",
  "no-javascript",
]);

function buildSupplementalScenarioPlan(manifest, representativeContract) {
  if (!Array.isArray(representativeContract?.routes)) {
    throw new TypeError("representative route contract is missing");
  }
  const scenarios = manifest?.verification?.supplemental?.scenarios;
  if (!Array.isArray(scenarios) || scenarios.length === 0) {
    throw new TypeError("supplemental scenario contract is missing");
  }
  const ids = scenarios.map((record) => record.id);
  if (
    ids.some((id) => !SUPPLEMENTAL_SCENARIO_IDS.has(id)) ||
    new Set(ids).size !== ids.length
  ) {
    throw new TypeError(
      "supplemental scenario ids must be unique and supported",
    );
  }
  const pages = new Map(manifest.pages.map((page) => [page.route, page]));
  const viewports = new Map(
    manifest.verification.viewports.map((viewport) => [viewport.id, viewport]),
  );
  const themes = new Set(manifest.verification.themes);
  const families = new Set(
    representativeContract.routes.map((record) => record.family),
  );
  const plan = [];
  for (const record of scenarios) {
    const page = pages.get(record.route);
    if (!page) {
      throw new TypeError(
        `supplemental route is absent from page inventory: ${record.route}`,
      );
    }
    if (!families.has(record.family)) {
      throw new TypeError(
        `supplemental route family is unsupported: ${record.family}`,
      );
    }
    if (!Array.isArray(record.viewports) || record.viewports.length === 0) {
      throw new TypeError(`supplemental viewport list is empty: ${record.id}`);
    }
    if (!Array.isArray(record.themes) || record.themes.length === 0) {
      throw new TypeError(`supplemental theme list is empty: ${record.id}`);
    }
    for (const viewportId of record.viewports) {
      const viewport = viewports.get(viewportId);
      if (!viewport) {
        throw new TypeError(`unsupported supplemental viewport: ${viewportId}`);
      }
      for (const theme of record.themes) {
        if (!themes.has(theme)) {
          throw new TypeError(`unsupported supplemental theme: ${theme}`);
        }
        plan.push({
          route: record.route,
          routeFamily: record.family,
          scenarioId: record.id,
          pageKind: page.page_kind,
          viewport: { ...viewport },
          theme,
        });
      }
    }
  }
  return plan;
}

module.exports = { buildSupplementalScenarioPlan };
