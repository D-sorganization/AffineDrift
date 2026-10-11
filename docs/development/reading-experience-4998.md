# Reading Experience Review Implementation

Governing epic: [AffineDrift #4998](https://github.com/D-sorganization/AffineDrift/issues/4998).
Base revision: `05ddd506a` (current `origin/main` when the worktree was created).

## Acceptance and Verification

| Recommendation | Implementation | Verification |
| --- | --- | --- |
| One primary homepage action | Start Here button, shorter introduction, secondary catalog links | Source contract and desktop/mobile navigation tests |
| Honest featured reading | Featured Reading replaces undated Latest Writing; each book appears once | Unique-link and heading checks; historic anchors retained |
| Three initial audience choices | Science, mathematics, and model goals; specialist plans remain one link away | All three destinations and specialist link checked in the browser; persona coverage retained |
| Shared evidence definitions | Both pages include generated definitions from `config/maturity.yml` | Generator boundary, authority-change, and committed-output freshness tests |
| Readable article metadata | Source titles for prerequisite routes; safe Markdown links; publication date shown once; citation-only pages use a simple link | Real Pandoc and Quarto tests, with unsafe-link and date uncertainty cases |
| Measure and reduce page overhead | Navigation pages disable irrelevant Scholar exports; research articles retain them | Document-byte browser gates supplement existing runtime budgets |

## TDD and Design Contracts

- Before production edits, eight entry/content contract tests failed. Five of eight initial metadata integration cases failed, while the three unsafe-target cases already passed.
- A date-presentation test failed before updating the post-render text. A publication-only fixture exposed an invented review date in the refactor; it failed before the conditional was corrected.
- Further regression tests failed before fixing audience-only metadata inventing a status, placing citation-only links after the body, and writing portable LF bytes for the generated include.
- The generator tests initially failed at collection because the generator did not exist. They now exercise all canonical definitions and boundaries, authority changes, incomplete vocabularies, empty boundaries, and stale output.
- Prerequisite rendering separates route resolution, markup handling, and card composition. Only safe link targets become links. The card's HTML boundary escapes labels and validates class slugs.
- The canonical maturity loader supplies definitions; the two reader pages do not keep independent prose copies. Existing enum validation is reused.
- Metadata helpers have focused responsibilities and use direct collaborators. The former monolithic filter is split into card composition, prerequisite rendering, and shared HTML helpers.
- Scientific caveats, open critiques, review status, and verified scholarly citation metadata remain in scope for regression testing. No scientific claim is promoted by these changes.

## Measured HTML Overhead

Before edits, the local homepage render contained **469,180 bytes** of HTML,
including **995** `citation_reference` tags occupying **393,723 bytes** when
serialized by BeautifulSoup. The first updated homepage render was **72,459
bytes**, with no reference tags (approximately **85% less HTML**).

These are uncompressed document sizes, not page-load times or Core Web Vitals.
Research pages retain Google Scholar metadata. Navigation pages still retain
their normal canonical and social metadata.

## Verification Notes

- Quarto is pinned to and locally rendered with 1.8.26.
- Browser tests use the repository's Playwright suite with desktop Chromium
  and Mobile Chrome projects. Node 24.19.0 satisfies the installed packages'
  engine requirements; the host default Node 25 does not.
- Python validation must use `py -3.12`: adding Python 3.12 to PATH does not
  change this host's `python3.exe`, which resolves to Python 3.13.
- Run Quarto renders before browser tests. Concurrent Playwright output cleanup
  caused Quarto's directory scanner to encounter a disappearing artifact path.
- Before Jest/browser validation, run the repository's frontend sync and CSS
  bundler, as CI does. A raw Quarto render alone does not produce the flattened
  stylesheet required by the existing Jest contracts.

The full Python 3.12 run reported 7,714 passes, 30 skips, and 11 failures.
Four failures asserted the superseded navigation/duplication contracts; their
replacements preserve route reachability, monograph caveats, and shared state
definitions. Three shell integration tests pass with Git Bash on PATH. The
JavaScript minifier test passes with Python UTF-8 mode. The explainer tests pass
after restoring canonical LF caption bytes (no tracked content change). The
figure reproducibility test passes with the pinned Matplotlib 3.11.2 installed
in an isolated temporary directory; the host has 3.10.8. The pin scanner includes
generated `_site` partials; the same test passes with the generated directory
temporarily outside the checkout. Deployment pruning does not remove those
partials. No source pin was changed. Full-run coverage was 80.21%, above the
configured 75% floor.

Final focused Python validation passed **113 tests**. Jest passed **41 suites**
(626 tests; 19 skipped). The final desktop Chromium and Mobile Chrome run passed
**34 tests**, covering the new reading experience and existing homepage checks.
The browser checks include navigation, document budgets, axe accessibility,
keyboard focus, overflow, and console errors. Desktop and mobile screenshots
were inspected. Six relevant pages were rendered with Quarto 1.8.26.

The local browser fixture contains nine rendered pages and a manifest generated
for that subset; it is not represented as full-site coverage. CI retains the
strict full-site manifest and render requirements. The Python CI job intentionally
has no Quarto: metadata integration tests follow the existing optional-runtime
skip convention there and run explicitly after pinned Quarto setup in the E2E job.
All ten metadata integration cases passed locally after that CI-placement fix.

Final HTML sizes: homepage 72,459 bytes; Start Here 72,792; How to Read 73,924;
article catalog 157,053. All four contain zero `citation_reference` tags. The
representative research article retains 995 tags in its 682,949-byte document.

The central pre-PR wrapper has an existing Black argument-expansion defect:
it passes individual characters from `--check` as paths. Tracked in
[Repository_Management #2066](https://github.com/D-sorganization/Repository_Management/issues/2066).
Its diff type checks, affected tests (37), Semgrep/import checks, and policy
checks passed. Direct Ruff/Black/type checks and normal Git hooks supply the
equivalent lint/format validation; the wrapper itself is not reported green.

A full local Quarto build was stopped after 46 pages because it was taking
substantially longer than representative renders. Full-site acceptance remains
with the required CI build. A concurrent repeat of the focused suite timed out
in an existing synthetic citation render; the isolated 113-test rerun passed.
