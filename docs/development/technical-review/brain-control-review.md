# Brain Control: Complete Mechanics and Neuroscience Review

## Scope and State

Issue #4347 under epic #4009, corpus #4021 and Physics #4054. Both original
editions were read completely; the original print chapter was approximately
5,761 words. The complete replacement, numerical controls, final print/web
reading and local checks pass. Protected delivery remains pending. Branch
`fix/4347-brain-control-rigor`, parent `1cc701de1b44c581634b860dddcc0d349c77c31a`.
The source is ch24; the compiled book numbers it Chapter 28. Preserve peer
Chapter 29/impact work, immutable publications and scientific-authority pins.

## Findings and Decisions

1. The original forward predictor equated a next state with a continuous-time
   derivative. Restore the current state and time increment: x-next = x + dt F.
   Distinguish a discrete transition from a vector field and local second-order
   truncation from first-order accumulated Euler error. Measurement innovations
   compare the same sensory quantity at the same timestamp.
2. Define the torque-level state with q/v, positive-definite M, complete bias c,
   gravitational g and actuator map B. Drift includes the velocity block; it is
   neither free energy nor a substitute for muscle work. Contact requires its
   corresponding constraint equations. Neural drive, activation, muscle/tendon
   memory and moment-arm force mapping are separate objects. Torque affinity
   does not automatically imply affinity in every neural input.
3. The input matrix is generally rectangular and has a zero position block.
   Replace an ordinary inverse with bounded, weighted allocation and an explicit
   desired-minus-achieved residual. An exact derivative requires b in G U.
   Weights carry units/priorities; regularization changes the optimization.
   Full joint inverse dynamics still requires feasibility and trajectory feedback.
4. For G = (0,0,1,1)^T and b = (0,1,3,0)^T, least squares gives 1.5, or 1 under
   |u| <= 1, leaving (0,1,2,-1)^T. The unachievable position derivative and
   conflicting acceleration requests are distinct. Instantaneous rank deficiency
   does not prove finite-time uncontrollability: acceleration changes later position.
5. Preparation can set feedforward commands and feedback gains. Learning a policy
   does not make its execution open-loop. Delayed observations require timestamp
   matching and propagation; prediction cannot identify an unobservable state.
   The illustrative projected proportional policy is not a universal neural law.
6. Preserve earlier 20–45/50–100/>100 ms EMG onset examples and their experimental
   bounds. Parallel pathways are not a serial delay sum. Onset is different from
   useful task authority; adding a full force-development delay to a latency
   already measured through force onset double-counts processes.
7. Reaction time and flicker thresholds do not define a neural clock. Pure delay
   has unit magnitude and phase -omega d: 50 ms gives -90 degrees at 5 Hz and
   -180 degrees at 10 Hz. Stability depends on the complete specified loop,
   including plant/controller gain and phase. A shaft mode is not the whole plant.
8. Derive finite-horizon response using the state-transition matrix and input
   integral. A newly informed input begins only after its defined delay; prepared
   activity and other pathways remain. The changing mechanical kernel can rotate,
   amplify or cancel contributions. An instantaneous drift ratio cannot replace it.
9. With zero initial activation and a unit step, a = 1-exp(-h/tau) and normalized
   impulse is h-tau(1-exp(-h/tau)). For tau = 50 ms and h = 10/40/100 ms, the
   impulses are 0.937/12.466/56.767 ms. A constant 10 N m scale and h = 40 ms give
   0.12466 N m s, not a club-speed change without a mechanical response map.
   These are manufactured examples, not measured human timing constants.
10. Derive event-time perturbation from the implicit strike surface and include
    the resulting output shift. Require a smooth transverse pre-impact crossing;
    grazing and changing contact modes need separate treatment. Fixed-time speed
    and speed at impact are different comparisons.
11. Replace universal force-noise, proprioceptive-acuity and club-speed percentages
    with covariance propagation J Sigma J^T. Equal component SD 0.02 gives task
    variances 0.0004/0.0001/0.00076 under correlations 0/-0.75/0.9 and a normalized
    sum output. Correlation, sensitivity and observation error must be measured.
    Large drift does not establish stability, precision or automatic robustness.
12. Internal models and neural-region assignments are functional hypotheses, not
    anatomical implementations of textbook equations. Bound cerebellar LTD and
    motor-cortical population claims to their studied tasks. Remove universal
    clinical inability statements and the unverified Feynman epigraph.
