## 2026-07-17 - Bumped Pillow to 12.3.0 to fix pip-audit vulnerabilities
**Vulnerability:** Pillow 12.2.0 has multiple known vulnerabilities (e.g., PYSEC-2026-2253).
**Learning:** Security audits run during the CI pipeline will fail the build if vulnerable dependencies are present in `requirements.txt`.
**Prevention:** Regularly audit dependencies locally using `pip-audit -r requirements.txt` and update to patched versions (e.g., 12.3.0) when failures occur.
