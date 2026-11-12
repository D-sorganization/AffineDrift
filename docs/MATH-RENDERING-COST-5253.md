# Math rendering cost on Theory Part 1 (#5253, idea 6 of #5248)

Status: **partial evidence, measurement only.** No production switch, no SSR
prototype built yet (see "Not done").

## Baseline (client MathJax, current build)

Source: nightly `cross-browser-nightly` run 41985000660 (2026-11-05, `main`),
artifact `lighthouse-mobile`, report for `/articles/theory-part1.html`
(Lighthouse 12.6.1, mobile emulation, simulated throttling, **1 run**).
Reproduce the attribution from any Lighthouse JSON:

```bash
python3 scripts/lighthouse_math_cost.py REPORT.json
```

| Metric | Whole page | Math-related scripts |
| --- | --- | --- |
| Performance score | 0.37 | n/a |
| LCP | 9754 ms | LCP element is the intro `div.description`, not math |
| Total blocking time | 759 ms | n/a |
| Transfer size | 1,994,233 B | 207,575 B (10.4 %) |
| Script boot-up (total) | n/a | 1262 ms (`tex-chtml.js` 912 + `ui/lazy.js` 350) |
| Script boot-up (scripting only) | n/a | 875 ms |
| Render-blocking | 12 resources | 152 ms (the local `equation-runtime-gate.js`; MathJax itself is not render-blocking) |

## Reading

- MathJax is already lazy (`ui/lazy`) and loaded off the critical path. It is
  not the LCP element and not render-blocking.
- Its measurable cost is about 1.26 s of simulated boot-up, of which about
  0.88 s is scripting, plus about 0.2 MB (10 %) of transfer. That is the upper
  bound any build-time (SSR) math could recover from boot-up and blocking time;
  it does not address the 9.8 s LCP, which is dominated by render-blocking
  Bootstrap CSS/JS (largest wasted: `bootstrap.min.css` 6.6 s, `bootstrap.min.js`
  2.1 s, `bootstrap-icons.css` 2.9 s in the same report).
- Conclusion for #5248 idea 6: build-time math SSR would remove at most about
  1.3 s of boot-up on this page. Fixing the render-blocking assets first buys far
  more LCP. SSR is not justified on this evidence alone.

## Not done (acceptance gaps)

- Only **one** Lighthouse run per URL is recorded by `config/lighthouserc.json`
  (`numberOfRuns: 1`); the issue asks for three. Variance is unquantified.
- No branch-local SSR prototype or build-time delta. It needs a build-time math
  renderer (for example the `katex` package) added through the lockfile, which is
  a dependency decision for the owner. Quarto's own `html-math-method: katex` is
  client-side, so it would measure a lighter client renderer, not SSR.
