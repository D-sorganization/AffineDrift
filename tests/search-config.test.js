const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");

describe("Search configuration (#4504)", () => {
  test("_quarto.yml configures an explicit search block (overlay, limit, keyboard shortcut)", () => {
    const quartoYml = fs.readFileSync(path.join(ROOT, "_quarto.yml"), "utf8");

    // Isolate the `search:` block nested under `website:` (two-space indent).
    const searchBlockMatch = quartoYml.match(
      /\n {2}search:\n((?: {4,}.*\n?)+)/,
    );
    expect(searchBlockMatch).not.toBeNull();
    const searchBlock = searchBlockMatch[1];

    expect(searchBlock).toMatch(/type:\s*overlay/);
    expect(searchBlock).toMatch(/limit:\s*\d+/);
    expect(searchBlock).toMatch(/keyboard-shortcut:/);
  });

  test("site-head.html does not emit an unverified SearchAction", () => {
    const siteHead = fs.readFileSync(
      path.join(ROOT, "_includes", "site-head.html"),
      "utf8",
    );

    expect(siteHead).not.toMatch(/SearchAction/);

    // The remaining JSON-LD WebSite block must still be valid JSON.
    const match = siteHead.match(
      /<script type="application\/ld\+json">([\s\S]*?)<\/script>/,
    );
    expect(match).not.toBeNull();
    expect(() => JSON.parse(match[1])).not.toThrow();
  });

  test("search-maturity-badge.js is loaded after the body", () => {
    const afterBody = fs.readFileSync(
      path.join(ROOT, "_includes", "site-after-body.html"),
      "utf8",
    );

    expect(afterBody).toMatch(/<script src="\/js\/search-maturity-badge\.js">/);
  });
});
