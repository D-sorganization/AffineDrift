# Local Validation and Publication Handoff

## Delivered Manuscript

26 numbered chapters plus an introduction, approximately 49,500 whitespace-delimited source words, and a 135-page Pandoc/XeLaTeX PDF. Sources are registered in the main website navigation, bibliography, and a standalone Quarto book configuration. Four Luna agents drafted assigned chapters; the primary agent reviewed and corrected the scientific reasoning and integrated the manuscript. No new executable production code is included.

## Local Acceptance

Eight source validation commands passed: citation-key resolution, bibliography cross-file consistency, title case, single H1, Quarto syntax scan, terminology, LaTeX quotation marks, and LaTeX environments. Title case, citation keys, and syntax were rerun after the final scientific changes. All 27 immutable UpstreamDrift file/directory targets extracted from the manuscript exist in the local audited snapshot. The ledger contains 53 unique URL targets; local existence is not HTTP or claim verification.

Pandoc/XeLaTeX rendered successfully, with one missing mathematical-tau character warning in a bold font. A sample interior page was inspected; exhaustive PDF inspection, accessibility, site route checks, and Quarto rendering remain pending. A source AST scan found no raw LaTeX blocks outside recognized mathematics after display-math cleanup. The PDF was built before adding its download link to the introduction; this editorial download link is the only introduction difference.

## Pending or Excluded Gates

Quarto and pytest are unavailable, so site builds and the full repository regression did not run. The global style-discipline validator found 385 existing violations in repository styling; this change adds no CSS. The legacy cross-file xref tool checks other configured books, so its pass is not evidence about this book. Live external links and primary-source metadata still require validation. The network-dependent metadata checker was inadvertently started and terminated; its exit is excluded from acceptance.

GitHub CLI returned a quota error and invalid authentication. Remote publication requires restored own-agent authentication, the current repository workflow, a linked issue/change fragment, protected review and deployment acceptance. No push, PR, merge, or deployment was performed.

## Rebuilding the Preview

The JSON command beside this record captures the successful Pandoc invocation. Its input was assembled in chapter order from index.qmd and numbered qmd sources, removing index YAML and assigning preview-only chapter anchors. In-book .html links were rewritten to those anchors. This assembly is a local preview step, not a replacement for Quarto. The canonical reproducible publication command is `quarto render articles/forward_dynamics_matching --to pdf` after installing the repository's required toolchain; render the root website separately.
