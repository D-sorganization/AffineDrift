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

## 2025-02-19 - QuerySelectorAttribute vs Live Collection Iteration
**Learning:** Selecting elements with specific attributes via `document.querySelectorAll('img[loading="lazy"]')` requires a full DOM scan and parsing of the selector. It's often faster to iterate over a live collection like `document.images` and check the attribute manually (`img.getAttribute("loading") === "lazy"`).
**Action:** When searching for global elements like forms, images, or links that also require specific attributes, iterate over the built-in HTMLCollections and do manual filtering instead of relying on complex `querySelectorAll` selectors.

## 2025-02-19 - QuerySelector vs Live Collection Iteration for Tags
**Learning:** `document.querySelectorAll("tag")` requires a full DOM scan and parsing of the selector. It's often faster to iterate over a live collection like `document.getElementsByTagName("tag")` which is O(1) time complexity.
**Action:** When searching for global elements like standard tags (`nav`, `aside`, `main`, `textarea`, `pre`, `section`), always prefer `document.getElementsByTagName` over `document.querySelectorAll` combined with a `for...of` loop.

## 2025-10-28 - DOMTokenList vs String Manipulation
**Learning:** Manually manipulating space-separated attributes (like `rel` or `class`) using `.split(" ")` and `.join(" ")` in loops creates unnecessary arrays and string copies, causing garbage collection overhead. Using `.split("/").pop()` on URLs is similarly wasteful compared to `substring()`.
**Action:** Always use native `DOMTokenList` APIs (like `element.classList` or `element.relList`) to add, remove, or toggle tokens directly without JS memory allocation. Use `substring(lastIndexOf("/"))` for simple path extractions.

## 2025-02-19 - Safe DOM Iteration with Live Collections
**Learning:** When iterating over live HTMLCollections (e.g., `document.getElementsByTagName()`) to optimize DOM queries, changing attributes like `aria-label` is generally safe as it doesn't mutate the DOM structure or the collection itself (unlike wrapping elements or changing classes used in `getElementsByClassName`). Reusing collections for subsequent loops is also highly efficient.
**Action:** When migrating from `querySelectorAll` to live collections, evaluate whether the loop body alters the criteria of the collection. If it only modifies independent attributes, it is perfectly safe to iterate directly using `for...of` without `Array.from()`.

## 2025-02-21 - QuerySelector with Complex CSS on Links vs Live Collection Iteration
**Learning:** Complex CSS selectors on links like `document.querySelectorAll('.navbar-nav a.nav-link[href^="#"]')` or `document.querySelectorAll('.navbar-nav a[href^="https://github.com"]')` can be extremely slow on large pages. Iterating over `document.links` and checking `href` and `classList` is much faster.
**Action:** Replace `querySelectorAll` with iteration over `document.links` for operations that search for links with specific attributes or classes.

## 2025-02-19 - QuerySelector Descendant Check vs HTMLCollection
**Learning:** Checking for specific descendants (like images or SVGs inside a link) using `element.querySelector("img, svg")` requires parsing a CSS selector and traversing the subtree. Using `element.getElementsByTagName("img").length` is significantly faster as it utilizes live, cached collections.
**Action:** When replacing expensive CSS selectors within descendant checks, prefer direct tag lookups using `getElementsByTagName()` and evaluating the `.length` property to avoid the overhead of parsing CSS selectors for every iterated element.
