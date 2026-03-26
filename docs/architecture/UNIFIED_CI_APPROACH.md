# Unified CI/CD Approach - AffineDrift Repository

**Last Updated:** 2025-01-27
**Version:** 1.0.0
**Repository:** D-sorganization/AffineDrift
**Tech Stack:** Quarto (website), Python (tools), HTML/CSS/JS (static site)

---

## Table of Contents

1. [Overview](#overview)
2. [Key CI/CD Principles](#key-cicd-principles)
3. [Tool Versions](#tool-versions)
4. [Workflow Templates](#workflow-templates)
5. [Python CI Workflow](#python-ci-workflow)
6. [Quarto Document Validation](#quarto-document-validation)
7. [Website Validation](#website-validation)
8. [Best Practices](#best-practices)
9. [Security Checks](#security-checks)
10. [Quality Check Scripts](#quality-check-scripts)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This document defines the unified CI/CD approach for the AffineDrift repository. AffineDrift is a Quarto-based website hosting technical writing, mathematical content, and interactive Python tools.

The repository uses a **hybrid approach** for CI/CD:

- **Python code**: Standard Python CI with pytest, ruff, mypy, black
- **Quarto documents**: Validation and rendering checks
- **Website files**: HTML/CSS/JS validation and accessibility checks

### Repository Structure

```
AffineDrift/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Main CI workflow
│       ├── pr-quality-check.yml      # PR quality checks
│       └── deploy.yml                # GitHub Pages deployment
├── .cursor/
│   └── rules/
│       ├── .cursorrules.md          # Cursor AI rules
│       └── matlabrules.md           # MATLAB rules (for reference)
├── content/                          # Technical writing content
│   ├── *.qmd                         # Quarto documents
│   ├── *.tex                         # LaTeX documents
│   └── *.md                          # Markdown documents
├── tools/                             # Interactive Python tools
│   └── wrist-universal-joint/        # Example tool
├── scripts/
│   └── quality-check.py             # Python quality checks
├── docs/                             # Generated documentation
├── _site/                            # Built website (GitHub Pages)
├── ruff.toml                         # Ruff configuration
├── mypy.ini                          # Mypy configuration
└── requirements.txt                  # Python dependencies (if needed)
```

---

## Key CI/CD Principles

### 1. Pinned Versions ✅

All tool versions are explicitly specified for reproducibility:

```yaml
pip install ruff==0.5.0 mypy==1.10.0 black==24.4.2 pytest==8.3.3 pytest-cov==6.0.0
```

**Rationale:** Prevents unexpected CI failures from tool updates.

### 2. Comprehensive Detection 🔍

Automatically find source directories and files:

```bash
# Check multiple possible locations
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f tools/*/requirements.txt ]; then pip install -r tools/*/requirements.txt; fi
```

**Rationale:** Works across different repository structures.

### 3. Proper Exit Codes ⚠️

Preserve failure codes for GitHub Actions:

```bash
# ✅ Good - Preserves exit code
ruff check . || exit 1

# ❌ Bad - Masks failures
ruff check . || true
```

**Exception:** Use `continue-on-error: true` in step definition for non-blocking checks.

### 4. Quarto Document Validation 📄

Validate Quarto documents render correctly:

```yaml
- name: Setup Quarto
  uses: quarto-dev/quarto-actions/setup@v2
  with:
    version: prerelease

- name: Validate Quarto documents
  run: quarto check
```

**Rationale:** Ensures technical writing is properly formatted and renders correctly.

### 5. Website File Validation 🌐

Validate HTML/CSS/JS before deployment:

```yaml
- name: Validate HTML
  run: npx html-validate "*.html"

- name: Check CSS
  run: npx stylelint "*.css"
```

**Rationale:** Ensures website files are valid and accessible.

### 6. Security Checks 🔒

Dependency scanning and secret detection:

```yaml
- name: Run Bandit security check
  continue-on-error: true
  run: bandit -r content tools --exclude '**/Archive/**','**/Drafts/**'
```

**Rationale:** Catch security vulnerabilities early.

### 7. Documentation Checks 📚

Markdown linting and docstring validation:

```yaml
- name: Lint Markdown files
  run: markdownlint-cli2 "**/*.md"

- name: Check for docstrings
  run: pydocstyle content tools
```

**Rationale:** Maintain documentation quality.

### 8. Replicant Branch Support 🌳

Include replicant branches in workflow triggers:

```yaml
on:
  push:
    branches: [main, master, copilot/*]
  pull_request:
    branches: [main, master, copilot/*]
```

**Rationale:** CI runs on AI-assisted development branches.

### 9. Quality Check Scripts 📋

Support standard locations:

```bash
if [ -f scripts/quality-check.py ]; then
  python scripts/quality-check.py
fi
```

**Rationale:** Flexibility across repositories.

### 10. Fail-Fast Strategy ⚡

Always include in matrix strategies:

```yaml
strategy:
  fail-fast: true
  matrix:
    python-version: ["3.11", "3.12"]
```

**Rationale:** Stop early on first failure to save CI time.

---

## Tool Versions

### Python Tools

| Tool       | Version | Purpose             |
| ---------- | ------- | ------------------- |
| ruff       | 0.5.0   | Fast Python linter  |
| mypy       | 1.10.0  | Static type checker |
| black      | 24.4.2  | Code formatter      |
| pytest     | 8.3.3   | Testing framework   |
| pytest-cov | 6.0.0   | Coverage plugin     |
| bandit     | 1.7.7   | Security scanner    |
| pydocstyle | 6.3.0   | Docstring checker   |

### Website Tools

| Tool              | Version | Purpose               |
| ----------------- | ------- | --------------------- |
| html-validate     | latest  | HTML validator        |
| stylelint         | latest  | CSS linter            |
| markdownlint-cli2 | latest  | Markdown linter       |
| pa11y-ci          | latest  | Accessibility checker |

### Quarto

| Tool   | Version    | Purpose                           |
| ------ | ---------- | --------------------------------- |
| quarto | prerelease | Document rendering and validation |

---

## Python CI Workflow

The main CI workflow (`ci.yml`) includes:

1. **Python Lint and Test**: Ruff, MyPy, Black, pytest
2. **Quarto Validation**: Document structure and rendering checks
3. **Website Validation**: HTML/CSS/JS validation
4. **Markdown Linting**: Documentation quality checks

### Key Features

- Runs on all pushes and PRs to main/master/copilot branches
- Non-blocking checks for Quarto and website validation (warnings only)
- Comprehensive Python code quality checks
- Automatic detection of Python files in content/ and tools/ directories

---

## Quarto Document Validation

Quarto documents are validated for:

- **Structure**: Valid Quarto project configuration
- **Syntax**: Proper .qmd file syntax
- **Rendering**: Documents render without errors
- **Links**: Internal and external links work correctly

### Exclusions

- `_site/` - Generated output
- `.quarto/` - Quarto cache
- `docs/` - Generated documentation
- `Archive/` and `Drafts/` directories

---

## Website Validation

Website files are validated for:

- **HTML**: Valid HTML5 syntax
- **CSS**: Valid CSS3 syntax
- **JavaScript**: Valid JavaScript syntax
- **Accessibility**: ARIA labels and semantic HTML
- **Common Issues**: TRACKED_TASK comments, console.log statements

### Tools Used

- `html-validate` - HTML validation
- `stylelint` - CSS linting
- `pa11y-ci` - Accessibility checking

---

## Best Practices

### Python Code

1. **Always use type hints**: Functions should have return type annotations
2. **Document constants**: All constants must have units and sources
3. **No placeholders**: No TRACKED_TASK, TRACKED_DEFECT, or NotImplementedError
4. **No magic numbers**: Use named constants with citations
5. **Comprehensive tests**: Include negative tests for error handling

### Quarto Documents

1. **Validate before commit**: Run `quarto check` locally
2. **Test rendering**: Ensure documents render correctly
3. **Check links**: Verify all internal and external links work
4. **Consistent formatting**: Use consistent mathematical notation

### Website Files

1. **Validate HTML**: Use html-validate before committing
2. **Check accessibility**: Ensure ARIA labels and semantic HTML
3. **Optimize assets**: Compress images and minimize CSS/JS
4. **Test responsiveness**: Verify mobile-friendly design

---

## Security Checks

Security checks run as part of PR quality checks:

- **Bandit**: Scans Python code for security vulnerabilities
- **Dependency scanning**: Checks for known vulnerabilities in requirements
- **Secret detection**: Warns about potential secrets in code

### Exclusions

- Archive directories
- Draft directories
- Generated files (\_site/, docs/)

---

## Quality Check Scripts

The `scripts/quality-check.py` script checks for:

- **Placeholders**: TRACKED_TASK, TRACKED_DEFECT, NotImplementedError
- **Magic numbers**: Hardcoded scientific constants
- **Missing docstrings**: Functions without documentation
- **Missing type hints**: Functions without return types

### Running Locally

```bash
python scripts/quality-check.py
```

### Exclusions

- Archive/ and Drafts/ directories
- Generated files (\_site/, docs/, .quarto/)
- Quality check scripts themselves

---

## Troubleshooting

### CI Failures

1. **Python linting fails**: Run `ruff check .` locally and fix issues
2. **Type checking fails**: Run `mypy .` locally and add type hints
3. **Quarto validation fails**: Run `quarto check` locally
4. **Website validation fails**: Run `html-validate *.html` locally

### Common Issues

1. **Missing type hints**: Add return type annotations to functions
2. **Magic numbers**: Replace with named constants
3. **Placeholders**: Remove TRACKED_TASK/TRACKED_DEFECT comments
4. **Quarto rendering errors**: Check Quarto project configuration

### Getting Help

- Check workflow logs in GitHub Actions
- Run checks locally before pushing
- Review `.cursor/rules/.cursorrules.md` for coding standards

---

## Repository-Specific Notes

### AffineDrift Characteristics

- **Primary Content**: Technical writing (Quarto, LaTeX, Markdown)
- **Python Tools**: Interactive simulators and analysis tools
- **Website**: Static HTML/CSS/JS hosted on GitHub Pages
- **MATLAB Code**: Python-based static analysis (if MATLAB files exist)
- **Deployment**: Automatic via GitHub Pages on push to main

### Directory Structure

- `content/`: Technical writing content (exclude Archive/ and Drafts/)
- `tools/`: Interactive Python tools
- `docs/`: Generated documentation (excluded from checks)
- `_site/`: Built website (excluded from checks)
- `.quarto/`: Quarto cache (excluded from checks)

### Code Quality Rules

See `docs/CODE_QUALITY_RULES.md` for detailed quality requirements for:

- Python code
- HTML
- CSS
- JavaScript
- MATLAB
- Quarto documents
- Markdown

---

**Last Updated:** 2025-01-27
**Maintained by:** D-sorganization
