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
    function createSunSvg() {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("width", "18"); svg.setAttribute("height", "18");
      svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none");
      svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "2");
      svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round");
      svg.setAttribute("aria-hidden", "true");

      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", "12"); c.setAttribute("cy", "12"); c.setAttribute("r", "5");
      svg.appendChild(c);

      const lines = [
        ["12", "1", "12", "3"], ["12", "21", "12", "23"],
        ["4.22", "4.22", "5.64", "5.64"], ["18.36", "18.36", "19.78", "19.78"],
        ["1", "12", "3", "12"], ["21", "12", "23", "12"],
        ["4.22", "19.78", "5.64", "18.36"], ["18.36", "5.64", "19.78", "4.22"]
      ];
      for (const pts of lines) {
        const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
        l.setAttribute("x1", pts[0]); l.setAttribute("y1", pts[1]);
        l.setAttribute("x2", pts[2]); l.setAttribute("y2", pts[3]);
        svg.appendChild(l);
      }
      return svg;
    }

    function createMoonSvg() {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("width", "18"); svg.setAttribute("height", "18");
      svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none");
      svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "2");
      svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round");
      svg.setAttribute("aria-hidden", "true");

      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z");
      svg.appendChild(p);
      return svg;
    }

    function updateBtn(theme) {
      btn.textContent = "";
      btn.appendChild(theme === 'dark' ? createSunSvg() : createMoonSvg());
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
