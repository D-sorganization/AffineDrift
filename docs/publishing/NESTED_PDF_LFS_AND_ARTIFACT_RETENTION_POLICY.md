# Nested PDF, Git LFS Intent, and Reproducible Build-Artifact Retention Policy

## Executive Summary and Authority Boundaries

This document establishes the authoritative asset retention, storage placement, and Git LFS scoping
policy for the AffineDrift repository in accordance with `#5543`. It clarifies the design intent of
root-only Git Large File Storage (LFS) configuration, formalizes the inventory of nested publication
assets, and sets binding verification rules for reproducible build-artifact retention.

This policy records actionable operational boundaries without authorizing history rewrites, blanket
binary deletions, unapproved LFS migrations, or runner-count expansions.

## Git Attributes and Root-Only LFS Scoping Intent

At inspected main commit `8aa16c04e`, `.gitattributes` specifies:

```gitattributes
*.pdf binary
/*.pdf filter=lfs diff=lfs merge=lfs -text
```

### Why Root-Only Scoping Is Intentional

1. **Static Site and GitHub Pages Delivery:**
   AffineDrift is an educational publishing platform deployed to GitHub Pages. GitHub Pages serves
   committed repository files directly via its global CDN without on-the-fly Git LFS smudge
   hydration. If nested PDFs were converted to Git LFS pointers without specialized CDN proxying,
   readers, academic indexers, and automated browsers would receive 130-byte text pointer stubs
   (`version https://git-lfs.github.com/spec/v1`) rather than valid PDF binary documents (`%PDF-`).

2. **Runner Hygiene and CI Checkout Performance:**
   The primary CI and deployment workflows (`.github/workflows/deploy-website.yml`,
   `.github/workflows/ci-standard.yml`) execute `actions/checkout` without `lfs: true` to ensure fast,
   deterministic, and network-independent checkouts. Keeping published articles committed as native
   hydrated Git binary blobs guarantees that all local linters, Quarto builds, and offline test suites
   function reliably without external LFS bandwidth consumption, quotas, or rate-limit failures.

3. **Accidental Commit Guard:**
   The root rule `/*.pdf filter=lfs ...` intentionally prevents accidental commits of unvetted,
   monolithic PDF dumps or raw export bundles directly into the repository root.

## Asset Categorization and Publishing Inventory

Repository binary assets are strictly categorized into four operational tiers:

### Reviewed Publication Outputs

- **Scope:** Completed authoritative textbooks and peer-reviewed technical reports (e.g.,
  `articles/The_Physics_of_Golf/main.pdf`, `articles/shot_pattern_analysis/report.pdf`,
  `articles/The_Geometry_of_Motion/Volume_{0..V}/main.pdf`,
  `articles/Launch_Monitor_Technology_Review/main.pdf`).
- **Consumers:** External readers, academic citations, textbook companion site downloads, library
  indexes.
- **Storage Tier:** Native Git binary blobs within `articles/` subdirectories.
- **Retention Requirement:** Permanent, immutable per publication release. Never deleted or
  unhydrated.
- **Verification Rule:** Tracked in canonical manifests with page-count floors, minimum byte sizes,
  and SHA-256 integrity checks enforced by `scripts/check_publishing_assets.py`.

### Source Figures and Vector Graphics

- **Scope:** Vector diagrams and raster figures required for textbook compilation (e.g.,
  `articles/**/figures/*.pdf`, `articles/**/figures/*.png`, `pics/`, `static/images/`).
- **Consumers:** Quarto compilation, LaTeX `compile-textbooks.yml`, web article rendering.
- **Storage Tier:** Native Git binary blobs co-located with article sources.
- **Retention Requirement:** Permanent, tracked alongside source text.
- **Verification Rule:** Enforced by `scripts/check_image_budget.py` and
  `scripts/check_publishing_assets.py` to prevent corruption or zero-byte files.

### Immutable Evidence and Verification Records

- **Scope:** Experimental datasets, motion capture camera calibration registries, trust panel
  ledgers (`data/trust/*.json`), and visual regression screenshots (`docs/ux-evidence/`).
- **Consumers:** Scientific integrity gates, CI verification suites, peer reviewers.
- **Storage Tier:** Tracked in Git with strict commit hashing and ledger seals.
- **Retention Requirement:** Durable scientific record; amendments require evidence-ladder approval.
- **Verification Rule:** Governed by `scripts/regenerate_claim_audit_evidence.py` and associated
  contract validators.

### Reproducible Build Outputs and Ephemeral CI Artifacts

- **Scope:** Rendered `_site/` build artifacts, `artifacts/build-manifest.json`, test coverage
  reports (`coverage.xml`), and Playwright test traces.
- **Consumers:** Automated deployment jobs and PR reviewers.
- **Storage Tier:** Generated dynamically from deterministic source files; stored as ephemeral GitHub
  Actions artifacts (retention 7–30 days).
- **Retention Requirement:** Strictly ephemeral; excluded from long-term Git tracking.
- **Verification Rule:** Verified for reproducibility using pinned lockfiles and
  `scripts/write_build_manifest.py --check`.

## Ephemeral CI Retention vs. Durable Publication Storage

| Asset Category | Storage Tier | Retention Window | Restoration SLA | Mutation Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Reviewed Publications** | Git binary blob | Permanent | Zero-latency local checkout | Immutable upon approval |
| **Source Figures** | Git binary blob | Permanent | Zero-latency local checkout | Versioned with source |
| **Scientific Evidence** | Git / Trust ledgers | Permanent | Deterministic ledger check | Ledger-controlled |
| **CI Build Artifacts** | Actions artifact cache | 7–30 days | Generated on demand | Rebuilt per commit |

## Automated Verification Oracles and Integrity Contracts

Automated regression prevention is enforced by `scripts/check_publishing_assets.py` and
`tests/test_check_publishing_assets.py`:

1. **Attribute Contract:** Asserts that `.gitattributes` maintains root-only LFS scoping (`/*.pdf`)
   and binary classification (`*.pdf binary`).
2. **Payload Hydration Check:** Confirms that no tracked PDF in `articles/` or `content/` contains the
   Git LFS pointer header (`version https://git-lfs.github.com/spec/v1`).
3. **Non-Zero and Magic Bytes Check:** Confirms that all tracked PDFs are non-empty and start with the
   canonical `%PDF-` magic header.
4. **Canonical Deliverable Oracle:** Verifies that core publication assets satisfy minimum byte-size
   and SHA-256 integrity thresholds.

## Migration Safeguards and Reversibility Protocol

Any future restructuring or offloading of binary assets must adhere to the following protocol:

- **No Blanket Deletions:** Assets may not be purged without prior domain inventory and approval.
- **Bandwidth and Quota Modeling:** Any LFS or external CDN migration must provide measured transfer
  and billing impact models prior to execution.
- **Offline Restoration Proof:** Any alternative storage architecture must prove clean offline
  checkout, build, and serving capabilities without network access.
- **Owner Approval:** Final authorization must be granted by repository leadership before altering
  storage tiers.
