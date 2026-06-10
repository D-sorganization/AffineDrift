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

## 2026-04-02 - Icon-only button accessibility with dynamic state
**Learning:** Hardcoding generic `aria-label`s on stateful icon-only buttons (like dark mode toggles) provides a poor experience, as screen readers read the generic label followed by the emoji character (e.g., "Toggle dark mode, Sun"). Furthermore, it doesn't clearly convey the *action* that will happen.
**Action:** For stateful icon-only buttons, dynamically update the `aria-label` to explicitly describe the action ("Switch to light mode") and wrap the visual emoji/icon in `<span aria-hidden="true">` so it's ignored by screen readers.

## 2024-04-03 - Accessible UI Status Updates
**Learning:** When dynamic UI elements like status containers update text content (e.g., "Saved", "Cleared"), screen readers will not announce these changes by default, leaving users unaware of the outcome of their actions.
**Action:** Ensure that status container elements include `aria-live="polite"` and `aria-atomic="true"` to notify screen readers of content changes gracefully.
## 2024-04-05 - Auto-Growing Textareas Missing Resize Constraints
**Learning:** While calculating and applying `scrollHeight` creates a dynamic auto-growing textarea, failing to hide the native resize handle (`resize: none`) and scrollbar (`overflow: hidden`) before the calculation can result in user-conflict (where manual resizing fights the JS logic) and visual jitter.
**Action:** When initializing auto-growing textareas, always assert `style.resize = "none"` and `style.overflow = "hidden"` on the element prior to applying dynamic height event listeners.

## 2026-04-06 - Alt Text Fallback for Modal Images
**Learning:** When images are promoted to a modal view (lightbox), relying solely on `<figcaption>` can leave images that only use `alt` attributes without visual context or descriptive text in the modal state.
**Action:** When promoting an image to a modal view, if no `<figcaption>` is present, fall back to extracting and displaying the image's `alt` text to preserve contextual information for all users.

## 2026-04-11 - Actionable Empty States
**Learning:** For optimal UX in search or filter features, empty states ('no results') should not be dead ends.
**Action:** Always provide an actionable, one-click reset mechanism (e.g., a 'Clear Search' button) that clears the query and restores focus to the input field.

## 2026-04-12 - Native Tooltips for Icon-Only Buttons
**Learning:** While icon-only buttons rely on aria-label for screen readers, they lack native on-hover tooltips for sighted users without a title attribute, creating a gap between accessibility and standard usability.
**Action:** Always pair aria-label with a matching title attribute on interactive icon-only elements to ensure sighted mouse users receive visual hints.

## 2026-04-29 - MathJax Overflow on Mobile Devices
**Learning:** Display math equations (MathJax) often exceed standard viewport widths on mobile devices. Without explicit container constraints, they cause horizontal page scrolling, breaking responsive layout and causing frustration for touch users.
**Action:** Always wrap or target `.math.display` and `mjx-container[display="true"]` with `overflow-x: auto; max-width: 100%; -webkit-overflow-scrolling: touch;` to ensure they scroll internally without breaking the main viewport layout.

## 2026-06-01 - Focus Management for Sidebar Detail Views
**Learning:** When a list item dynamically updates a separate details pane (like a sidebar), screen reader users are left unaware of the change unless focus is explicitly moved to the new content.
**Action:** Add `tabindex="-1"` and call `.focus({ preventScroll: true })` on the details container after updating its content, cleaning up the `tabindex` on blur.

## 2026-06-02 - Accessible Dynamic Empty States
**Learning:** When dynamic UI areas like history sidebars become empty (e.g., initially loaded without data or cleared), screen readers must be notified.
**Action:** Always provide `role="status"` and `aria-live="polite"` on dynamically rendered empty state elements so that the absence of data is clearly communicated to assistive technologies.
## 2026-05-18 - Dynamic ARIA Labels on Collapsible Components
**Learning:** Static labels on collapsible components (like accordions) fail to communicate their current state and available action. Hardcoding `aria-expanded` is insufficient if the base label doesn't update.
**Action:** Always dynamically update both `aria-label` and native `title` tooltips on collapsible headers (e.g., "Expand [Title]" vs "Collapse [Title]") based on their `aria-expanded` state.

