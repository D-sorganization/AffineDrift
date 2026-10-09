# Impact Chapter Preparation During #4836 Validation

Read-only preparation, not a claimed issue, source edit, accepted review or corpus credit. The 1,949-word original-index chapter is the next longest source carrying Full Technical Audit Pending; earlier #4725 corrected only its launch weights and inverse sensitivity. The complete current chapter was read on 2026-10-03. Current SHA-256: b5ebc251d65548b3316819900a03ac5bf14b5ccffb0fd73c3298d97ec4d51e70.

## Candidates Requiring Adjudication

- The opening assigns a forward/inverse architecture to every optical/radar system. Product-specific evidence is needed; the physical collision model does not establish every instrument's implementation.
- Define axes, handedness, face-normal and contact-point velocity before D-plane statements. Collinear vectors do not define a unique plane/normalized spin axis. Centered, initially stationary, isotropic/contact assumptions and off-center coupling need explicit boundaries.
- The diagram uses -2.6 degrees where its displayed 0.76(-2)+0.24(-6) rule yields -2.96 degrees. Correct a manufactured diagram without inventing a measurement.
- Spin loft is acos(n dot p). In target-frame spherical angles its cosine is sin(alpha)sin(lambda)+cos(alpha)cos(lambda)cos(face-path), not generally cos(face-path)cos(dynamic loft). Old coordinate conventions cannot be silently equated to modern launch-monitor definitions.
- A scalar normal impulse predicts the normal ball-velocity component under its uncoupled assumptions. Total ball speed can contain tangential impulse. The listed mass/COR/loft table is not a universal physical ceiling and does not alone prove an instrument faulty. Normal effective mass depends on inertia/strike geometry; no automatic shaft-mass correction.
- The gear simplification includes an erroneous times 100 relative to its cited author's Equation 2a. Also distinguish a historical sample standard deviation from a universal +/-2.5% model-accuracy guarantee. An optical strike measurement informs an inverse model; it does not eliminate contact-model discrepancy.
- Spin empirical fits, spin-axis decomposition, loft-times-200 and yardage/shot-shaping claims require units, axes, domains and provenance. Avoid assigning universal saturation thresholds or optimal instrument priorities.
- Derive the inclined-plane path example with declared geometry. A real curved swing need not be represented by one fixed plane or the specified product algorithm.

## Bounded Primary Reading

[Tutelman's original 3-D model](https://www.tutelman.com/golf/ballflight/3dlaunch.php): read complete main-page text/equations and nomenclature footnote; linked inverse-model and approximation appendix and image pixels were not read. The author explicitly distinguishes his historical loft terminology from later nomenclature and describes a later TrackMan comparison. This is an author model, not a general experimental validation or proof of a hard smash ceiling. Do not describe its origin as fitted to that later comparison without evidence.

[Tutelman's gear model, part 1](https://www.tutelman.com/golf/ballflight/gearEffect1.php): read complete main text/equations and numeric table, not linked source data or image pixels. Equation 2a is 16.4 V_b x in the declared mph/inch units, without times 100. The 2.5% figure describes a filtered historical inertia/depth sample, not all current drivers or total prediction error. Conditional no-slip/separation reasoning requires mechanical scrutiny.

Henrikson et al. (2020), DOI 10.3390/proceedings2020049027: direct MDPI opens failed. A primary publisher search result supplied abstract, model opening and conclusion excerpts only; no full-text/figure audit is claimed. It compares compliant-contact predictions with measurements and explores friction dependence. Existing bibliography omits authors. Before editing, account for the bibliography and compiled PDF frozen by the prior radar review; do not silently rewrite old acceptance digests.

## Reuse and Delivery Boundaries

The previously reviewed articles/impact-mechanics-and-ball-flight.qmd already treats contact mobility, normal/tangential coupling, geometric versus mass centers, and conditional gear effect. Read those sections and their original evidence before creating duplicate derivations or code. Current work remains #4836 and delivery of #4840; do not start an impact rewrite until those checkpoints are secure.

Follow-up comparison read the existing reference sections Contact-Point Effective Inverse Mass, Normal Restitution and Its Scalar Limit, empirical horizontal/vertical launch ratios and Spin Axis Geometry. They already distinguish the coupled contact operator from its scalar limit and reject a universal trigonometric spin-tilt identity. This comparison is a consistency lead, not new independent acceptance of that full reference.
