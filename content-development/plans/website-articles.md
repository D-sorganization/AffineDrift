# Website articles — development plan

**Corpus:** 191 `.qmd` across `articles/`, `books/`, `pages/`, `resources/`, `models/`,
`repositories/`, `critiques/` (~60,700 lines).
**Review:** 2026-07-31 — ~210 findings, 17 P0.
**Epics:** [#3532](https://github.com/D-sorganization/AffineDrift/issues/3532) (accuracy),
[#3533](https://github.com/D-sorganization/AffineDrift/issues/3533) (framing).

## What is right, and should be preserved

- **`superposition.qmd` is the site's best page.** Abstract, opening callout, §6.2 and closing
  scope box all state that superposition is instantaneous and pointwise, and that trajectories do
  not superpose. It never slides between the two. Use it as the template.
- **Provenance callouts** on `index.qmd`, `overview.qmd` and `drifter-manifesto.qmd` name what is
  established literature and what is original AffineDrift synthesis. This is genuinely good
  practice and should be extended sitewide.
- **The four research-review stubs** are correctly scoped and hedged, free of the automatic-
  sequencing and cross-sport-transfer overclaims that were the historical risk.
- **`book-reviews.qmd` is honest** about having no finished reviews.
- Internal `.html` link integrity is clean — zero dangling targets.
- The DCR article now handles accessibility-versus-controllability well, with an explicit callout
  and a norm-dependence section.
- Prior audit items confirmed fixed: the UpstreamDrift page labels unshipped APIs as proposed, and
  the stale `Golf_Modeling_Suite` name is gone.

## The four problems

1. **Fabricated computational output** in the tangent corpus
   ([#3534](https://github.com/D-sorganization/AffineDrift/issues/3534)) — the most damaging class
   of error on the site.
2. **Two real bugs in shipped JavaScript**
   ([#3535](https://github.com/D-sorganization/AffineDrift/issues/3535)) — the rotation converter
   is wrong at 180° and at gimbal lock, masked by its own presets.
3. **Corrections sitting beside the errors they replaced**
   ([#3536](https://github.com/D-sorganization/AffineDrift/issues/3536)).
4. **The Geometry of Motion Quarto mirror was never successfully rendered**
   ([#3537](https://github.com/D-sorganization/AffineDrift/issues/3537)) — roughly one equation in
   six fails to typeset.

## What this corpus needs added

- **Executable cells.** Zero exist in either textbook mirror. Making numeric blocks real Quarto
  `{python}` cells is the structural fix for the fabricated-output class.
- **Citations.** Only **2 inline `[@key]` citations across 7,921 lines** of reference articles,
  against 491 available bibliography entries and a `CLAUDE.md` standard requiring them.
- **`Ṁ − 2C` skew-symmetry and the Christoffel caveat appear nowhere** in the article corpus, yet
  `null-space-constraint-jacobian.qmd` silently depends on it and the Lagrangian _reference_ never
  defines `C` at all.
- **Answers to the six unanswered critiques**, one of them self-rated High severity. An
  acknowledged open critique is a credibility asset; a silently unanswered one is a liability.
- **Link the notebooks.** Per-chapter Jupyter notebooks exist at `notebooks/geometry_of_motion/`
  and nothing in `resources/` links them.
- **Generate reading lists from `.bib`** — the hand-maintained author/title strings are what
  produced "Boyd & Boyd" and Khalil-with-Isidori's-title.
