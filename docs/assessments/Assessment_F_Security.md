# Assessment: Security (Category F)

**Score: 9/10**

## Findings
Security posture is strong for a static site generator.
- `SECURITY.md` defines reporting process.
- Dependencies are pinned in `requirements.txt`.
- `simpleeval` is used for safe evaluation of expressions.

## Strengths
- Explicit security policy.
- Usage of `simpleeval` prevents code injection in math tools.
- CI checks for security vulnerabilities (Bandit mentioned in memory).

## Weaknesses
- Local build scripts run with user privileges (standard for dev tools).

## Recommendations
1. Regularly audit `requirements.txt` for vulnerabilities using `dependabot` or `safety`.
