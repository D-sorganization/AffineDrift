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
const mockData = Array.from({length: 100000}, (_, i) => ({
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

// Combine scoreEntry logic into the filter
const script3 = testScript.replace('return queryTerms.every((term) => haystack.includes(term));',
`
            let allMatch = true;
            let score = queryTerms.length;
            for (const term of queryTerms) {
                if (haystack.indexOf(term) === -1) {
                    allMatch = false;
                    break;
                }
                if (entry._searchTitle.indexOf(term) !== -1) score += 5;
                if (entry._searchAuthors.indexOf(term) !== -1) score += 3;
                if (entry._searchConcepts.indexOf(term) !== -1) score += 2;
            }
            if (allMatch) {
                entry._searchScore = score;
                return true;
            }
            return false;
`).replace(`    const scored = entries.map((entry) => ({
      entry,
      score: scoreEntry(entry, queryTerms),
    }));

    scored.sort((a, b) => {
      if (state.sort === "newest")
        return (b.entry.year || 0) - (a.entry.year || 0);
      if (state.sort === "oldest")
        return (a.entry.year || 0) - (b.entry.year || 0);
      if (state.sort === "title")
        return a.entry.title.localeCompare(b.entry.title);
      if (b.score !== a.score) return b.score - a.score;
      return (b.entry.year || 0) - (a.entry.year || 0);
    });

    return scored.map((item) => item.entry);`,
`
    const scored = [...entries];
    if (queryTerms.length === 0) {
        scored.forEach(e => e._searchScore = 0);
    }

    scored.sort((a, b) => {
      if (state.sort === "newest")
        return (b.year || 0) - (a.year || 0);
      if (state.sort === "oldest")
        return (a.year || 0) - (b.year || 0);
      if (state.sort === "title")
        return a.title.localeCompare(b.title);
      if (b._searchScore !== a._searchScore) return b._searchScore - a._searchScore;
      return (b.year || 0) - (a.year || 0);
    });

    return scored;`);

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

        const iterations = 50;
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

runTest(testScript, 'Original');
runTest(script3, 'Combined Filter/Score');
