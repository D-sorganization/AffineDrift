# Passive Distributed Control Article Review

Issue #4836, epic #4009. Baseline `503fb4fe6e686fcdcc13a8ac56c5039d313fbff6`.
This review covers the complete standalone article, including its old equations,
code, attribution and related-link descriptions. It is separate from the earlier
Chapter 27 review (#4336). The prior route record is preserved in
`passive-control-article-prior-review.json`; its old review commit supplies no
acceptance for this revision. The original-corpus row remains pending until the
new source commit is bound to the claim ledger.

## Scientific Decisions

1. **Attribution and Input:** Remove the unverified Bosch quotation and the
   claim that expertise implies input tending to zero. Declare the retained
   state, input and fixed settings before interpreting drift. Mechanical
   passivity is a storage and boundary-power inequality; autonomous closed-loop
   behavior can still involve nonzero feedback forces. The energy derivative
   requires a storage gradient, not a vector-field norm or a DCR value.
2. **Attraction and Phase:** Separate recurring observations, invariant
   attractors, periodic orbits and contraction. A radial/phase example derives
   the transverse return multiplier and the neutral phase direction. A finite
   downswing is not evidence of an asymptotically stable limit cycle. Return
   maps require a section and reset/relabeling convention.
3. **Impedance and Learning:** Distinguish motion variability, anatomical
   dimension, co-contraction, impedance and feedback gain. The constant-reference
   PD example retains its balancing force at zero error. The scalar stochastic
   example derives a conditional variance, not a universal exploration floor.
   The football pilot's attrition and coupled practice/feedback changes limit
   component-specific attribution; no golf intervention benefit is established.
4. **Walking and Tendons:** Gravity supplies downhill walkers' losses;
   controlled level-ground robots do not establish uncontrolled human behavior.
   Tendon extension need not imply eccentric fascicle motion. Remove the
   unsupported Achilles percentage and a universal load–hold–release optimum.
   Tissue, activity, denominator, interval and uncertainty must accompany any
   energy fraction. Mechanical, electrical and metabolic costs are distinct.
5. **Topology and Initial State:** Choose one horizontal mass, one grounded
   damper, two bilateral linear springs and a massless series junction. Enforce
   equal spring forces algebraically, giving `y = k_m x/(k_m+k_t)` and
   `k_eff = k_m k_t/(k_m+k_t)`. An independent junction initial displacement
   violates that constraint. A force-mismatch relaxation ODE instead introduces
   another damping mechanism; a small denominator is not an algebraic constraint.
6. **Work and Storage:** Include kinetic energy and both springs. Integrate
   signed actuator work and nonnegative damping loss with the motion, giving
   `E-E(0) = W-D`. With the illustrative parameters, initial storage is 1/6 J,
   initial junction displacement is 1/300 m and damping ratio is sqrt(5/3).
   The model is overdamped. An 80 N force interval does not impose an isometric
   hold. Negative actuator work and dissipation exceeding net input work are
   compatible with absorption and depletion of initial storage.
7. **Coupling and Inference:** Separate input-map, inertial, constraint and
   constitutive coupling. Off-diagonal acceleration responses do not identify
   fascia. A prescribed variable stiffness introduces an additional energy
   exchange term. Golf-specific interpretations need declared tasks, retained
   states, perturbations, measurements and falsifiers; the numerical fixture
   does not identify a neural policy, tissue property or coaching optimum.

## Primary Reading and Its Limits

- [Bosch, 2015 publisher preview](https://www.2010uitgevers.nl/wp-content/uploads/2020/10/9789490951276.pdf):
  introduction and explanatory opening through printed page 11. The preview
  acknowledges hypothetical models and motivates integration. It does not
  establish the removed quotation or a zero-input expertise theorem. No full
  book review is claimed.
- [McGeer, 1990](https://courses.ece.ucsb.edu/ECE594/594D_F13Byl/papers/McGeer90.pdf):
  abstract/opening and the local step-map stability discussion on printed page
  70 (PDF page 9), with Table 1 visually inspected. No full-paper audit.
- [Collins et al., 2005](https://groups.csail.mit.edu/robotics-center/public_papers/Collins05.pdf):
  main prose and selected mechanical-power discussion on printed pages
  1082–1085, including visual inspection of the return-map material on 1084.
  No supplementary-material or comprehensive human-cost review.
- [Fukunaga et al., 2001](https://pmc.ncbi.nlm.nih.gov/articles/PMC1088596/):
  abstract and metadata only. Six men walking at 3 km/h provide bounded evidence
  about fascicle/tendon behavior. No full PDF, figures, golfer measurement or
  metabolic-cost measurement was examined.
- [Ker et al., 1987](https://www.nature.com/articles/325147a0): abstract and
  metadata only. The foot-arch observation does not verify the article's old
  Achilles percentage. This is not a claim that the full paper contains no
  Achilles measurements, and no replacement percentage is invented.
- [Manchester and Slotine, v2 manuscript](https://arxiv.org/abs/1209.4433v2):
  PDF pages 1–4 through definitions, Theorems 1–3 and their surrounding proof
  text, and the opening transverse-linearization discussion. Metric and
  invariant-region hypotheses matter. No complete-paper or independent proof
  audit, nor verification of these hypotheses in golf, is claimed.
- [Schöllhorn, Hegen and Davids, 2012](https://opensportssciencesjournal.com/VOLUME/5/PAGE/100/PDF/):
  framing and Methods through printed page 105. The paper reports 24 assigned
  participants, 12 completing all tests/training, and four analyzed per group.
  The conventional group received corrections; the differential groups changed
  movement variation and omitted corrective feedback. These protocol differences
  do not isolate one causal component. No complete statistical reanalysis.

## Numerical and Publication Evidence

The new reusable solver has a recorded failing import test before implementation
and 14 subsequent passing tests. An independent matrix exponential checks every
sampled motion state and force-interval boundary. Additional tests cover
massless-junction balance, compatible preload, work/storage/loss closure,
unforced undamped conservation, nonzero holding force with zero work and invalid
inputs. Integration is segmented at prescribed force jumps. The default trace
has 301 samples and a maximum energy-balance residual of approximately
`7.42e-11 J`. This is a manufactured software check, not physical validation.

The initial two executable Quarto cells were rendered, but the first full
regression found the repository prohibition on executable site cells: 6,748
cases passed and one publication-contract test failed. The page now presents
plain runnable Python, with a checked SVG generated outside site publication.
A generator regression failed before implementation and then passed, checking
repeatable output and readable SVG labels. The existing no-executable-cell gate
is retained unchanged. The first four-cell mobile/desktop,
light/dark browser run passed with no serious/critical axe findings, but manual
inspection still caught a narrow title beside the code menu and an Invalid Date
label. Source-level HTML metadata disables that menu, provides a direct source
link, and suppresses parsing of the unverified publication marker; the article
states the missing publication date explicitly. A lightbox supports inspection of
the energy figure at readable size; a concise caption keeps the plot clear on
mobile, while the surrounding prose retains the modeling qualifications. No site-wide layout or metadata repair is
claimed. Final browser and full-suite results are recorded separately in the
validation record after they run; earlier automated success alone is not visual
acceptance.

Four earlier agy Gemini 3.8 Flash helpers were adjudicated for the screw review.
Two subsequent agy calls failed for insufficient credits; no fresh helper
evidence, purchase or repeated retry is claimed for this article. Scientific
decisions and verification remain with the lead reviewer.
