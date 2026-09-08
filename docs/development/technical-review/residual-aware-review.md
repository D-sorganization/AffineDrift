# Residual-Aware Control Review

## Scope and Reading Record

Issue #4286 under epic #4009, corpus #4021 and tangent-series batch #4056. Both the user-facing technical argument and the accessible/critic panels are in articles/tangent-hyperplane-articles/Advanced/Residual-Aware_Control.qmd. All1,666 lines (the indexed8,125-word source), every code block, all application tables and both appendix proofs were read completely on2026-09-08. No exercises existed in the original. Existing src/affine_control/residuals.py and the explicit mock boundary at src/affine_control/ddp.py were inspected. The broader series and existing optimizer are not certified by this reading.

The original theorem drops Phi and substitutes the linearized deviation; its appendix turns an approximation back into a claimed bound. The constant-gain feedback dependence is lost by redefining an already specified Hessian constant. C2 does not justify O(norm cubed). A vector Hessian is a bilinear map with an output norm, not a dimensionless maximum slice without its norm convention. A local autodiff sample is not a regional bound. The pendulum Hessian sign is positive(g/L)sin(theta), and the stated damping/residual units are inconsistent.

The square-root timestep changes units and is not a safety factor. Regridding changes total horizon, quadrature, dynamics derivatives and nominal alignment. The code mixes RK4 rollout with Euler derivatives, omits dt in cost derivatives, invokes JIT functions with non-static function arguments, produces array/scalar shape conflicts, and publishes timings from a baseline whose body is pass. Those outputs cannot serve as reported simulation evidence. The article's observer computes its initial deviation from the current measurement, conflating tracking error and innovation, and its counters do not enforce consecutive samples through the hysteresis gap.

A Taylor-validity radius supplies no robust invariant tube. Impacts do not send finite state residuals to infinity and admit hybrid derivatives under stated transversality/rank/contact assumptions. Angular rate, reversal and intrinsic curvature are distinct. The quadrotor/ATRIAS/golf result tables lack reproducible derivations or artifacts; retain their intended scientific questions while replacing the claimed observations with actual checked teaching examples and a stated evaluation protocol. The accessible and critic sections must use the same corrected argument and cannot assume expert nervous systems minimize a particular residual.

## Mathematical Direction

Use scaled state/control coordinates and a declared comparison. For the smooth field F(t,z,v), let e=z-zbar, eta satisfy etadot=A eta+B deltav with eta(t0)=e(t0), and r=e-eta. The exact integral Taylor remainder N is evaluated on the actual joined state/control deviation and satisfies ||N||<=M||[e,deltav]||^2/2 within a convex certified tube. Then rdot=A r+N and r(t)=integral Phi(t,s)N(s)ds. Feedback may instead be incorporated into a closed-loop field with its own derivatives and domain; do not mix those two conventions.

An independent scalar counterexample xdot=x+x^2 about zero has x(t)=epsilon exp(t)/(1-epsilon(exp(t)-1)), eta=epsilon exp(t), and a positive remainder larger than the original unpropagated epsilon^2 integral for admissible epsilon,T. This will anchor the numerical regression.

For ||N||<=q and a propagator bound exp(a(t-s)), a local zero-reset residual is <=q expm1(a h)/a (limit q h when a0). Derive a time bound with log1p rather than a dimensioned square root. This is a local linearization remainder budget, distinct from numerical integration error, event-time error and the full-horizon propagated sum. Keep terminal time fixed when redistributing intervals.

Explain sampled vector-Hessian estimates, field remainder, flow remainder, numerical defect, measurement innovation and task/output error separately. Connect task-propagated errors to clubface/speed/strike outputs, activation/compliance states and contact events. Give a robust scalar tube counterexample/containment calculation and conditions for switching, feasible fallback and deadlines. No speedup/stability/physiological claim follows from a small residual alone.

## Publication Continuity

Spine PR #4285 is open with protected squash auto-merge enabled at113a63a55bda2a2a76db3b1c4316fd0b0dbbc551. First push stopped in the title checker with MemoryError; no remote branch existed and no AffineDrift push process remained. Memory recovered, the unchanged normal push passed every hook, and the ready PR was created. Preserve the failed log and successful retry. The residual-aware branch starts at that head; replay only #4286 commits onto the eventual protected spine squash before first push.

