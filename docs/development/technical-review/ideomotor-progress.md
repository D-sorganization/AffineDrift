# Ideomotor Review — Regular PR #4829

Accepted source `f488f45f3254fa40f98bedceb5edaa11280bb70c` and binding `8f42bde9155478397dc13910362a6e98555a1ec7` verified on remote. Regular PR #4829 is open and attached; registration SELF. All 61 post-binding checks pass. Full regression: 6655 passed, 29 skipped, 187 deselected, 60 warnings, 79.36% coverage. Seven Flash helpers adjudicated. Frozen decisions and reading limits: reports/technical-review/ideomotor-review.md. 101 source audits plus whole-book consistency remain. Await predecessor #4824 exact-head CI and delivery, then reconcile ancestry and remove the temporary merge hold. Earlier preparation notes below are historical.

---

# Ideomotor Review Progress — No Acceptance

Full original and revised article read. Issue #4825 is claimed; article, module and tests are drafted on `fix/ideomotor-rigor-4825`. Five supplied-text agy CLI Gemini 3.8 Flash outputs have been adjudicated: inventory, test draft, module draft, editorial review and handoff consistency. No source acceptance or corpus credit yet.

The exact original Python example was executed in memory: u=0, angle remains0.3rad after one explicit Euler step, angular velocity becomes-0.02899053227347741rad/s, angle-to-torque sensitivity0. Its single-step angle objective cannot select a nonzero torque from zero initialization. The claimed learned model has no learning procedure. Gradient scaling omits2 on both terms, changing the effective learning rate rather than the minimizer. Scalar code should not be described as a general vector controller.

Accept helper concerns about prior-versus-likelihood precision, forward-model scope, unsupported zero-control expertise, and feedback timing as review questions. Reject its blanket classification of the free-energy identity as erroneous: the written identity is valid for normalized q. Action mechanisms need explicit dependencies/preferences; expected free energy is not mandatory for every continuous-time active-inference formulation. Reject any blanket claim that feedback delays necessarily cause instability; this depends on gains, delay, dynamics and architecture. Its latency numbers and expert energy/EMG claims remain unverified. Drift means zero declared input, not necessarily passive physiology.

The revised article distinguishes sensory prediction error from desired-output tracking, forward evaluation from inverse action selection, physical input from corrective feedback, and mechanistic hypotheses from established neuroscience. The replacement example states explicit units, constraints, a horizon that permits angle response, and mathematical verification, without asserting a learned neural implementation.

Primary reading is limited to the specific abstracts and passages recorded below. No full-paper acceptance, literature-wide review or human validation is claimed.

## Partial Primary Reading

Todorov/Jordan2002 abstract read at https://www.nature.com/articles/nn963 : task-relevant correction and tolerated redundant variability, not zero total actuation. Author PDF located at https://roboti.us/lab/papers/TodorovNatNeurosci02.pdf after the old Washington URL redirected to an archive; full paper not yet read.

Feldman/Friston2010 https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00215/full : abstract, introduction, selected Methods recognition/hierarchical-model prose, and attention/gain discussion read. This is a proposed precision/gain account illustrated with simulated attention tasks, not direct golfer evidence. Distinguish precision of sensory noise from prior precision and control cost. Mathematical equations omitted in the text extraction were not visually inspected. Do not copy its t-statistic analogy as an identity: standard error is not inverse variance. No full-paper or simulation acceptance. PMC endpoint had a challenge; publisher text accessible. Friston2010 PDF request failed; subsequent publisher abstract/key-point reading is recorded below, without full-paper credit.

## Reading and Adjudication Update

Issue4825 claimed22:46UTC expiry; worktreeAffineDrift-ideomotor-review, branchfix/ideomotor-rigor-4825, baseline4cf785ecc. Source/module/tests now drafted, no source acceptance or credit.

Todorov/Jordan2002: additionally read selected introduction/optimality/forward-estimator and discussion/limitation passages. Not full paper or supplement. Wolpert/Kawato1998 authorPDF abstract, selected Sections5.1/5.2 responsibility/output equations and conclusions read in text extraction; no visual equation acceptance claimed. TEC2001 publisherabstract andmetadata read; Friston2010 publisherabstract/keypoints only. No new human experiment or literature-wide review.

Four Flash helpers adjudicated: inventory; numericaltests; module draft; editorial. Tightened equilibrium tolerance, added independent zero-input cost and nonmutation checks, and renamed misleading timestep terminology. Replaced customRK4 with existingSciPyDOP853; fixed inverse-unit names and removed clipping of invalid optimizer candidates. Max-step subdivisions explicitly differ from adaptive accepted-step count.19REDmissingmodule tests ->19GREEN. Ruff/Black100/targetedmypy pass.

Editorial: accepted explicit infinite-horizon LTI/LQR conditions, future-output sensitivity scope and lack of scalar-global-optimum certificate. Added posterior variance and post-update residual clarification. Rejected claims that position-error feedback requires forward integration (ordinarypositionfeedbackisvalid), that VFEidentity fails whenyvaries (it is pointwise; constancy matters only for the selected optimization), that every active-inference model requiresEFE, and that one transientvelocityincrease provesdestabilization. Replanning alone is not a general MPCstability guarantee. Sourcealreadydistinguishes terminalangle fromrest.

## Publication and Validation Checkpoint

HTML render and all 12 content gates pass. All 656 publishable titles pass. Four light/dark, mobile/desktop browser cells pass with zero serious/critical axe findings. Both widths render all 88 math nodes (nine displays), without errors, placeholders or page overflow. All display equations were visually inspected on desktop, with a mobile gradient and code sample also inspected. Wide equations and code scroll; both mobile tables were verified to scroll from 0 to 445 px in their wrappers. Full regression is next.

The static checker initially found the test gravity literal; including the untracked new module then also found its gravity constant spelling and two nested-function docstrings. These concrete issues were fixed. A direct invocation of the local QA script could not import the repo; running it through runpy from the repository resolves the import context. Neither incident is hidden as a successful check.

The fifth Flash helper correctly identified stale issue, helper-count and primary-reading wording in this note. Those corrections were accepted; no technical acceptance authority was delegated. Parent PR #4820 delivery is independently verified in the committed receipt. PR #4824 remains under guarded auto-merge pending its site browser check at this checkpoint.
