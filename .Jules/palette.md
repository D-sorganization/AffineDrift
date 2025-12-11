## 2025-12-10 - Back to Top Accessibility
**Learning:** Long scrolling pages without a "Back to Top" mechanism create friction for keyboard and mouse users alike. Implementing this requires handling visibility state carefully to avoid focus traps on invisible elements.
**Action:** When adding floating action buttons, ensure they are removed from the accessibility tree (via `visibility: hidden` or `display: none`) when not visually present.
