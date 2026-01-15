## 2024-03-24 - Animated Accordion Icon
**Learning:** Adding a simple CSS rotation transform to an accordion icon (transforming '+' to 'x') provides immediate, intuitive feedback for the open/closed state without requiring complex icon swapping logic or additional assets.
**Action:** Use CSS transforms for state indicators whenever possible to keep the DOM clean and reduce JS complexity.

## 2026-02-14 - Inline Copy Action
**Learning:** For contact information like email addresses, a simple "Copy" button provides a necessary fallback for users who avoid default system handlers (like `mailto:`). Using `runWhenIdle` ensures this non-critical enhancement doesn't block the main thread.
**Action:** Always consider system-handler friction and provide inline alternatives (like copy buttons) for data that needs to be transferred to other apps.
