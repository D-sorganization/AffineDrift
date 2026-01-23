# MATLAB Code Analyzer GUI

Interactive graphical user interface for analyzing MATLAB code quality, detecting issues, and generating reports.

## Features

- **Code Quality Analysis:** Detect code smells, complexity issues, and style violations
- **Batch Processing:** Analyze multiple files or entire directories
- **Report Generation:** Export analysis results to various formats
- **Exclusion Patterns:** Configure files and directories to exclude from analysis
- **Recursive Scanning:** Optionally scan subdirectories

## Requirements

- MATLAB R2019b or later
- MATLAB Code Analyzer toolbox

## Installation

1. Add the tool directory to your MATLAB path:
   ```matlab
   addpath('tools/matlab_code_analyzer_gui');
   ```

2. Or navigate to the directory in MATLAB:
   ```matlab
   cd tools/matlab_code_analyzer_gui
   ```

## Usage

### Launching the GUI

```matlab
% From MATLAB command window
matlab_code_analyzer_gui
```

### GUI Controls

1. **Select Files/Directory:** Choose files or folders to analyze
2. **Exclusion Patterns:** Specify patterns for files to exclude (e.g., `*_test.m`, `temp_*`)
3. **Recursive:** Check to include subdirectories
4. **Analyze:** Run the analysis
5. **Export Results:** Save report to file

### Programmatic Usage

```matlab
% Analyze a single file
results = analyzeFile('myScript.m');

% Analyze a directory
results = analyzeDirectory('src/', 'Recursive', true, 'ExcludeFiles', {'*_test.m'});

% Export results
exportResults(results, 'report.md', 'Format', 'markdown');
```

## Configuration

### Exclusion Patterns

Common exclusion patterns:
- `*_test.m` - Test files
- `temp_*.m` - Temporary files
- `old_*.m` - Archived files
- `*.asv` - MATLAB autosave files

### Analysis Rules

The analyzer checks for:
- Code complexity (cyclomatic complexity)
- Unused variables
- Missing documentation
- Style violations
- Potential bugs
- Performance issues

## Output Formats

Supported export formats:
- **Markdown** (`.md`) - Human-readable reports
- **JSON** (`.json`) - Machine-readable data
- **CSV** (`.csv`) - Spreadsheet-compatible
- **HTML** (`.html`) - Web-viewable reports

## Troubleshooting

### "No files found" error
- Check that the directory path is correct
- Verify exclusion patterns aren't too broad
- Ensure `.m` files exist in the target directory

### Analysis hangs or is slow
- Reduce the scope (analyze fewer files)
- Disable recursive scanning for large directories
- Check for very large or complex files

### Permission errors
- Ensure MATLAB has read access to the target directory
- Check file permissions on Windows/Unix systems

## Contributing

To extend the analyzer:

1. Add new analysis rules in the rules configuration
2. Update the GUI layout if adding new controls
3. Add tests for new functionality
4. Update this README with new features

## See Also

- [matlab_utilities/README.md](../matlab_utilities/README.md) - Related MATLAB utilities
- [AGENTS.md](../../AGENTS.md) - MATLAB coding standards
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines
