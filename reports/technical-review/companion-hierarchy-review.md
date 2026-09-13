# Companion Hierarchy and Publication Repair

Issues #4375 and #4376, under epic #4009. Scientific source checkpoint:
`beca5d90e409ade8649bb57e4e1ab39dad7200ea`. Current implementation: SELF.

## Cause and Choice

The single-H1 website conversion in c1eab084 normalized chapter titles from
H1 to H2 without moving their existing H2 sections down with them. The web
renderer and direct PDF rebuild consequently treated 117 headings as chapters.
The stored 202-page PDF predated this regression and had the intended hierarchy,
but contained the old Chapter 30 scientific prose.

A wrapper-scoped Pandoc filter preserves chapter titles at H2 and demotes their
subordinate headings one level, stopping at Glossary or References. It preserves
all heading IDs and all non-heading document blocks. None of the thirty chapter
source files is rewritten by this hierarchy repair. In particular, Chapter 29
and the protected scientific monograph remain untouched.

The real-Pandoc tests first failed because the filter did not exist. Both now
pass against the complete expanded companion and a back-matter fixture. Actual
Quarto HTML confirms one H1, thirty H2 chapter sections, Chapter 30's H3 sections
numbered 30.1–30.3, and its H4 questions below those sections. Existing incoming
anchors are retained. HTML equation numbering is document-wide; PDF equation
numbering is per chapter. Both formats resolve the same declared equation IDs.

## PDF Build and Reading

Quarto with LuaLaTeX now builds 205 pages and exactly thirty numbered chapters.
Every chapter start was independently read from the PDF text; Chapter 30 starts
on physical page 188, as in the old PDF. Physical pages 188–200 (the whole revised
chapter), 201–202 (glossary), and 203–205 (references) were each visually read.
The equations, provenance figure and caption, links, and paragraph continuations
are legible. This is a Chapter 30 review and a whole-book hierarchy check; it does
not attest to the scientific correctness of every other chapter.

The checked PDF replaces both the canonical articles/ copy and the tracked
publication copy under docs/articles/, with identical bytes. PDF/source hashes
and browser observations are in `companion-hierarchy-verification.json`.

Rebuild from the repository root using the wrapper and its declared filter:

```text
quarto render articles/proximal-distal-a-journey-through-the-swing.qmd --to pdf --output companion-hierarchy-review.pdf --no-clean
```

On this installation the output is docs/companion-hierarchy-review.pdf. Quarto
can move an existing PDF out of articles/ while collecting project resources.
Before rebuilding, save the canonical PDF bytes; restore them in a finally
block whether the subprocess succeeds or fails. Promote the separately named
output to both canonical/publication paths only after checking the build, all
chapter numbers, and the revised pages. This prevents a failed render from
silently deleting or replacing the published artifact. Do not use the earlier
286-page curiosity-review.pdf.

## Browser Reading and Limitations

The mobile stylesheet scaled both the outer math span and MathJax container,
reducing a 17.78px text size to 12.8461px equations. A Chapter 30 scoped override
preserves inherited text size at both levels. Existing accessible math regions
supply keyboard focus and native horizontal scrolling.

Eight cases (320, 390, 768, 1440px; light/dark) each have 47 typeset expressions,
four displays, no MathJax errors and no page overflow. At 320/390px the wide
point-transport expression responds to ArrowRight while its region retains
focus. Wider layouts fit without scrolling. All 21 desktop reading captures and
all eight mobile figure/equation captures were visually read. The scrollable
mobile screenshots show partial expressions at a deliberate scroll position;
the complete expression is accessible by scrolling.

A stale browser cache initially masked the new stylesheet. The final run disabled
HTTP cache and bypassed the local service worker; its loaded CSS and computed
font sizes were inspected. The initial multiline CLI invocation failed parsing;
`run-code --filename` executed the actual saved script successfully. There is
no service-worker update toast in the final captures. Existing floating site
controls overlap the bottom-right of some narrow captures, and the wide overview
figure's small labels still rely on zoom, its caption and alt text. These are
remaining presentation limits, not a claim of complete site accessibility.
The known legacy-polyfill CSP rejection remains in the unnormalized local page;
production normalization and the actual release route gate remain to be checked.

## Validation and Continuation

The first root run in this checkpoint passed 5335 tests but failed two root
hygiene checks because the browser session wrote 29 PNGs and its logs at the
repository root. Those scratch files were moved under docs/development/technical-review;
all eight hygiene/hierarchy checks then passed. No allowlist was weakened.
Ruff and Black100 pass for the new test. A clean full-root rerun follows in the
canonical development log. Six unrelated generated registries/summaries were
restored after text equivalence or parsed-JSON equivalence excluding generated_on.

The pending main merge integrates the protected null-space squash 7f0fed76.
Only handoff/log/SPEC conflicted; current Chapter 30 records were retained after
comparison with both parents. Null-space deployment 34727537466 subsequently
succeeded at that exact SHA. Live artifact 10309086348 contains 960 unique cases
across 240 routes: every status, pass/failure, overflow and retry record was
individually checked, including all eight article/bibliography cases. All 240
actual route-level axe scans have no serious/critical findings. DL-#4371 can be
marked shipped. Chapter 30 still needs its own release review and regular PR;
the full companion route remains deferred in the scientific corpus inventory.

## Release-Gate Checkpoint

Clean root15451 passes5337 tests,29 skipped,132 deselected,59 warnings in192.94s
with79.29% coverage. The production verifier passes all14 width/theme records
for the wrapper route after the existing production polyfill normalization.
Every record was inspected: HTTP200, no failures, page overflow or retries.
One actual route-level axe scan has no serious/critical findings. Five freshness
dashboard evidence files independently match beca5d90 and their existing hashes;
its metadata review is rebound to that commit with an explicit limit against
provider scientific qualification. Other inventory routes are unchanged.
