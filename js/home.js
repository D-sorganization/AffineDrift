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
    const toggleButtons = document.querySelectorAll(".sidebar-section-toggle");
    toggleButtons.forEach((button) => {
      setSectionExpanded(button, isTrue(button.getAttribute("aria-expanded")));
      button.addEventListener("click", () => {
        const expanded = isTrue(button.getAttribute("aria-expanded"));
        setSectionExpanded(button, !expanded);
      });
    });
  }

  function setMobileMenuState({ sidebar, overlay, button }, open) {
    sidebar.classList.toggle("open", open);
    overlay.classList.toggle("active", open);
    button.setAttribute("aria-expanded", String(open));
    button.classList.toggle("is-open", open);
    document.body.classList.toggle("home-menu-open", open);
  }

  function initMobileMenu() {
    const button = document.querySelector(".mobile-menu-toggle");
    const sidebar = document.getElementById("home-sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    if (!button || !sidebar || !overlay) return;

    const state = { button, sidebar, overlay };
    setMobileMenuState(state, false);

    button.addEventListener("click", () => {
      const open = !isTrue(button.getAttribute("aria-expanded"));
      setMobileMenuState(state, open);
    });

    overlay.addEventListener("click", () => setMobileMenuState(state, false));

    sidebar.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth <= 768) {
          setMobileMenuState(state, false);
        }
      });
    });
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
