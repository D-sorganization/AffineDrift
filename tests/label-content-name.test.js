/**
 * WCAG 2.5.3 Label in Name — issue #5089.
 * Accessible names set in js/accessibility.js must contain visible label text.
 */

function visibleReadingTimeLabel(element) {
  const span = element.querySelector("span");
  return (span ? span.textContent : element.textContent).replace(/\s+/g, " ").trim();
}

function assertAccessibleNameContainsVisibleLabel(element) {
  const visible = visibleReadingTimeLabel(element);
  expect(visible.length).toBeGreaterThan(0);
  const ariaLabel = element.getAttribute("aria-label");
  if (ariaLabel) {
    expect(ariaLabel.toLowerCase()).toContain(visible.toLowerCase());
  }
}

describe("WCAG 2.5.3 label in name (#5089)", () => {
  const articlePath = "/articles/example-chapter.html";

  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = "";
    document.head.innerHTML = "";
  });

  test("reading-time estimate accessible name contains visible label text", () => {
    window.history.pushState({}, "", articlePath);
    document.body.innerHTML = `
      <main id="quarto-document-content">
        <header class="quarto-title-block" id="title-block-header">
          <div class="quarto-title-meta"></div>
        </header>
        <p>${"word ".repeat(500)}</p>
      </main>
    `;
    const { initReadingTime } = require("../js/accessibility.js");
    initReadingTime();

    const readingTime = document.querySelector(".reading-time-estimate");
    expect(readingTime).not.toBeNull();
    assertAccessibleNameContainsVisibleLabel(readingTime);
    expect(visibleReadingTimeLabel(readingTime)).toMatch(/min read \(estimate\)/);
  });

  describe("initAriaLabels", () => {
    let initAriaLabels;

    beforeEach(() => {
      const mod = require("../js/accessibility.js");
      initAriaLabels = mod.initAriaLabels;
    });

    test("Quarto TOC nav aria-label contains the visible On this page heading", () => {
      document.body.innerHTML = `
        <nav id="TOC" aria-label="Table of Contents">
          <h2 id="toc-title">On this page</h2>
          <ul><li><a href="#intro">Intro</a></li></ul>
        </nav>
      `;
      initAriaLabels();

      const toc = document.getElementById("TOC");
      const visible = document.getElementById("toc-title").textContent.trim();
      expect(toc.getAttribute("aria-label").toLowerCase()).toContain(visible.toLowerCase());
    });
  });
});