13. Derive a linear-predictor squared-error gradient with a signed update. This
    mathematical rule does not prove synaptic LTD or its necessity for learning.
    Different output nonlinearities, losses and eligibility assumptions change it.
14. Distinguish sensory prediction, task and reward errors. State the variational
    free-energy identity, support conditions and nonnegative KL term; it is an
    information quantity, not tissue energy. It does not prove neural implementation.
    Predictive processing, active inference and optimal feedback are not interchangeable.
15. An ideomotor account motivates action-effect hypotheses; it does not uniquely
    select muscle commands or prove a universal coaching instruction. Comparisons
    require specified cues, skills, retention, transfer and measured outcomes.
16. A temporal-difference example gives terminal reward errors 0.2 versus 0.8 for
    the same reward 1 under expectations 0.8 versus 0.2. A good shot does not
    identify which part of the routine deserves credit. Dopamine is not a simple
    good/bad-shot indicator or a complete scalar implementation of this model.
17. Recruitment order does not prescribe a 100–500 ms serial wait. Recruitment
    speed, discharge behavior, prior activation and force transmission jointly
    determine force development. Explosive isometric tibialis evidence cannot be
    assigned directly to wrist timing during golf.
18. Separate mechanical work, metabolic cost and computation. State dimension,
    neuron counts and movement duration do not specify optimizer solve time.
    Explain how inverse inertia, constraints, impedance, material state, sensing,
    preparation and feedback jointly shape the task. Replace all ten exercises
    with corrected premises, worked answers and explicit empirical limits.

## Primary Evidence and Reading Boundaries

No fresh full-paper reading is claimed for the sources below. Metadata, abstracts
and identified primary excerpts support deliberately bounded statements. Earlier
latency-review references and their qualifications are retained.

