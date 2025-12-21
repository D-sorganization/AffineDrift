# Bolt's Journal

## 2025-02-18 - First Journal Entry
**Learning:** Initial setup of the journal.
**Action:** Will add entries as I discover performance insights.

## 2025-02-18 - Scroll Handler Optimization
**Learning:** The `script.js` scroll handler was performing synchronous layout (reading `scrollHeight`) inside the `requestAnimationFrame` loop, potentially causing layout thrashing.
**Action:** Implemented a caching strategy using `ResizeObserver` to separate geometry reads from the scroll loop.
