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

## 2026-04-18 - Prevent DOM-based XSS via document.title in PDF Export
**Vulnerability:** DOM-based XSS via unescaped document.title used in PDF export functionality.
**Learning:** Even internal properties like document.title can be manipulated. If an attacker can control the title (e.g., via a URL parameter in some frameworks), injecting it directly into `.innerHTML` creates an XSS vulnerability.
**Prevention:** Always escape data from properties like document.title before injecting it into the DOM via `.innerHTML`.
## 2026-04-21 - Prevent DOM-based XSS in History URLs
**Vulnerability:** DOM-based XSS vulnerability in history modules where URLs from localStorage were assigned to href properties using an incomplete blacklist.
**Learning:** localStorage is an untrusted sink. Blacklisting specific protocols like javascript: is error-prone and misses data: or vbscript:.
**Prevention:** Always validate and sanitize URLs using an allowlist approach (e.g., using the URL constructor to strictly permit http: and https: protocols) before assigning them to href attributes.
## 2026-04-22 - Prevent DOM-based XSS in Metrics Widget
**Vulnerability:** DOM-based XSS via `innerHTML` used with template literals to render arrays of user-controlled data in `js/metrics.js`.
**Learning:** Using `innerHTML` with template literals to render arrays of user-controlled data (such as browsing history from `localStorage`) is brittle and can lead to XSS.
**Prevention:** To prevent DOM-based XSS when rendering arrays of user-controlled data, do not use `innerHTML` with template literals. Instead, build the list safely using `document.createDocumentFragment()`, `document.createElement()`, and securely set values using `textContent`.

## 2026-05-20 - Prevent DOM-based XSS in Bibliography Links
**Vulnerability:** DOM-based XSS vulnerability in `js/bibliography.js` where untrusted URLs from JSON data were directly interpolated into `href` attributes within `.innerHTML`.
**Learning:** Escaping HTML entities (`<`, `>`, `&`, `"`, `'`) is insufficient for preventing XSS in `href` attributes, as `javascript:` URIs do not require these characters to execute malicious code.
**Prevention:** Always parse and validate URLs with a strict allowlist (e.g., `http:` and `https:`) using the `URL` constructor before injecting them into `href` attributes, even if the data comes from seemingly trusted static JSON files.

## 2026-06-01 - DOM-based XSS via URL Normalization Bypass
**Vulnerability:** Untrusted URLs from `localStorage` were validated using `new URL(url, origin)` but the raw, unnormalized input string was assigned to the `href` attribute if the protocol check passed. This allows bypasses using URI-encoded or whitespace-padded schemes (e.g., `javascript%0A:alert(1)`), which parse as relative paths during validation but execute as malicious schemes when interpreted by the browser in the DOM.
**Learning:** Checking the protocol of a parsed URL is insufficient if the original, un-sanitized string is used for DOM assignment. The browser's HTML parser applies its own normalization which can differ from the URL constructor's parsing logic.
**Prevention:** Always assign the normalized output of the URL parser (e.g., `parsed.href`) back to the DOM attribute, rather than reusing the original untrusted input string.
## 2025-05-25 - Use custom AST evaluator instead of `new Function`
**Vulnerability:** Client-Side Code Injection (XSS) via `new Function` in `src/tools/wrist_universal_joint/grip_angle_simulator.html`.
**Learning:** Even with regex sanitization, `new Function` is susceptible to XSS because filtering characters safely without breaking valid inputs is extremely error-prone.
**Prevention:** Use a dedicated safe AST evaluator that only supports mathematical operations instead of dynamically compiling code via `new Function` or `eval`.
## 2026-07-20 - Prevent DOM-based XSS in DOM construction
**Vulnerability:** DOM-based XSS risk via `innerHTML` used with template literals in `addCheckbox` of the grip angle simulator.
**Learning:** Using `innerHTML` to construct DOM elements by interpolating variables is brittle and introduces XSS risks, even if the current inputs appear safe.
**Prevention:** To prevent DOM-based XSS when constructing DOM elements, always use native DOM methods like `document.createElement()` and securely set properties using `textContent`, `id`, `htmlFor`, etc.
## 2025-05-25 - Prevent DOM-based XSS in bibliography sort controls
**Vulnerability:** DOM-based XSS risk via `innerHTML` used with string concatenation to render sort buttons in `js/bibliography.js`.
**Learning:** Using `innerHTML` to construct DOM elements dynamically, even with static keys/labels, violates strict security policies and creates a brittle pattern that could be exploited if the data source becomes untrusted.
**Prevention:** Always use native DOM methods like `document.createElement()` and securely assign properties via `textContent`, `dataset`, and `setAttribute` instead of `innerHTML`.

## 2026-05-30 - Fix XML parsing vulnerability
**Vulnerability:** Unsafe XML parsing using `xml.etree.ElementTree` without `defusedxml` protection.
**Learning:** Using standard `xml.etree` for untrusted or external XML files can expose the system to XML vulnerabilities like entity expansion or external entity injection.
**Prevention:** Always use `defusedxml` when parsing XML to prevent XML-based attacks.

