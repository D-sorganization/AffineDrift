# Putting Mechanics Review

## Scope and Coordination

Epic #4009; corpus #4021; issue #4937. Complete ch32_putting.tex, its Quarto mirror and nomenclature.tex, with associated bibliography, publication lists and rebuilt PDF. Base workbench source 11564f73d; that review is still undergoing acceptance. Do not merge this PR into its topic parent. User authorizes continued review and protected remote-main delivery; regular PRs only.

Claim checked free before work. Lease technical-review-20261005-putting through 07:23:53 UTC on 5 October 2026, receipt5988628060; presence receipt5988644214 through07:25:28. Keep shared SPEC/HANDOFF/DEVELOPMENT_LOG untouched; preserve primary checkout .commit_msg. Corpus has407 rows and53 pending-prefix entries before workbench acceptance. Counts describe heterogeneous review scopes, not scientific completion percentages.

## Mechanical Decisions

The model begins after any bounce/flight. It assumes a rigid sphere, constant Coulomb sliding friction, stationary level plane and no rolling-resistance moment during slip. Signed slip s=v-R omega allows initial overspin, backspin and reverse translation. Friction opposes slip, not necessarily center velocity. Positive inertia factor kappa and positive friction are required. Transition displacement is signed; final rolling velocity may also be signed. The contact-work identity includes rotation and explains acceleration with energy loss.

For rolling on a plane, declare a resistance moment c_r N R opposing angular velocity, no normal spin and sufficient static traction. Eliminating traction gives the 1/(1+kappa) slope factor and level deceleration a0=c_r g/(1+kappa). A right-handed vector derivation uses resisting torque -c_r N R (n cross vhat). Zero resistance does not imply zero traction. Stop integration before the direction becomes undefined; a static law is needed to predict rest or restart. The local quadratic path is not an exact finite-putt aim or capture solution.

Stimpmeter distance and its notch/calibration must be distinguished from microscopic friction. Historical1.83m/s is an illustrative entry calibration, not a certification of every device or launch condition. The compound-pendulum equivalent length I_p/(m d) differs from head radius. A passive symmetric excursion has equal outgoing/return durations; a driven oscillator may yield a different timing ratio under its declared forcing. Distinguish head velocity, launch velocity and established-rolling velocity. The simple central free-mass collision is a conditional derivation; actual putter mass cannot silently replace impact effective inertia.

Nomenclature includes internal states in drift, nonminimal coordinate-speed maps, redundant actuation, constraint scaling and the coordinate-balance nature of drift power. Ideal constraint virtual work vanishes, but actual power is -lambda^T Phi_t for moving holonomic constraints. Stationarity is sufficient for zero power, not necessary. DCR is pointwise and metric/input-set dependent, not a reachability certificate.

## Primary Sources and Reading Scope

Penner, The Physics of Putting, Canadian Journal of Physics80(2),83–96,2002, DOI10.1139/p01-137. Author-uploaded complete text was read through the ResearchGate rendering; direct author-PDF download failed TLS verification and was not bypassed. Correct the author to A. Raymond Penner. The paper explicitly discusses initial spin/launch and uses a historical1.83m/s Stimpmeter entry estimate. Its Section2.4 prose has a no-resistance/traction inconsistency: the no-slip Newton–Euler equations require the5/7 slope factor. Do not copy its claim that rho=0 means zero contact traction and g sin(theta) acceleration. Derive the chapter result independently.

Karlsen, Smith and Nilsson, The Stroke Has Only a Minor Influence on Direction Consistency in Golf Putting Among Elite Players, Journal of Sports Sciences26(3),243–250,2008, DOI10.1080/02640410701530902. Full eight-page author-hosted PDF read; PubMed17917952 metadata checked. Study scope:71 skilled players,1301 approximately4m putts, stroke direction relative to the aim line. It does not supply universal hole-out probabilities. Replace the erroneous title/author/page metadata. The MacKenzie2011 entry used previously could not be verified by exact-title searching; remove the unsupported, now-unused entry without claiming nonexistence. Pelz's uncited book entry is retained; no claims from an unread book.

