# Completist Report: 2026-04-12

## Executive Summary
- **Critical Gaps**: 14
- **Feature Gaps (TODO)**: 22
- **Content Gaps**: 43
- **Technical Debt**: 8

## Critical Incomplete (Blocking)
| File | Line | Type | Content |
|---|---|---|---|
| `resources/resources-researchers.qmd` | 214 | Visible Placeholder | <img src="static/images/placeholder.svg" alt="Carol Putnam" class="website-preview"> |
| `resources/resources-researchers.qmd` | 271 | Visible Placeholder | <img src="static/images/placeholder.svg" alt="Phil Cheetham" class="website-preview"> |
| `resources/resources-researchers.qmd` | 303 | Visible Placeholder | <img src="static/images/placeholder.svg" alt="Masahide Hirashima" class="website-preview"> |
| `resources/resources-researchers.qmd` | 328 | Visible Placeholder | <img src="static/images/placeholder.svg" alt="John McPhee" class="website-preview"> |
| `src/tools/CONVERSION_GUIDE.md` | 76 | Visible Placeholder | - Displays `[Figure: See PDF version]` placeholder |
| `src/tools/CONVERSION_GUIDE.md` | 88 | Visible Placeholder | | Figures/TikZ    | Placeholder text             | Not converted          | |
| `.agent/workflows/lint.md` | 2 | Visible Placeholder | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.agent/workflows/lint.md` | 33 | Visible Placeholder | 1. **Find placeholder statements** (review manually): |
| `.agent/skills/lint/SKILL.md` | 3 | Visible Placeholder | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.agent/skills/lint/SKILL.md` | 30 | Visible Placeholder | 4. **Find and fix placeholder statements**: |
| `.agent/skills/lint/SKILL.md` | 42 | Visible Placeholder | - For placeholder statements, implement the functionality or remove if unnecessary |
| `.claude/skills/lint/SKILL.md` | 3 | Visible Placeholder | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.claude/skills/lint/SKILL.md` | 27 | Visible Placeholder | 4. **Find and fix placeholder statements**: |
| `.claude/skills/lint/SKILL.md` | 39 | Visible Placeholder | - For placeholder statements, implement the functionality or remove if unnecessary |

## Content Gaps (Website Specific)
| File | Line | Content |
|---|---|---|
| `styles.css` | 2624 | Placeholder Content Styling (Issue #869) |
| `css/search-metrics.css` | 432 | Lazy Loading Placeholder |
| `scripts/analyze_completist_data.py` | 194 | return {"file": f_path, "line": l_no, "text": c_txt, "type": "Placeholder"} |
| `scripts/analyze_completist_data.py` | 210 | if itype == "Placeholder" and any( |
| `scripts/analyze_completist_data.py` | 225 | "Placeholder": 4, |
| `scripts/analyze_completist_data.py` | 335 | placeholders: Placeholder content findings. |
| `scripts/generate_completist_data.py` | 256 | re.compile(r"return\s+None\s*#.*stub|placeholder", re.IGNORECASE), |
| `scripts/check_bibliography_quality.py` | 6 | - No 'et al.' placeholder author entries |
| `resources/resources-videos.qmd` | 202 | <div class="youtube-embed youtube-placeholder"> |
| `resources/resources-videos.qmd` | 203 | <div class="youtube-placeholder-content"> |
| `resources/resources-videos.qmd` | 204 | <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" strok |
| `resources/resources-videos.qmd` | 208 | <p class="youtube-placeholder-title">A. Sala Control Channel</p> |
| `resources/resources-videos.qmd` | 344 | <div class="youtube-embed youtube-placeholder"> |
| `resources/resources-videos.qmd` | 345 | <div class="youtube-placeholder-content"> |
| `resources/resources-videos.qmd` | 346 | <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" strok |
| `resources/resources-videos.qmd` | 350 | <p class="youtube-placeholder-title">Biomechanics of Movement</p> |
| `resources/resources-researchers.qmd` | 40 | <img src="https://www.stfx.ca/sites/default/files/styles/person/public/images/Human-Kinetics-Sasho%2 |
| `resources/resources-researchers.qmd` | 72 | <img src="https://webspace.yale.edu/Yale-golf-history/images/grober-2.jpg" alt="Robert Grober" class |
| `resources/resources-researchers.qmd` | 125 | <img src="https://www.drkwongolf.info/images/drkwon.jpg" alt="Dr. Young-Hoo Kwon" class="website-pre |
| `resources/resources-researchers.qmd` | 157 | <img src="http://wedgecraft.com/wp-content/uploads/2018/12/robjneal.png" alt="Rob Neal" class="websi |
| `resources/resources-researchers.qmd` | 189 | <img src="https://me-future.lafayette.edu/wp-content/uploads/sites/511/2016/03/steve-160x160.png" al |
| `resources/resources-researchers.qmd` | 239 | <img src="https://engineering.stanford.edu/sites/default/files/styles/large_square/public/media/imag |
| `tests/test_matlab_quality_check_refactor.py` | 20 | "% <PLACEHOLDER>", |
| `tests/test_matlab_quality_check_refactor.py` | 42 | assert any("Angle bracket placeholder found" in issue for issue in issues) |
| `tests/test_assess_repo.py` | 73 | return None  # noqa: placeholder for test fixture |
| `.hypothesis/constants/a6f6d219d65e194c` | 4 | ['#', '(?<![0-9])3\\.141', ':', 'Empty pass statement', 'GRAVITY_M_S2\\s*=\\s*', 'NotImplementedErro |
| `src/affine_control/ddp.py` | 79 | This skeleton serves as a placeholder for the algorithm structure. |
| `src/tools/publish_manual_article.py` | 124 | <!-- Manual TOC placeholder --> |
| `src/tools/code_quality/pattern_checker.py` | 18 | (re.compile(r"\bTODO\b"), "TRACKED_TASK placeholder found"), |
| `src/tools/code_quality/pattern_checker.py` | 19 | (re.compile(r"\bFIXME\b"), "TRACKED_DEFECT placeholder found"), |
| `src/tools/code_quality/pattern_checker.py` | 21 | (re.compile(r"NotImplementedError"), "NotImplementedError placeholder"), |
| `src/tools/code_quality/pattern_checker.py` | 23 | (re.compile(r"your.*here", re.IGNORECASE), "Template placeholder"), |
| `src/tools/code_quality/pattern_checker.py` | 24 | (re.compile(r"insert.*here", re.IGNORECASE), "Template placeholder"), |
| `src/tools/matlab_utilities/scripts/line_checks.py` | 9 | - append_banned_pattern_issues: Banned placeholder comment detection |
| `src/tools/matlab_utilities/scripts/line_checks.py` | 102 | (r"\bTODO\b", "Backlog marker placeholder found"), |
| `src/tools/matlab_utilities/scripts/line_checks.py` | 105 | (r"\bXXX\b", "Placeholder marker found"), |
| `src/tools/matlab_utilities/scripts/line_checks.py` | 106 | (r"<[A-Z_][A-Z0-9_]*>", "Angle bracket placeholder found"), |
| `src/tools/matlab_utilities/scripts/line_checks.py` | 107 | (r"\{\{.*?\}\}", "Template placeholder found"), |
| `content/wrist-as-universal-joint/Archive/Wrist_Universal_Gemini.tex` | 26 | % Placeholder for the image provided in the prompt |
| `tests/e2e/bibliography.spec.js` | 38 | const searchInput = page.locator('#bib-search, input[type="search"], input[placeholder*="search" i]' |
| `tests/e2e/search.spec.js` | 12 | 'input[type="search"], input[placeholder*="search" i]', |
| `articles/The_Geometry_of_Motion/Volume_V/chapters/ch10_golf_swing_project.tex` | 121 | drift[k] = 0.6 * self.clubhead_speed[k]  # Placeholder ratio |
| `articles/The_Geometry_of_Motion/Volume_V/chapters/ch10_golf_swing_project.tex` | 173 | analysis.joint_torques = np.random.randn(N, 3) * 10  # placeholder |

## Feature Gap Matrix
| Module | Type | Content |
|---|---|---|
| `AGENTS.md` | TODO | - ❌ **DO NOT** leave `TRACKED_TASK`/`TRACKED_DEFECT` markers for more than one sprint. |
| `AGENTS.md` | TODO | - **Read:** Codebase for TRACKED_TASK, TRACKED_DEFECT, NotImplementedError, pass statements |
| `service-worker.js` | TODO | // TRACKED_TASK #1459: Replace hardcoded version with content-hash cache busting via build pipeline |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with `part-number` label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with `part-number` label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with `supplement-number` label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove when Zotero fixes mapping of performer to `author` --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove conditional when Zotero stops double-mapping `event-place` and `publisher- |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: use `container-genre` here once available to allow a custom description of the jo |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: If CSL adds `date-part` detection, add two further conditions to address CMOS18 1 |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: when CSL provides date part detection, volume should be lowercase if there is a m |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: use CSL term for `available-date` when available --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: To prevent Zotero from printing `event-place`, due to its double-mapping of `publ |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: We expect `event-title` to be used, but processors and applications may not be up |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: We expect `event-title` to be used, but processors and applications may not be up |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: `DOI` or `URL` detection is the only way to distinguish radio/TV from podcasts, b |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove conditional when Zotero fixes double-mapping of `event-place` --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Is there a better CSL variable for a date of a multivolume work (CMOS18 14.21)? - |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove this conditional when `page` parsing is fixed for different locator types  |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: add variables for distributor and exhibitions if available in CSL --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Add `proposed` date here if that becomes available --> |
| `src/tools/code_quality/pattern_checker.py` | TODO | (re.compile(r"\bTODO\b"), "TRACKED_TASK placeholder found"), |

## Technical Debt Register
| File | Line | Type | Issue |
|---|---|---|---|
| `AGENTS.md` | 213 | Tech Debt | - ❌ **DO NOT** leave `TRACKED_TASK`/`TRACKED_DEFECT` markers for more than one sprint. |
| `AGENTS.md` | 428 | Tech Debt | - **Read:** Codebase for TRACKED_TASK, TRACKED_DEFECT, NotImplementedError, pass statements |
| `tests/notes-workspace.test.js` | 37 | Tech Debt | store.saveActive("Temp note"); |
| `src/tools/code_quality/pattern_checker.py` | 19 | Tech Debt | (re.compile(r"\bFIXME\b"), "TRACKED_DEFECT placeholder found"), |
| `tests/unit/test_check_bibliography_quality.py` | 48 | Tech Debt | """Write a bibliography JSON file to a temp dir and return its path.""" |
| `articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd` | 128 | Tech Debt | Together, these ideas form the foundation of modern nonlinear control: linearize, solve optimally on |
| `articles/Tangent Hyperplane Articles/LAYMANS_TERMS_SUMMARY.md` | 132 | Tech Debt | **Takeaway:** Linearization isn't a hack—it's the exact local structure of smooth systems. |
| `articles/Tangent Hyperplane Articles/LAYMANS_TERMS_SUMMARY.qmd` | 132 | Tech Debt | **Takeaway:** Linearization isn't a hack—it's the exact local structure of smooth systems. |
