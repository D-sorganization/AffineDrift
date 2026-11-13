# MM-6 — Quarto Render Checklist (Motion Measurement)

**Issue:** [#5414](https://github.com/D-sorganization/AffineDrift/issues/5414)  
**Epic:** [#5408](https://github.com/D-sorganization/AffineDrift/issues/5408)

Use this list for the motion-measurement series sources under
`docs/development/motion-measurement/`. Execute from the repo root.

## Commands

```bash
quarto render docs/development/motion-measurement/part-1-representing-orientation.qmd
quarto render docs/development/motion-measurement/part-2-joint-coordinates-velocity-consequences.qmd
```

## Pass criteria (from issue)

- [ ] `quarto render` completes with **zero warnings** for both parts.
- [ ] KaTeX math, callouts, tables, and interactive figures render in HTML.
- [ ] All citations resolve (`@` keys present in the project bibliography).
- [ ] Front matter keeps **`draft: true`** (per series gate).

## Notes

- If render warns about a stale cross-reference, fix the source `.qmd` rather than silencing the check.
- Record the Quarto version used in the PR description when first green.
- MM-5 panel review tracked in `research/motion-measurement/critiques/mm5-panel-review.md`.
