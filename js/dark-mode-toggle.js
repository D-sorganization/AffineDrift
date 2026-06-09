(function () {
  const STORAGE_KEY = 'affinedrift-theme';
  const root = document.documentElement;

  function applyTheme(theme) {
    // data-theme drives the site's custom CSS variables; data-bs-theme drives
    // Bootstrap 5.3's native dark mode so the navbar, sidebar/TOC, code blocks,
    // and tables recolor too (otherwise the page renders half-dark).
    root.setAttribute('data-theme', theme);
    root.setAttribute('data-bs-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // Apply on load
  applyTheme(getPreferredTheme());

  // Create toggle button
  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'theme-toggle';

    function updateBtn(theme) {
      btn.innerHTML = theme === 'dark'
        ? '<span aria-hidden="true">☀️</span>'
        : '<span aria-hidden="true">🌙</span>';
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    }

    updateBtn(getPreferredTheme());

    btn.addEventListener('click', function () {
      const current = root.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      updateBtn(next);
    });

    // Insert into navbar
    const navbar = document.querySelector('.navbar') || document.querySelector('nav') || document.body;
    navbar.appendChild(btn);
  });

  // Listen for system preference change
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });
})();
