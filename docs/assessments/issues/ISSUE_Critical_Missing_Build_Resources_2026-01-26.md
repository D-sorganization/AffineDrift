---
title: Critical Missing Build Resources for Startup Launcher
labels: incomplete-implementation, critical, deployment, bug
assignee: unassigned
---

## Description
The Completist Audit (2026-01-26) identified a critical deployment failure regarding the startup launcher feature.

### Issue
The files `src/js/startup-launcher.js` and `src/css/startup-launcher.css` are referenced in the HTML header (configured via `_quarto.yml`) but are **not** present in the `docs/` build output.

*   **Expected:** `https://affinedrift.com/js/startup-launcher.js` and `/css/startup-launcher.css` should exist.
*   **Actual:** These files return 404 Not Found on the live site (and are missing from `docs/`).
*   **Impact:** The splash screen feature fails to load, potentially leaving the user staring at a blank screen or a broken UI during the initial load, and generating console errors.

### Root Cause
These files are not explicitly listed in the `resources` section of `_quarto.yml`, so Quarto does not copy them to the output directory during the build process.

## Required Actions
- [ ] Update `_quarto.yml` to include `src/js/startup-launcher.js` and `src/css/startup-launcher.css` (or the directory `src/js/` and `src/css/`) in the `resources` list.
- [ ] Re-run the build and verify that `docs/js/startup-launcher.js` and `docs/css/startup-launcher.css` exist.
