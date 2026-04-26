# Completist Assessment Report - 2026-04-26

## Executive Summary
This report summarizes incomplete implementations, placeholders, and missing content across the codebase.

## Critical Incomplete (Blocking)
- `Visible placeholder: resources/resources-videos.qmd:202:<div class="youtube-embed youtube-placeholder">`
- `Visible placeholder: resources/resources-videos.qmd:203:<div class="youtube-placeholder-content">`
- `Visible placeholder: resources/resources-videos.qmd:204:<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="youtube-placeholder-icon">`
- `Visible placeholder: resources/resources-videos.qmd:208:<p class="youtube-placeholder-title">A. Sala Control Channel</p>`
- `Visible placeholder: resources/resources-videos.qmd:344:<div class="youtube-embed youtube-placeholder">`
- `Visible placeholder: resources/resources-videos.qmd:345:<div class="youtube-placeholder-content">`
- `Visible placeholder: resources/resources-videos.qmd:346:<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="youtube-placeholder-icon">`
- `Visible placeholder: resources/resources-videos.qmd:350:<p class="youtube-placeholder-title">Biomechanics of Movement</p>`
- `Visible placeholder: resources/resources-researchers.qmd:40:<img src="https://www.stfx.ca/sites/default/files/styles/person/public/images/Human-Kinetics-Sasho%20MacKenzie.png?h=c1788fc8&itok=ka_v5jaE" alt="Sasho MacKenzie" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:72:<img src="https://webspace.yale.edu/Yale-golf-history/images/grober-2.jpg" alt="Robert Grober" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:125:<img src="https://www.drkwongolf.info/images/drkwon.jpg" alt="Dr. Young-Hoo Kwon" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:157:<img src="http://wedgecraft.com/wp-content/uploads/2018/12/robjneal.png" alt="Rob Neal" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:189:<img src="https://me-future.lafayette.edu/wp-content/uploads/sites/511/2016/03/steve-160x160.png" alt="Steven Nesbit" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:214:<img src="static/images/placeholder.svg" alt="Carol Putnam" class="website-preview">`
- `Visible placeholder: resources/resources-researchers.qmd:239:<img src="https://engineering.stanford.edu/sites/default/files/styles/large_square/public/media/image/stanford-person-default-profile-image.png?h=55541bb6&itok=iT3JNdt_" alt="Felix Zajac" class="website-preview" onerror="this.src='static/images/placeholder.svg'">`
- `Visible placeholder: resources/resources-researchers.qmd:271:<img src="static/images/placeholder.svg" alt="Phil Cheetham" class="website-preview">`
- `Visible placeholder: resources/resources-researchers.qmd:303:<img src="static/images/placeholder.svg" alt="Masahide Hirashima" class="website-preview">`
- `Visible placeholder: resources/resources-researchers.qmd:328:<img src="static/images/placeholder.svg" alt="John McPhee" class="website-preview">`
- `Visible placeholder: articles/inverse-dynamics-bibliography.md:104:# Note: Placeholder for a review if specific one exists, otherwise rely on Tutelman`
- `Visible placeholder: articles/rotation-converter.qmd:732:// Screw axis placeholder`
- `Visible placeholder: articles/rotation-converter.qmd:736:// Arc placeholder`
- `Visible placeholder: content/wrist-as-universal-joint/Archive/Wrist_Universal_Gemini.tex:26:% Placeholder for the image provided in the prompt`
- `Visible placeholder: articles/The_Geometry_of_Motion/Volume_V/chapters/ch10_golf_swing_project.tex:121:drift[k] = 0.6 * self.clubhead_speed[k]  # Placeholder ratio`
- `Visible placeholder: articles/The_Geometry_of_Motion/Volume_V/chapters/ch10_golf_swing_project.tex:173:analysis.joint_torques = np.random.randn(N, 3) * 10  # placeholder`
- `Visible placeholder: articles/The_Geometry_of_Motion/Volume_V/chapters/ch04_simulation.tex:71:# Placeholder for general n-DOF`

