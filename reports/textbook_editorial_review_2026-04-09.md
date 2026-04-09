# Publication-Level Editorial Review and Rewrite Log

Date: 2026-04-09  
Scope this run: `Drifter Manifesto` landing page, `theory-part1.qmd`, `theory-part2.qmd`  
Reviewer stance: senior commissioning editor, publication standard = advanced graduate / early doctoral text

## Current Publication Judgment

The core verdict remains unchanged from the prior automation pass: the AffineDrift textbook-scale manuscripts are still **not publishable** at graduate or doctoral textbook standard. The project contains real mathematical and biomechanical content, but the editorial problems are structural rather than cosmetic:

- original AffineDrift terminology is still too often presented as if it were settled theory;
- causal language still outruns what the chosen model actually identifies;
- citation density remains too low in the chapters making the broadest interpretive claims;
- web-native explanatory devices still intrude into texts that want to behave like manuscripts.

For this run, the highest-leverage target was the Drifter Manifesto entry sequence because that sequence sets the evidential tone for every downstream claim.

## Files Revised This Run

- `pages/drifter-manifesto.qmd`
- `articles/theory-part1.qmd`
- `articles/theory-part2.qmd`
- `reports/textbook_editorial_review_2026-04-09.md`

## What Changed

### 1. Series landing page rebuilt as a sober guide

The manifesto landing page no longer reads like a promotional hub. It now:

- states plainly that the control-affine form is standard mathematics while the golf-specific interpretation is original AffineDrift synthesis;
- tells readers how to use Parts 1-5 in sequence;
- labels the entire series as technical working manuscripts rather than peer-reviewed consensus;
- distinguishes model-internal claims from broader claims about causation, skill, or motor control.

Editorial effect: better front-door honesty, better structure, and less reputational risk with expert readers.

### 2. Part I now places the framework in the literature

`theory-part1.qmd` was revised to improve citation quality and epistemic discipline:

- added Quarto bibliography wiring to `../references/affine-drift.bib` with the Chicago author-date CSL;
- replaced broad introductory claims with literature-anchored framing around inverse dynamics, forward multibody models, and the known difficulty of moving from net torque to muscle-level inference;
- rewrote the methodological-defense response so the value of the affine structure is diagnostic rather than metaphysical;
- narrowed the scope language so later counterfactual chapters are described as model-relative diagnostics, not physiological proof.

Editorial effect: the chapter now behaves more like a formal theory chapter and less like a revelation narrative.

### 3. Part II now treats ZTCF and ZVCF as model-relative diagnostics

`theory-part2.qmd` received the strongest rewrite this run:

- removed the lay summary widget from the chapter opening;
- replaced the novelty framing with a literature-positioning note tied to control-affine systems, inverse dynamics, and contribution-analysis literature;
- rewrote the introductory sections so ZTCF and ZVCF are justified as reference problems posed against the same equations of motion, not as direct windows into muscular intent;
- deleted or softened rhetoric about "shadow swings," "dominant attractors," and inevitable late-swing motion;
- revised the numerical example so it remains illustrative bookkeeping rather than an implicit empirical claim about real swings;
- clarified why ZVCF is a bookkeeping device for separating configuration-dependent from velocity-dependent terms.

Editorial effect: the chapter is materially more defensible. It still needs deeper revision, but its main claims are now closer to what the mathematics can actually support.

## Remaining Editorial Liabilities

The Drifter Manifesto is still not publishable. The next obstacles are now clearer:

1. `theory-part1.qmd` still contains website-native widgets and high-drama abstract language that should be cut or moved to non-manuscript surfaces.
2. `theory-part3.qmd` and `theory-part5.qmd` still overclaim interpretive reach and use rhetoric that exceeds the evidence currently on page.
3. The series still lacks a consistent notation sheet and a catalog-wide policy distinguishing:
   - established result,
   - modeling assumption,
   - heuristic interpretation,
   - conjecture,
   - and open problem.
4. The golf-specific framework still needs a direct comparative section against inverse dynamics, induced acceleration / dynamic contribution analysis, and muscle-level modeling, stating what each method can answer that the others cannot.

## Recommended Next Pass

1. Rebuild `theory-part3.qmd` so the force taxonomy is restricted to statements that remain valid under clear model-boundary assumptions.
2. Strip remaining website-native widgets from `theory-part1.qmd` and `theory-part5.qmd`, especially where they interrupt formal exposition.
3. Start the chapter-by-chapter citation and quantitative-claim audit for `The_Physics_of_Golf`, beginning with Chapters 1-10 and 24-31 as previously prioritized.

## Bottom Line

This run improved the series at the right level: not by polishing prose locally, but by narrowing claims, restoring literature context, and making the counterfactual machinery answerable to the model that defines it. The Drifter Manifesto still requires substantial restructuring before publication, but Parts 1-2 are now closer to a defensible technical manuscript and farther from a manifesto voice.
