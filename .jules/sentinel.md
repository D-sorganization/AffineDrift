## 2025-02-23 - Prevent XSS in Notes Popout
**Vulnerability:** Cross-Site Scripting (XSS) via document.write in the notes pop-out feature.
**Learning:** Interpolating user-provided text directly into an HTML string passed to document.write, even with rudimentary character escaping, is brittle and insecure.
**Prevention:** Always use safe DOM properties like textContent or value to inject user-controlled data into the DOM.

## 2025-04-05 - Fix XSS in polynomial evaluation via `new Function`
**Vulnerability:** Client-Side Code Injection (XSS) via `new Function` in the polynomial signal generator of the grip angle simulator.
**Learning:** Even when intended to restrict evaluation to specific math functions, passing unsanitized user input to `new Function('...', 'return ' + expr)` allows attackers to craft payloads (e.g., `1; alert(1)`) to execute arbitrary JavaScript within the user's browser. Furthermore, naively filtering allowed string tokens (like `e`) can inadvertently break valid scientific notation (e.g., `1e-3`).
**Prevention:** To prevent XSS when evaluating mathematical expressions via `new Function` or `eval` in JavaScript, sanitize the input by explicitly replacing allowed functions/variables (e.g., `Math.sin`, `t`, `pi`) with empty strings, and using a strict regex (e.g., `/^[0-9\s\+\-\*\/\(\)\.\,eE]*$/`) on the remainder to ensure only basic math operators and valid numeric characters (including scientific notation exponents) are present.

## 2026-04-06 - Prevent DOM-based XSS in History URLs
**Vulnerability:** Found a DOM-based XSS vulnerability in `js/history.js` where URLs retrieved from `localStorage` were directly assigned to anchor `href` properties.
**Learning:** `localStorage` is an untrusted sink that can be polluted by other scripts or extensions on the same domain. Assigning arbitrary data from it to active properties like `href` allows injection of `javascript:` payloads.
**Prevention:** Always validate and sanitize URLs before assigning them to `href` attributes (e.g., ensuring they do not start with `javascript:`).
## 2026-04-07 - Prevent DOM-based XSS in Truncated Strings
**Vulnerability:** DOM-based XSS via unescaped truncated user input in the metrics widget.
**Learning:** When preparing user-controlled strings for display, wrapping them in helper functions like `truncate()` does not sanitize them. If the resulting truncated string is injected into HTML without escaping, it can execute malicious payloads.
**Prevention:** Always escape the final string immediately before injecting it into the DOM, even if it has passed through other formatting or utility functions like `truncate()`. Example: `${escapeHtml(truncate(userInput, 40))}`.

## 2026-04-07 - Add Content Security Policy Meta Tag
**Vulnerability:** Missing Content Security Policy (CSP) headers, making the site broadly susceptible to XSS if an injection point is found.
**Learning:** Implementing a strict CSP via the `<meta>` tag in the site's global HTML head (e.g. `_includes/site-head.html`) adds a defense-in-depth layer against script and style injections.
**Prevention:** Always include a baseline Content Security Policy restricting resources like scripts and styles to 'self' and explicitly allowed domains (like unpkg/js_deliver).

## 2026-04-07 - Allow MathJax and YouTube origins in CSP
**Vulnerability:** A strict Content Security Policy (CSP) blocked the loading of essential third-party assets (MathJax from jsdelivr) and embedded YouTube videos, leading to CI smoke test failures and missing functionality.
**Learning:** When enforcing 'default-src \'self\'', you must explicitly list every third-party domain required for fonts, stylesheets, and embedded frames. Relying solely on 'self' in a site relying on CDNs causes immediate functional breakage.
**Prevention:** Always test CSP updates thoroughly across all page types (especially pages with embeds and math formulas) and monitor console errors or automated end-to-end tests for blocked assets.
## 2025-04-07 - Prevent DOM-based XSS in Template Literals
**Vulnerability:** DOM-based Cross-Site Scripting (XSS) via `innerHTML` assignment using template literals containing user-controlled URLs and text in `.qmd` history components.
**Learning:** Directly interpolating potentially unsafe object properties (like `item.url` and `item.title` from `localStorage`) into a string that is assigned to `innerHTML` is inherently unsafe and can execute injected payloads (e.g., `javascript:` URIs).
**Prevention:** Always use safe DOM APIs such as `document.createElement`, `textContent`, and proper validation logic (e.g. checking protocol before assigning to `a.href`) instead of string interpolation into `innerHTML`.
