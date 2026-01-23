# Tools Directory

This directory contains utility tools and scripts for the AffineDrift project.

## Directory Structure

```
tools/
├── matlab_code_analyzer_gui/    # GUI tool for MATLAB code analysis
├── matlab_utilities/            # MATLAB utility functions
│   ├── quality/                 # Code quality checking utilities
│   ├── scripts/                 # MATLAB helper scripts
│   └── testing/                 # Testing utilities
├── latex_to_qmd.py             # LaTeX to Quarto markdown converter
└── update_navigation.py         # Navigation menu updater
```

## Python Tools

### latex_to_qmd.py
Converts LaTeX documents to Quarto markdown format (.qmd).

**Usage:**
```bash
python -m tools.latex_to_qmd input.tex output.qmd
```

### update_navigation.py
Updates the navigation menu structure in `_quarto.yml` based on content changes.

**Usage:**
```bash
python -m tools.update_navigation
```

## MATLAB Tools

### matlab_code_analyzer_gui
Interactive GUI for analyzing MATLAB code quality and generating reports.

See `matlab_code_analyzer_gui/README.md` for detailed documentation.

### matlab_utilities
Collection of MATLAB utility functions for quality checking, testing, and code analysis.

See `matlab_utilities/README.md` for detailed documentation.

## Related Scripts

Additional build and maintenance scripts are located in the `scripts/` directory. See `scripts/README.md` for documentation.

## Contributing

When adding new tools:
1. Create a dedicated subdirectory or module
2. Add a README.md with usage instructions
3. Include docstrings in all functions
4. Add tests in the `tests/` directory
5. Update this README with a brief description

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [scripts/README.md](../scripts/README.md) - Build and maintenance scripts
- [AGENTS.md](../AGENTS.md) - Coding standards and best practices
