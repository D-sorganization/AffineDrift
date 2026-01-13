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
