# F-AD-010

**Service worker cache-first for non-precached assets; SVG/JSON/PDF not in the cache-busting hash**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | correctness | high | S | proposed |

**Locations:** `service-worker.js:142`, `service-worker.js:157`, `scripts/update_sw_cache_version.py:33`, `scripts/update_sw_cache_version.py:45`

## Finding

- Severity: Medium  - Category: correctness (stale research content)
- Confidence: high
- Location: service-worker.js:140-160; scripts/update_sw_cache_version.py:33-48
- Evidence:
  ```js
  // service-worker.js:142  "Static subresources (CSS/JS/images/fonts) are content-hashed by CACHE_NAME"
  event.respondWith(cacheFirst(event.request, {...}))
  ```
  but `HASH_SOURCES`/`HASH_GLOBS` (update_sw_cache_version.py:33-48) cover only `js/*.js`, `css/**/*.css` and
  two root files. SVG figures (`articles/figures/**`), `data/*.json` fetched by widgets, and PDFs are served
  cache-first with stale-while-revalidate → a returning reader sees the previous deploy's figure until the
  *second* load.
- Failure scenario: you fix F-AD-001, deploy, and a reviewer who visited last week still sees the hand-drawn figure.
- Why a newer engineer misses this: the comment at line 142 asserts a property the hash script does not provide.
- Proposed change: either extend `HASH_GLOBS` to `articles/**/*.svg`, `data/**/*.json`, `**/*.png`, or route
  those types through `networkFirstWithTimeout` like navigations; or (cleanest) emit content-hashed filenames at
  render time and keep cache-first.
- Verification: Playwright offline.spec: deploy a changed SVG, reload once, assert new bytes.
- Effort: S

## Draft Pull Request

**Title:** `fix(sw): hash figures, data JSON and PDFs in cache version`

### Why This Matters (The Pitch)

A reviewer who visited the site last week can still be looking at last week's figure. The service worker serves non-precached assets cache-first, and a comment claims images are content-hashed, but the hash script covers only `js/*.js`, `css/**/*.css` and two root files. SVG figures, widget data JSON and PDFs are served stale-while-revalidate, so a returning reader sees the previous deploy until the second load. That matters directly for F-AD-001: you fix the hand-drawn figures, deploy, and the one person you most want to see the fix does not. The change is small and the stakes are reader-facing: extend `HASH_GLOBS` to include `articles/**/*.svg`, `data/**/*.json` and `**/*.png`, or route those types through `networkFirstWithTimeout`. The comment at line 142 then becomes true.

### Proposed PR Body

## Problem
`service-worker.js:140-160` serves static subresources cache-first, claiming they are content-hashed by `CACHE_NAME`, but `scripts/update_sw_cache_version.py:33-48` hashes only `js/*.js`, `css/**/*.css` and two root files. SVG figures, `data/*.json` and PDFs are not covered.

## Change
- [ ] Extend `HASH_GLOBS` to `articles/**/*.svg`, `data/**/*.json`, `**/*.png`, or route those types through `networkFirstWithTimeout`
- [ ] Correct the comment at `service-worker.js:142` to match behavior

## Verification
Playwright offline.spec: deploy a changed SVG, reload once, assert new bytes.

## Risk and Rollback
Cache version will change on more files, so more deploys invalidate the cache; revert the commit to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-010


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