Foundations PR #4284 is published at a9e531fd26c30ef5e5de8727d85a1b67cc2a6d9f. Deployment34224541139 succeeded; exact-revision artifact10056277209 passes956/956 on239 routes, zero serious/critical axe findings, retries or transient responses. The405-source corpus is unfinished. No subagents. Do not commit/push/switch during checkout test/build/render/browser QA.

## Connected Editions and Critique Adjudication

The complete LAYMAN companion (indexed 2,815 words), CRITIC companion (indexed
4,625 words), and compact part 7 (indexed 822 words) were read in full, including
all assertions, suggested remedies, tables and references. They belong in the
same correction because they teach or evaluate the same theorem and repeat the
unsupported application claims. Scope expanded within #4286; no separate claim
of a complete broader-series audit is made.

The critique itself incorrectly made the induced-norm inequality depend on LQR
optimality; assigned RK4 global order two; rejected a conservative Frobenius
bound; claimed a lower stability step h >= 1/L; described clipping as protective;
claimed innovations separate noise from nonlinearity; and reported a wrong
Fisher p-value and an unjustified universal sample-size recommendation. It also
praised nonfunctional code and treated unsupported tables as empirical evidence.
Those are corrected explicitly, not retained as authoritative criticism.

For the hypothetical independent-groups table [[3,17],[1,19]], SciPy's two-sided
Fisher p-value is 0.6049896049896051 and the greater-odds one-sided value is
0.30249480249480254. An independent hypergeometric enumeration verifies the
two-sided probability sum. These numbers are not evidence that an experiment
existed. Paired trials would require paired outcomes and a different analysis.

Classical RK4 is checked directly using its four stages on y'=-y: the step-one
amplification is 3/8 and the step-three amplification is 11/8. A non-normal
matrix exponential demonstrates transient norm amplification despite negative
eigenvalues. A two-output quadratic field demonstrates the missing Euclidean
output-norm factor. These tests support the argument rather than merely checking
that particular prose strings appear.

## Implementation and Initial Verification

TDD RED: all 18 new flow-bound tests failed on the original implementation.
The tests cover independent quadrature, positive/zero/negative/tiny growth,
earlier-error propagation, subdivision invariance, an exact nonlinear
counterexample, invalid dimensions/signs/growth arrays, and overflow handling.
The scalar-example suite initially failed collection because its module did
not yet exist. Logs: residual-aware-red.log and residual-examples-red.log.

The corrected existing API adds optional interval growth rates, validates
one-dimensional finite non-negative bound data, and propagates a scalar
comparison recurrence. The three-argument sum is preserved with an explicit
nonexpansive-propagator assumption. Ordinary floating point is not promoted to
verified interval arithmetic. Existing component-Hessian API semantics and the
tracking-discrepancy monitor are preserved with technically accurate docs.
The sequential recurrence is intentional: each interval propagates the previous
bound without subtracting large cumulative exponents.

New src/tools/residual_control_examples.py provides the interval inversion and
exact scalar flow with an explicit domain before its finite-time pole. The
article's numerical values are independently checked: terminal 0.02765806173346,
actual remainder 0.00047524344887, old expression 0.000319452804947, conditional
bound 0.00131443126473; interval limit 0.16823611831060648 seconds. Pendulum
derivative sign and scalar robust-tube boundaries are also tested.

Initial GREEN: 85 existing/new flow and contract checks passed; the expanded
suite now passes 108 tests with three expected warnings from explicitly labeled
DDP mock contract tests. Ruff and Black pass on the edited/new code. An initial
lambda-style lint failure was fixed with a typed local function. Full root,
content, static and final render/browser verification remain pending.

The advanced article's first render succeeded and retained all 78 captured
historical main-content IDs (the exact JSON is authoritative if recounted).
The direct companions retain old subsection links as aliases at the matching
revised topic: 25 lay aliases and 59 critique aliases. Original Pandoc parses
are only anchor inventories, not visual proof. Final four-page rendering and
all-section visual inspection remain required.

## Primary-Source Reading Boundaries

