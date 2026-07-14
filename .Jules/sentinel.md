
## 2026-07-14 - Pillow Dependency Vulnerabilities
**Vulnerability:** The `Pillow` dependency version `12.2.0` contained multiple vulnerabilities flagged by `pip-audit` (e.g., PYSEC-2026-165, PYSEC-2026-2250), which caused the CI pipeline to fail.
**Learning:** Even utility libraries used for image processing can contain critical security flaws that block CI.
**Prevention:** Always ensure dependencies are updated to their patched versions (e.g., `12.3.0` for `Pillow`) when `pip-audit` flags them during CI.
