# Content Development

This directory is where AffineDrift's **written content** is planned, reviewed, and held to a
standard — the textbooks, the articles, and the reference material. Code quality is governed by
`CLAUDE.md`, `SPEC.md`, and CI. This is the equivalent for prose, mathematics, and citations.

## Who this is for

The site's target reader is a **biomechanics or robotics researcher**: graduate level,
comfortable with Lie groups, screw theory, optimal control, contraction analysis, Hill-type
muscle models, and induced-acceleration analysis. They will check the mathematics, try to
reproduce the results, and cite the work — or dismiss all of it over one confidently-stated
error.

Everything in this directory exists to make the content survive that reader.

## What is here

| File                                       | Purpose                                                                 |
| ------------------------------------------ | ----------------------------------------------------------------------- |
| [`RIGOR_GUIDE.md`](RIGOR_GUIDE.md)         | The standard content must meet. Read before writing or editing.         |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How to run a content review, and the severity rubric.                   |
| [`plans/`](plans/)                         | Per-corpus development plans: what each body of content needs.          |
| [`FINDINGS_INDEX.md`](FINDINGS_INDEX.md)   | The 2026-07-31 full-corpus review — findings mapped to tracking issues. |

## The one thing to know first

**Both textbooks exist twice.** A LaTeX tree produces the PDFs and a Quarto tree produces the
website:

- `articles/The_Physics_of_Golf/chapters/*.tex` ↔ `articles/The_Physics_of_Golf/quarto/*.qmd`
- `articles/The_Geometry_of_Motion/Volume_*/chapters/*.tex` ↔ `articles/The_Geometry_of_Motion/quarto/*.qmd`

They are maintained by hand and **they have diverged in both directions**. A correction applied
to one tree and not the other is the single most common defect in this repository's history — it
is how a closed issue left the book still stating a golf ball weighs 150 grams while the website
correctly said 45.93 g.

**Any content change must be applied to both trees, or explicitly justified as tree-specific.**
Tracked in [#3499](https://github.com/D-sorganization/AffineDrift/issues/3499), which also carries
the pending owner decision on whether one tree should become canonical.

## Working here

1. **Read [`RIGOR_GUIDE.md`](RIGOR_GUIDE.md).** It is short and it is the contract.
2. **Check the plan** for the corpus you are touching, in [`plans/`](plans/).
3. **Find or file a tracking issue.** Content changes are traceable to an issue the same way code
   changes are.
4. **Apply to both trees.**
5. **Verify.** Numbers must be reproducible, citations must resolve, and the book must still
   compile.

## Status

Live status is **not** duplicated here. It lives in the tracking issues and in
`data/roadmap.yml`, rendered by `pages/development-roadmap.qmd`. Hand-maintained status tables
go stale — this repository has the receipts — so this directory links rather than restates.

Current umbrella epics:

| Epic                                                                | Scope                                          |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| [#3491](https://github.com/D-sorganization/AffineDrift/issues/3491) | Textbook build integrity                       |
| [#3500](https://github.com/D-sorganization/AffineDrift/issues/3500) | Citation and bibliography integrity            |
| [#3509](https://github.com/D-sorganization/AffineDrift/issues/3509) | The Geometry of Motion: technical accuracy     |
| [#3521](https://github.com/D-sorganization/AffineDrift/issues/3521) | The Physics of Golf: technical accuracy        |
| [#3522](https://github.com/D-sorganization/AffineDrift/issues/3522) | Notation, symbol and parameter consistency     |
| [#3532](https://github.com/D-sorganization/AffineDrift/issues/3532) | Website articles: technical accuracy           |
| [#3533](https://github.com/D-sorganization/AffineDrift/issues/3533) | Site framing: claims vs reality                |
| [#3542](https://github.com/D-sorganization/AffineDrift/issues/3542) | Content development: depth and reproducibility |
