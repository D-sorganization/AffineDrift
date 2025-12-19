## 2025-05-19 - Layout Thrashing in Animation Loop
**Learning:** Interleaving DOM reads (getBoundingClientRect) and writes (style updates) forces the browser to recalculate layout synchronously for every iteration.
**Action:** Batch DOM reads and writes into separate phases. Read all necessary metrics first, then apply all style changes. This reduces N reflows to 1 reflow.
