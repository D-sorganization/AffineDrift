# Dimensionality and Integration Review

Issue #4885; scientific-review epic #4009; corpus #4021. Both original articles and both complete revisions were read. Original index weights are1,562 and1,578words. Review is limited to these two authored QMD sources; linked chapters and immutable provider publications are not recertified.

## Technical Decisions

The dimensionality article now separates configuration, state, actuator-input, task-nullspace and data-representation dimensions. Independent regular constraints and constant task rank are explicit. A singular scalar example demonstrates why a Jacobian kernel need not equal the exact level-set dimension. Passive dynamics do not remove state dimensions; a synergy restricts available inputs. Smooth finite-time flow, asymptotic attraction, approximate reduction and neural inference remain separate.

Phase-volume decay does not establish contraction: diag(1,-2) gives an explicit expanding direction. The metric inequality has its total derivative and domain hypotheses. Autonomous orbital convergence allows phase shift; a downswing with impact is not assumed periodic. The three-link manufactured mass matrix has M13=3, disproving bandwidth-one joint coupling without claiming experimental data. Tree ABA complexity and dense local trajectory-optimization costs retain algorithmic assumptions. The PCA example has exact harmonics and declared arbitrary feature scaling; noiseless intrinsic dimension one and linear variance rank four are different claims. Added full-support noise is not described as retaining a strictly one-dimensional distribution.

The integration guide binds provider support facts to the installed draft snapshot and keeps engine documentation separate from provider scientific qualification. Pinocchio pip distribution pin, import pinocchio and conda package pinocchio are distinguished. GPU MuJoCo requires an appropriate accelerator backend; Drake optimization is not a blanket formal guarantee. Fabricated asset paths, obsolete parser usage, unverified environment ID, tested-all-platform claims and empirical expert-rho threshold were removed. A published installation workflow is presented at its stated revision with explicit nonexecution status. Engine extras remain outside its core-import acceptance. Educational experiments are proposals, not promised implemented features.

## Primary Evidence and Reading Scope

- Installed provider manifest and active-lock: exact source27b6eeadbbd970bebb8926a3c83aeaea1f6ee4da, manifestSHA256a1c9a799ecceb4e81f28c50755fb50ad28f390ed8db335b64ecb89028f910b06; inspected engine entries, source and compatibility fields, publication blockers and all workflow identifiers, with installation-verification contract read in full. Immutable generated pages were not edited.
- https://github.com/stack-of-tasks/pinocchio : project installation and feature sections, read2026-10-04; package identity only, no local install test.
- https://mujoco.readthedocs.io/en/stable/mjx.html : introduction, installation and backend distinctions, read2026-10-04. No GPU execution or timing benchmark claimed.
- https://drake.mit.edu/installation.html and https://drake.mit.edu/pydrake/pydrake.multibody.parsing.html : supported-configuration and parser documentation, read2026-10-04. No platform-wide compatibility certification.
- https://myosuite.readthedocs.io/en/latest/tutorials.html : documented Gym helper/environment examples, read2026-10-04; guide links version-specific tutorials instead of asserting a new golf environment.
- https://royfeatherstone.org/spatial/v2/ : articulated-body versus composite-rigid-body routines and model interface. Dense three-link counterexample independently derived from endpoint velocity Jacobians.
- https://underactuated.csail.mit.edu/trajopt.html : iLQR/DDP section; local approximations and derivative distinction. Displayed complexity is a declared dense matrix-algebra bound, not a quoted universal implementation benchmark.
- https://arxiv.org/pdf/1209.4433 : introduction and Theorems1–2/domain assumptions on pages1–2; not a claim of reading every later proof. Nonvanishing-flow qualification avoids treating equilibria as periodic orbits.
- https://underactuated.csail.mit.edu/limit_cycles.html : orbital/transverse treatment used for interpretation; no new certificate constructed.
- https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002434 : author summary, conceptual/model arguments and inference limits. Does not disprove neural synergies or validate a specific golfer.
- Actual Volume0–V main.tex chapter includes and current book overview pages establish the repaired chapter map. Source chapter1 in VolumeIV was read for consistency with its existing corrected task/force/nullspace distinctions.