USGA Stimpmeter Instruction Booklet, official cached search text: measurement Steps3–6, opposite-direction averages and alternate2X notch. Direct PDF retrieval returned403; do not claim local PDF inspection. Official2013 USGA introduction corroborates doubling the alternate-notch average. Source URL: https://www.usga.org/content/dam/usga/pdf/imported/StimpmeterBookletFINAL.pdf.

OpenStax University Physics Volume1 Section11.1 rolling Newton–Euler equations and Section15.4 physical pendulum, lines88–118, read. Own derivations and examples are not copied passages. Links: https://openstax.org/books/university-physics-volume-1/pages/11-1-rolling-motion and https://openstax.org/books/university-physics-volume-1/pages/15-4-pendulums.

Grober2011, arXiv1103.2827,17-page preprint: abstract and pages1–10 read, especially driven oscillator and fixed timing/velocity-shape relation on pages6–8. This is a proposed conditional model, not evidence that an unforced pendulum establishes an optimal human tempo. Do not adopt the paper's reverse inference that matching distance scaling uniquely establishes each underlying constant: products can compensate. Link: https://arxiv.org/abs/1103.2827.

Downloaded complete papers remain untracked research inputs and must not be committed wholesale.

## Delegation and Adjudication

agy Gemini3.8 Flash original scientific audit, independent derivation proposal, Quarto conversion and final scientific review completed. Lead checked source claims and mechanics. The final-review prompt inadvertently requested a Quarto comparison without supplying that mirror; the helper correctly declined that comparison. No parity acceptance is credited to that run.

Rejected helper claims: positive forward torque is the only possible cause of asymmetric timing; zero actual constraint power occurs if and only if constraints are stationary; unsupported typical restitution/mass ranges; unverified bibliography corrections. The independent-math helper used the wrong cross-product order for resisting torque, although its final acceleration was correct. It also gave a downslope displacement ten times too small and reported numerical integration without executing it. Its proposed solver stopped the entire derivative near zero slip, which would improperly stop translational position too. None of those claims/code were adopted. Lead-written independent checks execute actual NumPy/SciPy calculations.

The Quarto conversion preserves the prose and equations; lead corrected colon cross-reference IDs to Quarto prefixes and removed LaTeX prose nonbreaking-space syntax. Mathematical content still needs final rendered inspection. Symbol reuse in nomenclature is explicitly chapter-local; mass/modal-count and strain/regularizer are distinct quantities.

## Executed Checks and Remaining Work

Publication reachability test: RED reproduced missing inclusion; GREEN passes after adding chapter to both contents lists. No tests weakened.

independent-checks.py.txt executes six100-case checks: slip Newton–Euler/contact work, rolling torque/energy, central collision momentum/restitution, compound-pendulum release energy, small-amplitude period remainder, and moving-constraint power. JSON records separate tolerances. Numerical DOP853 slope example at0.1s: x=0.1992504663m,y=0.0012196682m; quadratic y=0.0012227288m. Halving time reduces the error by8.0074, consistent with a cubic leading remainder. Calibration examples distinguish exact and small-angle amplitudes. These are manufactured mechanics checks, not measured golfer validation.

First LaTeX pass and BibTeX succeed; subsequent resolution passes and scoped pixel inspection pending. Quarto chapter renders successfully into its book _book directory. Do not commit generated website HTML or browser-cache folders. Source-level whole-corpus title/citation/trust checks, frozen pre-PR/full regression and acceptance remain pending. Workbench S first full regression had7224passes and2root-hygiene failures due to .playwright-cli; its artifact has been moved safely and clean rerun is ongoing. Do not accept S based on the failed run.

## Delivery Guidance

B PR4889 is on fetched main63028ca3c7234795aa8f4f9a818e0d8ceacceb2d with its four accepted blobs verified; lease released receipt5988604242. C PR4891 targets main at59ce890cfe93a587a2dad37665ca7951b3bad4c6; central auto-merge guard armed. Verify actual merge and its three implementation plus15 latest E/F/G blob hashes before advancing H PR4902. Never treat a topic-base merge as remote-main delivery.

C/J/M/O/P leases renewed through07:40UTC; E/F/G/H/I/K/L/N/Q through06:24; R through06:08; S through06:45; T through07:23. Renew active work as needed. R regular PR4936 is the parent of workbench S; T must integrate S's acceptance before its own corpus update. App artifact attachment cap100 is known; attempt required attachment after creating each PR, but do not remove unrelated artifacts.

