# Biology and Nonlinear Dynamics Review

Date: 2026-09-08. Issue #4294; parent epic #4009 and corpus #4021.
Branch: `fix/4294-biology-nonlinear-dynamics`, based on inverse PR head ccb32b03.
Replay only this batch after that base onto protected main before first push.
No subagents; no commit, push or branch operation during checkout QA.

## Scope and Original Findings

Read all 1,146 lines of the Volume IV biology chapter and the complete diff
against the integration edition. The editions were substantively identical
apart from citation commands/keys, typography and a theorem environment error.
Their original inventory lengths are 7,219 and 7,213 words. Both are now
synchronized complete treatments, approximately 5,500 words, with two figures,
worked examples, a proved sufficient stability condition and six exercises.

Also read the complete public Volume IV chapter map and the volume preface.
The preface repeated unsupported neural-depth arithmetic and empirical numbers,
and claimed that exercises and worked examples did not exist. It now describes
the research question and actual uneven review status. The public page links
the current protected-main source and PDF, while preserving the earlier pinned
notebook/chapter snapshot links and explaining the difference. Only this chapter
and preface are substantively certified by this batch; the other volume chapters
and the complete 405-source corpus remain under review.

Original errors included a shortening force law with reversed behavior, an
eccentric force law with incompatible units, series/parallel force confusion,
incorrect tendon extension and missing activation state. Preflex, baseline tone,
attraction, neural control and metabolic economy were conflated. The HKB
transition was reversed throughout text, figure and exercise. Synergy rank was
equated to controllability; UCM tangent directions to an exact task manifold and
unobservable dynamics. Dynamic stiffness was called force/velocity impedance,
and an improper transfer was assigned a finite disturbance gain. A universal
stiffness/noise law and metabolic law were asserted without support. The
unconditional hierarchical Lyapunov theorem was false. Exercises presupposed
results, including a UCM ratio above one for arbitrary random noise.

The attributed opening quotation could not be verified. Its removal is based
on unsupported attribution, not a claim that the reviewer proved who wrote it.
Bosch's flexible components are not defined as costly errors. The complete book
was not obtained or claimed read; the publisher preview and author's own account
bound the brief attribution retained here.

## Primary Sources and Their Limits

- Haken, Kelso and Bunz (1985), DOI10.1007/BF00336922. Downloaded the author-lab
  ten-page PDF from https://ccs.fau.edu/hbblab/pdfs/1985_Haken_Kelso_Bunz_Biol_Cyb.pdf.
  Read experiment/phase convention and reduced potential derivation, especially
  pages347–350. The change is anti-phase to homologous-muscle in-phase; the
  reduced first-order law follows from V=-a cos(phi)-b cos(2phi). It is not a
  metabolic-energy function or a universal golf-timing law.
- Millard, Uchida, Seth and Delp (2013), DOI10.1115/1.4023390. Downloaded the
  eleven-page author PDF https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf;
  read model assumptions and activation/series-equilibrium equations. Models
  distinguish excitation, activation, fiber length, pennation and tendon strain.
  The chapter's elementary smooth force-velocity example is explicitly its own
  illustration, not the paper's fitted Bezier curves or a human measurement.
- Hogan (1984), DOI10.1109/TAC.1984.1103644. Author-host download failed;
  obtained the same primary paper from the STIFF summer-school archive. Read the
  posture experiment and discussion/limitations. Gaussian perturbation strength
  is taken toward zero in the stated analysis, and the experiment does not
  establish stiffness proportional to arbitrary target uncertainty. The new
  quasistatic optimization is a fully specified teaching model.
- Kutch and Valero-Cuevas (2012), DOI10.1371/journal.pcbi.1002434. Downloaded the
  eleven-page author PDF from valerolab.org. Read abstract, experimental/model
  construction and proposed discrimination tests. Biomechanical counterexamples
  show why low EMG dimensionality alone does not identify fixed neural grouping;
  they do not show that neural synergies never exist.
- Scholz and Schoner (1999), DOI10.1007/s002210050738. Primary abstract describes
  testing controlled-variable hypotheses in sit-to-stand. The level-set, tangent,
  covariance and finite-step equations in this chapter are independently derived
  mathematical explanations, not claims of a universally observed variance ratio.
