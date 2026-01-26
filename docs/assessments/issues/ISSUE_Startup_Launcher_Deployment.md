---
title: Critical Deployment Failure - Startup Launcher
labels: incomplete-implementation, critical, deployment
assignee: unassigned
status: open
---

# Critical Deployment Failure: Startup Launcher Script Missing

## Description
The file `src/js/startup-launcher.js` and its corresponding CSS `src/css/startup-launcher.css` are implemented in the source tree and referenced in `_quarto.yml` via `include-in-header`. However, they are not listed in the `resources` section of `_quarto.yml` and are not being copied to the build output (`docs/`).

## Impact
Users visiting the site experience a 404 error for the startup script, preventing the splash screen from loading and potentially causing console errors that degrade the user experience.

## Remediation
- Add `src/js/startup-launcher.js` to the `resources` list in `_quarto.yml`.
- Verify `src/css/startup-launcher.css` is correctly handled by Quarto's CSS processing or add it to resources if needed.
- Verify the build output contains `docs/js/startup-launcher.js`.
