# Security Guidelines

AffineDrift enforces security policies throughout the codebase. This guide
documents security requirements enforced by CI (bandit, pip-audit, SAST gates)
and the patterns contributors must follow.

## Secrets Management

**Never commit secrets** — API keys, tokens, passwords, or credentials must
never appear in source code, configuration files, or documentation.

### What Counts as a Secret

- API keys (`sk-...`, `ghp_...`, `AIza...`)
- OAuth tokens and bearer tokens
- Private SSH keys
- Database connection strings with credentials
- Environment-specific passwords
- GitHub Personal Access Tokens

### Where to Store Secrets

Use environment variables or your deployment platform's secret store:

```bash
# Local development — .env file (MUST be in .gitignore)
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# GitHub Actions — repository secrets
# Settings > Secrets and variables > Actions > New repository secret
```

```yaml
# .github/workflows/ci-standard.yml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

**Never** use `echo` to print secrets in CI steps.

### Detecting Accidental Secret Commits

CI runs `git-secrets` and `trufflehog` pattern scanning. If a secret is
accidentally committed:

1. **Do not** just delete the secret in a new commit — it remains in history.
2. Rotate the credential immediately.
3. Contact the repository owner to purge the history if needed.
4. Use `git filter-repo` or GitHub's secret scanning alert workflow.

## Input Validation and Sanitization

### Python

All external inputs (CLI args, file contents, API responses) must be validated
before use. Do not trust user-provided data:

```python
import re
from pathlib import Path

# Good — validate before use
def load_config(config_path: str) -> dict:
    path = Path(config_path).resolve()
    if not path.is_file():
        raise ValueError(f"Config file not found: {config_path}")
    if path.suffix not in {".yaml", ".yml", ".json"}:
        raise ValueError(f"Unsupported config format: {path.suffix}")
    ...

# Good — validate numeric inputs
def set_swing_speed(speed_mph: float) -> None:
    if not (0.0 < speed_mph <= 200.0):
        raise ValueError(f"swing_speed must be in (0, 200] mph, got {speed_mph}")
    ...
```

### SQL Injection Prevention

AffineDrift does not use raw SQL, but if adding database access, always use
parameterized queries:

```python
# Good — parameterized
cursor.execute("SELECT * FROM articles WHERE slug = ?", (slug,))

# NEVER do this — SQL injection vulnerability
cursor.execute(f"SELECT * FROM articles WHERE slug = '{slug}'")
```

### Path Traversal Prevention

Resolve and validate paths before file I/O:

```python
import os
from pathlib import Path

def read_article(filename: str, base_dir: Path) -> str:
    # Resolve to absolute path and verify it's within the allowed directory
    resolved = (base_dir / filename).resolve()
    if not str(resolved).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal attempt: {filename}")
    return resolved.read_text(encoding="utf-8")
```

### JavaScript XSS Prevention

Never insert untrusted data directly into the DOM:

```javascript
// Good — use textContent for text data
element.textContent = userInput;

// Good — sanitize before innerHTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userMarkdown);

// NEVER do this — XSS vulnerability
element.innerHTML = userInput;
```

Avoid `eval()`, `Function()`, and `setTimeout(string)` with user-controlled
input — these are code injection vectors.

## Dependency Security

### Python Dependencies

All Python dependencies are pinned in `requirements.txt`. CI runs `pip-audit`
to detect known vulnerabilities:

```bash
# Check locally
pip-audit --requirement requirements.txt
```

When updating dependencies:

1. Update the version in `requirements.txt`.
2. Run `pip-audit` to confirm no new vulnerabilities.
3. Run the full test suite.
4. Update `requirements-docker.lock` if the Docker build is affected:

```powershell
py -3.12 -m piptools compile --allow-unsafe --generate-hashes `
  --resolver=backtracking `
  --output-file requirements-docker.lock `
  requirements.txt
```

### JavaScript Dependencies

CI scans `package.json` dependencies with `npm audit`:

```bash
# Check locally
npm audit

# Fix auto-fixable vulnerabilities
npm audit fix
```

Pin dependencies to exact versions in `package-lock.json`. Do not use
`*` or `latest` version ranges.

### Automated Dependency Updates

Dependabot is configured to open PRs for outdated dependencies. These PRs:

- Are automatically triaged by CI
- Run the full test suite
- Must pass `pip-audit` / `npm audit`
- Can be merged without manual review if all checks pass

## Static Analysis (SAST)

CI runs **bandit** for Python static security analysis:

```bash
# Run locally
python -m bandit -r src/ -c pyproject.toml
```

Common bandit findings and how to handle them:

| Finding | Action |
|---------|--------|
| `B101: assert_used` | Use `if not condition: raise` in production code (not `assert`) |
| `B301: pickle` | Avoid `pickle` for untrusted data; use `json` or `msgpack` |
| `B310: urllib_urlopen` | Add `# noqa: S310` with a comment justifying the URL is trusted |
| `B603: subprocess_without_shell_equals_true` | Use `shell=False` (default) |
| `B608: hardcoded_sql_expressions` | Use parameterized queries |

Add `# noqa: B<code>` with a justification comment only when a finding is a
known false positive.

## Docker Security

The Dockerfile follows minimal-privilege principles:

- Base image is pinned to a specific digest (not `latest`).
- Quarto `.deb` checksum is verified before installation.
- Dependencies are installed from the hash-locked `requirements-docker.lock`.
- The container runs as a non-root user where possible.
- No secrets are baked into the image.

```dockerfile
# Good — pinned digest
FROM python:3.12-slim@sha256:<digest>

# Good — verify checksum
RUN echo "<sha256sum>  quarto.deb" | sha256sum --check
```

## HTTPS and Certificate Validation

Always use HTTPS for external requests. Do not disable certificate verification:

```python
# Good
import requests
response = requests.get("https://api.example.com/data", timeout=10)

# NEVER do this — disables certificate validation
response = requests.get(url, verify=False)
```

In the link checker and tools that make HTTP requests, the default SSL context
is used (system trust store). Custom certificate handling requires explicit
justification.

## Logging Security

Do not log sensitive data:

```python
# Good
logger.info("User authenticated: %s", username)

# Bad — logs a secret
logger.debug("Using API key: %s", api_key)

# Good — log only presence, not value
logger.debug("API key configured: %s", bool(api_key))
```

## Security Audit Trail

Significant security decisions are tracked in:

- `docs/GOVERNANCE.md` — agent approval policies
- Issue labels: `security`, `vulnerability`, `dependency-update`
- PR labels: `security-fix`

Security fixes use the `fix(security):` commit prefix and reference CVE or
bandit finding IDs:

```
fix(security): sanitize polynomial eval to prevent XSS (bandit B610)

Closes #3040
```

## Reporting Vulnerabilities

This is a personal research repository. To report a security issue:

1. Open a GitHub issue with the `security` label.
2. For sensitive disclosures, use GitHub's private vulnerability reporting:
   **Security tab > Report a vulnerability**.

Do not post exploit details in public issues.

## References

- [OWASP Top 10](https://owasp.org/Top10/)
- [bandit documentation](https://bandit.readthedocs.io/)
- [pip-audit documentation](https://pypi.org/project/pip-audit/)
- [Conventional Commits security type](https://www.conventionalcommits.org/)
- `docs/GOVERNANCE.md` — repository governance policy
- `docs/development/code-style-guide.md` — coding standards