- Loram and Lakie (2002), DOI10.1113/jphysiol.2002.025049. Primary article and
  publisher abstract report insufficient intrinsic ankle stiffness in their
  quiet-standing protocol; this bounds the posture counterexample. No clinical
  recommendation or universal numeric threshold is inferred from the study.
- Newell (1986), Constraints on the Development of Coordination, pp341–360,
  DOI10.1007/978-94-009-4460-2_19. University-hosted scanned chapter downloaded.
  Text extraction was empty; visually read title metadata and pp347–348,
  including the organism/task/environment categories and triangle on p348.
- Bosch publisher preview: https://www.2010uitgevers.nl/wp-content/uploads/2020/10/9789490951597.pdf.
  Copyright page verifies English2020, publisher and ISBN978-94-90951-59-7.
  Author site https://www.fransbosch.systems/language-landing-page-english-template
  explicitly describes stable and flexible components (Chapter3,p108).
  Practitioner claims are framed as hypotheses, not formal stability results.
- Existing Hill1938, Loeb1995 and other retained canonical metadata used in the
  scoped bibliography. Integration Loeb and Hogan entries were demonstrably
  different erroneous records; replaced them with the canonical verified records.
  Added four primary records and three missing canonical citation keys to the
  integration bibliography. All11 chapter keys resolve in both bibliographies.

## Derivations and Independent Checks

The force law uses negative fiber velocity for shortening and gives0 at nu=-1,
1 at zero and eccentric limit1.5. Chosen c=.25,d=.1 matches derivative5 on both
sides. At nu=-.5 and+.1, active force with a=.5,F0=1000 is83.333 and625 N.
The series balance includes cos(alpha); tendon extension uses tendon slack
length. Positive tension produces -J_length^T F. A constant-time-scale activation
model gives a=.8/e=.2943 after .04s of zero excitation; force need not vanish.

Tendon integral with k20000 N/m and extension.02m stores4J at400N; release
over.02s gives200W average without creating energy. Upright local stability
needs K>mgh as well as positive damping/inertia. A radial limit cycle has decaying
radius but a neutral phase. Crossing dimensionless cost curves at sqrt2 supplies
no gait vector field.

HKB derivatives are lambda0=-a-4b and lambdapi=a-4b. For a1, b.5→.2,
anti-phase derivative changes -1→+.2; in-phase stays stable. A state exactly at
the now-unstable equilibrium requires a perturbation to leave it. UCM circle
example: tangent increment(0,.1) at(1,0) gives zero linear change but actual.01
task error. Isotropic covariance has equal per-dimension projected variances.
Double integrator has instantaneous input rank1 but control/observation rank2.

Constant opposing.03m moment arms with100N each give zero net torque;
longitudinal stiffness10000N/m each gives18Nm/rad. Dynamic stiffness F/X differs
from impedance F/V and compliance X/F. The chosen stiffness optimization has
K0=(sigma_F^2/rho)^.25:100N/m, or the upper bound150N/m for larger forcing.
Numerical minimization independently agrees. Dense frequency sweeps agree with
the analytic compliance H-infinity peak in resonant/nonresonant cases.

The stable-parts counterexample has matrix[-1,2;2,-1], eigenvalues1,-3 and
positive summed-V derivative along(1,1). The replacement theorem bounds all
cross-couplings in a positive-definite symmetric decay matrix and includes its
proof. Three equal decay rates with neighbor coupling.2 give minimum eigenvalue
1-.2sqrt2=.7172. Local/global and hybrid-reset limits are explicit.

`tests/test_biology_dynamics_rigor.py` contains independent symbolic, integration,
matrix and numerical-optimization checks. Initial13 cases pass; parameterizing
the optimization cases yields14. There is no production Python change.

## Build, QA and Failed Attempts

Initial source reads and source diff are complete. Main and integration TeX
bodies are identical. Full Volume IV builds with pdflatex, BibTeX, makeindex
and repeated pdflatex. The first attempted output-log path used one too many
parent directories and failed before compilation; corrected it. Several long
sentences and a heading overran the narrow print width; rewrote them rather
than shrinking type. Figure-anchor renaming did not remove the existing
duplicate-anchor warnings and was reverted. Those warnings also occur throughout
the untouched volume; do not claim the entire book is warning-free.

