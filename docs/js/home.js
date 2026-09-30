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

    const titleEl = button.getElementsByTagName("h3")[0];
    const titleText = titleEl ? titleEl.textContent.trim() : "section";
    const actionText = expanded ? "Collapse" : "Expand";
    button.setAttribute("aria-label", `${actionText} ${titleText}`);
    button.setAttribute("title", `${actionText} ${titleText}`);
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

  // Mobile menu handling is owned solely by the unified navbar implementation
  // in js/navigation.js::initNavbarCollapse() (Quarto's .navbar-toggler /
  // #navbarCollapse). The old no-op initMobileMenu() and its markup were
  // removed (issue #3327, closes #2955).

  function init() {
    initCollapsibleSections();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
