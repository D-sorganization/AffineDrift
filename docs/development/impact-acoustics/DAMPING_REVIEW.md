# Coriolis Energy and Viscous Damping Review

## Ownership and Scope

- Parent: AffineDrift #4253; follow-up #4277; final synthesis #4255 remains open.
- Worktree: `C:/Users/diete/Repositories/AffineDrift-impact-damping`.
- Branch: `docs/4277-coriolis-energy-accounting`.
- Base: `4748e674db5c3f7d0c981282f6cf4a8ea9dd86ed`.
- This correction updates the paired Physics of Golf chapter 29 sources and
  rebuilds the book. It does not certify every retained claim in that chapter.
- Tools T1 #5077 merged at `f7254461399ac18e5667a0215afd90a9ebff9d22`.
  Tools T3's elastic energy/tangent checkpoint is published at
  `b625eb2cca279472795a93896776fdef6ac33995`; loaded equilibrium, contact,
  calibrated acoustics, downstream studies and physical/blinded gates remain open.

## Corrections

Two statements treated Coriolis terms as implicit damping. The corrected
first-order state representation uses independent local coordinates
x=[q;v], with qdot=v, f0=[v;-M^-1(Cv+g)], fd=[0;-M^-1 Dv], and
G=[0;M^-1 B]. Coefficients are evaluated at the current state. Quaternion
coordinates require qdot=N(q)v; a closed chain requires reactions or consistent
constraint elimination. These are not interchangeable unconstrained models.

For the symmetric viscous model D=D^T positive semidefinite, loss is v^T Dv.
Nonnegative diagonal entries alone do not establish passivity of a coupled
matrix. In a consistent time-independent Lagrangian model,
v^T Cv=0.5 v^T Mdot v, so Coriolis terms balance kinetic-metric variation.
They create no additional heat-loss channel. The complete energy rate retains
actuator work, constraint/boundary work and explicit dissipation; stationary
ideal constraints do zero work, while prescribed moving constraints may do work.

The two-joint example now gives a1,d=-(M^-1)12 c2 v2=M12 c2 v2/det(M).
The former extra inverse-mass determinant factor was removed. Total loss is
c2 v2^2; the acceleration effect's sign depends on configuration and velocity.
Uniform velocity scaling makes the inertial quadratic term scale quadratically;
changing only one component can increase, decrease or reverse individual terms.
Perturbation growth/decay does not identify physical damping or sound radiation.

## Sources and Editorial Boundaries