## 2026-05-19 - Improved collapsible sidebar accessibility
**Learning:** In the home page collapsible sidebar menu, the toggle buttons (`.sidebar-section-toggle`) only updated `aria-expanded` attributes without updating the `aria-label` or `title` to explicitly indicate the new action ("Expand" or "Collapse") to screen readers. This created an accessibility issue where users are not properly informed of what clicking the button will do next based on the current state.
**Action:** Update both the `aria-label` and `title` attributes dynamically when the sidebar section toggle state changes to explicitly read "Expand [Section Name]" or "Collapse [Section Name]" based on the new `aria-expanded` state.

## 2026-06-03 - Dynamic ARIA Labels on Collapsible Components (Laymans & Critics)
**Learning:** While the newly refactored `laymans-terms` and `critics-corner` elements correctly set `aria-expanded`, their `aria-label` and `title` attributes were not dynamically updated. Sighted users did not receive native tooltips about what the expand/collapse icon does, and screen readers did not receive context about the upcoming action.
**Action:** Dynamically update both `aria-label` and `title` on these components based on their `aria-expanded` state, explicitly declaring "Expand [Title]" or "Collapse [Title]".

## 2024-05-24 - Native Tooltips for Mobile Navbar Toggle
**Learning:** Mobile menu toggle buttons (hamburger icons) often rely solely on `aria-label` for screen readers but lack a native tooltip (`title`) for sighted users using hover (e.g., zoomed desktop or pen users).
**Action:** Always pair `aria-label` with a corresponding `title` attribute on `.navbar-toggler` to ensure all users receive context about the menu's state and action.
## 2026-05-26 - Add title attributes to icon-only buttons
**Learning:** Icon-only buttons with `aria-label` are accessible to screen readers, but sighted mouse users lack context. Adding `title` attributes provides native tooltips, clarifying the action before clicking.
**Action:** Always pair `aria-label` with a `title` attribute on custom icon-only buttons to ensure both accessibility and visual UX.

## 2026-05-26 - Dynamic ARIA Labels on Workspace Toggle
**Learning:** Similar to other collapsible components like sidebars and accordions, floating toggle buttons like the Project Notes workspace toggle need dynamic `aria-label` and `title` attributes based on their expanded state so screen readers and mouse users understand the upcoming action.
**Action:** Dynamically update both `aria-label` and `title` on the Project Notes toggle button explicitly declaring "Expand Project Notes" or "Collapse Project Notes" based on its state.
## 2024-06-03 - Native Tooltips for Icon-Only and Missing Native Tooltips
**Learning:** While icon-only buttons rely on aria-label for screen readers, they lack native on-hover tooltips for sighted users without a title attribute, creating a gap between accessibility and standard usability. Many standard buttons across the app also lack them, hiding explicit functionality from hovering users.
**Action:** Always pair aria-label with a matching title attribute on interactive icon-only elements, and generic buttons, to ensure sighted mouse users receive visual hints.
## 2026-06-03 - Dynamic Aria Labels and Titles for Collapsible Elements
**Learning:** Collapsible elements that lack dynamic `aria-label` or `title` values provide inadequate feedback to screen reader users, confusing their context.
**Action:** Always update both the `aria-label` and `title` dynamically alongside `aria-expanded` state changes to ensure full accessibility support and clearer visual tooltips.
## 2026-06-10 - Native Tooltips for Social Links
**Learning:** Sighted mouse users lack context for icon-only social links that rely solely on `aria-label`. Adding `title` attributes provides native tooltips, clarifying the destination.
**Action:** Always pair `aria-label` with a `title` attribute on icon-only social links to ensure both accessibility and visual UX.
