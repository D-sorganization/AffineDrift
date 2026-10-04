# 0002. Interactive Technology Stack

## Status

Accepted. This records Board decision D3, option (d), for AffineDrift issue
#4531 (WEB-06.1) under epic #4543 (E6, Interactive Models and
Reproducibility).

- **Decision source:** `docs/development/website-improvement-draft-issues-2026-09-29.md`,
  §5, row D3. The recommendation reads "OJS for lightweight widgets and
  Pyodide for faithful `src/` model execution, both self-hosted".
- **Board disposition:** recorded on PR #4485 on 2026-09-29 (Runner Dashboard
  Board session `th_eda845e6415b`; Alpha, Charlie and Delta present, a
  quorum of 3 of 4). The Board accepted all 14 epics, including E6. It held
  only D4, D7 and D8 for owner decision (§6 of the same file), so D3 stands
  as recommended.

This ADR gates #4533, #4534 and #4540. It decides nothing about D4
(canonical versions), D7 (content licence) or D8 (external review model).

## Context

The site has no `{ojs}`, Pyodide or Shinylive content. Its interactive pieces
are plain JavaScript:

- The rotation converter (`articles/rotation-converter.qmd`) loads Three.js
  0.147.0 and `OrbitControls` from `cdn.jsdelivr.net`.
- The grip-angle simulator
  (`src/tools/wrist_universal_joint/grip_angle_simulator.html`) loads
  Plotly 2.26.0 from `cdn.plot.ly`.
