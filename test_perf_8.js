const fs = require('fs');
const { JSDOM } = require('jsdom');

const dom = new JSDOM(`<!DOCTYPE html><html lang="en"><body>
  <input type="text" id="bib-search">
  <div id="bib-list"></div>
  <div id="bib-count"></div>
  <div id="bib-sort-controls"></div>
  <div id="bib-details"></div>
</body></html>`, { url: "http://localhost" });

global.window = dom.window;
global.document = dom.window.document;
global.setTimeout = (fn, ms) => fn();
global.clearTimeout = () => {};
global.AbortController = dom.window.AbortController;
global.debounce = (fn, ms) => fn;
global.performance = require('perf_hooks').performance;

// Generate huge dataset
const mockData = Array.from({length: 50000}, (_, i) => ({
  id: `entry_${i}`,
  title: `Title ${i} with some keywords like golf and swing`,
  authors: [`Author ${i}A`, `Author ${i}B`],
  concepts: [`concept_${i % 10}`, `concept_${i % 5}`],
  year: 2000 + (i % 25),
  description: `A very long description for entry ${i} that contains some terms`
}));

global.fetch = () => Promise.resolve({
  ok: true,
  json: () => Promise.resolve(mockData)
});

const script = fs.readFileSync('js/bibliography.js', 'utf8');
const testScript = script.replace('debounce((event) => {', '((event) => {');

// Simply change includes to indexOf !== -1
const scriptIndexOf = testScript.replace(/includes\(/g, 'indexOf(').replace(/\)/g, ') !== -1');


const runTest = (testCode, name) => {
    eval(`
      (function() {
        ${testCode}
      })();
    `);

    setTimeout(() => {
        const searchInput = document.getElementById('bib-search');
        searchInput.value = "golf";
        searchInput.dispatchEvent(new window.Event('input'));

        const iterations = 20;
        const times = [];

        for (let i=0; i<iterations; i++) {
            searchInput.value = i % 2 === 0 ? "golf swing keyword other" : "golf other keywords";
            const t0 = performance.now();
            searchInput.dispatchEvent(new window.Event('input'));
            const t1 = performance.now();
            times.push(t1 - t0);
        }

        const avg = times.reduce((a, b) => a + b, 0) / iterations;
        console.log(`${name} Average search time: ${avg.toFixed(2)}ms`);
    }, 100);
};

// runTest(testScript, 'Original');
// runTest(scriptIndexOf, 'indexOf');
