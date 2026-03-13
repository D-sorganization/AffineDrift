(function () {
  const STORAGE_KEY = 'affinedrift-theme';
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
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
    btn.id = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.title = 'Toggle dark/light mode';
    btn.innerHTML = '☀️';

    function updateBtn(theme) {
      btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
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
