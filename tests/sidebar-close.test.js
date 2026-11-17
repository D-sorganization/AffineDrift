const { initSidebarClose } = require('../js/navigation.js');

/** Quarto's docked sidebar and its phone toggle, as rendered on article pages. */
const SIDEBAR_HTML = `
  <button class="quarto-btn-toggle" aria-controls="quarto-sidebar"></button>
  <nav id="quarto-sidebar" class="sidebar collapse">
    <div class="sidebar-menu-container"></div>
  </nav>
`;

describe('sidebar close button (issue #5325)', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  test('adds a labelled close button as the first child of the sidebar', () => {
    document.body.innerHTML = SIDEBAR_HTML;

    initSidebarClose();

    const button = document.querySelector('#quarto-sidebar').firstElementChild;
    expect(button.matches('button.sidebar-close')).toBe(true);
    expect(button.type).toBe('button');
    expect(button.getAttribute('aria-label')).toBe('Close navigation');
    expect(button.getAttribute('aria-controls')).toBe('quarto-sidebar');
  });

  test('closes through the Quarto toggle and returns focus to it', () => {
    document.body.innerHTML = SIDEBAR_HTML;
    const toggle = document.querySelector('.quarto-btn-toggle');
    const onToggle = jest.fn();
    toggle.addEventListener('click', onToggle);

    initSidebarClose();
    document.querySelector('.sidebar-close').click();

    expect(onToggle).toHaveBeenCalledTimes(1);
    expect(document.activeElement).toBe(toggle);
  });

  test('is idempotent', () => {
    document.body.innerHTML = SIDEBAR_HTML;

    initSidebarClose();
    initSidebarClose();

    expect(document.querySelectorAll('.sidebar-close')).toHaveLength(1);
  });

  test('does nothing on pages without a docked sidebar toggle', () => {
    document.body.innerHTML = '<nav id="quarto-sidebar"></nav>';

    initSidebarClose();

    expect(document.querySelectorAll('.sidebar-close')).toHaveLength(0);
  });
});
