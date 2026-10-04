# Bosch Insertion-Plan Technical Review

Issue #4877 belongs to epic #4009 and corpus review #4021.
The complete 1,615-word baseline insertion plan was reviewed, including all six destination groups.
The revised source is `articles/bosch_integration/cross_references/existing_chapter_additions.tex`; its two companion bibliography fragments were checked for the identities used here.
This is an editorial insertion plan, not an automatically included chapter or a public route.
The six destination chapters were not rewritten or newly certified by this review.

## Argument and Corrections

The useful central question is how tissue mechanics, neural action, task demands and environmental interaction jointly shape movement.
The revision preserves that question while separating a mechanical possibility, a control model, a biological mechanism and an intervention outcome.
None follows automatically from the others.

1. **Attribution:** Unverified quotation-style assertions and universal training prescriptions become explicitly identified manuscript synthesis. Bosch motivates integration; his framework does not prove a golf intervention or a universal neural algorithm.
2. **Force Transmission:** Anatomical continuity, an actual load path and neural control are separate claims. A passive spring illustrates force transmission without a new command. A coupled response does not identify fascia as its cause.
3. **Structural Stability:** An elastic-network analogy does not establish equilibrium or stability. The revised sufficient local test requires a smooth conservative system, positive definite kinetic energy, a regular stationary constrained equilibrium and positive definite reduced second variation. Constraint curvature and preload matter; semidefinite and changing-contact cases need further analysis.
4. **Control and Attractors:** Closing a plant with feedback produces a dynamical system. Attraction does not establish cost optimality. A nondimensional scalar example gives two attracting feedback policies with different costs, without claiming incompatibility between optimal control and dynamical systems.
5. **Learning and Transfer:** Similarity must be stated in terms of the relevant forces, velocities, contact, information and outcomes. Retention and transfer are distinct from practiced-task improvement. Neither exact-task-only learning nor universal failure of conditioning or part practice is established.
6. **Intrinsic Response:** Mechanical response before a new feedback command can include already activated muscle as well as passive tissues. Fixed activation does not remove length, velocity or internal-state dependence. No universal latency or physiological optimality is asserted.
7. **Co-Contraction:** With fixed equal/opposite moment arms and admissible bounded forces, adding a common force increment preserves net torque. This instantaneous allocation identity does not establish realizable commands or universal changes in stiffness, joint loading or metabolism.
8. **Sequencing and Power:** Simultaneous equal/opposite actuator torques on two fixed-axis rotors need not deliver equal/opposite powers. Segment-speed peak order therefore cannot establish non-overlapping action, a neural cause or an optimal training rule. Real segment balances also need joint-force power, external loads and frame conventions.
9. **Passivity and Adaptation:** Declare the subsystem boundary, storage and effort-flow pairs. Changing stiffness or preload may exchange energy. A measured stiffness change does not identify tissue adaptation, prior activation, geometry or feedback as the cause, and a mechanism does not establish a task benefit.

The scalar example is deliberately deterministic and nondimensional.
The surrounding text retains time dependence, partial observations, estimator state and stochastic descriptions where relevant.
Quadratic effort penalties and joint mechanical power are not treated as measured metabolic expenditure.
For golf and humanoid modeling, the resulting argument asks what changed, what was held fixed and what observation would contradict the proposed explanation.

## Primary Reading and Its Limits

Reading took place on 2026-10-04.
The following are primary materials or publisher-deposited metadata; the limits are part of the record.

