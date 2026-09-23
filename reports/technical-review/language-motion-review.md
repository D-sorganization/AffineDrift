# The Language of Motion: Paired Technical Review — #4444

## Scope and Argument

Read both complete Chapter 2 editions, including definitions, coordinate
equations, the print diagram, phase table, anatomical interpretations and all
exercises. Read the corrected Chapter 3 convention and parameter contract and
its numerical helper and independent tests. This is a full chapter review
under #4021/#4009; the September 13 route-only review under #4054 was limited.

The chapter now follows a declared configuration through rates, state, endpoint
motion and the force/contact assumptions required to interpret a golf outcome.
It supplies the language needed by later dynamics chapters without treating an
exact planar calculation as a calibrated human model. Neither this chapter nor
the rebuilt book PDF completes the remaining corpus or whole-book review.

## Corrected Findings

1. **P1 — Coordinates and Geometry:** The print convention contradicted its
   sine/negative-cosine equations; its angle arcs did not meet the links. The web
   edition switched between a relative distal angle and an angle from horizontal.
   Both claimed full spatial reconstruction. Use upward y, counterclockwise
   rotation from downward vertical, and a relative second coordinate. Reuse the
   computed Chapter 3 SVG/PDF with explicit model and anatomical boundaries.
2. **P1 — Dimensions and State Closure:** Qualify local independent coordinates,
   angular seams, the torus, redundant descriptions and planar versus spherical
   pendula. Distinguish configuration, compatible velocity, tangent space and
   predictive state. State the model/input/regularity requirements, internal
   states, delays and hybrid reset boundaries. A turning point of one coordinate
   does not imply a stationary mechanism.
3. **P1 — Constraints and Reachability:** Separate geometric admissibility from
   finite-time, input-limited reachability. Use the constraint Jacobian's rank,
   distinguish holonomic and nonholonomic restrictions, and require feasible
   sticking contacts. Remove universal anatomical ranges, injury-at-a-wall
   inference and the claim that reactions are independent of muscular loading.
4. **P1 — Kinematics and Physical Interpretation:** Give the directional
   Jacobian, its cancellation and rank-loss examples, the acceleration curvature
   terms and moving-support boundary. Angular-rate addition is not a complete
   explanation of dynamic coupling. Net inverse-dynamics moments do not uniquely
   identify individual muscle, ground or grip forces.
5. **P1 — Numerical and Human Evidence:** Remove conflicting allegedly canonical
   physiological parameters and unsupported typical shoulder rates. Use Chapter
   3's explicitly manufactured geometry and a differentiable trajectory with
   signed derivatives. Do not label its endpoint as measured impact or explain
   every post-impact deceleration solely by ball energy transfer. All six
   exercises now declare their models and give worked answers.
6. **P2 — Paired Publication:** Preserve public chapter and historical section
   destinations, correct printed chapter-reference labels, pair the formerly
   unpaired geometry, and retain the required On This Site bridge. Reuse existing
   diagram and reading-size math styles. No shared styling or production
   numerical module was changed.

## Independent Checks

The initial 21-case run had 12 expected failures and nine passes. Eleven failed
cases detected concrete old claims in the paired sources; the twelfth required
the absent reproducible trajectory. All 21 now pass. The tests execute the
published Python example, differentiate independently fitted coordinate
polynomials, and check endpoint velocity/acceleration with the existing model.

For T = 0.5 s, the manufactured samples have first angles 90, 67.5 and 0 degrees
and first rates 0, -180 and -360 degrees/s. Second angles are -45, -22.5 and 0
degrees, with constant rate +90 degrees/s. At the final state, endpoint velocity
is (-2.2 pi, 0) m/s and acceleration is (-5.4 pi, 3.65 pi^2) m/s^2. At the first
coordinate's turning point, endpoint speed is still pi/2 m/s.

Additional independent cases cover Jacobian cancellation, projected-state
ambiguity, translating support velocity and the rolling-sphere contact-velocity
constraint. The sphere has five configuration DOF and three admissible
instantaneous velocity components under ideal point-contact rolling with spin
allowed; no-slip alone is not a two-coordinate orientation model.

The existing figure audit correctly failed when the old TikZ drawing was
removed. Its actual counts are now four TikZ figures, 32 included print graphics,
33 web figures and three remaining unpaired figures elsewhere in the book.
All 58 combined Chapter 2, Chapter 3 and figure-parity checks pass. Content lint passes 131 cases with four existing skips. No remaining
figure elsewhere is silently certified by this change.

## Primary References and Limits

- Read the [Modern Robotics configuration-space lesson](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-3-1-configuration-space-topology/)
  for circle/torus topology and coordinate seams.
- Read its [configuration and velocity constraints lesson](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-4-configuration-and-velocity-constraints/)
  for the independent-rank and nonholonomic distinction.
- Read the [MIT multibody chapter](https://underactuated.mit.edu/multibody.html)
  for relative-angle two-link kinematics and the mechanics formulation.

The numerical trajectory, cancellation, sphere contact calculation and worked
answers are explicit model calculations checked independently here. They are
not experimental results attributed to those references. No new population
rate, tissue limit, participant measurement or coaching benefit is asserted.

## Rendering and Reproduction

The exact final measurements and source hashes are in
language-motion-render-verification.json. Root-site HTML must be built in the
root website context, not only the nested Quarto book project. The local check
uses the production legacy-polyfill sanitizer on the rendered page; the CSP
policy and sanitizer are unchanged. A root render followed by the repository's
public-site verifier reproduces the production contract.

Rebuild print from articles/The_Physics_of_Golf with pdflatex main.tex, bibtex
main, makeindex main.idx, then two further pdflatex passes. The complete current
book builds to 527 pages. All ten Chapter 2 pages (physical 41–50) were inspected;
after wording and typography refinements, the five changed pages were rendered
and reread. The final bridge heading was checked again. Chapter 2 has no final
layout or undefined-reference warnings. Existing layout warnings elsewhere
remain outside this chapter review. The PDF is regenerated from the unchanged
rest-of-book sources, not claimed byte-identical outside Chapter 2.

The old epigraph, incorrect TikZ sketch and unsupported phase table are replaced
by the checked narrative, paired geometry and reproducible example. No source
outside this chapter was rewritten. The source/render evidence is committed
before the route is rebound, so an older limited review cannot certify new bytes.
