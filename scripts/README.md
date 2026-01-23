# Scripts Directory

This directory contains build, maintenance, and automation scripts for the AffineDrift project.

## Build & Deployment Scripts

### generate_sitemap.py
Generates the sitemap.xml file for SEO and search engine indexing.

**Usage:**
```bash
python scripts/generate_sitemap.py
```

**Output:** `sitemap.xml` in the project root

### generate_search_index.py
Creates the search index for the site's search functionality.

**Usage:**
```bash
python scripts/generate_search_index.py
```

**Output:** `docs/search.json`

### generate_bibliography_data.py
Processes bibliography data from YAML/JSON sources and generates structured bibliography files.

**Usage:**
```bash
python scripts/generate_bibliography_data.py
```

**Input:** `data/bibliography.yaml`
**Output:** `data/bibliography.json`

## Content Processing Scripts

### add_meta_descriptions.py
Adds or updates meta descriptions in HTML files for SEO optimization.

**Usage:**
```bash
python scripts/add_meta_descriptions.py
```

**Target:** HTML files in `docs/` directory

### scan_quarto_syntax.py
Scans Quarto (.qmd) files for syntax issues and potential problems.

**Usage:**
```bash
python scripts/scan_quarto_syntax.py [path]
```

**Options:**
- `path`: Directory or file to scan (default: current directory)

### check-equations.py
Validates mathematical equations in markdown files for LaTeX syntax errors.

**Usage:**
```bash
python scripts/check-equations.py
```

**Target:** `.qmd` and `.md` files in `articles/` directory

## Quality & Assessment Scripts

### seo_audit.py
Performs comprehensive SEO audit of the generated site.

**Usage:**
```bash
python scripts/seo_audit.py
```

**Output:** SEO audit report with recommendations

### assess_repo.py
Analyzes repository structure, code quality, and generates assessment reports.

**Usage:**
```bash
python scripts/assess_repo.py
```

**Output:** Assessment report in `assessments/` directory

### baseline_assessments.py
Creates baseline quality metrics for tracking improvements over time.

**Usage:**
```bash
python scripts/baseline_assessments.py
```

**Output:** Baseline metrics in `assessments/` directory

### generate_assessment_summary.py
Generates summary reports from individual assessment files.

**Usage:**
```bash
python scripts/generate_assessment_summary.py
```

**Input:** Assessment files in `assessments/` directory
**Output:** `assessments/summary.md`

### create_issues_from_assessment.py
Automatically creates GitHub issues from assessment findings.

**Usage:**
```bash
python scripts/create_issues_from_assessment.py
```

**Requirements:** GitHub CLI (`gh`) must be installed and authenticated

## Development Workflow

### Typical Build Process

1. **Content Updates:**
   ```bash
   # Check equations in articles
   python scripts/check-equations.py
   
   # Scan for syntax issues
   python scripts/scan_quarto_syntax.py articles/
   ```

2. **Build Site:**
   ```bash
   quarto render
   ```

3. **Post-Build:**
   ```bash
   # Generate search index
   python scripts/generate_search_index.py
   
   # Generate sitemap
   python scripts/generate_sitemap.py
   
   # Add meta descriptions
   python scripts/add_meta_descriptions.py
   ```

4. **Quality Checks:**
   ```bash
   # Run SEO audit
   python scripts/seo_audit.py
   
   # Run repository assessment
   python scripts/assess_repo.py
   ```

## Requirements

All scripts require Python 3.8+ and dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Key Dependencies

- `beautifulsoup4` - HTML parsing
- `pyyaml` - YAML file processing
- `lxml` - XML processing
- `requests` - HTTP requests (for SEO audit)

## Contributing

When adding new scripts:

1. **Follow naming conventions:** Use lowercase with hyphens or underscores
2. **Add docstrings:** Document all functions and modules
3. **Include usage examples:** Add `if __name__ == "__main__"` block with examples
4. **Update this README:** Add entry with description and usage
5. **Add tests:** Create corresponding test file in `tests/`
6. **Use logging:** Prefer `logging` module over `print()` statements

## See Also

- [tools/README.md](../tools/README.md) - Utility tools documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [AGENTS.md](../AGENTS.md) - Coding standards and best practices
