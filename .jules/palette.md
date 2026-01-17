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