## Independent Calculations

The QA independent-checks.json records the centered harmonic SVD, endpoint-velocity mass matrix, stable nonnormal linear example and divergence counterexample. PCA cumulative fractions are4/7,5/7,6/7,1; the95%linear-variance count is4. The straight planar model has1 m rods,1 kg point masses, relative angles and mass-matrix units kg m^2. The stable example A=[[-1,10],[0,-1]] has poles-1,-1 but symmetric-part eigenvalues-6,4. These are manufactured mathematical checks, not physical measurements or provider-engine execution.

## Flash Delegation and Adjudication

Five agy CLI gemini-3.8-flash-low tasks completed: original dimensionality inventory, original integration inventory, bounded prose assembly from lead-approved dimension definitions, and one consistency pass per revised article. Helpers did not claim issues, edit sources, publish PRs or supply scientific authority. Lead wrote and reviewed the canonical revisions.

Accepted suggestions: remove conversational history from the integration guide, and make the total metric derivative explicit. Rejected suggestions: pose-versus-velocity distinction is not a conflation; N was already explicitly defined; the PCA arithmetic and approximately86% statement agree; ordinary total-derivative notation is correct; generic link lists do not certify provider engines; the guide already disclaims workflow execution and labels experiments proposed. The original helper's replacement contraction claim and compressed DDP complexity were not adopted without hypotheses. The prose helper's strictly2n phrase was not used to deny additional internal states.

## Validation and Remaining Work

Numerical checks and665-source title check passed. Both Quarto page renders succeeded. Browser review is in progress; the initial element screenshots were taken before intersection-triggered appearance and lazy mathematics completed, so those pale/blank images are not accepted render evidence. Navigation to actual anchors shows normal text and matrices. Desktop table wrappers intentionally scroll; a viewport-wide no-overflow check alone does not certify every table cell. Initial raw-preview console errors are the unpruned legacy polyfill CSP block and absent public-site manifest; no production-site failure is inferred. Raw Quarto title metadata displays Invalid Date for inherited Date unverified metadata; publication date remains unverified, never replaced with an invented date.

Full regression, final browser acceptance, canonical source hashes and regular protected PR delivery remain pending. Parent #4886 is open and now has guarded auto-merge armed; verify actual remote-main delivery before claiming it merged.

## Final Source Checkpoint

All63 focused citation/date, claim-audit and SPEC tests pass after regenerating the two source evidence digests. The initial run's one stale-digest failure remains recorded; it was not a scientific failure or silently skipped check. Final two page builds pass. Code and display equations were shortened for narrow screens without changing their mathematical meaning. Source-side unit spacing is explicit. The63-test result follows these final edits.

Browser samples covered desktop counts, recursive mass matrix and PCA sections, title cards, and mobile dimension/ratio text. Both390px viewports had document width390px and no MathJax error elements; the dimension page had50 math containers and integration7. Integration table wrappers have269px viewport and714px scrollable width; programmatic rightward scrolling was verified. Initial element captures were rejected because intersection-triggered opacity and lazy math had not settled. Accepted actual-navigation samples are named counts-visible, matrix-visible, pca-visible and accepted-mobile-ratio; accepted-mobile-contraction is misnamed and actually shows configuration-count prose after resize, so it must not be cited as a final contraction-equation screenshot. This is sampled local layout evidence, not complete live-site or browser accessibility certification.

The standard CSS bundler temporarily included nine existing canonical anchor-accessibility lines absent from the tracked bundle. That generated-only difference was restored and is excluded from this PR. No canonical CSS was edited. Raw-preview CSP polyfill and missing manifest limitations remain; the production pipeline has separate pruning/manifest steps. Inherited Invalid Date presentation is tracked as #4888. A routine Flash implementation dispatch was attempted but refused by the fleet dispatcher because agy lacks a working unattended tool allowlist (RM#1800). No permission bypass or implementation helper launch occurred. Five completed read-only helpers remain the correct count.

Save this source checkpoint, freeze it, then run the full suite. Preserve the packaging artifacts and run root/metadata checks afterward. The corpus rows remain pending until final acceptance. Do not promote these source drafts from the already accepted parent parameter review.
