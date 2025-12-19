## 2025-12-10 - Back to Top Accessibility
**Learning:** Long scrolling pages without a "Back to Top" mechanism create friction for keyboard and mouse users alike. Implementing this requires handling visibility state carefully to avoid focus traps on invisible elements.
**Action:** When adding floating action buttons, ensure they are removed from the accessibility tree (via `visibility: hidden` or `display: none`) when not visually present.

## 2025-12-11 - Code Copy Discoverability
**Learning:** For technical documentation, the ability to copy code snippets is expected. Implementing this via client-side injection allows for consistent behavior across different content generation sources (Quarto vs custom HTML) without modifying the build pipeline.
**Action:** Use `navigator.clipboard` with visual feedback (e.g., "Copied!" state) to confirm the action, and ensure the button is keyboard accessible.

## 2025-12-12 - Skip Link Injection
**Learning:** For sites using static generators (like Quarto) where the HTML template is hard to modify or shared across many pages, injecting critical accessibility elements like "Skip to Content" links via JavaScript is a valid strategy. It ensures presence on all pages without complex template overrides.
**Action:** When working with generated sites, use `document.body.insertBefore(link, document.body.firstChild)` to inject skip links, ensuring they are the first focusable element.

## 2025-12-13 - Accordion Accessibility
**Learning:** Accordions require explicit programmatic linkage between headers and content panels. Using `aria-controls` and managing `aria-hidden` states ensures screen reader users understand the relationship and state of the content, which visual cues alone don't provide.
**Action:** Ensure all accordion headers have `aria-controls` pointing to the content ID, and synchronize `aria-hidden` on the content with the `aria-expanded` state of the header.

## 2025-05-18 - Nested Path Asset Resolution
**Learning:** Automated site generators (like Quarto) may generate nested pages (e.g., `docs/articles/`) that incorrectly reference root-level assets with relative paths (e.g., `src="script.js"` instead of `../script.js`). This silent failure breaks all JavaScript-dependent UX/accessibility features on those pages.
**Action:** Always verify relative asset paths in generated subdirectories and use post-processing scripts to correct depth-dependent links if the generator lacks configuration for it.
