# Mobile Publication Readiness

Epic tracker for a mobile-friendly article and projection experience (#5317).

## Child Issues

| Issue | Status | Notes |
| --- | --- | --- |
| #5313 | Route audit manifest + Playwright smoke expansion | `config/mobile-layout-audit-routes.json` |
| #5314 | Touch targets | `tests/touch-targets-css.test.js`, Playwright |
| #5315 | (closed when merged) | See git history |
| #5316 | Mobile smoke baseline | `tests/e2e/mobile-smoke.spec.js` |

Follow-on mobile UX issues (#5323, #5326, etc.) link here but ship in their own pull requests.

## Verification

- Phone smoke: `npx playwright test tests/e2e/mobile-smoke.spec.js --project=chromium`
- Lighthouse mobile baseline: `config/lighthouserc.json` (nightly workflow)