## Content Gaps
- `Incomplete Doc: scripts/analyze_completist_data.py:277 generate_mermaid_charts`
- `Incomplete Doc: scripts/analyze_completist_data.py:394 priority_score`
- `Incomplete Doc: scripts/generate_assessment_summary.py:279 generate_summary`
- `Incomplete Doc: scripts/create_issues_from_assessment.py:50 create_github_issue`
- `Incomplete Doc: scripts/create_issues_from_assessment.py:75 prepare_issue_data`
- `Incomplete Doc: scripts/create_issues_from_assessment.py:109 process_assessment_findings`
- `Incomplete Doc: scripts/check_coverage_gates.py:53 __post_init__`
- `Incomplete Doc: scripts/scan_quarto_syntax.py:26 setup_logging_with_timestamp`
- `Incomplete Doc: scripts/scan_quarto_syntax.py:33 find_markdown_files`
- `Incomplete Doc: scripts/scan_quarto_syntax.py:76 __init__`
- `Incomplete Doc: scripts/check_bibliography_quality.py:90 check_no_et_al_authors`
- `Incomplete Doc: scripts/check_bibliography_quality.py:144 check_papers_have_doi_or_url`
- `Incomplete Doc: scripts/mypy_autofix_agent.py:595 run_agent`
- `Incomplete Doc: scripts/sync_frontend_assets.py:86 sha256`
- `Incomplete Doc: scripts/sync_frontend_assets.py:90 sync_one`
- `Incomplete Doc: scripts/sync_frontend_assets.py:121 main`
- `Incomplete Doc: scripts/baseline_assessments.py:42 generate_assessment_report`
- `Incomplete Doc: tests/test_file_and_content_utils.py:32 test_empty_dirs_returns_empty`
- `Incomplete Doc: tests/test_file_and_content_utils.py:36 test_collects_qmd_files`
- `Incomplete Doc: tests/test_file_and_content_utils.py:43 test_excludes_underscore_prefixed`
- `Incomplete Doc: tests/test_file_and_content_utils.py:51 test_returns_sorted`
- `Incomplete Doc: tests/test_file_and_content_utils.py:57 test_uses_default_dirs_when_none`
- `Incomplete Doc: tests/test_file_and_content_utils.py:65 test_multiple_dirs`
- `Incomplete Doc: tests/test_file_and_content_utils.py:78 test_reads_valid_frontmatter`
- `Incomplete Doc: tests/test_file_and_content_utils.py:94 test_handles_missing_frontmatter`
- `Incomplete Doc: tests/test_file_and_content_utils.py:101 test_handles_malformed_frontmatter`
- `Incomplete Doc: tests/test_file_and_content_utils.py:107 test_requires_existing_file`
- `Incomplete Doc: tests/test_file_and_content_utils.py:111 test_requires_non_none_path`
- `Incomplete Doc: tests/test_file_and_content_utils.py:122 test_finds_qmd_in_root`
- `Incomplete Doc: tests/test_file_and_content_utils.py:128 test_excludes_site_dir`
- `Incomplete Doc: tests/test_file_and_content_utils.py:138 test_include_root_false`
- `Incomplete Doc: tests/test_file_and_content_utils.py:149 test_empty_dir_returns_empty`
- `Incomplete Doc: tests/test_file_and_content_utils.py:155 test_finds_md_files`
- `Incomplete Doc: tests/test_file_and_content_utils.py:162 test_exclude_readme`
- `Incomplete Doc: tests/test_file_and_content_utils.py:171 test_include_qmd`
- `Incomplete Doc: tests/test_file_and_content_utils.py:178 test_empty_result_when_no_dirs`
- `Incomplete Doc: tests/test_file_and_content_utils.py:184 test_finds_by_extension`
- `Incomplete Doc: tests/test_file_and_content_utils.py:191 test_multiple_extensions`
- `Incomplete Doc: tests/test_file_and_content_utils.py:199 test_returns_empty_on_no_match`
- `Incomplete Doc: tests/test_file_and_content_utils.py:203 test_with_explicit_paths`
- `Incomplete Doc: tests/test_file_and_content_utils.py:209 test_recursive_search`
- `Incomplete Doc: tests/test_file_and_content_utils.py:216 test_requires_non_empty_extensions`
- `Incomplete Doc: tests/test_properties.py:322 square`
- `Incomplete Doc: tests/test_properties.py:333 square`
- `Incomplete Doc: tests/test_properties.py:344 square`
- `Incomplete Doc: tests/test_properties.py:362 __init__`
- `Incomplete Doc: tests/test_properties.py:376 __init__`
- `Incomplete Doc: tests/test_properties.py:391 __init__`
- `Incomplete Doc: tests/test_properties.py:398 double`
- `Incomplete Doc: tests/test_logging_utils.py:6 test_imports`
- ... and 472 more.

