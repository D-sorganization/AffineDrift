## 2025-12-14 - Focus Visibility on Hidden Interactivity
**Learning:** Interactive elements that are visually hidden until hover (like "Copy" buttons or "Back to Top") create severe accessibility traps for keyboard users if they remain invisible when focused. `opacity: 0` removes visibility but not focusability.
**Action:** Always ensure that any element with `opacity: 0` transitions to `opacity: 1` on `:focus` (not just `:hover`) and includes a clear, high-contrast focus indicator (e.g., `outline`) to orient the user.

## 2025-05-20 - Memory vs. Reality in Stylesheets
**Learning:** I encountered a situation where my memory bank confidently stated that "print styles are included in `styles.css`", but a codebase inspection revealed they were completely missing.
**Action:** Always verify "known facts" from memory against the actual codebase state using `grep` or manual inspection, especially for "invisible" features like print media queries that might be easily lost during refactors.

## 2025-06-12 - Re-Implementing Standard Features in Custom Themes
**Learning:** When disabling standard framework features (like Quarto's TOC) to implement custom versions, standard sub-features (like permalink anchors) are often lost. Users expect these "invisible" utilities on documentation sites.
**Action:** When auditing custom implementations of standard patterns (TOCs, navbars), explicitly check for the "micro-features" that usually come for free, such as anchor links, active state tracking, and keyboard shortcuts.

## 2025-06-15 - Focus Management on Scroll Actions
**Learning:** When using JavaScript to scroll the page (like "Back to Top"), simply scrolling visually is insufficient for keyboard users. The focus remains at the trigger point (often the bottom of the page), forcing users to tab backwards through the entire document.
**Action:** Always programmatically move focus to the target area (e.g., `document.body` or a specific heading) when triggering significant scroll actions to synchronize the visual viewport with the keyboard context.

## 2025-12-15 - Scrollable Regions and Accessibility
**Learning:** Adding `overflow: auto` to containers (like tables) makes them responsive but creates a "keyboard trap" if not managed correctly. Keyboard users need to be able to focus the scrollable region (`tabindex="0"`) to scroll it using arrow keys, and screen reader users need a label (`aria-label`/`aria-labelledby`) to know what the region contains.
**Action:** When creating responsive wrappers for content, always add `role="region"`, `tabindex="0"`, and a descriptive label to ensure the scrollable area is discoverable and operable by all users.
