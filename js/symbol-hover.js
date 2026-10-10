/** Pointer tooltips for symbol hover references (WEB-11.6, #4584).
 * scripts/filters/symbol-hover.lua marks symbols with the MathJax class
 * `symref symref--KEY` and lists their definitions in a <details> after the
 * equation. That list is the keyboard and screen-reader path; this script only
 * adds a visual tooltip for pointer users, so the tooltip is aria-hidden.
 * Listeners are delegated, which also covers MathJax's lazy typesetting.
 */
(function (root) {
  'use strict';
  const KEY_PREFIX = 'symref--';
  const KEY_RE = /^[A-Za-z][A-Za-z0-9]*$/;

  /** Symbol key of the marked symbol containing `element`, or null. */
  function keyFrom(element) {
    const marked = element && element.closest ? element.closest('.symref') : null;
    if (!marked) return null;
    const name = Array.from(marked.classList).find(c => c.startsWith(KEY_PREFIX));
    return name ? name.slice(KEY_PREFIX.length) : null;
  }

  /** {name, definition} from the page's symbol list, or null if not listed. */
  function definitionFor(doc, key) {
    if (!KEY_RE.test(key)) return null;
    const item = doc.querySelector(`.symbol-refs [data-symref="${key}"]`);
    if (!item) return null;
    return {
      name: item.querySelector('dt').textContent.trim(),
      definition: item.querySelector('dd').textContent.trim(),
    };
  }

  function tooltip(doc) {
    let tip = doc.querySelector('.symbol-hover-tip');
    if (!tip) {
      tip = doc.createElement('div');
      tip.className = 'symbol-hover-tip';
      tip.setAttribute('aria-hidden', 'true');
      tip.hidden = true;
      doc.body.appendChild(tip);
    }
    return tip;
  }

  function show(doc, target, entry) {
    const tip = tooltip(doc);
    tip.textContent = `${entry.name}: ${entry.definition}`;
    const box = target.getBoundingClientRect();
    const view = doc.defaultView;
    tip.style.left = `${box.left + view.scrollX}px`;
    tip.style.top = `${box.bottom + view.scrollY + 6}px`;
    tip.hidden = false;
  }

  function hide(doc) {
    const tip = doc.querySelector('.symbol-hover-tip');
    if (tip) tip.hidden = true;
  }

  /** Attach the delegated listeners to `doc` once. */
  function bind(doc) {
    const flags = doc.documentElement.dataset;
    if (flags.symbolHoverBound) return;
    flags.symbolHoverBound = 'true';
    doc.addEventListener('mouseover', event => {
      const key = keyFrom(event.target);
      const entry = key && definitionFor(doc, key);
      if (entry) show(doc, event.target.closest('.symref'), entry);
    });
    doc.addEventListener('mouseout', event => {
      const marked = event.target.closest && event.target.closest('.symref, .symbol-hover-tip');
      const next = event.relatedTarget;
      if (!marked) return;
      if (next && next.closest && next.closest('.symref, .symbol-hover-tip')) return;
      hide(doc);
    });
    doc.addEventListener('keydown', event => {
      if (event.key === 'Escape') hide(doc);
    });
  }

  const api = {keyFrom, definitionFor, bind};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root.document) {
    root.SymbolHover = api;
    bind(root.document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
