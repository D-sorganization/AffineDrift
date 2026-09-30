# Math Accessibility Verification — #4565 (WEB-09.5)

Findings for the E9 accessibility-conformance check on whether the site's
`connect-src 'self'` CSP (`_includes/site-head.html`) blocks MathJax
speech-rule locale fetches, and whether lazy typesetting breaks screen
reader access to math.

## Reinterpreting the Second Acceptance Criterion

The issue asks that "the explorer and speech work without CSP errors, or
assets are self-hosted." MathJax's SRE-backed `[a11y]/explorer` component
(the one that fetches speech-rule locale JSON, the fetch `connect-src
'self'` could block) is not loaded anywhere in this codebase —
`_includes/mathjax-loader.html` only sets `enableAssistiveMml: true`, which
makes MathJax emit a real `<math>` MathML tree inside a hidden
`<mjx-assistive-mml>` element using its own internal converter, with no
network fetch involved. So "the explorer and speech work" does not apply
literally; the criterion is reinterpreted here as **"explorer is not loaded;
the assistive-MathML path it would otherwise cover has no CSP errors,"**
which is what the automated checks below actually verify.
Regression-guarded by `tests/mathjax-loader.test.js` ("does not load the
SRE-backed explorer module...").

## Automated Findings

- **A real CSP violation was found and fixed — not the one the issue
  hypothesized, but a real one.** CI's `e2e-tests` job initially failed:
  `/articles/theory-part1.html` (and the other math-heavy pages) loaded
  `https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js`, which
  `script-src` (no `cdnjs.cloudflare.com` in its allow-list) blocks. This is
  Pandoc's own legacy ES6 polyfill, injected by `html-math-method: mathjax`
  regardless of the custom loader — unrelated to the explorer/SRE path the
  issue asked about, but a genuine CSP error on every math page.
  `scripts/prune_internal_docs_from_deploy.py` already strips this tag
  (`strip_legacy_math_polyfill`), but `.github/workflows/ci-standard.yml`'s
  `e2e-tests` job only ran that pruning step *after* the Playwright E2E
  suite, right before manifest generation — so the un-pruned tag was still
  present in `docs/` when Playwright loaded the pages. Fixed by moving the
  prune call into the "Sync Frontend Assets" step, before Playwright runs;
  the CSP itself was not widened. No local render was available to reproduce
  this before the CI-based review caught it (see "What Could Not Be
  Verified" for why Quarto isn't available in this environment).
- **Assistive MathML is present after lazy typesetting.** The E2E test
  (`tests/e2e/accessibility.spec.js`, "math pages expose assistive MathML
  with no CSP-blocked speech/locale requests (#4565)") waits for
  `mjx-assistive-mml` to attach on each of the three math-heavy pages,
  confirming the hidden MathML layer screen readers read from is actually
  produced once `ui/lazy` typesets the equations — lazy loading does not
  silently skip the accessibility layer. Whether the *remaining* console
  errors and failed requests are clean (beyond the polyfill fix above) is
  confirmed by that same test once CI reruns against this branch; it is not
  independently re-verified in this document.

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
issue. `_includes/site-head.html`'s CSP and `_includes/mathjax-loader.html`'s
configuration are unchanged — the CSP was not widened to work around the
polyfill finding above. The one production-adjacent change is
`.github/workflows/ci-standard.yml`'s step ordering, so the `e2e-tests` job
tests the artifact that actually ships (post-pruning) instead of a
transient pre-prune render.
