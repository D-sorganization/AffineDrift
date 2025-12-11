## 2025-12-10 - Back to Top Accessibility
**Learning:** Long scrolling pages without a "Back to Top" mechanism create friction for keyboard and mouse users alike. Implementing this requires handling visibility state carefully to avoid focus traps on invisible elements.
**Action:** When adding floating action buttons, ensure they are removed from the accessibility tree (via `visibility: hidden` or `display: none`) when not visually present.

## 2025-12-11 - Code Copy Discoverability
**Learning:** For technical documentation, the ability to copy code snippets is expected. Implementing this via client-side injection allows for consistent behavior across different content generation sources (Quarto vs custom HTML) without modifying the build pipeline.
**Action:** Use `navigator.clipboard` with visual feedback (e.g., "Copied!" state) to confirm the action, and ensure the button is keyboard accessible.