## Final Source and Render Checkpoint

Parent S is accepted and integrated at f3626e205, regular PR4938, draftfalse,agent:codex. Its app attachment hit the100-item cap. Corpus now52pending-prefix rows before this three-row acceptance. R lease renewed through approximately08:02UTC via the existing REST lease protocol, receipt5988991594, because GraphQL quota is exhausted until06:21:05UTC. C is still not confirmed merged; successful central guard arming may enqueue a merge, so auto_merge:null alone is not proof of failure.

Additional adjacent bibliography correction: Penner2003 used by the impact chapter had the wrong author/title/journal/volume/pages. Author-hosted primary PDF cover metadata and Crossref DOI10.1088/0034-4885/66/2/202 agree on A Raymond Penner, The Physics of Golf, Reports on Progress in Physics66(2),131–171,2003. Metadata corrected; this is not a new complete review of that impact chapter or41-page paper.

Five successful Flash jobs, including a separate complete TEX/QMD parity review with no omitted mathematical content. Final lead edits split long equations for mobile, corrected duplicated Equation labels and clarified symbol reuse/time-dependent drift. Independent six100-case checks passed. Twenty focused publication/trust tests passed; an earlier run detected a stale bibliography evidence digest after an intervening edit, fixed through regeneration and rerun. Root bibliography-quality check passes169entries, but its default scope is not the entire golf bibliography; actual golf citations are checked by the book build.

Final LaTeX pass11:534pages,145printed bibliography entries, no undefined citations/references or rerun request. The new nomenclature overfull line was reworded; remaining two minor overfull warnings occur in the historical list of figures and another chapter heading. PDF pixels inspected at physical pages5–8,17,248–251,518,520,522,523,527. Final changed nomenclature and bibliography pages reinspected; unchanged putting pages retain the inspected layout. No claim that all534pages were visually or technically reviewed in this batch.

Quarto final render passes. Phone390 and desktop1440 have93math containers,zero MathJax errors and viewport-width documents. All mobile content inspected in sequential crops; desktop slope/cross-references inspected. The standalone book preview initially lacked the root CSS resource; its canonical4-line putting-chapter.css was copied unchanged into the preview server css directory, matching its root-relative resolved URL. The deployed website obtains canonical css through Quarto resources. The selector wraps long bibliography URLs; no scientific content hidden. Before this fix the document was697pixels wide on390; corrected to390. Favicon404 is an unrelated local-preview limitation. Do not commit browser caches/screenshots, paper downloads or generated HTML.

## Accepted Source and Current Delivery

Frozen source e38a370c6 passed7227 tests,29skipped,210deselected,60warnings in650.82s; coverage93.25%,exit0,tracked tree empty before and after. Twenty focused tests and all scoped science/render checks pass. The original pre-PR run failed only the central PDF title validator. Repository_Management#1994 corrects Roman-number boundaries and If capitalization without changing book titles; repaired central e985130a passes all eight current gates and the one mapped publication test. That central fix is committed and proceeding through its own regular PR.

The three complete corpus scopes are now accepted at the frozen source;52 to49 pending-prefix rows out of407. See putting-mechanics-validation.json for ten canonical acceptance hashes. Main delivery remains separate from acceptance. Preserve failure logs and do not claim every534-page book page was reviewed.

C PR4891 actually merged to remote main e37354e7b9aedd036039bf2c6a202d4049f5b6a2. All18 latest C/E/F/G canonical hashes match that commit; receipt c-efg-main-verification.json. Four leases released (receipts5989267448,5989268609,5989269746,5989270913). H PR4902 now targets main,remotehead118b2a811c57c6602232d78bf331c5b742e21586,central guard armed; actual merge not yet confirmed. Other active leases renewed where needed. Future GitHub operations use the configured Codex GitHub App in an isolated runtime, preserving owner credentials.

Next scientific batch U #4939 reviews the six tangent-series articles and applications appendix. Its independent worktree starts from T source; integrate this acceptance before updating its corpus. Flash audits are advisory: reject claims that state-dependent gains invalidate control affinity, that every cost Hessian is a contraction metric, or that same-time variational propagation alone predicts a state-triggered landing event.