## Feature Gap Matrix
| File | Type | Description |
|---|---|---|
| `AGENTS.md` | TODO | - ❌ **DO NOT** leave TRACKED_TASK/TRACKED_DEFECT markers for more than one sprint. |
| `AGENTS.md` | TODO | - **Read:** Codebase for TRACKED_TASK, TRACKED_DEFECT, NotImplementedError, pass statements |
| `service-worker.js` | TODO | // TRACKED_TASK #1459: Replace hardcoded version with content-hash cache busting via build pipeline |
| `config/tech_debt_budget.json` | TODO | "TRACKED_TASK": 20, |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with part-number label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with part-number label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Replace with supplement-number label when CSL provides one --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove when Zotero fixes mapping of performer to author --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove conditional when Zotero stops double-mapping event-place and publisher-place --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: use container-genre here once available to allow a custom description of the journal volume --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: If CSL adds date-part detection, add two further conditions to address CMOS18 14.74: delimiting with ":" if there is a volume and no month or issue or supplement number; delimiting with ", " or there is an issue or supplement number and no month --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: when CSL provides date part detection, volume should be lowercase if there is a month, but otherwise capitalized --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: use CSL term for available-date when available --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: To prevent Zotero from printing event-place, due to its double-mapping of publisher-place and event-place. Remove this when that is changed. --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: We expect event-title to be used, but processors and applications may not be updated yet. This macro ensures that either event or event-title can be accepted. Remove if processor logic and application adoption can handle this. --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: We expect event-title to be used, but processors and applications may not be updated yet. This macro ensures that either event or event-title can be accepted. Remove if processor logic and application adoption can handle this. --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: DOI or URL detection is the only way to distinguish radio/TV from podcasts, but it is obviously imprecise; modify if CSL provides a podcast type --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove conditional when Zotero fixes double-mapping of event-place --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Is there a better CSL variable for a date of a multivolume work (CMOS18 14.21)? --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: remove this conditional when page parsing is fixed for different locator types --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: add variables for distributor and exhibitions if available in CSL --> |
| `references/chicago-author-date.csl` | TODO | <!-- TRACKED_TASK: Add proposed date here if that becomes available --> |
| `scripts/analyze_completist_data.py` | TODO | todos: TRACKED_TASK marker findings. |
| `scripts/generate_completist_data.py` | TODO | """Scan files for completion markers (TRACKED_TASK, TRACKED_DEFECT, etc).""" |
| `scripts/check_tech_debt_budget.py` | TODO | MARKERS = ("TRACKED_TASK", "TRACKED_DEFECT", "HACK", "XXX") |
| `scripts/check_tech_debt_budget.py` | TODO | MARKER_RE = re.compile(r"\b(TRACKED_TASK|TRACKED_DEFECT|HACK|XXX)\b", re.IGNORECASE) |
| `src/tools/code_quality/pattern_checker.py` | TODO | (re.compile(r"\bTODO\b"), "TRACKED_TASK placeholder found"), |
| `.agent/workflows/lint.md` | TODO | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.agent/workflows/lint.md` | TODO | grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" . |
| `.agent/skills/lint/SKILL.md` | TODO | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.agent/skills/lint/SKILL.md` | TODO | - Search for TRACKED_TASK, TRACKED_DEFECT, XXX, HACK comments |
| `.agent/skills/lint/SKILL.md` | TODO | grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" . |
| `.claude/skills/lint/SKILL.md` | TODO | description: Run linting tools (ruff, black, mypy) and fix placeholder/TRACKED_TASK statements |
| `.claude/skills/lint/SKILL.md` | TODO | - Search for TRACKED_TASK, TRACKED_DEFECT, XXX, HACK comments |
| `.claude/skills/lint/SKILL.md` | TODO | grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" . |
| `scripts/analyze_completist_data.py` | Mock/Stub | analyze_placeholders |
| `scripts/generate_completist_data.py` | Mock/Stub | scan_for_placeholders |
| `scripts/generate_completist_data.py` | Mock/Stub | scan_for_stub_functions |
| `tests/test_assess_repo.py` | Mock/Stub | test_assess_error_handling_mock |
| `src/core/protocols.py` | Empty Func | dynamics |
| `src/core/protocols.py` | Empty Func | linearize |
| `src/core/protocols.py` | Empty Func | __call__ |
| `src/core/protocols.py` | Empty Func | __call__ |
| `src/core/protocols.py` | Empty Func | __call__ |
| `src/core/protocols.py` | Empty Func | __call__ |
| `src/core/protocols.py` | Empty Func | __call__ |
| `src/affine_control/ddp.py` | Mock/Stub | adaptive_timestep_ddp_mock |
| `src/tools/fix_html_validation.py` | Empty Func | main |
| `src/tools/publish_manual_article.py` | Empty Func | wrap_in_article_section |
| `src/tools/wrap_sidebars.py` | Empty Func | wrap_file |
| ... | | and 8 more. |

