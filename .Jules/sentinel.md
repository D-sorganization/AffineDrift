
## 2026-07-16 - Dependency Security Update
**Vulnerability:** `pip-audit` detected vulnerabilities in `Pillow` version `12.2.0` (PYSEC-2026-2253, PYSEC-2026-2255, PYSEC-2026-2257, PYSEC-2026-2256, PYSEC-2026-2254, PYSEC-2026-3453, PYSEC-2026-3451, PYSEC-2026-3452) blocking the build.
**Learning:** Resolving dependency vulnerabilities is critical to unblock CI, regardless of primary task persona.
**Prevention:** Upgraded `Pillow` to secure version `12.3.0` in `requirements.txt`.
