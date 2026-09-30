# Math Accessibility Verification — #4565 (WEB-09.5)

Findings for the E9 accessibility-conformance check on whether the site's
`connect-src 'self'` CSP (`_includes/site-head.html`) blocks MathJax
speech-rule locale fetches, and whether lazy typesetting breaks screen
reader access to math.

## Automated Findings

- **MathJax explorer/SRE is not loaded.** `_includes/mathjax-loader.html`
  only sets `enableAssistiveMml: true`, which makes MathJax emit a real
  `<math>` MathML tree inside a hidden `<mjx-assistive-mml>` element using
  its own internal converter — no `[a11y]/explorer` component and no
  `speech-rule-engine` locale package are loaded. Locale JSON fetches (the
  network requests that `connect-src 'self'` would block) only happen when
  the explorer component is loaded, so today there is no code path that can
  trip that CSP directive. Regression-guarded by
  `tests/mathjax-loader.test.js` ("does not load the SRE-backed explorer
  module...").
- **No CSP violations or failed requests on math-heavy pages.**
  `tests/e2e/accessibility.spec.js` ("math pages expose assistive MathML
  with no CSP-blocked speech/locale requests (#4565)") loads three
  math-heavy pages — `/articles/theory-part1.html`,
  `/articles/affine-nature-golf-swing.html`, and
  `/articles/The_Geometry_of_Motion/quarto/ch01_foundations.html` — waits
  for lazy MathJax typesetting to finish, and asserts zero console messages
  matching a CSP-violation signature and zero failed network requests. This
  runs in CI's Playwright E2E lane (full site render required); see
  "What Could Not Be Verified" below for why it was not run against a local
  render in this change.
- **Assistive MathML is present after lazy typesetting.** The same test
  waits for `mjx-assistive-mml` to attach on each page, confirming the
  hidden MathML layer screen readers read from is actually produced once
  `ui/lazy` typesets the equations — lazy loading does not silently skip the
  accessibility layer.

## What Could Not Be Verified

**A real NVDA or VoiceOver run was not performed.** This CLI agent has no
screen reader installed and no human available to listen to and transcribe
synthesized speech output — a screen-reader trial is a human-in-the-loop
verification step outside what a coding agent can execute or fabricate
(see the fleet's deferred-validation policy). `docs/A11Y-PHASE2.md` already
lists "Test on Windows NVDA" / "Test on iOS VoiceOver" as unchecked manual
checklist items for the same reason.

The manual protocol below is provided so a human tester can close this
criterion without re-deriving the test plan.

## Manual Screen-Reader Test Protocol (For a Human Tester)

Run against a local `quarto render` (or the deployed site) with the pages
below, and record the actual announced text for each step in a comment on
issue #4565 (or a new evidence file linked from there):

1. **NVDA (Windows) or VoiceOver (macOS)**, default verbosity, on:
   - `/articles/theory-part1.html`
   - `/articles/affine-nature-golf-swing.html`
   - `/articles/The_Geometry_of_Motion/quarto/ch01_foundations.html`
2. For each page: navigate by heading (`H` in NVDA, VO+Cmd+H in VoiceOver)
   into a section containing a display equation, then read the equation
   with the screen reader's "read current line/item" command.
3. Record: (a) whether the equation is announced at all (vs. silently
   skipped), (b) whether the announced content is intelligible math speech
   or a MathML/LaTeX-source dump, (c) any browser console or NVDA log
   errors mentioning "Content Security Policy" or a failed network request
   during that navigation.
4. File the recording (transcript or screen capture) as the evidence this
   issue's first acceptance criterion requires, then close it out.

## Scope Note

Issue #4565 is labeled `type:test`: a verification issue, not a feature
issue. No production code changed. `_includes/site-head.html`'s CSP and
`_includes/mathjax-loader.html`'s configuration are unchanged — the finding
is that they already satisfy the second acceptance criterion, now enforced
by regression tests.
