## 2024-05-23 - Property Access vs Constructor Overhead
**Learning:** In hot loops or large DOM queries (like iterating hundreds of links), accessing `link.hostname` is significantly faster than `new URL(link.href)`.
**Action:** When working with anchor elements, always prefer `HTMLHyperlinkElementUtils` properties (`hostname`, `pathname`, etc.) over creating new `URL` objects.

## 2024-05-24 - String.split() Memory Overhead
**Learning:** `String.prototype.split` allocates an array of new strings, which is O(N) memory. For large texts (like articles), this creates unnecessary GC pressure just to count items.
**Action:** Use a manual character loop or iterator for counting logic to maintain O(1) memory usage.

## 2025-02-18 - Live Collections vs QuerySelector
**Learning:** `document.images` and `document.links` provide O(1) access to live HTMLCollections, avoiding the overhead of `querySelectorAll` (O(N) traversal) for global element iteration.
**Action:** Use native collections for global iterators (images, links, forms) instead of selectors when possible.

## 2025-10-26 - MathJax Lazy Typesetting
**Learning:** For long technical articles with hundreds of equations, default MathJax typesetting blocks the main thread. The `ui/lazy` extension significantly improves TTI by only typesetting equations in the viewport.
**Action:** Always enable `ui/lazy` in MathJax v3 configuration for content-heavy pages.

## 2025-10-27 - Streamlit Matplotlib Caching
**Learning:** Matplotlib figure generation is a significant bottleneck in interactive Streamlit apps. Re-creating `Figure` objects on every script rerun causes noticeable lag.
**Action:** Use `@st.cache_resource` (with `max_entries` limit) to cache functions that return Matplotlib `Figure` objects. This keeps the live figure object in memory and avoids expensive reconstruction, dramatically improving responsiveness.

## 2026-03-30 - Scroll Event Listener Consolidation
**Learning:** Multiple separate `window.addEventListener("scroll", ...)` calls performing identical or near-identical geometry checks (like calculating `window.scrollY > SCROLL_THRESHOLD`) cause redundant DOM thrashing. In this codebase, the "Export to PDF" button used a debounced scroll listener while the "Back to Top" button used an optimized `requestAnimationFrame` loop.
**Action:** When adding scroll-dependent UI elements (like sticky headers or floating buttons), always merge their visibility logic into a single, shared `requestAnimationFrame` tracked scroll loop rather than attaching isolated event listeners.
