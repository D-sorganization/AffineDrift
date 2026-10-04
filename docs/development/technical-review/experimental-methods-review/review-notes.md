# Experimental Methods Review Notes

Issue #4898, epic #4009, corpus #4021. Complete original and revised source chapter 7 read. No source acceptance yet. Worktree AffineDrift-experimental-methods-review; parent camera source 15b8c7bd8. The ordinary source goal remains active.

## Findings and Adjudication

The original residual-analysis intercept has length units, not frequency. The corrected explanation distinguishes the fitted ordinate intercept from its horizontal intersection with the residual curve; no universal optimum is asserted. The CoP derivation now declares a right-handed upward frame, signed height and consistently ground-on-person wrench. Simultaneously negating force and moment preserves CoP; the original expression could match a different signed-height convention, so reject the helper's claim of universal impossibility. Specific force is an observation at the sensor point and requires orientation and gravity to recover kinematic acceleration. Physiological electromechanical delay is not an instrumental clock offset.

First read-only agy Gemini 3.8 Flash helper completed exit0. Accepted the bounded CoP, residual-analysis, forward/backward response, specific-force and timing concerns. Rejected its claim that copied neighboring derivatives become zero; its malformed universal cutoff compensation formula; unsupported STA rotation magnitudes; its purported residual-intercept limit expression; and calling the established specific-force relation conjectural. Higher cutoff is not automatically required for acceleration.

Second Flash helper rederived the wrench and IMU relations and two numerical examples of each. Lead checked the component algebra. Reject its claim that cross-product algebra itself changes sign in every downward right-handed frame; all vectors must be transformed consistently. Reject its suggestion that the accelerometer relation applies only at the center of mass: it always describes the sensor location; lever-arm terms are required only to transfer acceleration to another point. Do not adopt its unsourced universal force threshold. General sloped planar contact is handled by a plane-aligned frame; arbitrary nonplanar contact needs a different model.

## Source Reading Scope

SciPy official butter and sosfiltfilt API pages read in full for design frequency, second-order sections, axis, padding and offline forward/backward behavior. These are software semantics, not biomechanical cutoff recommendations.

Peters et al. (2010), DOI 10.1016/j.gaitpost.2009.09.004: PubMed abstract and metadata read. It describes more than 30 mm thigh and up to 15 mm tibial STA, with small and selected populations. No full-paper review claimed. Existing Chiari/Leardini entries remain; their detailed experimental data have not been newly replicated.

Winter (2009), publisher DOI 10.1002/9780470549148 and chapter pagination verified at Wiley. Scoped original-author text for residual analysis in Section 3.4.4.3 (printed pp. 71–73) was read via the indexed book-text mirror at https://studylib.net/doc/28101400/biomechanics-and-motor-control-of-human . It distinguishes the ordinate intercept from the horizontal intersection. No full textbook read or copying of its figures claimed.

Kristianslund et al., DOI 10.1016/j.jbiomech.2011.12.011: author-institution six-page manuscript at https://www.klokeavskade.no/globalassets/publications/kristianslund_2012_j-biomechan_effect-of-low-pass-filtering-on-joint-moments-from-inverse-dynamics.pdf . Abstract and initial methods (physical pp. 1–3 portions) read; later excerpt inspected, not a complete study replication. The statement retained concerns condition-sensitive inferred moments and rankings in sidestep cutting, not a universal filter mandate. The later critical letter was found but direct PMC access returned a verification page; no full-letter reading claimed.

Besomi et al. (2020), DOI 10.1016/j.jelekin.2020.102438: PubMed abstract and metadata read. It supports multiple task-dependent normalization choices; no complete CEDE matrix or clinical certification is claimed. Analog Devices specific-force/dead-reckoning technical section consulted; the displayed algebra is independently derived with an explicit world-from-sensor rotation.

## Executable Listing

TDD: original listing produced 9 failed and 8 passed targeted cases. Integer positions lost fractional values; finite/shape/order contracts were missing. Revised listing converts to floating data, validates finite uniformly sampled inputs and filter parameters, uses SOS on axis zero, declares single-pass cutoff semantics, and marks endpoint derivatives unavailable. All 17 targeted cases pass, including the analytic half-amplitude sinusoid after two passes and derivatives within discretization tolerance. Neither passing these cases nor replacing boundary values proves experimental accuracy. Full chapter compilation, final editorial review, numerical checks and frozen regression remain.

## Final Mechanics Helper

Third read-only Flash helper completed. Its claimed CoP sign defect is contradicted by its own correct expansion and all three numerical outputs; reject the defect. The gravity equation was already consistent; adopted an explicit upward-world gravity vector and an explicit same-frame/same-origin action/reaction qualifier. Reject calling gravity direction a different physical convention, unsupported calibration matrix dimensions, universal filter bands and scope expansion. The plane and calibration assumptions are already explicit. Analog Devices full relevant dead-reckoning, loose-coupling and application-limit sections read; do not adopt its swivel-chair motion constraints as general inertial-navigation guarantees.

Fourth Flash helper completed. Accepted specifying one scalar coordinate in the residual formula. Reject its short-record defect: every valid order is at least one, padlen at least six, and every zero/two-frame input is already rejected. Reject its incomplete SOS default formula: SciPy compensates the odd-order zeros/poles at the origin; our explicit padding is permitted and not a general edge-accuracy guarantee. Do not add unsourced rotational STA ranges. Black100 and Ruff pass; 17 listing cases still pass after final text edits. Woodman Cambridge TR696 scoped Sections 2, 6.2 and 8 read for corroborating orientation/gravity/drift limits, not added as a new citation or used for current device performance.

## Scoped PDF Verification

Final 73-page Volume III inspected physically on pages 3–6 (updated preface and complete TOC), 51–57 (complete Chapter 7, listing, equations, exercises and schematic), and 71–73 (all 38 printed bibliography entries). No unresolved references. Initial diagram-label collisions and long new URL overflow corrected in canonical source, rebuilt and re-inspected. Existing warnings in unchanged Chapters 6, 8, 9 and 10, duplicate figure destinations and missing-author/package-name notices remain outside this chapter acceptance. Four manufactured algebra/filter-response identities each pass 100 cases with maximum residual 4.27e-14. These checks do not establish experimental accuracy.