| Material                                                                                                                                                                   | Inspected Scope                                                                                                                                              | Use and Limit                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Bosch 2020 Publisher Preview](https://www.2010uitgevers.nl/wp-content/uploads/2020/10/9789490951597.pdf)                                                                  | Copyright/ISBN, contents and introduction, printed pp. 11–17                                                                                                 | Running-based agility scope, limits of broad theories and contextual whole/part practice. Not a full-book review or golf intervention evidence.                                 |
| [Bosch 2015 Publisher Preview](https://www.2010uitgevers.nl/wp-content/uploads/2020/10/9789490951276.pdf)                                                                  | Copyright/ISBN and opening material                                                                                                                          | Bibliographic identity and broad strength/coordination framing. No full-book or intervention-effect verification.                                                               |
| [Haken, Kelso and Bunz 1985](https://ccs.fau.edu/hbblab/pdfs/1985_Haken_Kelso_Bunz_Biol_Cyb.pdf)                                                                           | Opening, sections 1–2 and surrounding section-3 text                                                                                                         | Rhythmic hand coordination, not a universal neural-control model. Extracted equations contain OCR artifacts; none is reproduced in the insertion plan. No complete proof audit. |
| [Todorov and Jordan 2002](https://roboti.us/lab/papers/TodorovNatNeurosci02.pdf)                                                                                           | Printed pp. 1226–1228, opening control assumptions and discussion of dynamical systems; [publisher metadata/abstract](https://www.nature.com/articles/nn963) | Supports a declared control problem and compatibility with dynamical descriptions. No full empirical reanalysis or identification of a golfer's objective.                      |
| [Rack and Westbury 1974](https://pubmed.ncbi.nlm.nih.gov/4424163/)                                                                                                         | Full abstract and bibliographic metadata                                                                                                                     | Activated cat-muscle short-range stiffness. No full-paper reading, human impedance estimate or training prescription.                                                           |
| [Hogan 1984 Author-Lab Copy](https://newmanlab.mit.edu/wp-content/uploads/2017/06/1984-adaptive-control-of-mechanical-impedance-by-coactivation-of-antagonist-muscles.pdf) | Indexed primary opening/abstract excerpt; publisher-deposited Crossref metadata for DOI 10.1109/TAC.1984.1103644                                             | Forearm/hand coactivation and impedance example. Direct PDF retrieval failed; no full-paper reading claimed.                                                                    |
| [Loeb 1995 DOI](https://doi.org/10.1109/IEMBS.1995.579743)                                                                                                                 | Publisher-deposited Crossref metadata only; IEEE full text inaccessible                                                                                      | Corrected conference identity, volume and pages. Not evidence of paper content; not cited by the revised prose.                                                                 |

The 2020 ISBN is corrected to 978-94-90951-59-7 in the golf fragment; the 2015 ISBN is corrected to 978-94-90951-27-6 in both fragments.
Both Todorov entries now use the registered title and DOI 10.1038/nn963.
The golf Loeb and Hogan entries now match their checked publication identities.
The HKB typo variants are replaced by the existing canonical `HakenKelsoBunz1985` key after checking consumers.
Rack/Westbury is added to both fragments using the inspected author metadata.
Unrelated bibliography entries and existing Scholz aliases are not newly certified or broadly cleaned up.

## Independent Checks and Presentation

`bosch-insertion-independent-checks.json` records exact SymPy checks of the scalar cost, torque invariance and ideal-rotor momentum/power identities.
The manufactured rotor fixture changes kinetic energy by 11/4 J while conserving total axial angular momentum under its assumptions.
These are mathematical checks, not empirical observations.

Two local QA wrappers compile the actual fragment with each companion bibliography using pdflatex, biber and repeat pdflatex passes.
Each resolves the six prose citation keys; an additional QA-only Loeb citation exposes its corrected metadata.
Both final builds exit zero, produce five pages and have no undefined citation/reference or overfull-box warnings.
All five golf-wrapper pages were visually inspected, including equations and all references.
PyMuPDF comparison found identical extracted text and identical native RGB page pixels between the two wrappers.
This validates the fragment presentation under the QA wrappers, not integration into all destination books or website rendering.

The first golf-wrapper build used an unquoted PowerShell output-directory argument and wrote into a literal `$taskRender` directory; the subsequent biber command failed.
That failed build and logs are preserved under the local QA directory.
Quoting the interpolated argument corrected the command; the failed attempt is not counted as success.
No TeX installation or update was performed.

## Delegation and Adjudication

Six successful `agy --model gemini-3.8-flash-low --print` helpers handled inventory, counterexample preparation, bibliography consistency, algebra, candidate bibliography entries and revised-prose review.
They received supplied text and had no source-editing or delivery authority.
Their outputs are candidates, not independent evidence.

Lead review rejected helper suggestions claiming that optimal control and attractor descriptions are incompatible, that conservation alone disproves non-overlap, and that asymptotic stability is a universal prerequisite for finite control cost.
It also rejected a claimed equilibrium requirement for instantaneous force allocation; universal monotonic co-contraction effects; strict positive Hessian as a necessary stability condition; and an unverified exclusively active, exactly zero-delay definition of preflex.
The rotor equations were correct: the accepted improvement was to say explicitly that the actuator absorbs power **from** the proximal rotor.
Useful suggestions included force-capacity limits and clearer estimator/noise scope.
Bibliography candidates were checked against the inspected metadata, including the Rack author initials, rather than copied wholesale.

Raw helper outputs, compilation logs, wrappers, page images and metadata responses remain in `docs/development/technical-review/` in this worktree.
The durable validation record distinguishes source, mathematical, presentation and repository checks from protected delivery.
No production code or tests were added for this editorial correction.

A seventh Flash helper audited this report. Its proposed contradictions between scoped bibliography metadata checks and compilation, and between distinct bibliography files and identical selected rendered entries, were rejected: these are separate claims, and the actual paired PDFs were compared. The report explicitly limits acceptance to this plan. Its useful attribution concern was resolved by identifying the rejected statements as helper suggestions.
