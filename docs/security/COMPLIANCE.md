# D-sorganization Compliance & Security Posture

This document defines the compliance readiness and security baseline for the D-sorganization fleet of repositories, addressing SEC-010 of Epic #3060.

## 1. Automated Security Controls
- **Dependency Scanning**: All repositories (Tools, UpstreamDrift, Gasification_Model, Runner_Dashboard, AffineDrift) use GitHub Dependabot for automated vulnerability patching (SEC-007).
- **Static Analysis**: Enforced via `ruff` and `mypy` in CI pipelines across the fleet.

## 2. Access Management & Secrets (SEC-002)
- Zero secrets are permitted in the source code.
- All secrets and API tokens are managed via GitHub Secrets or enterprise secret vaults (e.g., Azure Key Vault / AWS Secrets Manager).

## 3. Network & Application Security
- **Security Headers (SEC-005)**: All public-facing backend routers explicitly implement HSTS, CSP, X-Frame-Options, and X-Content-Type-Options.
- **CORS Hardening (SEC-006)**: Permissive origins are blocked. Only verified organization UI hosts are permitted for cross-origin requests.
- **Rate Limiting (SEC-003)**: Unauthenticated routes (such as Auth/Dev-login endpoints) restrict client IP attempts using rolling window limits (e.g., 5 attempts / 5 mins).

## 4. Remediation & Auditing
- **OWASP Remediation (SEC-004)**: Input sanitization, CSRF tokens, and parameter validation block OWASP Top 10 injection vectors.
- **Vulnerability Response**: Critical vulnerabilities must be patched within 24 hours (P0).