- The DCR widget (#4535, `js/dcr-visualizer.js`) is a hand-written
  JavaScript mirror of `src/affine_control/reachability.py`. It is kept
  honest by one shared fixture, `tests/fixtures/dcr_visualizer_parity.json`,
  which both `tests/test_dcr_visualizer_parity.py` and
  `tests/dcr-visualizer.test.js` read.

Epic E6 plans more widgets, some of which run real models, such as the ZTCF
explorer driven by `src/affine_control/ztcf_contract.py`. Re-implementing
such models in JavaScript would create a second, unreviewed copy of the
science. Each copy can drift from the Python source that the articles cite.

Constraints that any choice must respect:

- The site is a static Quarto build (`output-dir: docs`) served from
  `affinedrift.com`.
- `service-worker.js` precaches a fixed asset list. Its `CACHE_NAME` is
  rewritten from a content hash by `scripts/update_sw_cache_version.py`,
  which runs in `npm run build`. `tests/e2e/offline.spec.js` asserts that
  cached pages work offline.
- `_includes/site-head.html` sets a site-wide Content-Security-Policy whose
  `connect-src` is `'self'`.
- `config/runtime_performance_budget.json` (WEB-10.1, #4570) holds the
  per-route LCP, CLS, TBT and transfer budgets that
  `tests/e2e/performance_budget.spec.js` enforces.
- `src/affine_control/*` depends only on the standard library, NumPy, SciPy
  (`scipy.integrate`) and the in-repo `src.core` package. All three are
  available in the Pyodide distribution.

Options considered (D3):

| Option | Strength | Weakness |
| --- | --- | --- |
| (a) Plain JS or OJS only | Small, fast, native to Quarto | Every model is re-implemented in JS, so parity rests only on tests |
| (b) Pyodide only | Runs the cited `src/` code unchanged | Several MB on first use; too heavy for a slider and a plot |
| (c) Shinylive | Python UI in the browser | Brings its own UI framework and a larger runtime; ties widget UI to Shiny |
| (d) A mix | Each widget pays only for what it needs | Two runtimes to govern; needs a rule for which one a widget uses |

## Decision

Adopt option (d).

### 1. Choosing a Runtime

- **OJS** (`{ojs}` cells, or plain JS modules under `js/`) is for lightweight
  widgets. These show closed-form or short-iteration mathematics, such as a
  slider over a formula or a plot of a precomputed trajectory.
- **Pyodide** is for faithful model execution. Use it when a widget runs a
  function from `src/affine_control/*` (or another `src/` package) that
  integrates dynamics, solves an optimisation, or would need more than about
  50 lines of ported logic.
- When in doubt, use Pyodide. A JavaScript port is allowed only when the
  ported logic is small enough to review line by line against the Python it
  mirrors.
- Shinylive is not adopted.

### 2. Self-Hosting, No CDN

All widget code, runtimes, packages and data are served from the site's own
origin.

- **Pyodide.** A pinned Pyodide release (the core runtime plus the NumPy and
  SciPy packages that `src/` needs) is vendored under
  `vendor/pyodide/<version>/`. `loadPyodide({ indexURL })` points at that
  path. The version, file list, SHA-256 hashes and SPDX licence (MPL-2.0) are
  recorded in a committed lock file next to it. The lock is checked by a
  Python test. A version bump is its own pull request.
- **OJS.** Quarto ships the OJS runtime in the built site. Widget cells must
  not call `require()` or `import` with a remote URL, and must not use a
  standard-library binding that the Observable resolver fetches from a CDN.
  Any such library is vendored under `vendor/<library>/<version>/` and
  imported from there.
- **Enforcement.** Each widget page gets a Playwright assertion that the
  widget makes no cross-origin requests while loading and running. A test
  also scans widget sources for CDN hosts (`cdn.jsdelivr.net`, `unpkg.com`,
  `cdn.plot.ly`, `esm.sh`, `cdn.skypack.dev`).
- **Content-Security-Policy.** The first Pyodide widget amends the CSP only
  as far as WebAssembly needs (`'wasm-unsafe-eval'` in `script-src`). It never
  adds a third-party host. `https://cdn.jsdelivr.net` leaves the CSP when the
  CDN migrations below are complete.

### 3. Offline and PWA Behaviour

- **OJS widgets** and their vendored libraries are small, so they join the
  service worker's precache list. Each such file is also added to
  `HASH_SOURCES` in `scripts/update_sw_cache_version.py`, so changing it
  busts `CACHE_NAME` (the script's existing contract: every listed path must
  exist).
- **The Pyodide runtime is not precached.** It is too large to download
  during service-worker install. On first activation, its files are stored
  cache-first in the versioned cache. Later visits, including offline ones,
  then load it locally. The runtime is immutable per version, because its
  path contains the version. `HASH_SOURCES` therefore lists the Pyodide lock
  file, the module manifest (§5) and the widget loader, not the
  multi-megabyte binaries.
- **Honest offline fallback.** If a Pyodide widget is activated offline before
  its runtime is cached, it does not fail silently. It shows a static result
  rendered from the same golden vectors that the parity tests use, labelled
  as precomputed, and states that live execution needs one online visit.
- `tests/e2e/offline.spec.js` gains a case for each runtime class when its
  first widget lands.

### 4. Performance Budget per Widget Class

Numbers are compressed bytes transferred by the widget beyond the host page.
Time to interactive (TTI) is measured from the widget becoming visible (OJS)
or from the user's activation (Pyodide) until the widget sets
`data-widget-ready="true"` and responds to input. Measurements use
Playwright's Chromium with 4× CPU throttling and a 1.6 Mbit/s, 150 ms RTT
network, the Lighthouse mobile profile.

| Widget class | Example | Loads | KB transferred (max) | TTI (max) |
| --- | --- | --- | --- | --- |
| A. Plain JS or OJS, 2-D | DCR widget (#4535) | With the page | 60 KB | 1.0 s |
| B. OJS with a vendored plotting library | Trajectory plot over a fixture | With the page | 250 KB, of which 200 KB is the shared library (charged once per page) | 2.0 s |
| C. OJS with vendored 3-D (Three.js) | Rotation converter | With the page | 400 KB, of which 350 KB is the shared library (charged once per page) | 3.0 s |
| D1. Pyodide, NumPy only, cold | A `reachability.py` model | On activation only | 9,000 KB | 12 s |
| D2. Pyodide with SciPy, cold | ZTCF explorer (`scipy.integrate`) | On activation only | 20,000 KB | 20 s |
| D. Pyodide, warm (runtime cached) | Any class D widget | On activation only | 150 KB (widget code and wheel) | 4 s |

Rules that go with the table:

- Classes A to C load with the page. Their bytes also count against the
  route budget in `config/runtime_performance_budget.json`. A widget may not
  push its page past that budget.
- Class D loads nothing until the reader activates it. The activation control
  states the cold download size (for example, "Run the model (about 9 MB on
  first use)"). Pyodide loads in a Web Worker, so it adds no main-thread
  blocking time to the page.
- These are ceilings. Any widget may come in under them, and a widget's own
  pull request may tighten its class. Raising a ceiling needs a superseding
  ADR or an issue with the measurements, under the fleet rule against
  loosening budgets.
- A Playwright check, run per widget, records the transferred bytes and TTI
  against this table. It is added with the first widget of each class.

### 5. How Widgets Import `src/` Code

- **Pyodide widgets execute the repository's own Python source.** WEB-06.2
  (#4532) made `src` installable: `pyproject.toml` builds the `affinedrift`
  wheel from the `src*` packages. The site build copies the wheel built from
  the same commit under `vendor/affinedrift/`. A widget installs it with
  `micropip.install(<same-origin URL>, deps=False)`. Pyodide already supplies
  NumPy and SciPy, and the wheel's other runtime dependencies are not used by
  browser-executed modules. `from src.affine_control.reachability import ...`
  then resolves exactly as it does in pytest.
- The build writes a manifest of each browser-executed module in the wheel,
  with its SHA-256. A Python test fails if any entry differs from its `src/`
  original, so the browser can never run stale science.
- Modules staged for the browser may import only the standard library, NumPy,
  SciPy and other `src/` modules. They must perform no file or network I/O at
  import time. Widget-specific glue (argument parsing and output shaping)
  lives in the widget, not in `src/`.
- **OJS and plain JS widgets** keep their mathematics in a pure, DOM-free
  module under `js/` (the `js/dcr-visualizer.js` pattern), so Jest can test it.
  Each exported function cites the Python function it mirrors in a comment, as
  `src/affine_control/<module>.py::<function>`.

### 6. Parity Strategy

Browser and Python results are kept in agreement by golden vectors generated
from Python.

- **Location.** `tests/fixtures/widgets/<widget-id>.parity.json`, one file per
  widget, generated by a Python script that has a `--check` mode. The existing
  `tests/fixtures/dcr_visualizer_parity.json` is the precedent. It moves to
  this format when its widget is next edited, not before.
- **Fixture format** (`affinedrift/widget-parity/v1`), a JSON object with:
  - `schema`: `"affinedrift/widget-parity/v1"`;
  - `widget`: the widget id;
  - `source`: the Python reference, as `src/<package>/<module>.py::<function>`;
  - `source_sha256`: the SHA-256 of that module when the file was generated;
  - `generator`: the script and command that produced the file;
  - `tolerance`: `{"abs": <float>, "rel": <float>}`, the default for every
    case;
  - `cases`: a list of `{"id", "inputs", "expected"}` objects, where an entry
    may override `tolerance`. Values are JSON numbers or nested arrays of
    them. Non-finite values are encoded as the strings `"NaN"`, `"Infinity"`
    and `"-Infinity"`.
- **Tolerance policy.** A value passes when
  `|actual − expected| ≤ abs + rel × |expected|`, element by element. The
  generator sets the tolerance, never the test.

  | Computation | `abs` | `rel` |
  | --- | --- | --- |
  | Pyodide running unchanged `src/` code | 1e-12 | 1e-12 |
  | JS port of closed-form expressions | 1e-12 | 1e-12 |
  | JS port of iterative or integrated results (ODE, root finding) | 1e-9 | 1e-9 |

  These match the precision that the DCR widget's Jest tests already use
  (12 and 9 decimal places). A tolerance is never widened to make a test
  pass. Widening needs an issue with measurements, cited in the commit under
  the fleet `Tolerance-Change-Evidence` rule.
- **Checks.**
  - pytest regenerates each fixture in memory and fails if it differs from
    the committed file, or if `source_sha256` no longer matches the source.
    The committed vectors therefore always reflect current `src/`.
  - Jest (`npm test`) loads the fixture and checks every case against the
    pure JS module of each OJS or JS widget.
  - Playwright (`npx playwright test`) loads each Pyodide widget in Chromium,
    runs every case through the real widget path, and compares against the
    fixture. Pyodide cannot run under jsdom, so Playwright is the parity check
    for class D.

### 7. Existing CDN Uses: Follow-Up Migrations Only

This ADR does not migrate them. Each is a separate follow-up that vendors the
same pinned version under `vendor/`, removes the CDN tag, and adds the
no-cross-origin assertion:

- `articles/rotation-converter.qmd`: Three.js 0.147.0 and `OrbitControls`
  from `cdn.jsdelivr.net`;
- `src/tools/wrist_universal_joint/grip_angle_simulator.html`: Plotly 2.26.0
  from `cdn.plot.ly`.

Until those land, both pages are exempt from the no-CDN rule. No new widget
may add to the exemption.

## Consequences

- Faithful widgets run the same Python that the articles cite, so parity with
  `src/` holds by construction rather than by porting. Light widgets stay
  small and fast.
- Two runtimes have to be governed. The rules in §1 and the budget table make
  the choice explicit for each widget.
- Pyodide's cold download is several megabytes. That is acceptable only
  because it is opt-in, disclosed, off the main thread and cached afterwards.
  Readers who never activate a model widget pay nothing.
- Vendoring makes the repository responsible for runtime updates and licence
  records, and it removes third-party availability and privacy exposure from
  the reader's path.
- Every widget adds a generated parity fixture and a Jest or Playwright parity
  check. A change to a cited `src/` function now fails CI until its fixtures
  are regenerated, which is intended.
- The CSP gains `'wasm-unsafe-eval'` when the first Pyodide widget lands, and
  loses `https://cdn.jsdelivr.net` once the migrations in §7 are done.
- Out of scope: building any widget, the CDN migrations, the vendoring
  tooling itself, and decisions D4, D7 and D8.
