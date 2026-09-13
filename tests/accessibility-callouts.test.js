/**
 * Tests for Quarto collapsible callout keyboard activation — issue #4374.
 * Verifies that .callout-header[data-bs-toggle='collapse'] elements:
 * 1. Receive role="button" and tabindex="0"
 * 2. Are activated by Enter and Space (matching click behavior)
 * 3. Support idempotent initialization without double-binding listeners
 * 4. Do not trigger when inner interactive elements (e.g. links) are activated
 * 5. Update aria-expanded state to reflect panel expansion
 */

let initAriaLabels;

describe("Quarto Callout Keyboard Activation (issue #4374)", () => {
  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = "";
    document.head.innerHTML = "";
    const mod = require("../js/accessibility.js");
    initAriaLabels = mod.initAriaLabels;
  });

  function buildCallout(options = {}) {
    const isExpanded = options.isExpanded || false;
    const innerHtml = options.hasInnerLink
      ? '<div class="callout-title-container"><a href="#test">Inner Link</a> Callout Title</div>'
      : '<div class="callout-title-container">In Layman\'s Terms</div>';

    document.body.innerHTML = `
      <div class="callout callout-style-default callout-note callout-titled">
        <div class="callout-header d-flex align-content-center"
             data-bs-toggle="collapse"
             data-bs-target=".callout-1-contents"
             aria-controls="callout-1-contents"
             aria-expanded="${isExpanded}">
          ${innerHtml}
        </div>
        <div id="callout-1-contents" class="callout-1-contents callout-collapse collapse ${isExpanded ? "show" : ""}">
          <div class="callout-body-container callout-body">
            <p>Simplified explanation content</p>
          </div>
        </div>
      </div>
    `;

    // Simulate click handler (matching Bootstrap collapse behavior)
    const header = document.querySelector(".callout-header");
    const content = document.querySelector(".callout-1-contents");
    header.addEventListener("click", () => {
      const currentExpanded = header.getAttribute("aria-expanded") === "true";
      const nextExpanded = !currentExpanded;
      header.setAttribute("aria-expanded", String(nextExpanded));
      if (nextExpanded) {
        content.classList.add("show");
        content.style.height = "120px";
      } else {
        content.classList.remove("show");
        content.style.height = "0px";
      }
    });

    return { header, content };
  }

  test('wires role="button" and tabindex="0" on callout toggles', () => {
    const { header } = buildCallout();
    initAriaLabels();

    expect(header.getAttribute("role")).toBe("button");
    expect(header.getAttribute("tabindex")).toBe("0");
  });

  test("Enter key activates collapsible header matching click behavior", () => {
    const { header, content } = buildCallout({ isExpanded: false });
    initAriaLabels();

    expect(header.getAttribute("aria-expanded")).toBe("false");

    const enterEvent = new KeyboardEvent("keydown", {
      key: "Enter",
      bubbles: true,
      cancelable: true,
    });
    header.dispatchEvent(enterEvent);

    expect(enterEvent.defaultPrevented).toBe(true);
    expect(header.getAttribute("aria-expanded")).toBe("true");
    expect(content.classList.contains("show")).toBe(true);
    expect(content.style.height).toBe("120px");
  });

  test("Space key activates collapsible header and prevents default scrolling", () => {
    const { header, content } = buildCallout({ isExpanded: false });
    initAriaLabels();

    const spaceEvent = new KeyboardEvent("keydown", {
      key: " ",
      bubbles: true,
      cancelable: true,
    });
    header.dispatchEvent(spaceEvent);

    expect(spaceEvent.defaultPrevented).toBe(true);
    expect(header.getAttribute("aria-expanded")).toBe("true");
    expect(content.classList.contains("show")).toBe(true);
  });

  test("Spacebar key alias activates collapsible header", () => {
    const { header } = buildCallout({ isExpanded: false });
    initAriaLabels();

    const spacebarEvent = new KeyboardEvent("keydown", {
      key: "Spacebar",
      bubbles: true,
      cancelable: true,
    });
    header.dispatchEvent(spacebarEvent);

    expect(spacebarEvent.defaultPrevented).toBe(true);
    expect(header.getAttribute("aria-expanded")).toBe("true");
  });

  test("repeated initAriaLabels calls are idempotent and do not cause double toggles", () => {
    const { header, content } = buildCallout({ isExpanded: false });

    // Call init multiple times
    initAriaLabels();
    initAriaLabels();
    initAriaLabels();

    // Trigger Enter once
    const enterEvent = new KeyboardEvent("keydown", {
      key: "Enter",
      bubbles: true,
      cancelable: true,
    });
    header.dispatchEvent(enterEvent);

    // If double toggled, it would end up false. It must remain true (single activation).
    expect(header.getAttribute("aria-expanded")).toBe("true");
    expect(content.classList.contains("show")).toBe(true);
  });

  test("non-activation keys (Tab, ArrowDown, Escape) do not trigger toggle or preventDefault", () => {
    const { header } = buildCallout({ isExpanded: false });
    initAriaLabels();

    for (const key of ["Tab", "ArrowDown", "ArrowUp", "Escape", "a"]) {
      const event = new KeyboardEvent("keydown", {
        key,
        bubbles: true,
        cancelable: true,
      });
      header.dispatchEvent(event);

      expect(event.defaultPrevented).toBe(false);
      expect(header.getAttribute("aria-expanded")).toBe("false");
    }
  });

  test("inner interactive links inside header do not trigger callout toggle on Enter", () => {
    const { header } = buildCallout({ isExpanded: false, hasInnerLink: true });
    initAriaLabels();

    const innerLink = header.querySelector("a");
    expect(innerLink).not.toBeNull();

    const linkEnterEvent = new KeyboardEvent("keydown", {
      key: "Enter",
      bubbles: true,
      cancelable: true,
    });
    innerLink.dispatchEvent(linkEnterEvent);

    // Should not trigger callout toggle
    expect(header.getAttribute("aria-expanded")).toBe("false");
  });
});
