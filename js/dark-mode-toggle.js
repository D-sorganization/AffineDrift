(function () {
  const STORAGE_KEY = 'affinedrift-theme';
  const root = document.documentElement;

  function applyTheme(theme, persist) {
    // data-theme drives the site's custom CSS variables; data-bs-theme drives
    // Bootstrap 5.3's native dark mode so the navbar, sidebar/TOC, code blocks,
    // and tables recolor too (otherwise the page renders half-dark).
    root.setAttribute('data-theme', theme);
    root.setAttribute('data-bs-theme', theme);
    // Only persist when the user makes an EXPLICIT choice (clicks the toggle).
    // Persisting the system-derived theme on load would freeze the site on the
    // first-visit theme and permanently disable the prefers-color-scheme
    // listener below, so a user whose OS flips dark<->light at sunset would stay
    // stuck (issue #3333). On load we apply but do not store.
    if (persist) {
      localStorage.setItem(STORAGE_KEY, theme);
    }
  }

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // Apply on load WITHOUT persisting (so system-preference changes keep working).
  applyTheme(getPreferredTheme(), false);

  // Create toggle button
  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'theme-toggle';

    // Inline SVG icons (sun / moon) render consistently across platforms, unlike
    // emoji glyphs whose appearance varies by OS/font (issue #3333).
    const SUN_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    const MOON_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';

    function updateBtn(theme) {
      btn.innerHTML = theme === 'dark' ? SUN_SVG : MOON_SVG;
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    }

    btn._updateBtn = updateBtn; // let the OS-preference listener refresh the icon
    updateBtn(getPreferredTheme());

    btn.addEventListener('click', function () {
      const current = root.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next, true); // explicit user choice -> persist
      updateBtn(next);
    });

    // Insert into navbar
    const navbar = document.querySelector('.navbar') || document.querySelector('nav') || document.body;
    navbar.appendChild(btn);
  });

  // Listen for system preference change. Because load no longer persists, this
  // keeps firing for visitors who have not made an explicit choice.
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(e.matches ? 'dark' : 'light', false);
      const toggle = document.getElementById('theme-toggle');
      if (toggle && typeof toggle._updateBtn === 'function') {
        toggle._updateBtn(e.matches ? 'dark' : 'light');
      }
    }
  });
})();
