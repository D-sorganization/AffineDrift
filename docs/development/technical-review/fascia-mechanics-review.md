# Fascia Chapter: Complete Mechanical and Evidence Review

## Scope and Status

Issue #4341 under #4009, #4021 and Physics #4054. Branch
`fix/4341-fascia-mechanics-rigor`, parent 7ba2db42c76da91b8db563fcf6ee0647b334c327.
The long original LaTeX chapter and Quarto differences have been inspected.
The paired replacement and complete chapter reading are implemented. Preserve chapter labels,
historical links, eight exercises, peer ch29/impact work and immutable publication.
The DCR companion critique review is separately queued as #4340.

## Findings and Decisions

- Replace the combative myth/reality framing with explicit questions, measured
  findings, model assumptions and golfer-level unknowns. The opening denied
  sensory and force-transmission roles later presented as established facts.
- Collagen can be stiff and elastic. Material modulus differs from structural
  stiffness; direction, site, strain range and protocol matter. Withdraw the
  unsupported tissue hierarchy and universal composition percentages.
- A passive stretched tissue exerts force and can supply transient output
  power. It cannot create net energy over a closed passive cycle. Myofibroblast
  contractility exists on different scales from a downswing; do not convert
  pharmacologically stimulated rat strips into golfer power evidence.
- Correct the original 10 cm² to 0.001 m². The stated 0.1 m length gives
  0.125 J at 1 MPa and 5% strain, not 1.25 J. Both are hypothetical calculations;
  neither supports a whole-body 3–7% golf energy fraction. The separate
  10 cm × 10 cm × 5 cm exercise gives 0.625 J and 0.25% of a 250 J clubhead.
- Derive energy by integrating elastic stress. With strain-dependent secant
  modulus, tangent modulus is E + strain*dE/dstrain. Fixed-stress and fixed-
  strain comparisons reverse the stiffness/energy ordering.
- Use a thermodynamically explicit internal-state viscoelastic model. Kelvin
  damping does not prove tissue becomes liquid at slow rates or cannot store
  energy at fast rates. Define relaxation time and loading protocol.
- Show virtual power through tissue length Jacobians, distinguish redistribution
  from dissipation, and demonstrate directional coupling. Mechanical loading
  is not neural co-activation. Include activation, sensory and memory states
  before declaring a control-affine decomposition.
- Replace the false stacked skin/fascia/muscle/tendon/bone anatomy diagram with
  a declared mechanical schematic. Tissue compartments and paths are not one
  universal series chain.
- Remove unsupported injury causation, generic recovery timelines, treatment
  rankings and fascia-specific performance claims. Mechanical, anatomical,
  sensory, training and clinical evidence answer different questions.

## Primary Sources and Reading Boundaries

- Bonaldi et al. (2023), DOI 10.3390/bioengineering10020226, existing bibliography
  key `glossaryFascia2023`. Abstract, sample collection, loading protocol,
  constitutive assumptions and result tables inspected. Four fresh-frozen
  human donors, ages 54–89; composite specimens loaded in directions defined
  relative to layer fibers. Linear-region moduli are directional measurements,
  not universal tissue constants. Failure ramp 0.5%/s; relaxation ramps 1%/s,
  held 300 s. These tests do not calibrate a golf-rate constitutive law.
- Schleip et al. (2019), DOI 10.3389/fphys.2019.00336. Selected histological
  and mechanographic methods, results discussion and species/time-scale
  limitations inspected. Human histology and rat organ-bath contraction tests
  must remain distinct. The authors do not establish a seconds-scale movement
  power contribution. The whole paper is not claimed as read.
- Stecco et al. (2007), DOI 10.1016/j.morpho.2007.05.002. Primary abstract read
  through Europe PMC after PubMed returned an empty page: 20 upper limbs,
  regional innervation differences. Anatomical receptors suggest sensory
  relevance; this is not a measurement of golf proprioceptive contribution.
- Carvalhais et al. (2013), DOI 10.1016/j.jbiomech.2012.11.044. Primary abstract
  read: 37 subjects, latissimus tensioning with passive hip torque/position and
  EMG measurements. Supports a bounded coupling interpretation, not exclusive
  whole-body meridians or a measured golf energy transfer fraction.
