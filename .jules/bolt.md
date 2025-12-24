## 2025-02-18 - First Journal Entry
**Learning:** Initial setup of the journal.
**Action:** Will add entries as I discover performance insights.

## 2025-02-18 - Scroll Handler Optimization
**Learning:** The `script.js` scroll handler was performing synchronous layout (reading `scrollHeight`) inside the `requestAnimationFrame` loop, potentially causing layout thrashing.
**Action:** Implemented a caching strategy using `ResizeObserver` to separate geometry reads from the scroll loop.

## 2025-02-18 - Batch DOM Insertion with DocumentFragment
**Learning:** Several functions in `script.js` (`generateTableOfContents`, `updateHistorySidebar`, `initArticleHistory`) were appending elements to the DOM in a loop. While modern browsers are efficient, this technically triggers multiple reflows/repaints.
**Action:** Refactored these functions to build the DOM subtree in a `DocumentFragment` first, then append the entire fragment to the DOM in a single operation. This ensures only one reflow per list generation.

## 2025-02-18 - Template Caching in Build Script
**Learning:** `build-html.py` was reading the template file from disk for every single page generation (35+ times). While the OS file cache mitigates this, it's an unnecessary system call overhead.
**Action:** Modified the script to read the template into memory once at startup and pass the string content to the generation function. This reduces file I/O operations from O(N) to O(1).
