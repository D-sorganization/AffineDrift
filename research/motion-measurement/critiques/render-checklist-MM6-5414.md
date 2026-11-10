# MM-6 — Quarto Render Checklist (Motion Measurement)

**Issue:** [#5414](https://github.com/D-sorganization/AffineDrift/issues/5414)  
**Epic:** [#5408](https://github.com/D-sorganization/AffineDrift/issues/5408)

Use this list when the motion-measurement series `.qmd` sources are present in the repo (paths TBD from the epic). Execute from the repo root.

## Commands

```bash
quarto render <path-to-part-A>.qmd
quarto render <path-to-part-B>.qmd
```

(Replace with the actual file paths once linked in #5408.)

## Pass criteria (from issue)

- [ ] `quarto render` completes with **zero warnings** for both parts.
- [ ] KaTeX math, callouts, tables, and interactive figures render in HTML.
- [ ] All citations resolve (`@` keys present in the project bibliography).
- [ ] Front matter keeps **`draft: true`** (per series gate).

## Notes

- If render warns about a stale cross-reference, fix the source `.qmd` rather than silencing the check.
- Record the Quarto version used in the PR description when first green.
