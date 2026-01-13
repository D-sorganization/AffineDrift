## 2024-05-22 - Preserving Context in Modal Views
**Learning:** In scientific interfaces, images often carry critical metadata (captions) that are essential for interpretation. "Zooming in" on the image without carrying the caption over creates a "context loss" where the user sees the detail but loses the explanation.
**Action:** Always ensure that when promoting an element (like an image to a lightbox), its associated descriptor (caption/figcaption) is promoted with it to maintain semantic integrity.

## 2024-05-23 - Focus Trapping in Modals
**Learning:** When opening a modal (like a lightbox), failing to trap focus allows keyboard users to tab "behind" the modal into the main content. This breaks the mental model of a modal dialog and can leave users lost in invisible content.
**Action:** Always implement a focus trap (cycling Tab/Shift+Tab) within any element with `role="dialog"` or `aria-modal="true"`.
