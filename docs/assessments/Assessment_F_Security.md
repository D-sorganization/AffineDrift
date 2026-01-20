# Assessment: Security

## Grade: 8/10

## Analysis
Security is appropriate for a static site but has minor gaps in policy.
- **Static Content**: Low attack surface as there is no backend database or user auth.
- **Dependencies**: `package-lock.json` and pinned Python versions ensure reproducibility.
- **External Links**: `script.js` automatically adds `rel="noopener noreferrer"` to external links.

## Strengths
- `rel="noopener noreferrer"` enforcement in JS.
- No sensitive data storage.
- Strict CI checks for tool versions.

## Weaknesses
- **Missing Policy**: No `SECURITY.md` file to define reporting process.
- `script.js` uses `innerHTML` in a few places (e.g., `button.innerHTML`), which is generally safe here but requires care.

## Improvement Plan
- Create `SECURITY.md`.
- Review `innerHTML` usage for potential XSS (low risk here as inputs are controlled).
