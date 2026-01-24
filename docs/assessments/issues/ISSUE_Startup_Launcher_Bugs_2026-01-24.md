---
title: Critical Logic Bugs in Startup Launcher
labels: incomplete-implementation, critical, bug
---

# Critical Logic Bugs in Startup Launcher

The Completist Audit (2026-01-24) identified two critical logic bugs in `src/js/startup-launcher.js` that compromise the startup sequence and public API.

## 1. `isReady` State Never Set
**Severity:** Critical
**Description:** The internal state variable `state.isReady` is initialized to `false` but is never updated to `true` anywhere in the codebase.
**Impact:** The public API `window.AffineDriftStartup.isReady()` essentially always returns `false`. Any external scripts or integration tests waiting for this signal will hang indefinitely or fail.
**Fix Required:** Update `state.isReady = true` inside the `revealPage()` function (or wherever the transition to "ready" is finalized).

## 2. Progress Bar Initialization Failure
**Severity:** High
**Description:** The script attempts to get the progress bar element (`document.getElementById('ad-splash-progress-bar')`) immediately upon initialization. However, if the script is loaded in the `<head>` (as configured in `service-worker.js`), `document.body` is null, so the splash screen creation is deferred to `DOMContentLoaded`.
**Impact:** `state.progressElement` is assigned `null` because the element does not exist in the DOM at the time of assignment. Consequently, the progress bar visual width is never updated during the loading sequence.
**Fix Required:** Move the assignment of `state.progressElement` to be inside the `createSplashScreen` function *after* the element has been successfully inserted into the DOM (inside the `DOMContentLoaded` callback if necessary).
