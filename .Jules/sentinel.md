## 2026-07-15 - Fix Pillow Vulnerabilities
**Vulnerability:** Multiple vulnerabilities identified in Pillow 12.2.0 via `pip-audit` (PYSEC-2026-2253, PYSEC-2026-2255, PYSEC-2026-2257, PYSEC-2026-2256, PYSEC-2026-2254).
**Learning:** Outdated dependencies can block CI pipelines due to active `pip-audit` checks.
**Prevention:** Update packages to patched versions immediately to unblock builds. Even if acting as a non-security persona (e.g., Palette), resolving these failures must be logged as a security fix.
