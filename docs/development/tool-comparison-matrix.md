# Tool Comparison Matrix

Quick reference guide for all tools and scripts in the AffineDrift project.

## Build & Deployment Tools

| Tool | Purpose | Input | Output | Dependencies | Use Case |
|------|---------|-------|--------|--------------|----------|
| `build-html.py` | Build HTML from Quarto | `.qmd` files | `docs/` directory | Quarto, Python | Full site build |
| `generate_sitemap.py` | Generate sitemap | `docs/` directory | `sitemap.xml` | Python, lxml | SEO optimization |
| `generate_search_index.py` | Create search index | HTML files | `docs/search.json` | Python, BeautifulSoup | Site search |
| `generate_bibliography_data.py` | Process bibliography | `data/bibliography.yaml` | `data/bibliography.json` | Python, PyYAML | Bibliography management |

## Content Processing Tools

| Tool | Purpose | Input | Output | Dependencies | Use Case |
|------|---------|-------|--------|--------------|----------|
| `add_meta_descriptions.py` | Add SEO meta tags | HTML files | Updated HTML | Python, BeautifulSoup | SEO enhancement |
| `scan_quarto_syntax.py` | Validate Quarto syntax | `.qmd` files | Syntax report | Python | Pre-build validation |
| `check-equations.py` | Validate LaTeX equations | `.qmd`, `.md` files | Error report | Python, regex | Math validation |
| `latex_to_qmd.py` | Convert LaTeX to Quarto | `.tex` files | `.qmd` files | Python | Content migration |

## Quality Assurance Tools

| Tool | Purpose | Input | Output | Dependencies | Use Case |
|------|---------|-------|--------|--------------|----------|
| `seo_audit.py` | SEO analysis | Generated site | Audit report | Python, requests | SEO optimization |
| `assess_repo.py` | Repository analysis | Codebase | Assessment report | Python | Quality review |
| `baseline_assessments.py` | Create quality baseline | Codebase | Baseline metrics | Python | Progress tracking |
| `generate_assessment_summary.py` | Summarize assessments | Assessment files | Summary report | Python | Executive summary |
| `create_issues_from_assessment.py` | Auto-create GitHub issues | Assessment report | GitHub issues | Python, GitHub CLI | Issue management |

## MATLAB Tools

| Tool | Purpose | Input | Output | Dependencies | Use Case |
|------|---------|-------|--------|--------------|----------|
| `matlab_code_analyzer_gui` | GUI code analyzer | `.m` files | Analysis report | MATLAB R2019b+ | Interactive analysis |
| `matlab_utilities/quality` | Code quality checker | `.m` files | Quality metrics | MATLAB | Automated checks |
| `matlab_utilities/testing` | Test runner | Test files | Test results | MATLAB | Automated testing |
| `matlab_utilities/scripts` | Helper scripts | Various | Various | MATLAB | Batch operations |

## Python Utilities

| Tool | Purpose | Input | Output | Dependencies | Use Case |
|------|---------|-------|--------|--------------|----------|
| `update_navigation.py` | Update nav menu | `_quarto.yml` | Updated config | Python, PyYAML | Navigation management |
| `wrist_simulator.py` | Biomechanics simulation | Parameters | Simulation data | Python, NumPy | Research analysis |

## Tool Selection Guide

### For New Contributors

**"I want to add a new article"**
1. Create `.qmd` file in `articles/`
2. Run `check-equations.py` to validate math
3. Run `scan_quarto_syntax.py` to check syntax
4. Build with `quarto render`
5. Run `generate_search_index.py` to update search

**"I want to improve SEO"**
1. Run `seo_audit.py` to identify issues
2. Use `add_meta_descriptions.py` to add meta tags
3. Run `generate_sitemap.py` to update sitemap
4. Verify with `seo_audit.py` again

**"I want to check code quality"**
1. Run `assess_repo.py` for full analysis
2. Use `baseline_assessments.py` to track progress
3. Run `generate_assessment_summary.py` for overview
4. Use `create_issues_from_assessment.py` to create tasks

### For Maintainers

**"I need to migrate LaTeX content"**
1. Use `latex_to_qmd.py` to convert files
2. Run `check-equations.py` to validate equations
3. Run `scan_quarto_syntax.py` to check syntax
4. Manual review and adjustments

**"I need to analyze MATLAB code"**
1. Use `matlab_code_analyzer_gui` for interactive analysis
2. Use `matlab_utilities/quality` for batch checks
3. Use `matlab_utilities/testing` to run tests
4. Review reports and fix issues

**"I need to update site navigation"**
1. Edit `_quarto.yml` manually or
2. Use `update_navigation.py` for automated updates
3. Build site to verify changes

## Tool Dependencies

### Python Tools
```bash
pip install -r requirements.txt
```

**Key packages:**
- `beautifulsoup4` - HTML parsing
- `pyyaml` - YAML processing
- `lxml` - XML processing
- `requests` - HTTP requests

### MATLAB Tools
- MATLAB R2019b or later
- No additional toolboxes required (optional: Statistics, Optimization)

### System Tools
- **Quarto** - Static site generator
- **GitHub CLI** (`gh`) - For issue creation
- **Git** - Version control

## Performance Characteristics

| Tool | Speed | Memory | Disk I/O | Notes |
|------|-------|--------|----------|-------|
| `build-html.py` | Medium | Medium | High | Full site build |
| `generate_sitemap.py` | Fast | Low | Low | Quick generation |
| `generate_search_index.py` | Medium | Medium | Medium | Parses all HTML |
| `seo_audit.py` | Slow | Medium | Low | Network requests |
| `assess_repo.py` | Slow | High | High | Full codebase scan |
| `matlab_code_analyzer_gui` | Medium | Medium | Low | Interactive GUI |
| `check-equations.py` | Fast | Low | Low | Regex-based |

## Common Workflows

### Daily Development
```bash
# 1. Make changes to .qmd files
# 2. Validate
python scripts/check-equations.py
python scripts/scan_quarto_syntax.py

# 3. Build
quarto render

# 4. Update search
python scripts/generate_search_index.py
```

### Pre-Commit
```bash
# Quality checks
ruff check .
ruff format .
mypy .
pytest

# Content validation
python scripts/check-equations.py
python scripts/scan_quarto_syntax.py
```

### Pre-Release
```bash
# Full quality audit
python scripts/assess_repo.py
python scripts/seo_audit.py

# Generate artifacts
python scripts/generate_sitemap.py
python scripts/generate_search_index.py
python scripts/generate_bibliography_data.py

# Create baseline
python scripts/baseline_assessments.py
```

### Issue Management
```bash
# Run assessment
python scripts/assess_repo.py

# Generate summary
python scripts/generate_assessment_summary.py

# Create GitHub issues
python scripts/create_issues_from_assessment.py
```

## Troubleshooting

### Tool Not Found
```bash
# Ensure Python packages installed
pip install -r requirements.txt

# Ensure tools directory in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Permission Errors
```bash
# Make scripts executable (Unix/Mac)
chmod +x scripts/*.py

# Or run with python explicitly
python scripts/script_name.py
```

### MATLAB Tools Not Working
```matlab
% Add to MATLAB path
addpath(genpath('tools/matlab_utilities'));
savepath

% Verify installation
which checkCodeQuality
```

## See Also

- [tools/README.md](../../tools/README.md) - Detailed tool documentation
- [scripts/README.md](../../scripts/README.md) - Script usage guides
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Development workflow
- [AGENTS.md](../../AGENTS.md) - Coding standards
