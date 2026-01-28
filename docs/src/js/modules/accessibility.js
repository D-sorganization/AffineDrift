/**
 * Accessibility Module
 * Handles ARIA labels, keyboard navigation, and accessibility features
 */

/**
 * Initialize ARIA labels for all interactive elements
 */
export function initAriaLabels() {
  // Table of Contents
  const toc = document.getElementById('TOC');
  if (toc && !toc.getAttribute('aria-label')) {
    toc.setAttribute('aria-label', 'Table of Contents');
  }

  // Sidebars
  const sidebars = document.querySelectorAll('.sidebar');
  sidebars.forEach((sidebar, index) => {
    if (!sidebar.getAttribute('aria-label')) {
      sidebar.setAttribute('aria-label', `Sidebar navigation ${index + 1}`);
    }
  });

  // Main content
  const main = document.querySelector('main, [role="main"]');
  if (main && !main.getAttribute('role')) {
    main.setAttribute('role', 'main');
  }

  // Navigation elements
  const navElements = document.querySelectorAll('nav');
  navElements.forEach((nav) => {
    if (!nav.getAttribute('aria-label') && !nav.getAttribute('role')) {
      nav.setAttribute('role', 'navigation');
    }
  });

  // Search inputs
  const searchInputs = document.querySelectorAll('input[type="search"]');
  searchInputs.forEach((input) => {
    if (!input.getAttribute('aria-label')) {
      input.setAttribute('aria-label', 'Search');
    }
  });

  // Buttons without labels
  const buttons = document.querySelectorAll('button:not([aria-label])');
  buttons.forEach((button) => {
    const text = button.textContent.trim();
    if (text && !button.getAttribute('aria-label')) {
      button.setAttribute('aria-label', text);
    }
  });
}

/**
 * Add heading IDs for anchor links
 */
export function addHeadingIds() {
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  const usedIds = new Set();

  headings.forEach((heading) => {
    if (!heading.id) {
      const text = heading.textContent;
      const id = generateUniqueId(text, usedIds);
      heading.id = id;
      usedIds.add(id);
    }
  });
}

/**
 * Setup keyboard navigation
 */
export function setupKeyboardNav() {
  // Escape key to close modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('.modal.show, [role="dialog"][aria-hidden="false"]');
      modals.forEach((modal) => {
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
      });
    }
  });

  // Ctrl/Cmd + K for search
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchButton = document.querySelector('.search-trigger');
      if (searchButton) {
        searchButton.click();
      }
    }
  });
}

// Helper function (would be imported from utils.js in real implementation)
function generateUniqueId(text, usedIds) {
  let baseId = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  
  if (!baseId) baseId = "section";

  let id = baseId;
  let counter = 1;

  const exists = (candidateId) => {
    return usedIds.has(candidateId) || document.getElementById(candidateId) !== null;
  };

  if (!exists(id)) {
    return id;
  }

  while (exists(id) && counter < 100) {
    id = `${baseId}-${counter}`;
    counter++;
  }

  return id;
}
