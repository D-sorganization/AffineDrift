/**
 * UX slice 4 (#5167): header and navigation behaviour.
 * Presentation/ARIA only; no article content is exercised here.
 */

describe('navbar ARIA (#5167)', () => {
  let initNavbarCollapse;

  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = `
      <header id="quarto-header">
        <nav class="navbar">
          <div class="navbar-container">
            <button class="navbar-toggler" role="menu" aria-label="Toggle navigation"></button>
            <div id="navbarCollapse" class="collapse navbar-collapse">
              <ul class="navbar-nav"><li><a class="nav-link" href="/a.html">A</a></li></ul>
            </div>
          </div>
        </nav>
      </header>`;
    ({ initNavbarCollapse } = require('../js/navigation.js'));
  });

  test('gives the navbar landmark a name', () => {
    initNavbarCollapse();
    expect(document.querySelector('nav.navbar').getAttribute('aria-label')).toBe(
      'Main navigation'
    );
  });

  test('does not nest a second navigation landmark in the collapse', () => {
    initNavbarCollapse();
    const collapse = document.getElementById('navbarCollapse');
    expect(collapse.getAttribute('role')).toBeNull();
    expect(collapse.getAttribute('aria-label')).toBeNull();
  });

  test('removes the invalid menu role from the toggler', () => {
    initNavbarCollapse();
    expect(document.querySelector('.navbar-toggler').hasAttribute('role')).toBe(false);
  });

  test('keeps an author-supplied navbar label', () => {
    document.querySelector('nav.navbar').setAttribute('aria-label', 'Primary');
    initNavbarCollapse();
    expect(document.querySelector('nav.navbar').getAttribute('aria-label')).toBe('Primary');
  });

  test('does not throw when the navbar is absent', () => {
    document.body.innerHTML = '';
    expect(() => initNavbarCollapse()).not.toThrow();
  });
});

describe('landmark uniqueness (#5167)', () => {
  let initAriaLabels;

  beforeEach(() => {
    jest.resetModules();
    ({ initAriaLabels } = require('../js/accessibility.js'));
  });

  test('display equations are focusable scroll areas, not repeated regions', () => {
    document.body.innerHTML = `
      <span class="math display">x=1</span>
      <span class="math display">y=2</span>`;
    initAriaLabels();
    for (const eq of document.querySelectorAll('.math.display')) {
      expect(eq.getAttribute('tabindex')).toBe('0');
      expect(eq.hasAttribute('role')).toBe(false);
      expect(eq.hasAttribute('aria-label')).toBe(false);
    }
  });

  test('unlabelled navs never share an accessible name', () => {
    document.body.innerHTML = '<nav></nav><nav></nav><nav></nav>';
    initAriaLabels();
    const labels = [...document.getElementsByTagName('nav')].map((n) =>
      n.getAttribute('aria-label')
    );
    expect(new Set(labels).size).toBe(labels.length);
    expect(labels.every(Boolean)).toBe(true);
  });
});
