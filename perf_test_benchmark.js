const fs = require('fs');
const { JSDOM } = require('jsdom');
const { performance } = require('perf_hooks');

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

const mockData = Array.from({length: 20000}, (_, i) => ({
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

let originalScript = fs.readFileSync('js/bibliography.js', 'utf8');

// The original script has this inside the scoring function:
//     for (const term of queryTerms) {
//      if (entry._searchTitle.includes(term)) score += 5;
//      if (entry._searchAuthors.includes(term)) score += 3;
//      if (entry._searchConcepts.includes(term)) score += 2;
//    }

const unoptimizedScript = originalScript.replace('debounce((event) => {', '((event) => {');

// In my optimized script, I remove those includes because the entry is ALREADY filtered to guarantee it includes the terms in the broader text, but we still want to give extra points if the title/author/concepts have it, so we can't just remove them.
