# Content Security Policy

## Issue
#2282: CSP contained `unsafe-inline` and `unsafe-eval` directives that negate XSS protection.

## Policy
- **Removed**: `unsafe-inline` (replaced with hashes for shared inline scripts and styles)
- **Removed**: `unsafe-eval` (no safe substitute - code should not use eval())
- **Required**: Use hash-based allowances for shared inline scripts and styles

## Implementation
The shared Quarto includes now carry CSP hashes for the inline JSON-LD,
bootstrapping scripts, and fallback styles that remain in the page head and
body partials.

## References
- [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/)
