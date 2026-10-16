# F-AD-025

**E2E self-hosted assertion attaches its request listener after page load**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | tests | high | S | proposed |

**Locations:** `tests/e2e/ztcf-explorer.spec.js:26`, `tests/e2e/ztcf-explorer.spec.js:39`, `tests/e2e/ztcf-explorer.spec.js:47`

## Finding

- Severity: Low  - Category: tests
- Confidence: high
- Location: tests/e2e/ztcf-explorer.spec.js:26-47
- Evidence: `await page.goto(route, …)` at line 26; `page.on("request", …)` registered at line 39;
  `expect(crossOrigin).toEqual([])` at 47 only sees requests made after typing into `#ztx-step`.
- Failure scenario: a CDN MathJax or font request on initial load is invisible to the test; the class-A "no
  cross-origin requests" claim in the comment is not what is tested.
- Proposed change: register the listener before `goto`, filter to requests whose initiator is the widget script.
- Effort: S

## Draft Pull Request

**Title:** `test(e2e): register self-hosted request listener before page.goto`

### Why This Matters (The Pitch)

The "stays self-hosted" test attaches its request listener after the page has loaded, so a CDN request on initial load is invisible. Register the listener before `goto` and filter to the widget's requests.

### Proposed PR Body

## Problem
`tests/e2e/ztcf-explorer.spec.js:26-47`: `page.goto` at line 26, `page.on("request", ...)` at line 39, and the assertion at 47 only sees requests after typing into `#ztx-step`.

## Change
- [ ] Register the listener before `goto`
- [ ] Filter to requests whose initiator is the widget script

## Verification
Run the spec; temporarily add a cross-origin request on load and confirm the test fails.

## Risk and Rollback
Test-only change; revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-025

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
