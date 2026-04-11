# Content Security Policy

## Issue
#2282: CSP contained `unsafe-inline` and `unsafe-eval` directives that negate XSS protection.

## Policy
- **Removed**: `unsafe-inline` (replaced with `strict-dynamic` for script-src)
- **Removed**: `unsafe-eval` (no safe substitute - code should not use eval())
- **Required**: Use nonce-based or hash-based script loading for inline scripts

## Implementation
If Quarto-generated HTML requires inline scripts, use the `include-in-header` option
to inject a CSP meta tag with nonce support instead of blanket `unsafe-inline`.

## References
- [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/)
