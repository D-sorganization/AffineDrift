/* Shim to load the root site script for nested pages. */
(() => {
  const offsetMeta = document.querySelector('meta[name="quarto:offset"]');
  const base = offsetMeta ? offsetMeta.getAttribute("content") : "/";
  const normalizedBase = base.endsWith("/") ? base : `${base}/`;
  const script = document.createElement("script");
  script.src = `${normalizedBase}script.js`;
  document.body.appendChild(script);
})();
