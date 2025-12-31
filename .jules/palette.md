## 2025-12-14 - Focus Visibility on Hidden Interactivity
**Learning:** Interactive elements that are visually hidden until hover (like "Copy" buttons or "Back to Top") create severe accessibility traps for keyboard users if they remain invisible when focused. `opacity: 0` removes visibility but not focusability.
**Action:** Always ensure that any element with `opacity: 0` transitions to `opacity: 1` on `:focus` (not just `:hover`) and includes a clear, high-contrast focus indicator (e.g., `outline`) to orient the user.

## 2025-05-20 - Memory vs. Reality in Stylesheets
**Learning:** I encountered a situation where my memory bank confidently stated that "print styles are included in `styles.css`", but a codebase inspection revealed they were completely missing.
**Action:** Always verify "known facts" from memory against the actual codebase state using `grep` or manual inspection, especially for "invisible" features like print media queries that might be easily lost during refactors.
