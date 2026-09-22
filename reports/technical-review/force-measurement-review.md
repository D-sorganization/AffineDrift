# Force Measurement: Complete Article Review

## Scope and Argument

Issue [#4420](https://github.com/D-sorganization/AffineDrift/issues/4420) belongs
to measurement #4059, corpus #4021 and epic #4009. The complete canonical
`articles/technology-force-measurement.qmd` was read sequentially, including its
accessible overview, five technical parts and references. Its earlier source-only
acceptance was reopened while this substantive review was completed.

The revised argument follows the dependencies from sensor response through a
calibrated contact wrench, momentum balance, model-dependent joint kinetics and
a testable performance hypothesis. Each step has different observations and
assumptions. Pressure distribution remains useful even though it does not
identify tangential traction. Contact loads remain informative even though they
do not uniquely identify muscle work or an effective coaching intervention.

## Findings and Corrections

1. **P1 — Wrench geometry and COP.** Both surface-height signs were wrong for
   the stated upward-positive frame. Derive the corrected equations from moment
   transport. A force at the COP generally needs a remaining normal couple;
   the COP is neither the COM nor the intersection of the wrench central axis
   with the surface. State the nonzero-force exception for the axis and the
   nonzero-normal-load exception for COP. The independently constructed
   800 N vertical-load example recovers the original COP, shows the height-sign
   errors and locates the displaced central-axis intersection.
2. **P1 — Uncertainty and observability.** Replace a universal inverse-load
   relative-error claim with a first-order Jacobian and correlated covariance.
   Bound the linearization away from an uncertain zero denominator. Surface
   height couples through the shear-to-normal ratio. Pressure-only sensing
   cannot uniquely recover tangential traction, and normal pressure plus a net
   wrench still generally cannot identify the bilateral shear/free-couple
   partition. Construct explicit alternatives rather than relying only on an
   equation count. Curved insoles require geometry and interface qualifications.
3. **P1 — Instrument physics.** Full-bridge compensation does not remove
   excitation scaling; explain ratiometric readout. Derive the ideal charge
   amplifier's high-pass response, distinguish step droop from offset drift,
   and give a bounded trial-duration calculation. Distinguish natural frequency,
   usable bandwidth, sampling and anti-alias filtering. A 1300 Hz cosine sampled
   at 2000 Hz is indistinguishable from a 700 Hz cosine. A loaded tare does not
   preserve an absolute standing load unless explicitly restored.
4. **P2 — Standards and specifications.** Replace the claim that no ASTM
   force-platform standard exists with the public scope of ASTM F3109-23,
   including its dynamic/treadmill/stair exclusions. Retain only qualified,
   model-specific AMTI specifications. Applied-load and full-scale denominators,
   typical accuracy and hysteresis, and positioner accuracy and COP uncertainty
   are distinct. Patents establish descriptions of architectures, not independent
   product accuracy or proof that every per-foot component is observable.
5. **P1 — Study quantities and transfer.** Worsfold's 18.2/14.2 N m comparison
   is torque range, not a positive peak. Leary's force at 150 ms was mislabeled
   as RFD; restore the actual RFD statistics and small-sample limits. Bincalar's
   percentages are an origin-dependent simulation metric, with two alternative
   improvements. Brady's gait findings do not establish a universal 9 mm golf
   threshold, and the reported relative errors decreased with speed. Joo's
   feature combinations concern different outputs, not one universal sequential
   improvement. Preserve device, population, coordinate and protocol context.
6. **P1 — Momentum, work and causal inference.** Include gravity and the
   declared golfer/club/ball system boundary. Distinguish footprint free couples
   from moments of separated foot forces. COP velocity is not material contact
   velocity, and COM force power is not generally contact or leg-muscle power.
   Nesbit's four-subject work accounting places hips with the core; its leg
   remainder is not the anatomical lower-limb share. Han reports force as well
   as moment associations. Add Jones's continuous-strategy counterevidence to
   the older two-cluster account; consistency does not establish optimality.
   Observational mediation and strength associations do not prove an intervention.
7. **P1 — Estimation and validation.** Whole-body kinematics estimates a net
   load under segment and external-load assumptions. Karatsidis's walking
   closure curves and ankle-referenced moments do not validate golf free moments.
   Li's subject-held-out golf evaluation is for filtered indoor force targets,
   not moments, impact transients or outdoor transfer. Offline bidirectional
   sequence accuracy does not establish causal real-time prediction. Kim's
   two-person motion-screw comparison does not validate a skill classifier or
   equate kinematic and wrench pitches. The final claim-to-measurement table
   explains what further evidence each inference needs.
8. **P2 — Readable presentation.** Browser interaction exposed a pre-existing
   selector mismatch: the overview button is inside a semantic heading, so the
   adjacent-sibling CSS did not expand its panel despite the updated ARIA state.
   An article-scoped stylesheet follows the panel's actual ARIA state, removes
   the arbitrary expanded-height cap and uses the active theme for its cards.
   Preserve normal display-math type size; longer expressions can scroll within
   the existing container rather than becoming tiny to fit a phone screen.

## Evidence and Access Limits

Primary sources were checked for the retained quantitative claims. Full material
was examined where available; an abstract check is not represented as a full
methodological audit. Sources and the exact sections inspected are also recorded
in the preparation notes under `docs/development/technical-review/`.

- Full-paper material: [Bincalar et al.](https://eprints.soton.ac.uk/499548/1/sensors-25-01283.pdf)
  (model, Section 5.1, equations 35–36, Table 1 and discussion),
  [Worsfold et al.](https://www.jssm.org/volume07/iss3/cap/jssm-07-408.pdf)
  (methods, torque-range definition and Table 1),
  [Nesbit and Serrano](https://pmc.ncbi.nlm.nih.gov/articles/PMC3899668/)
  (joint categories and work accounting),
  [Karatsidis et al.](https://doi.org/10.3390/s17010075)
  (model, fitted distribution curves, reference points and Table 11), and
  [Li et al.](https://doi.org/10.3390/biomimetics11030159)
  (participants, filters, subject folds and evaluation).
- Primary abstracts and metadata: Brady, Davidson, Cudejko, Joo, List,
  Chockalingam, Smith, Ball Parts I/II, Han, Jones 2023/2024, Leary, Johansen,
  Ren and Kim. Their public records are linked directly in the article.
  The retained Rachnavy observational qualification carries forward the primary
  review performed with the paired GRF chapter. Watson is cited for methods and
  terminology, without claiming a new full systematic-review appraisal here.
- Instrument sources: [NI bridge/excitation guidance](https://www.ni.com/en/support/documentation/supplemental/21/making-accurate-strain-measurements-improving-snr-and-determining-optimal-excitation-levels.html),
  [Kistler's time-constant explanation](https://www.kistler.com/US/en/time-constant-resistor/C00000161)
  and linked amplifier manual, [HPS400600 specifications](https://www.amti.biz/product/hps400600/),
  and [AMTI calibration description](https://www.amti.biz/optima-technology/).
  These remain manufacturer descriptions, not independent comparisons.
- Only the [ASTM public scope](https://store.astm.org/f3109-23.html) was accessed;
  no compliance assessment or access to the complete paid standard is claimed.
  AMTI/Bertec/Initial Force patent descriptions were inspected; other retained
  patent and bibliography entries received metadata checks. Correct the Tekscan
  title and remove an unsupported Seitz company attribution. Discard a guessed
  2007 Worsfold PDF that actually contained an unrelated muscle study.

## Independent Checks and Acceptance Boundaries

Eleven instrument/mechanics cases check central-axis geometry, COP finite
differences, covariance cancellation, distinct tangential tractions with equal
pressure, two bilateral partition alternatives, excitation ratios, two amplifier
time constants integrated from their ODE, aliasing/resonance and synchronized
peaks/lever-arm direction. These establish the stated model identities, not
physical device accuracy or human-performance effects. Existing GRF tests also
check the transported COP example.

The final root-configuration Quarto render is tested separately from scientific
validity. The companion render record contains the production verifier and
settled browser checks, with the precise visual-inspection scope. This article
is web-only; no new print-edition acceptance is implied. Source, tests, this
report and the render record are frozen at a committed checkpoint before the
route's findings are rebound. Protected merge and live publication are later
gates. This review does not complete the whole corpus or any whole-book pass.