## Technical Debt Register
- `Tech Debt Marker: config/tech_debt_budget.json:26:"HACK": 8,`
- `Tech Debt Marker: config/tech_debt_budget.json:27:"XXX": 10`
- `Tech Debt Marker: scripts/analyze_completist_data.py:101:fixme_markers = ["FIX" + "ME", "XXX", "HACK", "TEMP"]`
- `Tech Debt Marker: scripts/generate_completist_data.py:202:markers = ["TOD" + "O", "FIX" + "ME", "XXX", "HACK", "TEMP"]`
- `Tech Debt Marker: scripts/check_tech_debt_budget.py:17:MARKERS = ("TRACKED_TASK", "TRACKED_DEFECT", "HACK", "XXX")`
- `Tech Debt Marker: scripts/check_tech_debt_budget.py:18:MARKER_RE = re.compile(r"\b(TRACKED_TASK|TRACKED_DEFECT|HACK|XXX)\b", re.IGNORECASE)`
- `Tech Debt Marker: .hypothesis/constants/c893c2aeb23dac40:4:[b'\x00', 1024, '  %s: %d', '"""', '%s', "'''", ')\\b', '*', '--output-dir', '--repo-root', '--verbose', '-v', '.css', '.eot', '.gif', '.git', '.github', '.gz', '.html', '.ico', '.jpeg', '.jpg', '.js', '.json', '.jules', '.m', '.md', '.mp4', '.mypy_cache', '.pdf', '.png', '.py', '.pytest_cache', '.qmd', '.quarto', '.ruff_cache', '.scss', '.svg', '.tar', '.ts', '.ttf', '.txt', '.vscode', '.webm', '.webp', '.woff', '.woff2', '.yaml', '.yml', '.zip', '@abstractmethod', 'FIX', 'HACK', 'Implemented', 'ImplementedError', 'ME', 'Not', 'O', 'Output directory: %s', 'TEMP', 'TOD', 'XXX', '\\b(', '\\bcoming\\s+soon\\b', '\\blorem\\s+ipsum\\b', '\\bplaceholder\\b', '^\\s*\\.\\.\\.\\s*$', '^\\s*def\\s+(\\w+)\\s*\\(', '^\\s*pass\\s*$', '_', '__', '__main__', '__pycache__', '_site', 'abstract_methods.txt', 'archive', 'build', 'dist', 'docs', 'incomplete_docs.txt', 'legacy', 'node_modules', 'not_implemented.txt', 'placehold\\.co', 'rb', 'replace', 'store_true', 'stub_functions.txt', 'todo_markers.txt', 'utf-8', 'w', '|', '|raise\\s+Not']`
- `Tech Debt Marker: src/tools/code_quality/pattern_checker.py:19:(re.compile(r"\bFIXME\b"), "TRACKED_DEFECT placeholder found"),`
- `Tech Debt Marker: .agent/workflows/issues-5-combined.md:44:Closes #XXX, closes #XXX, closes #XXX, closes #XXX, closes #XXX`
- `Tech Debt Marker: .agent/workflows/lint.md:36:grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" .`
- `Tech Debt Marker: .agent/skills/update-issues/SKILL.md:132:| #XXX | Title | High | assessment.md |`
- `Tech Debt Marker: .agent/skills/update-issues/SKILL.md:137:| #XXX | Title | Fixed in commit abc123 |`
- `Tech Debt Marker: .agent/skills/update-issues/SKILL.md:142:| Description | #XXX |`
- `Tech Debt Marker: .agent/skills/issues-10-sequential/SKILL.md:96:| 1 | #XXX - Title | #YYY | Merged |`
- `Tech Debt Marker: .agent/skills/issues-10-sequential/SKILL.md:97:| 2 | #XXX - Title | #YYY | Merged |`
- `Tech Debt Marker: .agent/skills/lint/SKILL.md:32:- Search for TRACKED_TASK, TRACKED_DEFECT, XXX, HACK comments`
- `Tech Debt Marker: .agent/skills/lint/SKILL.md:37:grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" .`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:63:- #XXX: <brief description>`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:64:- #XXX: <brief description>`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:65:- #XXX: <brief description>`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:66:- #XXX: <brief description>`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:67:- #XXX: <brief description>`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:69:Closes #XXX, closes #XXX, closes #XXX, closes #XXX, closes #XXX`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:84:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:85:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:86:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:87:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:88:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:95:Closes #XXX, closes #XXX, closes #XXX, closes #XXX, closes #XXX"`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:140:| #XXX | Title | Fixed |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:141:| #XXX | Title | Fixed |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:142:| #XXX | Title | Fixed |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:143:| #XXX | Title | Fixed |`
- `Tech Debt Marker: .agent/skills/issues-5-combined/SKILL.md:144:| #XXX | Title | Fixed |`
- `Tech Debt Marker: .claude/skills/update-issues/SKILL.md:132:| #XXX | Title | High | assessment.md |`
- `Tech Debt Marker: .claude/skills/update-issues/SKILL.md:137:| #XXX | Title | Fixed in commit abc123 |`
- `Tech Debt Marker: .claude/skills/update-issues/SKILL.md:142:| Description | #XXX |`
- `Tech Debt Marker: .claude/skills/issues-10-sequential/SKILL.md:96:| 1 | #XXX - Title | #YYY | Merged |`
- `Tech Debt Marker: .claude/skills/issues-10-sequential/SKILL.md:97:| 2 | #XXX - Title | #YYY | Merged |`
- `Tech Debt Marker: .claude/skills/lint/SKILL.md:29:- Search for TRACKED_TASK, TRACKED_DEFECT, XXX, HACK comments`
- `Tech Debt Marker: .claude/skills/lint/SKILL.md:34:grep -rn "TRACKED_TASK\|TRACKED_DEFECT\|XXX\|HACK\|NotImplementedError\|pass$" --include="*.py" .`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:63:- #XXX: <brief description>`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:64:- #XXX: <brief description>`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:65:- #XXX: <brief description>`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:66:- #XXX: <brief description>`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:67:- #XXX: <brief description>`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:69:Closes #XXX, closes #XXX, closes #XXX, closes #XXX, closes #XXX`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:84:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:85:| #XXX | Title | Brief fix description |`
- `Tech Debt Marker: .claude/skills/issues-5-combined/SKILL.md:86:| #XXX | Title | Brief fix description |`
- ... and 8 more.
