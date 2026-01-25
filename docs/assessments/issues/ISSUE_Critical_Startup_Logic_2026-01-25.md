---
title: Critical Startup Logic Bugs in startup-launcher.js
labels: incomplete-implementation, critical, javascript, bug
assignee: unassigned
---

## Description
The `src/js/startup-launcher.js` script contains logic bugs that prevent the application from correctly signaling its ready state and initializing UI elements.

### Issues Identified
1.  **Infinite Loading State**: `state.isReady` is initialized to `false` and **never updated to `true`**.
    *   **Impact:** `window.AffineDriftStartup.isReady()` always returns `false`. Any dependent scripts waiting for this flag will hang indefinitely.
2.  **Progress Bar Initialization Failure**:
    *   **Detail:** The script attempts to query `state.progressElement` immediately when running in the `<head>`, before the body or the splash screen exists in the DOM.
    *   **Impact:** `state.progressElement` remains `null`, causing the progress bar visualization to fail (it never updates).

## Required Actions
- [ ] Update `startup-launcher.js` to set `state.isReady = true` when loading is complete.
- [ ] Refactor initialization logic to ensure `state.progressElement` is queried only after the splash screen has been successfully injected into the DOM.
