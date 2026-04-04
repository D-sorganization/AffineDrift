## 2025-02-23 - Prevent XSS in Notes Popout
**Vulnerability:** Cross-Site Scripting (XSS) via document.write in the notes pop-out feature.
**Learning:** Interpolating user-provided text directly into an HTML string passed to document.write, even with rudimentary character escaping, is brittle and insecure.
**Prevention:** Always use safe DOM properties like textContent or value to inject user-controlled data into the DOM.
