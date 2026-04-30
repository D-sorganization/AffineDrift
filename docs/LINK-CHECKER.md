# Link Checker: Quarto Reference & URL Validator

Validates Quarto internal references and external URLs across the documentation.

## Features

- **Internal References**: Validates `@sec-`, `@fig-`, `@eq-` references (Quarto cross-references)
- **External URLs**: Checks HTTP/HTTPS links with retry logic for fragile domains
- **GitHub Actions CI**: Automatic validation on PR and scheduled daily runs
- **Pre-commit Hooks**: Optional local validation before commit/push
- **Smart Retry Logic**: Handles timeouts for known-fragile domains (GitHub, ArXiv, etc.)

## Usage

### Command Line

Check internal references only:
```bash
python scripts/link-checker.py
```

Check external URLs only:
```bash
python scripts/link-checker.py --external-only
```

Check specific file:
```bash
python scripts/link-checker.py --file docs/index.qmd
```

Verbose output (shows found references/URLs):
```bash
python scripts/link-checker.py --verbose
```

### Exit Codes

- `0`: All checks passed
- `1`: Critical errors (broken internal references) — blocks merge
- `2`: Warnings (external URL failures) — non-blocking

### GitHub Actions

The workflow runs automatically on:
- **Pull requests**: Changes to .md, .qmd, or link-checker itself
- **Scheduled**: Daily at 2 AM UTC (detects broken external URLs)
- **Manual**: Trigger via workflow_dispatch

### Pre-commit Hooks

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

Configure in `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: link-checker-internal
        name: Check Quarto references
        entry: python scripts/link-checker.py
        language: python
        types: [markdown]
        stages: [commit]
```

## Configuration

### Timeout Settings

Default timeout: 5 seconds per URL
Max retries: 2 (for fragile domains)
Retry delay: 1 second

To customize, edit `TIMEOUT`, `MAX_RETRIES`, `RETRY_DELAY` in `scripts/link-checker.py`.

### Known Fragile Domains

These domains get more lenient handling (retries):
- github.com
- arxiv.org
- stackoverflow.com

Add more in `KNOWN_FRAGILE_URLS` in the script.

## Common Issues

### "Undefined reference: @sec-xyz"

This means a Quarto reference `@sec-xyz` is used but not defined. To fix:
1. Find where it's used: `grep -r "@sec-xyz" docs/`
2. Find where it should be defined: `grep -r "{#sec-xyz}" docs/`
3. If the label doesn't exist, create it or fix the reference

### External URL timeouts

These are warnings (non-blocking) but can indicate:
- Network issues
- Site temporarily down
- Overly restrictive timeout

Solutions:
1. Verify URL works manually
2. Add domain to `KNOWN_FRAGILE_URLS`
3. Increase timeout (edit script)
4. Remove or replace link if permanently broken

## Implementation Details

### Reference Discovery

The script finds label definitions by searching for:
- `{#sec-xxx}` — Section labels
- `{#fig-xxx}` — Figure labels
- `{#eq-xxx}` — Equation labels
- `{#tbl-xxx}` — Table labels
- `{#lst-xxx}` — Listing labels
- `{#exr-xxx}` — Exercise labels

### URL Validation

Uses Python's built-in `urllib`:
- Follows HTTP redirects
- Validates SSL certificates
- Custom User-Agent to avoid blocking
- Retry logic for fragile domains

### Quarto Integration

Works with standard Quarto markdown:
- `.qmd` files (Quarto markdown)
- `.md` files (plain markdown with Quarto references)

## Troubleshooting

**"Script not found"**
```bash
# Ensure it's executable
chmod +x scripts/link-checker.py
```

**"No markdown files found"**
```bash
# Check that .md and .qmd files exist
find . -name "*.md" -o -name "*.qmd"
```

**"Timeout errors in CI"**
- Increase timeout: Edit `TIMEOUT` in script
- Add domain to fragile list: Edit `KNOWN_FRAGILE_URLS`
- Check network connectivity

## Future Enhancements

- [ ] Cache for URL checks (avoid re-checking same URLs)
- [ ] Whitelist/blacklist for specific URLs
- [ ] Markdown link format detection `[text](url)`
- [ ] Integration with Quarto render process
- [ ] Reporter output formats (JSON, SARIF)
- [ ] Performance: Parallel URL validation
