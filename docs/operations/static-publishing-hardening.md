# Static Publishing Hardening

Epic tracker for professional deployment of affinedrift.com (#5321).

## Child Deliverables

| Issue | Topic | Artifact |
| --- | --- | --- |
| #5318 | Release and rollback | [site-release-rollback.md](./site-release-rollback.md) |
| #5319 | Build manifest / SBOM | `scripts/write_build_manifest.py`, `scripts/write_sbom.py` (CycloneDX), `schemas/build-manifest.schema.json`; published as the `build-provenance-<sha>` workflow artifact |
| #5320 | Post-deploy URL / SRI checks | [post-deploy-verification.md](./post-deploy-verification.md) |

Sidekick packaging remains on hold per fleet directive (GM #5478).

## Mobile Publication (Separate Epic)

Phone layout and performance work lives under #5317; see [mobile-publication-readiness.md](./mobile-publication-readiness.md).
