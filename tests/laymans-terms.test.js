/**
 * Tests for the shared "In Layman's Terms" component (#4494).
 *
 * The component markup is emitted by scripts/filters/laymans-terms.lua. The
 * test reads the wrapper markup straight from that filter so it exercises the
 * exact HTML every page receives, then drives the toggle in
 * js/ui-components.js (initLaymansTermsToggle).
 */

const fs = require('fs');
const path = require('path');

const FILTER_PATH = path.join(__dirname, '..', 'scripts', 'filters', 'laymans-terms.lua');

/**
 * Return the Lua long-string constant `name` from the filter source.
 * Precondition: the filter defines `local <name> = [[...]]`.
 */
function readLuaLongString(source, name) {
  const match = source.match(new RegExp(`local ${name} = \\[\\[([\\s\\S]*?)\\]\\]`));
  if (!match) {
    throw new Error(`${name} not found in ${FILTER_PATH}`);
  }
  return match[1];
}

function renderComponent(innerHtml) {
  const source = fs.readFileSync(FILTER_PATH, 'utf8');
  const open = readLuaLongString(source, 'OPEN_HTML');
  const close = readLuaLongString(source, 'CLOSE_HTML');
  document.body.innerHTML = `${open}${innerHtml}${close}`;
}

describe("In Layman's Terms component", () => {
  let initLaymansTermsToggle;
  let header;
  let content;

  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = '';
    ({ initLaymansTermsToggle } = require('../js/ui-components.js'));
    renderComponent('<p class="laymans-terms-intro">Plain words.</p>');
    header = document.querySelector('.laymans-terms-header');
    content = document.querySelector('.laymans-terms-content');
  });

  test('markup is open by default before any script runs', () => {
    expect(header.getAttribute('aria-expanded')).toBe('true');
    expect(content.getAttribute('aria-hidden')).toBe('false');
  });

  test('stays open by default after the toggle initialises', () => {
    initLaymansTermsToggle();
    expect(header.getAttribute('aria-expanded')).toBe('true');
    expect(content.hidden).toBe(false);
    expect(content.getAttribute('aria-hidden')).toBe('false');
    expect(header.getAttribute('aria-controls')).toBe(content.id);
    expect(header.getAttribute('aria-label')).toBe("Collapse In Layman's Terms");
  });

  test('toggling updates aria-expanded and the panel visibility', () => {
    initLaymansTermsToggle();

    header.click();
    expect(header.getAttribute('aria-expanded')).toBe('false');
    expect(content.hidden).toBe(true);
    expect(content.getAttribute('aria-hidden')).toBe('true');
    expect(header.getAttribute('aria-label')).toBe("Expand In Layman's Terms");

    header.click();
    expect(header.getAttribute('aria-expanded')).toBe('true');
    expect(content.hidden).toBe(false);
    expect(content.getAttribute('aria-hidden')).toBe('false');
  });

  test('the toggle is a focusable native button, so Enter and Space activate it', () => {
    expect(header.tagName).toBe('BUTTON');
    expect(header.getAttribute('type')).toBe('button');
    header.focus();
    expect(document.activeElement).toBe(header);
  });

  test('the heading wraps the toggle so the block appears in the outline', () => {
    expect(header.parentElement.tagName).toBe('H2');
    expect(header.textContent).toContain("In Layman's Terms");
  });
});
