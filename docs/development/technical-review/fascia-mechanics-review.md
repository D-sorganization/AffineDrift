# Fascia Chapter: Complete Mechanical and Evidence Review

## Scope and Status

Issue #4341 under #4009, #4021 and Physics #4054. Branch
`fix/4341-fascia-mechanics-rigor`, parent 7ba2db42c76da91b8db563fcf6ee0647b334c327.
The long original LaTeX chapter and Quarto differences have been inspected.
Implementation and print/web validation remain. Preserve chapter labels,
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
alone does not count as full reading. Biological study summaries will be
bounded; the comprehensive derivations are independent constructions.

## Validation and Delivery

Independent controls cover SI conversion, boundary-condition dependence,
nonlinear modulus, viscoelastic dissipation, memory, virtual power and coupling.
Publication regressions must fail against the original paired sources before
replacement. Full numerical, repository, HTML and affected PDF QA are pending.

Prior DCR PR #4339 remains open at 7ba2db42 with normal squash auto-merge;
static, JavaScript, links and benchmark checks pass at the last checkpoint,
with Python and browser checks still running. Continue exact delivery
verification at natural checkpoints; do not report the corpus complete.
