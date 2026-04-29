# Security Policy

## Reporting a Vulnerability

Please report vulnerabilities by emailing the repository owner or using GitHub's Private Vulnerability Reporting feature if enabled.

**Do not open public issues for security vulnerabilities.**

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Main    | :white_check_mark: |

---

## Secrets Management

This section documents how AffineDrift securely manages secrets and prevents accidental exposure of credentials.

### Never Hardcode Secrets

**DO NOT** commit any of the following to the repository:

- API keys (OpenAI, Anthropic, AWS, Google Cloud, etc.)
- Database passwords or connection strings with credentials
- OAuth tokens or refresh tokens
- SSH private keys
- Any bearer tokens or authentication credentials
- Docker registry credentials
- Slack webhooks or bot tokens

### How to Manage Secrets

#### Local Development

1. **Copy the template:** `cp .env.example .env`
2. **Fill in real values:** Edit `.env` with your actual API keys and credentials
3. **Keep it private:** `.env` is in `.gitignore` — never commit it
4. **Load before running:** `source .env` before executing your application

Example:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-key-here
source .env
python3 -m pytest  # Tests will use env vars from .env
```

#### Environment Variables in Code

Always read secrets from environment variables using `os.environ.get()`:

```python
# ✅ CORRECT: Use environment variables
import os

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# ❌ WRONG: Never hardcode
API_KEY = "sk-ABC123..."  # NEVER DO THIS
```

#### GitHub Actions / CI/CD

Secrets in GitHub Actions are managed via repository secrets:

1. Go to **Settings > Secrets and variables > Actions**
2. Click **New repository secret**
3. Enter the secret name (e.g., `OPENAI_API_KEY`) and value
4. In workflows, reference as `${{ secrets.OPENAI_API_KEY }}`

Example workflow:
```yaml
- name: Run tests with secrets
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: python3 -m pytest
```

### Automated Secret Detection

#### Pre-commit Hook (Local)

The repository includes `gitleaks` in pre-commit hooks to block commits containing secrets:

```bash
pip install pre-commit
pre-commit install
```

On next commit, gitleaks will scan for hardcoded secrets and **fail the commit** if any are found.

#### CI/CD Scanning (GitHub Actions)

Every PR and push to `main` or `staging` runs:
- **Gitleaks** — scans all committed code and history for secret patterns
- **.gitleaks.toml** — configures detection rules and allowlists

The CI will **fail** if hardcoded secrets are detected, preventing merge.

### If You Accidentally Commit a Secret

1. **Rotate the credential immediately** — assume it's exposed
2. **Remove from history:**
   ```bash
   # Option A: Use BFG Repo Cleaner (recommended)
   brew install bfg  # or download from https://rtyley.github.io/bfg-repo-cleaner/
   bfg --delete-files <filename>
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Option B: Git filter-branch (slower but built-in)
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch <path-to-secret-file>' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force-push to remote:**
   ```bash
   git push origin --force --all
   git push origin --force --tags
   ```
4. **Update .env.example** if needed to document the change
5. **Open an issue** noting the rotation date

### Secret Scanning Tools Used

- **Gitleaks** — Detects hardcoded secrets in git history and current commits
- **detect-secrets** — Baseline-aware secret detection (optional for local scanning)
- **Ruff security rules** — Catches unsafe patterns (shell injection, etc.)

To run detection locally without pre-commit:

```bash
# Install
pip install detect-secrets gitleaks

# Scan current directory
gitleaks detect --no-banner

# Create baseline
detect-secrets scan --all-files > .secrets.baseline
detect-secrets audit .secrets.baseline
```

### Best Practices

| DO                                                  | DON'T                                    |
| --------------------------------------------------- | ---------------------------------------- |
| Use `.env` for local development                   | Hardcode secrets in `.py` or `.js` files |
| Store secrets in GitHub Secrets for CI/CD          | Commit `.env` (keep in `.gitignore`)    |
| Use environment variable placeholders in code      | Log or print secret values                |
| Rotate credentials after accidental exposure       | Reuse old credentials                    |
| Document secret requirements in `.env.example`     | Keep secrets in version control history  |
| Use `os.environ.get()` with validation             | Trust users to provide secrets verbally  |

### Questions or Issues?

If you have questions about secrets management or discover a potential exposure:

1. Check this policy first
2. Review `.env.example` for variable names
3. Open a private security issue (GitHub Private Vulnerability Reporting)
4. Contact the repository owner
