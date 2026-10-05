# Joint Kinematics and Soft-Tissue Review

Issue #4901; epic #4009; corpus #4021. Lead read the complete original and revised chapter, derived the corrections and inspected all helper answers. Two read-only agy Gemini 3.8 Flash reviews and exit records are retained. This is a source/mathematics audit, not experimental biological acceptance.

## Conceptual Connections

Declare relative reference-frame derivatives and v_s=p_dot-omega cross p before extracting a screw axis. The axis is an instantaneous velocity-field line, not an anatomical hinge, surface contact path, or moving-origin trajectory. Pure translation has no unique finite line; rest does not identify a motion direction. A manufactured one-coordinate transform demonstrates migrating ISA without inventing a knee rolling ratio. The joint representation changes the force inference problem through contact, moment arms and constraints; observed motion alone does not identify its cause.

Replace universal knee rotation/migration and shoulder translation assertions with explicitly scoped model questions. Scapular point-on-surface equations remove their independent rank, not an assumed pair of freedoms. Retain contact-mode and whole-chain limitations. A four-coordinate published scapular model admits winging, showing why two surface position coordinates alone do not define complete scapular motion.

The ligament law uses a single force-scale parameter in both branches, making force and slope continuous. Strain stiffness has units N; the length tangent divides by zero-load length. Joint restoring stiffness also includes changing moment-arm geometry. The spinal compliance example declares small conjugate displacement/wrench increments, restoring sign, reference point, preload and local quadratic-energy assumptions. No tissue-failure or injury prediction follows.

## Evidence Read and Limits

Modern Robotics official Twists Parts 1 and 2 transcripts read in full (Northwestern, section 3.3.2), especially spatial/body representation and screw normalization. Bibliographic URL: https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-2-twists-part-2-of-2/. The chapter derives the velocity field independently.

Blankevoort and Huiskes 1991, DOI 10.1115/1.2894883: PubMed abstract and institutional publisher PDF https://pure.tue.nl/ws/portalfiles/portal/2342256/585374.pdf inspected for methods on printed pages 263–265, including equation 14 and zero-load length. The review does not reproduce parameter tables or claim a complete-paper/experimental replication. The paper uses the same k in both constitutive branches; k is explicitly N. Our examples and continuity proof are independently manufactured.

Seth et al. 2016, DOI 10.1371/journal.pone.0141028: abstract, scapular-kinematics introduction, Model and Methods joint definition and mobilizer formulation (equations 1–9) read at https://pmc.ncbi.nlm.nih.gov/articles/PMC4712143/. The four-coordinate and winging discussion is supported by those sections; no universal accuracy or performance claim is copied from the study. No new measurement or clinical authority is asserted.

## Flash Adjudication

Original helper correctly identifies missing reference-point conventions, zero-twist handling, ungrounded knee trajectory, constraint rank, ligament continuity and mixed stiffness units. Reject its q_wrong=q+p_perp sign: direct triple-product expansion gives q-p_perp. Pitch is unchanged by that particular reference-point substitution, so its blanket claim that both q and h become wrong is too strong. Displacement does not belong to dual se(3); wrenches are dual. NumPy division at rest produces invalid values/warnings rather than necessarily a Python ZeroDivisionError. No projective-coordinate implementation is needed for a function explicitly limited to finite axes.

Final helper confirms the revised equations and worked results but its intermediate arithmetic initially reverses omega cross q before correcting itself. Its frame-shift prose briefly reverses the direction of c despite deriving the correct formula. Its scalar constraint-variation cross-product order is wrong, while its following Jacobian row is correct. Reject those inconsistent intermediate statements; lead derivations and independent numerical checks govern acceptance. The chapter itself contains none of those erroneous expansions. A negative pitch gives speed magnitude abs(h)*norm(omega), not the helper's signed magnitude. No prose alteration was required by these rejected assertions.

## Verification

Actual listing RED: ten failed, three passed. GREEN: all 13 pass. Tests include manufactured recovery, frame transformation, degenerate rotation and invalid input. Five independent 100-case identities check screw recovery, changed reference frame, transform finite differences, ligament length tangent and elastic power; maximum residual 6.59e-10 below 1e-6. Full reproduction script and JSON retained.

Final build accepted-pass4.txt: 76 pages, 37 printed references, no unresolved citations/references. Lead inspected physical pages 3–6, 37–42 and 74–76; the final exercise page was rechecked after splitting its overlong mathematical data into a display. Chapter title and preface were corrected, and exercises start together on a separate page. Remaining overfull warnings are in unchanged Chapters 8–10; those chapters and historical duplicate destinations are not accepted by this review. Parent #4900 acceptance is integrated without changing its two chapter sources. Canonical Chapter 4/PDF/main/bibliography and exact regenerated audit bindings await checkpoint and frozen regression. Only this chapter row may advance after acceptance.
