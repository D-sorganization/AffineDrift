# MATLAB Utilities

Collection of MATLAB utility functions for code quality checking, testing, and analysis.

## Directory Structure

```
matlab_utilities/
├── quality/          # Code quality checking utilities
├── scripts/          # Helper scripts and automation
└── testing/          # Testing utilities and frameworks
```

## Quality Utilities

Located in `quality/` directory.

### Code Quality Checker

Analyzes MATLAB code for quality issues, style violations, and potential bugs.

**Usage:**
```matlab
% Check a single file
results = checkCodeQuality('myScript.m');

% Check a directory
results = checkCodeQuality('src/', 'Recursive', true);

% Generate report
generateQualityReport(results, 'quality_report.md');
```

### Configuration

Quality checks can be configured via `matlab_quality_config.m`:

```matlab
config = matlab_quality_config();
config.MaxComplexity = 15;
config.RequireDocstrings = true;
config.CheckNaming = true;
```

## Testing Utilities

Located in `testing/` directory.

### Test Runner

Automated test execution and reporting.

**Usage:**
```matlab
% Run all tests
results = runAllTests();

% Run specific test suite
results = runTestSuite('tests/unit/');

% Generate test report
generateTestReport(results, 'test_report.html');
```

### Test Helpers

Common testing utilities:
- `assertAlmostEqual()` - Floating-point comparison with tolerance
- `assertMatrixEqual()` - Matrix equality with element-wise comparison
- `mockFunction()` - Function mocking for unit tests
- `captureOutput()` - Capture command window output

## Scripts

Located in `scripts/` directory.

### Batch Processing

Utilities for processing multiple files:

```matlab
% Process all .m files in a directory
processAllFiles('src/', @analyzeFunction);

% Apply transformation to files
transformFiles('src/', @addHeader, 'Pattern', '*.m');
```

### Path Management

```matlab
% Add project paths
setupProjectPaths();

% Clean up paths
cleanupProjectPaths();

% Verify required toolboxes
checkRequiredToolboxes();
```

## Installation

1. Add utilities to MATLAB path:
   ```matlab
   addpath(genpath('tools/matlab_utilities'));
   ```

2. Or use the setup script:
   ```matlab
   cd tools/matlab_utilities
   setup
   ```

## Requirements

- MATLAB R2019b or later
- Required toolboxes (checked automatically):
  - Statistics and Machine Learning Toolbox (optional)
  - Optimization Toolbox (optional)

## Configuration Files

### matlab_quality_config.m

Configures code quality checking rules:
- Complexity thresholds
- Naming conventions
- Documentation requirements
- Style preferences

### run_matlab_tests.m

Configures test execution:
- Test discovery patterns
- Output formats
- Coverage reporting
- Parallel execution

## Best Practices

### Code Quality

1. **Run quality checks before committing:**
   ```matlab
   results = checkCodeQuality('src/');
   if ~isempty(results.errors)
       error('Quality checks failed');
   end
   ```

2. **Integrate with CI/CD:**
   ```bash
   matlab -batch "checkCodeQuality('src/'); exit(exitCode)"
   ```

### Testing

1. **Organize tests by type:**
   - `tests/unit/` - Unit tests
   - `tests/integration/` - Integration tests
   - `tests/performance/` - Performance tests

2. **Use descriptive test names:**
   ```matlab
   function test_calculateMean_withValidInput_returnsCorrectValue()
       % Test implementation
   end
   ```

3. **Run tests frequently:**
   ```matlab
   % Quick smoke test
   runTestSuite('tests/unit/critical/');
   
   % Full test suite
   runAllTests();
   ```

## Troubleshooting

### Path Issues

If functions are not found:
```matlab
% Verify paths
which checkCodeQuality

% Re-add paths
addpath(genpath('tools/matlab_utilities'));
savepath
```

### Toolbox Dependencies

Check for missing toolboxes:
```matlab
checkRequiredToolboxes();
```

### Performance

For large codebases:
- Use parallel processing: `parfor` in batch operations
- Exclude generated files: Configure exclusion patterns
- Cache results: Enable result caching in config

## Contributing

When adding new utilities:

1. **Follow naming conventions:**
   - Functions: `camelCase`
   - Classes: `PascalCase`
   - Constants: `UPPER_CASE`

2. **Add documentation:**
   - Function headers with description
   - Input/output specifications
   - Usage examples

3. **Include tests:**
   - Unit tests for all functions
   - Integration tests for workflows
   - Performance tests for critical paths

4. **Update this README:**
   - Add new utility descriptions
   - Update usage examples
   - Document configuration options

## See Also

- [matlab_code_analyzer_gui/README.md](../matlab_code_analyzer_gui/README.md) - GUI analyzer tool
- [AGENTS.md](../../AGENTS.md) - MATLAB coding standards
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines
- [tests/README.md](../../tests/README.md) - Testing documentation