- Li and Todorov (2004): publisher-indexed abstract, introduction, bibliographic
  metadata and beginning of the discrete iLQR formulation were read. Direct PDF
  retrieval returned 403. Use limited attribution to the paper's iLQR/model
  scope, not a claim to have audited its full proof. DOI corrected/added.
- Howell, Jackson and Manchester (2019): author-hosted PDF pages 1–4 text through
  the time-penalized formulation and projection algorithm was read. No benchmark
  result is imported or claimed replicated. The formulation supports the
  constrained-optimization distinction; the remainder of the paper is not
  recorded as fully read.
- Mayne, Seron and Raković (2005): publisher abstract and introduction read.
  Correct exact title and DOI. The article's scalar tube is independently
  derived; no full-paper proof replication is claimed.
- Kong and colleagues (2024): primary arXiv PDF definition 2, equations 9–14,
  differentiability/transversality and mode-sequence assumptions read. Event-time
  sensitivity is cited with that scope; no claim of complete 22-page review.

## Spine Protected Merge Checkpoint

PR #4285 merged as 982be51d6f5bff1d6d81e671cf92e8037332d6cd, confirmed at
15:10 UTC. CI Standard 34239448765 has all eight jobs successful, including
quality-gate. Protected deployment and exact live artifact verification remain
pending. No further lease is needed on closed #4283. Before the first residual
push, commit the completed slice and replay ONLY its commits after 113a63a5 onto
the protected spine squash/current main, preserving all intervening work.

## Root Validation and Repairs

The full root lane completed with 4,769 passes, one failure, 29 skips,
131 deselections and 59 warnings in 601.12 seconds. The single failure was
test_tangent_series_links_only_to_rendered_critique_pages: the new compact link
pointed at a deliberately excluded *_CRITIC.qmd. Keep the publication exclusion;
remove the two new public links to that internal critique. The critique itself
is corrected and will be rendered for local QA without changing public routes.
The root report before the following edge-case repair covered 11,986 of 12,919
source lines (92.78% rounded), versus the preceding 92.7617%; this is not a
claimed final full-root rerun or a final aggregate coverage measurement.

Static checks initially found that the duplicate mayne2005tube key in the
excluded tangent-hyperplane-contraction bibliography still carried the wrong
title. Its matching authors, journal, volume, pages and year identify the same
paper, so both titles and DOI now agree with the publisher. All 34 static
contracts pass after this repair. All 130 content checks pass with four skips
and 4,753 deselections. Root Ruff and Black pass (667 Python files unchanged
by the Black check); mypy passes 86 source files and the final edited helper
passes its subsequent targeted check.

Independent numerical inspection then found two representable-value edge cases
in the new teaching helpers: an intermediate budget/forcing ratio overflowed
although the logarithmic interval was finite, and subtraction lost x(0) for a
large initial state. Both were reproduced by failing tests before repair.
The interval helper now uses a log-domain branch when needed; the scalar flow
uses exp(-t)+initial*expm1(-t) in its denominator and explicitly rejects
unrepresentable output. Final helper functions are 30 and 29 lines long.

The first focused coverage invocation named a dotted source module, which
triggered NumPy's 'cannot load module more than once per process' during
collection. This was a measurement-command failure, not a test assertion.
Using coverage's filesystem source directory avoids pre-importing that module.
The final focused lane passes 116 tests with three expected mock warnings in
9.01 seconds; the new helper has all 35 statements covered (100%). That report
is explicitly module-scoped and does not replace the root coverage denominator.
The fixed public-link contract passes within this focused lane.

All root/focused/static/content processes had ended before the final four-page
render started. The deliberate localhost server was restarted on port 8767
(launcher PID 35872), and Playwright session affine-review was reopened
(browser PID 37172). No git mutation has run during QA.


## Responsive QA Diagnostics

The initial four-page responsive run recorded 56 variants and 42 failures.
Every failure was the CSP correctly rejecting Pandoc's obsolete CDN polyfill
on the three mathematical pages; the lay companion passed all 14 variants.
The existing deployment function strip_legacy_math_polyfill is now applied
to the local output. No CSP or verifier requirement is relaxed.

The initial continuous capture collected 188 advanced-article views before
an equation-edge assertion failed (12.8461px math, no horizontal displacement).
Those captures are diagnostic, not a claimed successful visual review. The
three mathematical sources now reuse the existing variational-chapter.css
readability rule; no shared stylesheet change is needed. A fresh four-page
render and independent per-page captures will verify the correction.