- Wolpert, Ghahramani and Jordan (1995), Science 269:1880–1882,
  [DOI](https://doi.org/10.1126/science.7569931): author-lab publication metadata
  and first-page primary PDF text read. Human hand localization in darkness with
  externally imposed forces supports predictive state estimation; no golf law.
- Churchland et al. (2012), Nature 487:51–56,
  [primary record](https://pmc.ncbi.nlm.nih.gov/articles/PMC3393826/),
  DOI 10.1038/nature11129: Nature metadata/summary, author-PDF first-page abstract
  and primary search excerpts of results/methods read. Monkey reaching population
  dynamics motivate alternatives to a fixed parameter code; no unique golf code.
- Del Vecchio et al. (2019), J Physiol 597:2445–2456,
  [official abstract](https://physoc.onlinelibrary.wiley.com/doi/10.1113/JP277396):
  complete abstract/key points and metadata read. Twenty men, tibialis anterior,
  explosive isometric task and decomposed high-density EMG. No wrist-time transfer.
- Friston et al. (2010), Biol Cybern 102:227–260,
  [author institution](https://discovery.ucl.ac.uk/id/eprint/20040/),
  DOI 10.1007/s00422-010-0364-z: abstract/metadata only. A specified theoretical
  formulation; the chapter derives the identity separately. The existing similarly
  named key cites a different review and was not repurposed.
- Pruszynski et al. (2011), Nature 478:387–390,
  [DOI](https://doi.org/10.1038/nature10436): official abstract and metadata read.
  Monkey perturbations and human stimulation support rapid multijoint integration
  around 50 ms in those experiments, not golf clubface correction.
- Todorov and Jordan (2002), Nature Neurosci 5:1226–1235,
  [DOI](https://doi.org/10.1038/nn963): official abstract read. Task-dependent
  variability is a model prediction conditional on cost, dynamics and uncertainty.
- Schonewille et al. (2011), Neuron 70:43–50,
  [primary record](https://pmc.ncbi.nlm.nih.gov/articles/PMC3104468/),
  DOI 10.1016/j.neuron.2011.02.044: author-institution metadata and primary search
  discussion excerpt read. Three LTD-deficient mutant lines retained learning in
  tested paradigms; compensation was not excluded. Direct PMC access presented a
  CAPTCHA and was not bypassed. This is not a full-paper reading claim.
- Schultz, Dayan and Montague (1997), Science 275:1593–1599,
  [primary abstract](https://pubmed.ncbi.nlm.nih.gov/9054347/): abstract read,
  DOI 10.1126/science.275.5306.1593 verified. Reward prediction, not routine-level
  causal credit from a successful shot.
- Hommel et al. (2001), BBS 24:849–878,
  [primary metadata](https://pubmed.ncbi.nlm.nih.gov/12239891/): Cambridge PDF
  abstract and PubMed metadata read; DOI 10.1017/S0140525X01000103. The existing
  key `hommel2009theory` is misleadingly named but its 2001 metadata is correct;
  retaining it avoids breaking other citations. No 2009 paper was substituted.

## Validation and Failure History

- New numerical/source tests were RED before the reproducer and rewrite. An
  initially handwritten expected residual had the wrong second-component sign;
  direct desired-minus-achieved arithmetic corrected the test. Nine mathematical
  controls then passed, followed by all 11 new controls with paired source checks.
- Final `py -3.12 -X utf8 -m pytest --cov`: 5,202 passed, 29 skipped,
  132 deselected; configured src-plus-scripts coverage 79.29% exceeds the existing
  75% gate. A report restricted to src is 92.9%; previous chapter reports used
  src-only coverage, so their 92.88% figure is not comparable to the broader total.
  No production code, coverage configuration or floor changed.
- Focused brain/parity tests: 34 pass. Existing sensorimotor content contract:
  6 pass. Complete content-lint lane: 131 pass, 4 skips. Static CI contracts:
  34 pass. Title audit: 636 sources pass. `scripts.link-checker --site-gate` passes.
- Configured mypy checks 91 source files successfully. Ruff and Black100 pass for
  new helper/tests. Figure-label placement was split into a helper to respect the
  50-line function limit; final maximum is 46 lines and all 11 brain tests repass.
- Full pdflatex/bibtex/two-pdflatex build succeeds, 544 pages. All chapter pages
  395–408 (printed 365–378), plus bibliography 528/536, were visually read. The
  final chapter log has no overfull/underfull or undefined-reference warnings.
  Arrow-to-label intersections in the initial figure were corrected using actual
  text-boundary clipping before the final print and web reading.
- Root selected-route Quarto render succeeds. Two duplicate historical/autogenerated
  heading IDs were found and corrected using explicit heading IDs. All 16 old web
  headings plus bibliography destination survive; all 18 explicit print labels
  and compatibility aliases survive. Never rerun the scratch converter blindly:
  its intermediate output predates the final duplicate-ID correction.
- Final web: 106 math items, 14 displays, one loaded descriptive SVG; no duplicate
  IDs or broken fragments. All 27 overlapping desktop captures were visually read.
  Seven widths (320–1920) in both themes pass; 90 math/figure region cases and
  50 keyboard-scroll checks pass. Mobile figure endpoints, dark wide equations and
  event formula endpoints were visually inspected. Full-size vector link remains.
- Canonical `scripts/verify-public-site.js`, axe fail mode: independently inspected
  all 14 final brain-route records, HTTP 200, zero failures/overflow and no high
  axe violations; axe scans once per route. The first copied scratch manifest
  still targeted the triple chapter; it was corrected and the brain route rerun.
  A local evidence parser initially assumed axe fields existed on every record;
  corrected it for the verifier's per-route scan policy and inspected all records.
- Exhaustive browser scan retains the shared moderate landmark-unique finding
  and accumulated session console messages; canonical fresh-page verification
  reports no gate failure. Existing deployment polyfill cleanup was applied only
  to local chapter output. No site-wide CSS or verifier policy was changed.
- Render-only date/format/digest churn in six generated files was identified and
  restored to HEAD bytes. Canonical scientific authority and immutable assets
  remain unchanged. Scratch screenshots/logs/converters are not publication inputs.

## Delivery and Continuation

Implementation 261925d2695594fd00eac89325f57ec37f6b25fd passed normal commit hooks.
Replay onto the parent squash preserved tree 50912a2fcdba0fae0f4c4331bd98ca4c74dbbc3c.
The central development-log validator found a missing SHA in this new entry,
now corrected, plus pre-existing peer #3903/#3902 metadata omissions. The local
shared-script path is absent; the central checker was run explicitly. Peer entries
were preserved. PR #4348 passed protected checks and squash-merged as
688dda81c3f0c38759d9994cbc0d5c0cd0478bd2. Exact deployment 34460868604 is in
progress; live verification remains pending. Parent triple PR #4346 published
successfully in deployment 34456863592 at 8808f68a; all 956 live records in
artifact 10144974541 were inspected. That successor also verifies the retained
fascia/DCR corrections after their original run's isolated CSS HTTP 503 and
cancelled retry. Continue the affine/constraint chapters and queued DCR critiques
#4340. The corpus remains unfinished.
