# Tangent Hyperplane Contraction

This directory is the dedicated textbook-development workspace for a full treatment of nonlinear control through tangent-space dynamics, contraction theory, and local optimal control.

## Purpose

- Maintain one coherent manuscript while developing a chaptered textbook structure.
- Keep the LaTeX source and Quarto source side-by-side for flexible publishing.
- Reuse validated AffineDrift article content where it directly supports high-dimensional nonlinear control.

## Layout

- `index.qmd`: Landing page and reading order.
- `textbook-main.qmd`: Consolidated manuscript intended to evolve into the primary textbook narrative.
- `chapters/`: Chapterized working files for iterative refinement.
- `manuscript/tangent-hyperplane-contraction.tex`: LaTeX manuscript source snapshot.
- `references.bib`: Shared bibliography for citations.
- `sources/source-map.md`: Mapping from existing AffineDrift content to textbook chapters.

## Suggested Workflow

1. Draft or revise in `chapters/*.qmd`.
2. Promote mature sections into `textbook-main.qmd`.
3. Keep equations and assumptions synchronized with `manuscript/tangent-hyperplane-contraction.tex`.
4. Update `sources/source-map.md` when drawing from additional AffineDrift content.

## Preview

```bash
quarto preview articles/tangent-hyperplane-contraction/index.qmd
quarto preview articles/tangent-hyperplane-contraction/textbook-main.qmd
```
