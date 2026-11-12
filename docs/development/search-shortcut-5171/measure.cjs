/** Controlled localhost snapshots for the #5171 keyboard fix; never publishes the site. */
const fs = require("fs");
const path = require("path");
const http = require("http");
const crypto = require("crypto");
const zlib = require("zlib");
const { execFileSync } = require("child_process");
const { pathToFileURL } = require("url");

const tools = process.env.AD_TOOL_ROOT;
const chromePath = process.env.AD_CHROME_PATH;
if (!tools || !chromePath) throw new Error("Set AD_TOOL_ROOT and AD_CHROME_PATH");
const out = path.resolve(process.argv[2]);
fs.mkdirSync(out, { recursive: true });
const puppeteer = require(path.join(tools, "puppeteer-core"));
const launcher = require(path.join(tools, "chrome-launcher"));
const sourcePath = "js/search-lazy-loader.js";
const before = execFileSync("git", ["show", `${process.env.AD_BASE_REV || "6ee9c59f89624ab6f58f3b566119f9ae829697ed"}:${sourcePath}`]);
const after = fs.readFileSync(sourcePath);
const origin = process.env.AD_SITE_ORIGIN || "https://www.affinedrift.com";
const routes = ["/", "/articles/theory-part1.html",
  "/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html"];
const views = [{ width: 375, height: 812 }, { width: 768, height: 1024 },
  { width: 1440, height: 900 }];
const cache = new Map();
const receipts = { origin, createdAt: new Date().toISOString(),
  source: { before: digest(before), after: digest(after) }, visual: [], lighthouse: [], keys: [] };
let variant = "before";

function digest(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function save(name, value) {
  fs.writeFileSync(path.join(out, name), zlib.gzipSync(JSON.stringify(value), { mtime: 0 }));
}

async function resource(url) {
  if (!cache.has(url)) cache.set(url, (async () => {
    const response = await fetch(new URL(url, origin), { signal: AbortSignal.timeout(30000) });
    return { status: response.status, type: response.headers.get("content-type"),
      bytes: Buffer.from(await response.arrayBuffer()) };
  })());
  return cache.get(url);
}

async function serve(request, response) {
  try {
    if (request.url === "/__keyboard-fixture") {
      response.setHeader("Content-Type", "text/html");
      response.end('<div id="quarto-search"></div><script id="quarto-search-options" '
        + 'type="application/json">{"keyboard-shortcut":["s","/"]}</script>'
        + '<script src="/js/search-lazy-loader.js"></script>');
      return;
    }
    const asset = request.url.split("?")[0] === `/${sourcePath}`
      ? { status: 200, type: "text/javascript", bytes: variant === "before" ? before : after }
      : await resource(request.url);
    response.writeHead(asset.status, { "Content-Type": asset.type || "application/octet-stream" });
    response.end(asset.bytes);
  } catch (error) { response.writeHead(502); response.end(String(error)); }
}

async function visualEvidence(base) {
  const browser = await puppeteer.launch({ executablePath: chromePath, headless: true });
  try {
    for (const [index, route] of routes.entries()) for (const view of views) {
      console.log(`opening ${variant} ${index} ${view.width}`);
      const page = await browser.newPage();
      await page.setViewport(view);
      await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
      const result = await page.goto(base + route, { waitUntil: "networkidle2", timeout: 60000 });
      if (!result.ok()) throw new Error(`${route}: HTTP ${result.status()}`);
      console.log(`loaded ${variant} ${index} ${view.width}`);
      await page.screenshot({ path: path.join(out, `${variant}-${index}-${view.width}.png`), fullPage: true });
      await page.addScriptTag({ path: path.join(tools, "axe-core/axe.min.js") });
      const axe = await page.evaluate(async () => window.axe.run(document, {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
      }));
      save(`${variant}-${index}-${view.width}-axe.json.gz`, axe);
      receipts.visual.push({ variant, route, ...view, violations: axe.violations.map(v =>
        ({ id: v.id, impact: v.impact, nodes: v.nodes.length })) });
      await page.close();
      console.log(`visual ${variant} ${index} ${view.width}`);
    }
    for (const key of ["s", "/"]) for (const modifier of ["ctrlKey", "metaKey", "altKey", "plain"]) {
      const page = await browser.newPage();
      await page.goto(base + "/__keyboard-fixture", { waitUntil: "networkidle2" });
      const result = await page.evaluate(({ key, modifier }) => {
        const event = new KeyboardEvent("keyup", { key, [modifier]: true, bubbles: true, cancelable: true });
        document.body.dispatchEvent(event);
        return { defaultPrevented: event.defaultPrevented,
          scripts: document.querySelectorAll("[data-lazy-search-asset]").length };
      }, { key, modifier });
      receipts.keys.push({ variant, key, modifier, ...result });
      await page.close();
    }
  } finally { await browser.close(); }
}

async function lighthouseEvidence(base) {
  const { default: lighthouse } = await import(pathToFileURL(path.join(tools, "lighthouse/core/index.js")));
  const { default: desktop } = await import(pathToFileURL(path.join(tools, "lighthouse/core/config/desktop-config.js")));
  for (const [index, route] of routes.entries()) for (const preset of ["mobile", "desktop"]) {
    const chrome = await launcher.launch({ chromePath, chromeFlags: ["--headless=new", "--disable-gpu"] });
    try {
      const result = await lighthouse(base + route, { port: chrome.port, output: "json",
        onlyCategories: ["performance", "accessibility", "best-practices", "seo"] },
      preset === "desktop" ? desktop : undefined);
      save(`${variant}-${index}-${preset}-lighthouse.json.gz`, result.lhr);
      const lhr = result.lhr, audit = name => lhr.audits[name]?.numericValue;
      receipts.lighthouse.push({ variant, route, preset, runtimeError: lhr.runtimeError || null,
        scores: Object.fromEntries(Object.entries(lhr.categories).map(([k, v]) => [k, v.score])),
        fcp: audit("first-contentful-paint"), lcp: audit("largest-contentful-paint"),
        tbt: audit("total-blocking-time"), cls: audit("cumulative-layout-shift"),
        transfer: lhr.audits["network-requests"].details.items.reduce((n, x) => n + (x.transferSize || 0), 0),
        requests: lhr.audits["network-requests"].details.items.length, warnings: lhr.runWarnings });
      console.log(`lighthouse ${variant} ${index} ${preset}`);
    } finally { await chrome.kill(); }
  }
}

async function main() {
  const server = http.createServer(serve);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    for (const next of ["before", "after"]) {
      variant = next;
      await visualEvidence(base);
      await lighthouseEvidence(base);
      save("receipts.json.gz", receipts);
    }
    receipts.assets = await Promise.all([...cache.entries()].map(async ([url, pending]) => {
      const asset = await pending;
      return { url, sha256: digest(asset.bytes), status: asset.status, type: asset.type };
    }));
    save("receipts.json.gz", receipts);
    fs.writeFileSync(path.join(out, "summary.json"), JSON.stringify(receipts, null, 2));
  } finally { server.closeAllConnections(); server.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
