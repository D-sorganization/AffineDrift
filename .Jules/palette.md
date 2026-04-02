## 2024-05-22 - Preserving Context in Modal Views
**Learning:** In scientific interfaces, images often carry critical metadata (captions) that are essential for interpretation. "Zooming in" on the image without carrying the caption over creates a "context loss" where the user sees the detail but loses the explanation.
**Action:** Always ensure that when promoting an element (like an image to a lightbox), its associated descriptor (caption/figcaption) is promoted with it to maintain semantic integrity.

## 2024-05-23 - Focus Trapping in Modals
**Learning:** When opening a modal (like a lightbox), failing to trap focus allows keyboard users to tab "behind" the modal into the main content. This breaks the mental model of a modal dialog and can leave users lost in invisible content.
**Action:** Always implement a focus trap (cycling Tab/Shift+Tab) within any element with `role="dialog"` or `aria-modal="true"`.

## 2025-05-22 - Autocomplete in Mixed Content
**Learning:** Even in Markdown/Quarto-generated sites, raw HTML forms are often necessary for custom interactivity. Forgetting standard `autocomplete` attributes in these "embedded" forms forces users to manually re-type common data (Name, Email), breaking the seamless flow expected even in static content.
**Action:** Audit all raw HTML forms embedded in `.qmd` or `.md` files for missing `autocomplete` attributes, especially for `name` and `email` fields.

## 2026-01-20 - Auto-Growing Textareas
**Learning:** Fixed-height textareas create friction for users writing detailed feedback, forcing them to scroll within a small viewport. This disconnects the user from their content.
**Action:** Implement auto-growing textareas that expand with content using `scrollHeight`, ensuring `resize: none` to prevent conflict and `overflow: hidden` to avoid scrollbar flicker until max-height is reached.

## 2026-03-30 - Added `aria-controls` to interactive expandable UI element.
**Learning:** Found a common pattern for accessible expand/collapse widgets: when an interactive element (like a button) expands or collapses a section, it is crucial to link it with `aria-controls` to the section's `id`. Moreover, managing the visual states of expanded / collapsed via CSS is not enough. The element must also correctly set `aria-expanded="true/false"` on the button and `aria-hidden="true/false"` on the controlled container depending on its state.
**Action:** When adding or auditing collapsible sections across the app (like sidebars, accordions, and dropdown menus), ensure both `aria-controls` is explicitly defined, and state elements `aria-expanded` and `aria-hidden` are actively toggled via JS logic matching the visual appearance.

## 2026-04-01 - Proper Accessible UI States for Sidebars
**Learning:** Collapsible sidebar sections in `home.js` were changing their display visually via CSS classes but lacked full aria accessibility properties linking the toggle to its contents. Without proper connection (`aria-controls`) and visual state synchronization (`aria-hidden`), screen reader users won't know the exact outcome of triggering the element.
**Action:** Always ensure that when writing or refactoring DOM manipulation logic for collapsible elements, `aria-controls` explicitly connects the button to its target `id`, and both `aria-expanded` and `aria-hidden` attributes correctly reflect the toggled state.

## 2025-03-03 - Context for External Links
**Learning:** Automatically adding target="_blank" and visual icons to external links without providing screen-reader-only text causes visually impaired users to lose context when navigating away from the current tab.
**Action:** Always include a visually-hidden (`.sr-only`) text span (e.g., "(opens in a new tab)") alongside or within the link when opening links in new tabs to provide explicit, accessible warnings for screen reader users.
