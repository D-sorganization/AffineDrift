# Bolt's Journal

## 2025-05-20 - [Initial Setup]
**Learning:** This project uses a custom Python script (`build-html.py`) to generate HTML from `.qmd` files, using `docs/articles.html` as a template. This means global optimizations must be applied to `docs/articles.html`.
**Action:** Always check `docs/articles.html` and `build-html.py` when making site-wide changes.

## 2025-05-20 - [Scroll Performance Optimization]
**Learning:** The legacy `script.js` had multiple `scroll` event listeners attached to the window, some debounced and some not (e.g., Back to Top). Furthermore, active section highlighting (TOC and Navbar) was causing layout thrashing by querying `offsetTop` and `getBoundingClientRect` inside loops on every scroll event.
**Action:** Implemented a `SectionGeometryCache` to pre-calculate element positions (updating only on resize) and a centralized `ScrollManager` that uses `requestAnimationFrame` to handle visual updates. This converts O(N) reflow operations per scroll into O(N) memory lookups.
