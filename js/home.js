/**
 * Homepage interaction module.
 * Keeps sidebar/menu behavior out of inline page scripts.
 */
(function () {
  "use strict";

  function isTrue(value) {
    return value === "true";
  }

  function setSectionExpanded(button, expanded) {
    const targetId = button.getAttribute("data-target");
    if (!targetId) return;
    const target = document.getElementById(targetId);
    if (!target) return;

    button.setAttribute("aria-controls", targetId);
    button.setAttribute("aria-expanded", String(expanded));
    target.setAttribute("aria-hidden", String(!expanded));
    target.classList.toggle("show", expanded);
  }

  function initCollapsibleSections() {
    // ⚡ Bolt Optimization: Use getElementsByClassName (O(1) live collection) instead of querySelectorAll (O(N))
    const toggleButtons = document.getElementsByClassName("sidebar-section-toggle");
    for (const button of toggleButtons) {
      setSectionExpanded(button, isTrue(button.getAttribute("aria-expanded")));
      button.addEventListener("click", () => {
        const expanded = isTrue(button.getAttribute("aria-expanded"));
        setSectionExpanded(button, !expanded);
      });
    }
  }

  // setMobileMenuState removed - functionality consolidated to navbar handler

  function initMobileMenu() {
    // CONSOLIDATED: Mobile menu handling moved to unified navbar implementation
    // The navbar-toggler (.navbar-toggler) and navbarCollapse (#navbarCollapse)
    // are now the single source of truth for mobile navigation across all pages.
    //
    // See js/navigation.js::initNavbarCollapse() for the unified implementation
    // that handles Escape key, arrow key navigation, and ARIA attributes.
    //
    // This function is retained for compatibility but does nothing.
    // TODO (Issue #2955): Remove this empty function after confirming no other
    // dependencies exist on it.
  }

  function init() {
    initCollapsibleSections();
    initMobileMenu();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
