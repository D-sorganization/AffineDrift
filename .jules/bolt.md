# Bolt's Journal

## 2025-02-18 - First Journal Entry
**Learning:** Initial setup of the journal.
**Action:** Will add entries as I discover performance insights.

## 2025-02-18 - Scroll Handler Optimization
**Learning:** The `script.js` scroll handler was performing synchronous layout (reading `scrollHeight`) inside the `requestAnimationFrame` loop, potentially causing layout thrashing.
**Action:** Implemented a caching strategy using `ResizeObserver` to separate geometry reads from the scroll loop.

## 2025-02-18 - Batch DOM Insertion with DocumentFragment
**Learning:** Several functions in `script.js` (`generateTableOfContents`, `updateHistorySidebar`, `initArticleHistory`) were appending elements to the DOM in a loop. While modern browsers are efficient, this technically triggers multiple reflows/repaints.
**Action:** Refactored these functions to build the DOM subtree in a `DocumentFragment` first, then append the entire fragment to the DOM in a single operation. This ensures only one reflow per list generation.