- Konrad and Tilp (2014), DOI 10.1016/j.clinbiomech.2014.04.013. Primary abstract
  read: six-week stretching/control study, 49 volunteers; increased range with
  no measured muscle/tendon structural change. It does not exclude all tissue
  adaptation under every intervention.
- Konrad, Budini and Tilp (2017), DOI 10.1007/s00421-017-3654-5. Primary abstract
  read: 17 volunteers, two stretching conditions; reported acute stiffness and
  range changes. This prevents a blanket purely neurological interpretation;
  neither trial isolates fascia or tests golf performance.

Full-text XML for the two open-access fascia papers is held as local scratch
reading material. Missing BeautifulSoup XML support was bypassed using the
standard-library XML parser; no dependency was installed. Source retrieval
alone does not count as full reading. Biological study summaries are
bounded; the comprehensive derivations are independent constructions.

## Implemented Argument and Reproduction

Both editions now connect anatomy, constitutive law, internal state, whole-body
forces, sensing and the impact task. The 13 independent checks derive the SI
energy examples, fixed-stress/fixed-strain reversal, nonlinear tangent modulus,
Kelvin ramp loss, standard-linear-solid energy balance and memory equation,
virtual-power identity and directional coupling counterexamples. The harmonic
solution gives storage/loss moduli and cycle loss; increasing frequency does
not monotonically increase loss per cycle. Perturbations are explicitly about
a tensile bias, and the parameters are manufactured examples.

The shared SVG/PDF replaces a misleading anatomical stack with exact relaxation
and harmonic loops. Reproduce it with
`py -3.12 -X utf8 docs/development/technical-review/build_fascia_mechanics_figures.py`.
Figure parity improves from 14 to 13 missing web figures; other chapters' gaps
remain in the generated inventory. All original print labels and 22 web heading
destinations remain. All eight exercises have worked answers. Five primary
bibliography records were added; the existing Bonaldi entry is reused.

## Validation and Delivery

- Initial RED: ten analytic controls passed; both paired publication checks
  failed against the original text. A harmonic identity check was then added.
- The first full suite found one legacy test that asserted the incorrect area
  and 1.25 J result. Its display-math purpose is retained with the corrected
  area, volume and 0.125 J equations; the independent SI calculation supplies
  the numerical check. Final full suite: **5,137 passed, 29 skipped, 132
  deselected**, 50 existing warnings, **92.88% coverage**. Command:
  `py -3.12 -X utf8 -m pytest tests/ --cov=src --cov-report=xml --timeout=60`.
- Affected fascia/PDF/figure contracts: **45 passed**. Content lint **131**,
  static checks **34**, title audit **636**, links, configured mypy and code
  quality pass. Ruff found one unused test variable and Black one formatting
  change; both were corrected and their checks rerun successfully.
- The complete 546-page book compiles with BibTeX and repeated pdflatex.
  Physical chapter pages **286–298** were visually read in full, plus the
  affected bibliography pages 533 and 537. Missing citation spaces and a
  print line overflow were corrected; affected pages were rerendered and read.
  Existing warnings elsewhere in the book are not claimed resolved.
- Full Quarto chapter: **25 overlapping reading captures**, all visually read;
  113 math spans, 15 display equations, one loaded accessible figure, all
  historical headings, no duplicate IDs or broken internal fragments.
- Canonical public-site gate: **14/14 passed**, zero serious/critical axe
  findings. Independent seven-width/two-theme checks show no document overflow
  or math errors. All 17 display/figure/table regions were exercised at 320,
  390 and 1440 pixels in both themes, including 48 keyboard-scroll checks wherever
  overflow occurred. Representative figure/table/equation endpoints were read
  in both themes. Shared moderate `landmark-unique` and persistent browser
  console findings remain; no zero-console or zero-all-severity claim is made.

Local captures and build drivers are scratch. Canonical chapter sources,
reproducible vector figure, tests, bibliography, book PDF and this audit carry
the implementation. Protected PR delivery is next; the corpus is unfinished.
The preceding DCR PR #4339 protected-squash-merged at
06ad67134fb08841281640d4373d9df1d7cc56ae; exact deployment 34447587020 failed before publication because the docs/ output pruning removed its bound development review. A durable-source relocation and boundary regression are required. Companion critiques remain queued as #4340.
