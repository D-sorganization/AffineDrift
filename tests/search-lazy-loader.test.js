const fs = require("fs");
const path = require("path");
const vm = require("vm");

const source = fs.readFileSync(path.join(__dirname, "../js/search-lazy-loader.js"), "utf8");

/** Execute the real loader with an inert script transport and isolated event boundary. */
function createHarness() {
  const handlers = {};
  const scripts = [];
  const trigger = {};
  const searchRoot = { querySelector: () => trigger, querySelectorAll: () => [trigger] };
  const options = { textContent: '{"keyboard-shortcut":["s","/"]}' };
  const document = {
    readyState: "complete",
    documentElement: {},
    body: { classList: { contains: () => false } },
    querySelector: (selector) => {
      if (selector === "#quarto-search") return searchRoot;
      if (selector === "#quarto-search-options") return options;
      return null;
    },
    addEventListener: (type, listener) => { handlers[type] = listener; },
    createElement: () => ({ dataset: {}, addEventListener: () => {} }),
    head: { appendChild: (script) => scripts.push(script) },
  };
  vm.runInNewContext(source, {
    document,
    window: { location: { href: "https://example.org/" }, requestAnimationFrame: () => {} },
    Element: class {},
    MutationObserver: class { observe() {} },
    URL,
    console,
    queueMicrotask,
  });
  return { document, handlers, scripts };
}

function keyEvent(harness, options) {
  return {
    key: "s",
    target: harness.document,
    defaultPrevented: false,
    preventDefault() { this.defaultPrevented = true; },
    stopImmediatePropagation() {},
    ...options,
  };
}

describe("lazy search preserves native modified shortcuts (#5171)", () => {
  test.each(["ctrlKey", "metaKey", "altKey"].flatMap((modifier) =>
    ["s", "/"].map((key) => [modifier, key])))
  ("does not intercept %s + %s", (modifier, key) => {
    const harness = createHarness();
    const event = keyEvent(harness, { key, [modifier]: true });
    harness.handlers.keyup(event);
    expect(event.defaultPrevented).toBe(false);
    expect(harness.scripts).toHaveLength(0);
  });

  test.each(["s", "/"])("plain %s still starts lazy search", (key) => {
    const harness = createHarness();
    const event = keyEvent(harness, { key });
    harness.handlers.keyup(event);
    expect(event.defaultPrevented).toBe(true);
    expect(harness.scripts).toHaveLength(1);
  });

  test("an unconfigured key remains untouched", () => {
    const harness = createHarness();
    const event = keyEvent(harness, { key: "x" });
    harness.handlers.keyup(event);
    expect(event.defaultPrevented).toBe(false);
    expect(harness.scripts).toHaveLength(0);
  });
});