[MIT Underactuated Robotics, multi-body dynamics](https://underactuated.mit.edu/multibody.html)
was read for the manipulator equation and kinetic-energy property. The separate
Caltech Murray PDF retrieval failed; no fresh full-text access is claimed.
The chapter links the canonical heavy-hit/contact/acoustic review and retains
its existing bibliography. No measurement or identified biological coefficient
was added or inferred from these algebraic identities.

Retained claims still needing a separate audit include biological damping
coefficients, relative steel/graphite loss assertions, the proximal/distal
energy-cascade hierarchy and quoted joint speeds, damping/control optimization
claims, and exercise premises. The root-to-tip hierarchy cannot follow merely
from a damping coefficient: actual relative rates and coupled state responses
must be evaluated. This focused correction must not be described as a complete
scientific validation of the chapter or the final program synthesis.

## Paired Sources and Rendering

Canonical changed source: `articles/The_Physics_of_Golf/quarto/ch29_joint_damping_friction.qmd`.
Paired print source: `articles/The_Physics_of_Golf/chapters/ch29_joint_damping_friction.tex`.
Print artifact: `articles/The_Physics_of_Golf/main.pdf`.
Changed Quarto fragments were converted through Quarto/Pandoc and integrated
with the paired print chapter, retaining surrounding labels and index entries.
Heading levels and Section references were checked in the print context.

Existing book macros already include their arguments. Visual QA caught and
removed duplicated M(q)(q) and C(q,qdot)(q,v) arguments in changed formulas.
The state mapping and energy proof use compact aligned equations for print and
mobile. Final PDF pages 226 and 229 were reviewed after the last corrections;
227, 228, 237 and 238 were also reviewed in the preceding build. The complete
566-page build succeeds with the existing 135 missing-glyph warnings and
repeated sec:sensitivity label. This is not a clean whole-book typography claim.

The PDF operation marker was invoked once for this edit; do not repeat it for
rebuilds. Git's bundled Perl is required on PATH for latexmk in this environment:
`C:/Program Files/Git/usr/bin`. Rebuild with
`latexmk -pdf -interaction=nonstopmode -halt-on-error -cd articles/The_Physics_of_Golf/main.tex`.

A standalone nested-book preview had 177 MathJax formulas and zero MathJax
errors, but mobile table overflow and numbered-heading contrast failures.
Root-site styles supply the intended table overflow and heading-color behavior;
actual root publication QA remains required. The complete root command
`quarto render --to html` is running. Its default clean removes docs/ because
that directory is also the site's generated output. Restore unchanged tracked
internal docs after rendering, recreate this review from its saved temporary
copy, and keep scratch/browser output away from docs/ until render completion.
No generated deletion should be committed. Use --no-clean for later local
renders where appropriate; do not change production build governance.

## Validation and Continuation

- 31 focused textbook/impact content tests passed.
- Title audit: 628 sources; SPEC check, Ruff and Black (657 files) passed.
- First full run used the local default 60-second timeout and stopped while
  extracting the unchanged protected proximal-distal monograph PDF.
- Actual CI uses 120 seconds. Full rerun: 4,587 passed, 29 skipped,
  131 deselected, two root-hygiene failures, 50 warnings (386.26 s).
  Both failures were the browser tool's untracked .playwright-cli root directory.
- Moving that scratch directory into development output made all six
  root-hygiene tests pass. No test timeout configuration or allowlist changed.
- Optional Streamlit and absent legacy entry-point skips remain explicitly
  reported; the protected monograph source/artifact was not modified.
- Full-site render, root-theme desktop/mobile/accessibility QA, generated-file
  cleanup, final turnover update and normal commit/push/PR gates remain pending.

Temporary logs use `impact-affine-damping-` in the Windows TEMP directory.
The initial root build also deletes untracked docs/ QA output; its mathematical
review results and exact commands are retained here and in those logs. Keep
final QA assets under the allowed development folder after root rendering.

## Final Local Publication Review

The complete root website render succeeded for all 238 targets. Root publication
QA exposed missing nested-book macros despite zero mjx-merror elements: MathJax's
undefined-command handling can render red text instead. The chapter's mass,
Coriolis, gravity and constraint-force shorthand is now expanded to portable
standard TeX in both paired sources. The final 36-target Physics of Golf render
used the root website configuration via
`quarto render articles/The_Physics_of_Golf --to html --no-clean` and succeeded.
A temporary profile experiment was removed; its render-list merge did not select
a single file. No project configuration change is committed.

The final PDF rebuild succeeds; pages 226-229 and 237-238 were rendered and
visually checked again. Eight browser screenshots cover state, energy,
mass-matrix and drift-summary sections at widths 1440 and 390. After waiting
for visible lazy math to typeset, all new equations render without undefined
commands. Both document widths equal the viewport; the older wide table and
mass matrix use local horizontal overflow. Axe reports zero violations in the
two new explanatory sections. The existing root CSP blocks its legacy polyfill
and some font fetches; nested stylesheet-import requests also report 404. Those
untouched site issues do not become a clean whole-site claim.

The root build's internal-document deletions were restored. Incidental trust
registries were compared as parsed JSON and differ only in generation dates
and formatting; they were restored rather than publishing unrelated evidence
updates. Generated site output and QA images are not staged. The root source
stylesheet was copied byte-for-byte for publication QA, then its tracked output
copy restored; no stylesheet change is committed. Browser/service-worker state
was cleared only on this task's local preview origin for fresh-source QA.

Final focused rerun passes all 37 textbook/impact/root-hygiene tests after the
portable-notation edit. The older mobile mass matrix is explicitly confirmed
as a local scroll area (client width 247 px, scroll width 345 px, overflow-x:auto),
not document overflow. The final PDF pages are all reviewed. Local QA is ended;
normal commit/push checks and protected PR delivery remain to be completed.
