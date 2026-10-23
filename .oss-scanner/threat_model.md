<!-- Security-scan threat model for AffineDrift (#5127), in the anthropics/oss-scanner layout.
     Free text; the scanner reads it before it starts. Paths are relative to /src in the image. -->

# Threat Model

## What This Project Does and Where Untrusted Input Enters

AffineDrift is the source of the static website <https://affinedrift.com>: Quarto
(`.qmd`) and LaTeX writing about golf biomechanics and affine control, plus Python
modeling code (`src/`), build and CI scripts (`scripts/`, `shared_scripts/`), Pandoc Lua
filters, browser JavaScript (`js/`, `service-worker.js`) and a few MATLAB utilities.
There is no server-side application: production is static files on a CDN. The repo
`Dockerfile` `runtime` stage only wraps `python -m http.server` for local preview.

Treat these as the entry points, most important first:

1. **Browser JavaScript shipped to every visitor** (`js/*.js`, `service-worker.js`,
   `_includes/*.html`). Inputs are the URL, `localStorage`, `postMessage` events and the
   JSON data files the page fetches from its own origin. Watch the DOM sinks:
   - `innerHTML` in `js/ztcf-explorer-ui.js`, `js/drift-control-sandbox-ui.js`,
     `js/dcr-visualizer-ui.js` and `js/dataset-explorer-ui.js`;
   - `js/notes-workspace.js`: a pop-out window `postMessage` channel (origin-checked),
     with notes kept in `localStorage`;
   - `js/bibliography.js`: renders bibliography entries and their links, after a URL
     protocol allowlist;
   - `js/dataset-explorer-ui.js`: builds fetch URLs from manifest fields such as
     `fixture.path` and `schema_path`;
   - `js/page-feedback.js`: builds a prefilled GitHub issue URL from the page URL;
   - `js/history.js`, `js/metrics.js` and `js/dark-mode-toggle.js`: parse
     `localStorage` JSON;
   - `src/tools/wrist_universal_joint/grip_angle_polynomial_evaluator.js`: a hand-written
     expression parser for user-typed polynomials;
   - `service-worker.js` and `js/service-worker-utils.js`: cache strategy, navigation
     fallback to `offline.html`, and the update `postMessage` flow (cache poisoning,
     serving stale or cross-origin responses).
2. **Content security policy and third-party script loading.**
   - `_includes/site-head.html` sets a meta CSP that allows `'unsafe-inline'` scripts
     and `https://cdn.jsdelivr.net`.
   - `_includes/mathjax-loader.html` injects MathJax from jsDelivr with an SRI hash.
   - Report weaknesses that turn an injection elsewhere into script execution, and
     missing or incorrect SRI.
3. **Build-time content processing.** Article front matter and prose are written by the
   maintainers. They also come from automated agent PRs, so treat them as
   semi-trusted.
   - The Pandoc Lua filters in `scripts/filters/*.lua` and `_extensions/status/status.lua`
     turn front matter into `pandoc.RawInline` / `RawBlock` HTML.
   - `scripts/filters/term-tooltip.lua` has its own `escape_html`.
   - `scripts/filters/schema-jsonld.lua` writes front-matter values into an inline
     `<script type="application/ld+json">` through `json_escape`. Check whether a value
     containing `</script>` breaks out.
   - Any filter that emits unescaped metadata into HTML is a stored XSS on the
     published site.
   - The Quarto `post-render` hooks `scripts/post_render_citations.py` and
     `scripts/move_skip_link.py` rewrite the rendered HTML with BeautifulSoup.
4. **Supply chain of the build.**
   - `scripts/install_programming_companion.py` downloads a GitHub Actions artifact
     with `gh` and extracts a zip. A member-name guard runs before `extractall`; check it
     for zip-slip gaps, for example backslashes or absolute names.
   - `src/affine_control/programming_companion/` (`transport.py`, `consumer.py`,
     `validation.py`, `store.py`) fetches upstream manifests over HTTPS, without
     redirects and with a byte cap, and verifies SHA-256 digests and schemas. A bypass
     of digest, schema or size checks is in scope.
   - Dependency pins: `requirements-docker.lock` (hash-pinned), `package-lock.json`,
     and the Quarto `.deb` SHA-256 in `Dockerfile`.
5. **Data and file parsers in the modeling and tooling code.**
   - `src/tools/wrist_universal_joint/torque_calculator.py` evaluates user-supplied
     polynomial expressions with `simpleeval.EvalWithCompoundTypes`. An escape to
     arbitrary Python, or unbounded CPU or memory use, matters here.
   - XML: `src/tools/robot_model_examples.py` and `scripts/generate_feed.py`.
   - PDF and archives: `shared_scripts/document_title_case.py` (`pypdf`, `zipfile`).
   - Other inputs: the JSON-schema validation under `schemas/` and `scripts/`,
     YAML front matter, and BibTeX under `references/`.
6. **Notebook execution.** Executable `{python}` cells in `.qmd` files and the notebooks
   in `notebooks/` run at render time or on mybinder.org (`environment.yml`). They run
   with the renderer's privileges.
7. **CI-time scripts** that touch git or the network: `scripts/automerge_guard.py`,
   `scripts/build-html.py`, `scripts/check_bibliography_metadata.py`,
   `src/tools/utils/shell_utils.py` and `src/tools/verify_images.py`. Look for command
   injection through branch names, file names or PR text. The `.github/` workflows
   themselves are not in the image (`.dockerignore` drops them).

## Components That Matter Most / Least

- **Most:** the browser JS and HTML includes, because they reach every visitor of
  affinedrift.com. Next come the Lua filters and post-render scripts that produce that
  HTML, then the companion acquisition and verification code and the build supply chain.
- **Medium:** the `simpleeval` evaluator and the parsers in `src/tools/` and
  `shared_scripts/`. They run on maintainer machines and CI runners, not in production.
- **Least:** the numerical models in `src/affine_control/`, `src/golf_simulation/`,
  `src/tangent_models/` and `src/core/`. Their inputs are maintainer-written parameters
  and fixtures. A numerical bug there is a correctness issue, not a security finding.
  The MATLAB code (`src/tools/matlab_*`) and `tools/` are local developer utilities.

## How to Exercise It

- Python: `python -m pytest tests -q`. The default lane is offline; `pyproject.toml`
  `addopts` deselect the slow, network, e2e and live-simulation markers. The suite is in
  `tests/`, one module per feature, for example `tests/test_check_security_audit.py`.
- JavaScript: `npx jest` runs `tests/**/*.test.js` under jsdom. The service-worker
  suites are `tests/service-worker-*.test.js`. Node modules are preinstalled in
  `/src/node_modules`.
- Lua filters: Quarto is installed, so a filter can run on a crafted document with no
  network, for example
  `quarto pandoc -f markdown -t html --lua-filter scripts/filters/schema-jsonld.lua x.md`.
  Some filters also need the Quarto filter context (`quarto render x.qmd`).
- Not prebuilt: the full site render (`quarto render .`, about 14 minutes). Render a
  single page instead. Playwright browsers are not installed, so the E2E suite cannot
  run offline.

## How You Rate Severity

- **Critical:** script execution on the published site that needs no user interaction
  and is reachable from data a visitor or a third party controls. Also a build
  supply-chain compromise that lets a third party ship code into the published site, for
  example a companion digest bypass or zip-slip into the site tree.
- **High:** stored XSS on the published site from content or front-matter values that
  the Lua filters, `_includes/` or post-render scripts emit unescaped. Also DOM XSS
  through `innerHTML` reachable from fetched data or the URL, a CSP or SRI weakness that
  enables a concrete injection, and code execution in a build or CI script from
  repository-controlled input such as file names, branch names or artifact contents.
- **Medium:** service-worker cache poisoning or serving the wrong origin's content, open
  redirects, `postMessage` origin-check gaps, and a `simpleeval` sandbox escape that
  needs a maintainer to run the tool on crafted input.
- **Low:** denial of service in local-only tooling (huge or pathological expressions,
  XML, PDF or JSON input to developer scripts), and self-XSS that needs the victim to
  paste content into their own notes or `localStorage`.
- Not a vulnerability: numerical inaccuracy, solver divergence or a scientific error in
  the models or articles. Those go to the claim-audit process, not here.

## Anything to Leave Alone

- Article prose, LaTeX and the scientific content (`articles/`, `books/`, `content/`,
  `pages/`, `critiques/`, `reports/`, `references/`): do not report claims, typos or
  citations.
- Vendored and third-party code: `node_modules/`, MathJax and other CDN libraries, and
  the vendored fleet tooling in `shared_scripts/` and `fleet-hooks/`. The fragment
  tooling is byte-identical to Repository_Management, so report it there. Report our
  use of a dependency, not bugs inside it.
- Generated output and reports: `_site/`, `.quarto/`, `_includes/generated/`, the
  `models/programming/` catalog pages, `assessments/`, internal documentation under
  `docs/`, and the lock files' contents.
- The local preview server in the repo `Dockerfile` `runtime` stage
  (`python -m http.server`). It is not production.
- `.github/` workflows: they are outside this image and are reviewed separately.
- No secrets live in the repository. `.env.example` holds placeholders only.
