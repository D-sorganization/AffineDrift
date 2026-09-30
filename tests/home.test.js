/**
 * Tests for js/home.js - collapsible sidebar sections on the homepage.
 */

function setReadyState(value) {
  Object.defineProperty(document, 'readyState', {
    configurable: true,
    writable: true,
    value,
  });
}

function loadHomeModule() {
  require('../js/home.js');
}

describe('home.js collapsible sidebar sections', () => {
  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = '';
  });

  test('initializes a collapsed section on load', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="panel-1" aria-expanded="false">
        <h3>Models</h3>
      </button>
      <div id="panel-1"></div>
    `;
    setReadyState('complete');

    loadHomeModule();

    const button = document.querySelector('.sidebar-section-toggle');
    const panel = document.getElementById('panel-1');
    expect(button.getAttribute('aria-controls')).toBe('panel-1');
    expect(button.getAttribute('aria-expanded')).toBe('false');
    expect(panel.getAttribute('aria-hidden')).toBe('true');
    expect(panel.classList.contains('show')).toBe(false);
    expect(button.getAttribute('aria-label')).toBe('Expand Models');
    expect(button.getAttribute('title')).toBe('Expand Models');
  });

  test('initializes an already-expanded section on load', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="panel-2" aria-expanded="true">
        <h3>Datasets</h3>
      </button>
      <div id="panel-2"></div>
    `;
    setReadyState('complete');

    loadHomeModule();

    const button = document.querySelector('.sidebar-section-toggle');
    const panel = document.getElementById('panel-2');
    expect(panel.classList.contains('show')).toBe(true);
    expect(panel.getAttribute('aria-hidden')).toBe('false');
    expect(button.getAttribute('aria-label')).toBe('Collapse Datasets');
  });

  test('toggles expanded state on click', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="panel-3" aria-expanded="false">
        <h3>Papers</h3>
      </button>
      <div id="panel-3"></div>
    `;
    setReadyState('complete');

    loadHomeModule();

    const button = document.querySelector('.sidebar-section-toggle');
    const panel = document.getElementById('panel-3');

    button.click();
    expect(button.getAttribute('aria-expanded')).toBe('true');
    expect(panel.classList.contains('show')).toBe(true);
    expect(panel.getAttribute('aria-hidden')).toBe('false');
    expect(button.getAttribute('aria-label')).toBe('Collapse Papers');

    button.click();
    expect(button.getAttribute('aria-expanded')).toBe('false');
    expect(panel.classList.contains('show')).toBe(false);
    expect(button.getAttribute('aria-label')).toBe('Expand Papers');
  });

  test('ignores a toggle button with no data-target', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" aria-expanded="false"><h3>Orphan</h3></button>
    `;
    setReadyState('complete');

    expect(() => loadHomeModule()).not.toThrow();
    const button = document.querySelector('.sidebar-section-toggle');
    expect(() => button.click()).not.toThrow();
    expect(button.hasAttribute('aria-controls')).toBe(false);
  });

  test('ignores a toggle button whose target element is missing', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="missing" aria-expanded="false">
        <h3>Ghost</h3>
      </button>
    `;
    setReadyState('complete');

    expect(() => loadHomeModule()).not.toThrow();
  });

  test('defers initialization until DOMContentLoaded when the document is still loading', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="panel-4" aria-expanded="false">
        <h3>Videos</h3>
      </button>
      <div id="panel-4"></div>
    `;
    setReadyState('loading');

    loadHomeModule();

    const button = document.querySelector('.sidebar-section-toggle');
    expect(button.hasAttribute('aria-controls')).toBe(false);

    document.dispatchEvent(new Event('DOMContentLoaded'));
    expect(button.getAttribute('aria-controls')).toBe('panel-4');
  });

  test('initializes immediately when the document is already interactive', () => {
    document.body.innerHTML = `
      <button class="sidebar-section-toggle" data-target="panel-5" aria-expanded="false">
        <h3>Software</h3>
      </button>
      <div id="panel-5"></div>
    `;
    setReadyState('interactive');

    loadHomeModule();

    const button = document.querySelector('.sidebar-section-toggle');
    expect(button.getAttribute('aria-controls')).toBe('panel-5');
  });
});
