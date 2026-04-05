## 2025-02-23 - Prevent XSS in Notes Popout
**Vulnerability:** Cross-Site Scripting (XSS) via document.write in the notes pop-out feature.
**Learning:** Interpolating user-provided text directly into an HTML string passed to document.write, even with rudimentary character escaping, is brittle and insecure.
**Prevention:** Always use safe DOM properties like textContent or value to inject user-controlled data into the DOM.

## 2025-04-05 - Fix XSS in polynomial evaluation via `new Function`
**Vulnerability:** Client-Side Code Injection (XSS) via `new Function` in the polynomial signal generator of the grip angle simulator.
**Learning:** Even when intended to restrict evaluation to specific math functions, passing unsanitized user input to `new Function('...', 'return ' + expr)` allows attackers to craft payloads (e.g., `1; alert(1)`) to execute arbitrary JavaScript within the user's browser. Furthermore, naively filtering allowed string tokens (like `e`) can inadvertently break valid scientific notation (e.g., `1e-3`).
**Prevention:** To prevent XSS when evaluating mathematical expressions via `new Function` or `eval` in JavaScript, sanitize the input by explicitly replacing allowed functions/variables (e.g., `Math.sin`, `t`, `pi`) with empty strings, and using a strict regex (e.g., `/^[0-9\s\+\-\*\/\(\)\.\,eE]*$/`) on the remainder to ensure only basic math operators and valid numeric characters (including scientific notation exponents) are present.