## 2026-06-03 - Prevent DOM-based XSS in info panel
**Vulnerability:** DOM-based XSS via `innerHTML` used with template literals in the model info panel of the grip angle simulator.
**Learning:** Using `innerHTML` to construct DOM elements by interpolating variables is brittle and introduces XSS risks, even if the current inputs appear safe.
**Prevention:** To prevent DOM-based XSS when constructing DOM elements dynamically, always use native DOM methods like `document.createElement()` and securely assign properties via `textContent` instead of `innerHTML`.

## 2026-06-11 - Prevent DOM-based XSS in grip angle simulator
**Vulnerability:** DOM-based XSS risk via `.innerHTML` used to update inertia display and clear containers in `src/tools/wrist_universal_joint/grip_angle_simulator.html`.
**Learning:** Using `.innerHTML` to update or clear DOM containers is a brittle anti-pattern that introduces XSS risks and violates strict security policies, even when the inputs appear safe (e.g., numbers from `toFixed()`).
**Prevention:** Always use native DOM APIs such as `.textContent` or `.appendChild(document.createTextNode(...))` to safely update text content or clear elements, avoiding `.innerHTML` entirely.
## 2026-06-13 - Enforcing .textContent over .innerHTML
**Vulnerability:** Clearing DOM elements using .innerHTML = "" violates strict security policies and risks DOM-based XSS if later modified.
**Learning:** Even safe-looking assignments like empty strings build a habit of using an unsafe API. Native DOM properties like .textContent are inherently immune to XSS.
**Prevention:** Strictly use .textContent = "" or document.createTextNode() for DOM insertion and clearing.
## 2026-06-14 - Prevent DOM-based XSS by replacing innerHTML
**Vulnerability:** DOM-based XSS risk via `innerHTML` used to render error and empty states dynamically in `js/bibliography.js`.
**Learning:** Using `innerHTML` to construct DOM elements dynamically, even with static keys/labels or escaped variables, violates strict security policies and creates a brittle pattern that could be exploited.
**Prevention:** Always use native DOM methods like `document.createElement()` and securely assign properties via `textContent` instead of `innerHTML`.
## 2026-06-16 - Prevent DOM-based XSS in PDF export
**Vulnerability:** DOM-based XSS risk via `innerHTML` used with template literals to construct the print title block in `js/pdf.js`.
**Learning:** Using `innerHTML` to construct DOM elements by interpolating variables is brittle and introduces XSS risks, even if the current inputs appear safe or use escaping functions.
**Prevention:** To prevent DOM-based XSS when constructing DOM elements dynamically, always use native DOM methods like `document.createElement()` and securely assign properties via `textContent` instead of `innerHTML`.
## 2026-06-17 - Prevent DOM-based XSS in Notes Workspace
**Vulnerability:** DOM-based XSS vulnerability in `docs/js/notes-workspace.js` where the Project Notes panel was constructed using `innerHTML` and a large template string.
**Learning:** Using `innerHTML` to construct complex DOM elements with many interactive children is a brittle pattern that violates strict security policies and introduces potential XSS risks.
**Prevention:** To prevent DOM-based XSS when constructing elements, always use native DOM APIs such as `document.createElement()`, `textContent`, `setAttribute()`, and `appendChild()` to securely build and assemble components.
## 2026-06-19 - Prevent SSRF in Verify Images Tool
**Vulnerability:** Server-Side Request Forgery (SSRF) risk in image verification where untrusted URLs were passed to `requests.get()` and `requests.head()`.
**Learning:** Even internal build tools that parse user-generated markdown need SSRF protection, as malicious authors can include loopback or private IPs (e.g., AWS metadata service) in image URLs.
**Prevention:** Always parse and validate hostnames to reject loopback, link-local, and private IP addresses before initiating outbound HTTP requests.
## 2026-06-21 - Prevent DOM-based XSS by replacing innerHTML
**Vulnerability:** DOM-based XSS risk via `innerHTML` used extensively across multiple JS modules.
**Learning:** Using `innerHTML` to construct DOM elements dynamically, even with static keys/labels or escaped variables, violates strict security policies and creates a brittle pattern that could be exploited.
**Prevention:** Always use native DOM methods like `document.createElementNS()`, `document.createElement()`, and securely assign properties via `textContent`, `dataset`, and `setAttribute` instead of `innerHTML`.
## 2026-07-15 - Prevent SSRF in Verify Images Tool (IPv6 and DNS Resolution)
**Vulnerability:** Server-Side Request Forgery (SSRF) risk in image verification where untrusted URLs were validated solely by string-based hostname checks before being passed to `requests.get()` and `requests.head()`. This could be bypassed using custom domains resolving to local IPs, or by using IPv6 literals (e.g., `[::1]`). Furthermore, `allow_redirects` was not explicitly disabled on the `requests.get()` fallback, allowing redirects to internal IPs.
**Learning:** String-matching against localhost or loopback strings is insufficient for SSRF protection because DNS can map arbitrary domains to internal addresses, and attackers can use various IP encoding formats.
**Prevention:** Always perform DNS resolution on the hostname using `socket.getaddrinfo()` (specifying `socket.AF_UNSPEC` to handle both IPv4 and IPv6) and validate the resulting IP addresses against private/loopback ranges. Explicitly disable HTTP redirects (`allow_redirects=False`) when fetching URLs to prevent bypasses.
