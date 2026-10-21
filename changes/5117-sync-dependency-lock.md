---
issue: 5117
summary: "Synchronize patched dependencies and repair accessible control names"
---

Synchronize the hashed Docker lock with pypdf 6.21.1 and Hypothesis 6.170.1,
preserving all other package versions. Update the PDF reader pin assertion;
scientific artifacts and their acceptance thresholds remain unchanged.

Repair the accessible names exposed by axe-core 4.14: titled Quarto callouts use
their visible content, and the metrics clear button announces its visible text.
Preserve authored labels, empty-title fallbacks, and keyboard behavior.

Validation: 30 Docker-lock and PDF contract tests, 48 affected JavaScript tests,
and a headless axe regression probe passed. Native every-route checks and the
protected merge queue remain required. Refs PR #5117.
