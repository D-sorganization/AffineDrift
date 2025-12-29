## 2025-12-14 - Focus Visibility on Hidden Interactivity
**Learning:** Interactive elements that are visually hidden until hover (like "Copy" buttons or "Back to Top") create severe accessibility traps for keyboard users if they remain invisible when focused. `opacity: 0` removes visibility but not focusability.
**Action:** Always ensure that any element with `opacity: 0` transitions to `opacity: 1` on `:focus` (not just `:hover`) and includes a clear, high-contrast focus indicator (e.g., `outline`) to orient the user.
