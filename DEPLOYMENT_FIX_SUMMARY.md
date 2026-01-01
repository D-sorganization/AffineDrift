# Deployment Fix Summary - Jan 2026 (Fixing Missing Checks)

## Problem Identified
The user reported that `AffineDrift` deployment "hasn't been acting right for over 2 days" and was missing "predeployment checks" and a "deployment check". 
Investigation revealed:
1.  **Silent Failures:** Critical scripts `tools/check_site_health.py` and `tools/check_links.py` were running but **not exiting with a non-zero code** when errors were found. This meant bad builds could pass silently.
2.  **Missing Verification:** The `deploy-website.yml` workflow did not actually run these checks, nor did it verify the final deployment.
3.  **Dependency Issues:** `check_site_health.py` requires `beautifulsoup4`, which was missing from `requirements.txt`.

## Changes Applied

### 1. Hardened Verification Scripts
Updated both check scripts to exit with `sys.exit(1)` if issues are found:
- `tools/check_site_health.py`: Now fails CI if broken links or orphaned files are detected in `docs/`.
- `tools/check_links.py`: Now fails CI if broken source links (markdown/html) are found.

### 2. Workflow Orchestration (`.github/workflows/deploy-website.yml`)
Updated the deployment workflow to enforce a strict quality gate:
- **Pre-build:** Runs `tools/check_links.py` to catch bad source links immediately.
- **Post-build:** Runs `tools/check_site_health.py` to verify the generated artifact (`docs/`) before upload.
- **Deployment Verification:** Added a `Verify Deployment` step that waits for propagation and runs `curl -f -I` against the live URL to ensure availability.

### 3. Dependencies
- Added `beautifulsoup4>=4.12.0` to `requirements.txt`.

### 4. Regression Testing
- Created `tests/test_deployment_integrity.py` to ensure that future edits to the workflow do not accidentally remove these critical checks.

## Verification
- Run `pytest tests/test_deployment_integrity.py` to confirm the workflow configuration is correct.
- Committing these changes will trigger the new workflow on `main`.

## Status
- **Ready for Merge:** All requested checks are implemented and tested.
