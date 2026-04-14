const fs = require('fs');

let content = fs.readFileSync('script.js', 'utf8');

// The code blocks section currently looks like this due to the previous replace logic:
/*
    // Copy to Clipboard
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) Live Collection) instead of querySelectorAll (O(N))
    const codeBlocks = Array.from(document.getElementsByTagName("pre"));
    for (const pre of codeBlocks) {
      if (pre.parentNode.classList.contains("code-wrapper")) return;
      if (!pre.textContent.trim()) return;
*/
content = content.replace(
  `    // Copy to Clipboard
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) Live Collection) instead of querySelectorAll (O(N))
    const codeBlocks = Array.from(document.getElementsByTagName("pre"));
    for (const pre of codeBlocks) {
      if (pre.parentNode.classList.contains("code-wrapper")) return;
      if (!pre.textContent.trim()) return;`,
  `    // Copy to Clipboard
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) Live Collection) instead of querySelectorAll (O(N))
    // We convert to array because we mutate the DOM in the loop adding wrappers
    const codeBlocks = Array.from(document.getElementsByTagName("pre"));
    for (const pre of codeBlocks) {
      if (pre.parentNode.classList.contains("code-wrapper")) continue;
      if (!pre.textContent.trim()) continue;`
);

fs.writeFileSync('script.js', content);
