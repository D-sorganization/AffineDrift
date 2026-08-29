/**
 * Inert Pandoc math-method target.
 *
 * Pandoc uses this local URL only to serialize TeX delimiters correctly. The
 * tested loader in `_includes/mathjax-loader.html` owns the conditional,
 * version-pinned MathJax request after it detects math in the rendered DOM.
 */