Spine publication is now verified: deployment 34242259512 succeeded at
982be51d6f5bff1d6d81e671cf92e8037332d6cd. Its exact-revision live artifact
10064015023 reports 956/956 passing variants across 239 routes, no serious or
critical axe findings, no retries and no transient responses.


## Full-Page Inspection and Presentation Repairs

The main article's 190 continuous views and 24 equation right-edge views were
inspected, including all proofs, six exercises and answers, code and tables.
This inspection found four literal commas before integration differentials;
the canonical TeX now uses thin spacing. It also found two new heading wrappers
that broke the existing adjacent-sibling panel CSS. Removing those wrappers
restores the standard button/content structure. Expanded panels and horizontal
table/code content require final targeted inspection after the repair.

The first equation-edge failure after the font repair was a capture-timing
error: the site's smooth scrolling had not finished when scrollLeft was read.
The capture now requests an instant scroll. It checks equation size against
the surrounding text size: 17.78px in ordinary body text and 15.3px in the
callout/appendix context. This verifies absence of compounded math shrinking
rather than imposing an unrelated constant on every typographic context.

The later 42 responsive failures were missing hashed Bootstrap assets, not the
previous CSP warning. Rendering the main article alone replaced the local
asset directory needed by the other three pages. All four are now rendered
together. The complete subsequent run passed 56/56 variants with zero serious
or critical axe findings; no retry or transient response occurred.

Dark-mode full-page inspection then caught a white Quarto appendix background
under light-colored proof and bibliography text. The three mathematical pages
now reuse css/nonlinearity.css, which contains the existing readable-math and
transparent-appendix rules. This supersedes the earlier variational stylesheet
choice without changing a shared stylesheet. A fresh four-page render and
final responsive and targeted captures follow. An extra capture attempt also
timed out because its theme button was outside the viewport; it now returns
to the top before changing themes. These diagnostics are retained; failed or
missing-asset captures are not counted as successful companion-page QA.

After the notation correction, all 130 content checks pass with four skips.
The title audit passes all 631 sources, style discipline reports zero
violations, and generated claim-audit digests/reports are current.


## Completed Local Verification

All four complete sources have been read and corrected. Full visual inspection
covered 190 main body views plus 24 equation edges, 52 lay-companion views,
81 critique views plus three equation edges, and 37 compact views plus one
equation edge. Final targeted inspection covered 81 main code/table/appendix
views and 25 critique table/appendix views. These replaced the affected earlier
presentation captures; they do not imply a fresh full-body capture after every
CSS adjustment.

Expanded HTML initially appeared as literal source because Markdown interpreted
its indentation as code. An explicit raw-HTML fence fixes that rendering. The
targeted dark inspection then exposed pale text on white panel cards. The new
article-local css/residual-control.css uses existing theme tokens for surfaces,
headings and introductions. All 18 final expanded-panel captures were visually
inspected. Ten additional expanded-state checks (320, 390, 768, 1024 and 1440px;
light and dark) report no clipping and no axe violations of any severity. The
first expanded-state harness required an explicit Playwright browser context;
that harness error was repaired before the successful run.

The complete responsive run passed 56/56 variants with zero serious/critical
axe findings. The article-local card repair subsequently passed 14/14 main-page
variants, followed by the final ten expanded-state checks after header/intro
contrast adjustments. All four final pages retain their 78/42/72/10 historical
IDs exactly once; all local stylesheet assets resolve. The immutable monograph
and root Quarto configuration have empty diffs.

Final content validation passes 130 checks, four skips, 4,798 deselections in
17.30s. Title audit passes 631 sources; style discipline has zero violations;
claim-audit reports are current; the new CSS passes Stylelint. Production code
is unchanged since the 116-pass focused lane, strict mypy and Ruff/Black checks
recorded above. The earlier full-root result remains 4,769 passes and one repaired
public-link failure, not a claimed all-green full-root rerun. All 35 statements
in the new teaching helper are covered. No local test, render or browser-QA
process remains running before staging; the deliberate server/browser can stay
available. Protected PR integration and live publication are next. The broader
405-source corpus remains unfinished.