First visual pass inspected all14 chapter pages, preface, two contents pages
and first two bibliography pages. Found a hyphenated large title, a cramped
tendon label, a broken section heading and low-contrast example title bars.
Corrected these locally and rebuilt; final changed pages still require inspection.
The original extraction missed the last contents and bibliography pages because
their running headers differ; extraction now selects complete contiguous ranges.

Book route renders successfully. Browser scroll captures and final root suite
are running. Ruff and Black669 pass. Initial broad mypy invocation rejected
the configured excluded scripts directory; a no-argument attempt had no target;
strict tools-only check exposed pre-existing optional-dependency errors. Running
the exact configured CI command is the appropriate unchanged lane; outcome pending.

First book audit refresh targeted only the motor-control route, but the index
also binds the volume preface. Refreshed all existing digest maps using the
same deterministic helper and preserved JSON formatting; seven digest fields
changed. Source-content hashes are current. Before final delivery, record the
new review revision after the content commit, without claiming the old audit
commit contains the new sources. Regenerated claim inventory changes one digest.

GitHub sub-issue API first rejected issue_id; sub_issue_id succeeded. #4294 is
attached to epic4009 and leased to codex through23:10:57UTC. Inverse #4291 /
PR4293 has protected-merged as b6dc729f9390793bade2b1d749e084ca2875271a;
main CI34279760601 and deployment34279760688 still require completion and exact
live-artifact verification. Vendor4290/4292 is already published with all956 checks.

## Final Local Verification

All 21 final affected PDF pages were visually inspected: preface, all three
contents pages, all 14 chapter pages and all three bibliography pages. Equations,
figures, title bars, references and exercises are readable. The full volume has
72 pages. Other chapters remain outside this substantive review.

The complete book reading page was inspected through 30 overlapping captures
in desktop light, phone light and phone dark modes. A subsequent axe run found
serious dark contrast failures in inline source code and the docked book menu.
The canonical code-theme and page-sidebar components now use the existing theme
tokens for foreground and background. The flattened CSS bundle was rebuilt.
Copying component mirrors alone did not change the flattened bundle; browser
HTTP cache also retained its old version after service-worker cleanup. A fresh
stylesheet URL verified the actual rebuilt asset. The final 14 width/theme
checks pass and both theme axe scans have no serious or critical violations.
Four additional desktop/phone theme captures were visually inspected. Quarto's
existing moderate landmark-unique finding remains in the navigation markup;
this is not a zero-violations accessibility certification. A scroll-position
timeout in the screenshot helper was fixed by returning to the top before
using the actual theme button.

Final root lane: 4,796 passed, 29 skipped, 131 deselected, 50 warnings in
557.36 seconds; coverage 79.04% exceeds the configured 75% floor. Content lane:
130 passed, 4 skipped, 4,822 deselected. All 34 configured static checks pass;
title audit 631, Ruff, Black 669 and exact CI mypy 86 pass. The two existing
theme suites pass all 54 tests. Scoped stylelint, CSS budget and CSS architecture
checks pass. Initial stylelint exposed a Quarto sourceCode selector placed above
the existing class-name exception; moved that documented exception above the
selector. Two direct Python script calls lacked the package root; their proper
module invocations pass. No production Python was changed.

Tests regenerated three presentation registries and summaries. Restored only
files independently compared with HEAD as identical except date/JSON formatting
or line endings. Intentional book-audit, claim-inventory and report updates are
retained. All checkout tests, builds and browser jobs finished before committing.

Inverse #4291 / PR #4293 is now published after protected squash b6dc729f.
Main CI 34279760601 and deployment 34279760688 succeed. Exact live artifact
10078282103 passes 956/956 checks across 239 routes. Delivery of this biology
batch remains pending; the next commit records its source revision.

Content commit f1430afe replayed onto protected main b6dc729f as 00a8f13c814062765ac2a41326ae2a72f3de3923; final trees are identical. Book audit source/render revision fields now bind that content commit; this is local render evidence, not a claim of deployment.


## Pull Request Delivery

PR #4296 is pushed from `fix/4294-biology-nonlinear-dynamics` at 887a855a.
The first push was correctly rejected because a metadata helper wrote the book
audit with Windows CRLF and formatting then normalized it after hashes had been
computed. Normalize the canonical file to LF before regenerating dependent
hashes; do not bypass the guard. Commit 887a855a repairs those dependent hashes.
The second normal push passed all hooks, including its unit-test lane. Protected
CI, merge and exact-revision publication remain pending.
