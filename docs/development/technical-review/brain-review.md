# Computational Brain: Paired Chapter Review

Issue #4303, native child of epic #4009; corpus #4021 and Physics batch #4054.
Branch `fix/4303-computational-brain` starts at wrist PR #4304 head bcc0b6dc.
After protected wrist squash, replay only commits after bcc0b6dc onto main.
The claim was free and a codex lease was posted through 2026-09-09T03:42:54UTC.
Both complete chapter editions and all 14 exercises were read. Their web/print
claims differ, so both require correction. No corpus completion is claimed.

## Argument and Defects

The chapter should explain how geometry, mechanics, learned prediction, feedback,
impedance and uncertainty cooperate in a golf swing. The original repeatedly
converts useful modeling hypotheses into discoveries about brain implementation.
It miscounts command schedules and anatomical coordinates, equates finite delay
with impossible feedback, treats drift as free work and small input sensitivity,
and treats low-rank EMG as fixed neural commands. The displayed linear impedance
law contradicts the claim that large errors produce no restoring force. Changing
stiffness or a reference trajectory can supply energy. Equal muscle activation
need not cancel torque. Generic grip and injury advice has no matching evidence.

The supposed driver-to-putter experiment, trial counts, brain-versus-AI table,
universal frequency comparisons and global-optimum claims lack valid support.
Yips are assigned a corrupted cerebellar program and an amygdala mechanism without
evidence; choking is reduced to one explanation. Two named imaging/kinematic
studies are unverified. Several bibliography keys disguise different authors,
years or publication types. Prior #2249 and #3546 fixed narrower passages but
left contradictions elsewhere. All exercises must be reconciled with the revised
argument, rather than asking the reader to prove the original false conclusions.

## Verification Plan

Check the published logarithm in both editions, then independently compare the
delayed activation/rotor response with ODE integration and convolution. Verify
frequency response, moving/time-varying impedance storage, counterexamples to
drift-insensitivity and neural-synergy inference, and separate energy boundaries.
Preserve historical labels/anchors, inspect the rebuilt print chapter and web
page, run repository checks and use normal protected delivery. No diagnosis,
golf-specific feedback latency or unique neural implementation follows from a
toy controller or reaching experiment.

## Sources and Reading Depth

- Saunders and Knill (2003), DOI 10.1007/s00221-003-1525-2, author-hosted
  [12-page paper](https://www.psychology.hku.hk/saunlab/pubWork/saunders_03_feedback.pdf):
  abstract, methods, results, discussion and latency-estimator appendix read.
  This is virtual-finger reaching, not golf. The observed mean detection latency
  is 163ms; their estimator simulation suggests about 25ms positive bias.
  They explicitly do not directly test a forward model. The complete main text
  and appendix were read, including the introduction. Reference entries were
  not individually investigated, and extracted equations have encoding loss;
  the figures were not visually reviewed. This is not an assertion that every
  cited source or every graphical detail was checked.
- Kutch and Valero-Cuevas (2012), DOI 10.1371/journal.pcbi.1002434,
  [primary experiment/model paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002434):
  complete abstract, introduction, methods, results, discussion and figure
  captions read. It supplies mechanical counterexamples, not a disproof of all
  neural synergies. The webpage's inline equations need separate visual reading;
  do not infer their exact notation from the text extraction.
- Pruszynski et al. (2011), DOI 10.1038/nature10436,
  [publisher abstract](https://www.nature.com/articles/nature10436): read.
  Multi-joint arm perturbation evidence concerns humans and rhesus monkeys;
  it does not determine a golf feedback bandwidth. PMC full text returned a
  browser challenge, as it did in the complete-swing review.
- Mazzoni and Krakauer (2006), DOI 10.1523/JNEUROSCI.5317-05.2006: abstract
  and metadata read. PMC is challenged and the publisher open failed. No full
  paper claim. Explicit and implicit adaptation can coexist and conflict.
- Adler et al. (2011), DOI 10.1002/mds.23824,
  [primary study abstract](https://pubmed.ncbi.nlm.nih.gov/21674625/): read.
  Distinguish self-report grouping from video-defined involuntary movements;
  the co-contraction comparison p=.08 is a trend, not decisive evidence.
- Burdet et al. (2001), DOI 10.1038/35106566: publisher/PubMed abstract and
  publisher supplementary stiffness explanation read. Full paper pending.
- Beilock and Carr (2001), DOI 10.1037/0096-3445.130.4.701: publisher abstract
  excerpt read; full paper pending. Golf putting and comparison tasks provide
  evidence for specific attention/pressure hypotheses, not a universal cause.

Hogan's 1985 impedance-control Part I abstract supports the interaction-dynamics
definition; it is not the different Biological Cybernetics paper under the
legacy `Hogan:1985` key. Dreamer's primary arXiv abstract and metadata establish
the dated image/world-model counterexample; the full paper was not read.
Crossref verifies Barto and Mahadevan (2003), correcting the omitted coauthor.
The misattributed `nicholson2005human` book is Philip Nelson's *Biological
Physics: Energy, Information, Life*, Freeman, 2004, ISBN9780716743729, verified
against author information and bibliographic catalogs. A provisional
2020/student-edition interpretation was rejected before the final build.
Legacy citation keys remain compatible; the new chapter does not use that book
as evidence for neural fragility. `adler2011focus` remains the Gallwey book it
actually describes; the new `Adler2011Yips` entry identifies the actual study.

## Independent Derivations and Exercise Resolution

These are model calculations and discriminating experimental designs. They do
not identify a neural implementation or establish golf-specific parameter values.
Both published editions include worked numerical checks and answer guidance.

1. **Schedules and Dimension.** Two hundred channels over thirty intervals give
   6000 entries and `7^6000` discrete schedules. The base-ten logarithm is
   5070.588240085541. Five channels give 150 entries and logarithm
   126.764706002139. At 1ns per evaluation the first enumeration takes
   `10^5061.58824` seconds. Neither count is a physical state dimension, number
   of distinguishable outcomes, or biological clock. Thirty intervals have
   thirty-one endpoint samples. The old anatomical list summed to14 rather
   than13 and mixed bilateral/aggregate coordinates; replace it with a
   reproducible model/constraint specification rather than another asserted
   anatomical total.
2. **Feasible Synergies.** A coefficient vector must lie in the polytope
   `{c: 0 <= Wc <= 1}`, intersected with any independently declared sign,
   activation and rate constraints. With `R=[1,-1]` and `W=[1,1]^T`, `RW=0`:
   one coefficient loses both torque directions available from independent
   activations. Coactivation-dependent stiffness is absent from this toy map.
   A separate four-muscle/two-coordinate length Jacobian produces rank-two
   length changes without imposing grouped neural commands. Neither example
   disproves biological coordination; each invalidates an inference from rank
   alone. Unequal arms/capacities give `.04*1000*.2-.03*800*.2=3.2Nm`, despite
   equal antagonist activation.
3. **Drift and Delivery Gain.** For zero initial state and constant input,
   `x(T)=(c+u)*expm1(aT)/a`; the input derivative is `expm1(aT)/a`, with limit
   `T` at `a=0`. At `a=10/s,T=.3s,c=1rad/s`, the gain is1.908553692319s and
   final nominal drift20.085536923188rad/s. A .01rad/s input changes the endpoint
   by .019085536923rad. ODE central differences independently verify the gain.
   Multibody delivery instead requires the propagated input kernel `C Phi B`,
   complete prepared state, feasible input set, latency and event-time terms.
   Large nominal drift says nothing by itself about those quantities or energy.
4. **Delayed Rotor.** Let elapsed time after command arrival be `s`. Solving
   `Ta*tau_dot+tau=U` with zero initial torque gives
   `tau(s)=U*(1-exp(-s/Ta))`. Convolving angular acceleration with the remaining
   time gives `delta_theta=(U/I)*integral_0^h (h-s)*(1-exp(-s/Ta)) ds`, hence
   `(U/I)*(h^2/2-Ta*h+Ta^2*(1-exp(-h/Ta)))`. Exponential expansion cancels the
   linear/quadratic terms, leaving `h^3/(6Ta)` in the bracket. At the declared
   `.3s/.06s/.04s/.05kgm²/.5Nm` parameters, perturbations at `.04,.18,.22,.26s`
   give `.135892192848,.006429917438,.000295509445,0rad`. The first three are
   `7.786049119,.368407132,.016931444deg`. Independent ODE and quadrature agree.
   Zero correction follows when `tp+L>=T` only under the stated causal command
   and zero perturbation-state assumptions. Existing motion/activation need not
   vanish. Activation has immediate post-delay response:2.469% after1ms when
   Ta40ms,63.212% after one time constant. It is not another dead time.
5. **Impedance and Work.** For `tau=-Ke-D*e_dot`, `V=Ke²/2` gives
   `tau*q_dot+V_dot=-D*e_dot²+tau*qd_dot+K_dot*e²/2`. Fixed reference/stiffness
   leaves the nonpositive damping term; moving references and stiffness
   modulation can add energy. At clamped `.1rad`, K10→30 adds
   `(30-10)*.1²/2=.1J`. A .2s ramp supplies .5W into storage. These are mechanical
   port balances, not metabolic budgets or guarantees for a full feedback loop.
6. **Two Errors.** A known aiming offset can cancel a visual rotation at the
   target while the observed cursor still differs from the predicted sensory
   consequence of the hand command. Record aiming reports/kinematics, perturbation
   and feedback, then examine aftereffects, washout, retention and controlled-load
   responses. A changed mechanical response is not automatically implicit
   adaptation; converging observations are needed to separate hidden states.
7. **Computational Descriptions.** A rollout predicts consequences using dynamics;
   a cached policy maps represented state to action; a value function estimates
   future return/cost under stated assumptions. They can be combined. Compare
   predictions under new loads, changed feedback and time pressure; neural
   attribution additionally needs appropriate physiological observations or
   interventions. Success and curve fitting alone do not identify stored code.
8. **Hierarchy.** A shot planner passes a desired delivery distribution and cost
   to a feasible motion planner, then an estimator/actuator controller implements
   the motion subject to force/contact bounds. State uncertainty, friction
   feasibility and saturation must travel upward. An infeasible request triggers
   replanning or a revised target, not impossible torque or ground reactions.
   This is an engineering architecture, not a brain-region map.
9. **Jerky Motion.** Delayed high-gain correction and an unstable/noisy moving
   reference can both produce jerks. Randomized perturbations with synchronized
   motion, force and EMG can test timing/phase predictions; changing feedback or
   task conditions can discriminate further. Similar traces, hidden muscle state
   and multiple possible mechanisms prevent simulation from diagnosing yips.
10. **Pressure Hypotheses.** Explicit monitoring predicts an execution-specific
    attention effect in appropriate practiced tasks; distraction predicts effects
    tied to diverted task resources. Independently manipulate attention and
    pressure and verify that manipulation. An absent predicted interaction under
    an adequately sensitive design counts against the specified account. A
    single miss, or a null study with poor manipulation/power, is inconclusive.
11. **Attention Experiment.** Stratify novice/experienced putters, randomize a
    specified attentional instruction and pressure condition, use matched targets
    and practice exposure, and record both instruction compliance/arousal and
    preregistered accuracy/dispersion. Counterbalance order or use parallel groups
    to address carryover. Test retention/transfer separately from immediate
    performance. Expertise remains an observational factor unless randomized
    training, rather than pre-existing groups, is the causal intervention.
12. **Frequency Response.** `|H|=1/sqrt(1+(omega*Ta)²)` and unwrapped phase
    `-omega*L-atan(omega*Ta)` follow from a unit-magnitude delay and first-order
    activation filter. At1/3/5Hz the magnitudes are
    `.969838831,.798471157,.622676993`; phases are approximately
    `-35.7078,-101.8156,-159.4881deg`. Stability also depends on plant, sensor and
    controller dynamics. Firing rate, sampling rate, bandwidth and resonance are
    distinct quantities; this partial transfer function certifies none of them.
13. **Matched Benchmark.** Declare task/target, embodiment/actuation, sensing,
    prior experience/pretraining, real versus simulated data, online computation,
    disturbances, allowed feedback and evaluation distribution. Include failure
    and uncertainty, not only best shots. Processor20W*.3s=6J and head
    `.5*.2*50²=250J` use different boundaries; their ratio is not efficiency.
    A head-only1m fall yields1.962J,0.7848% of250J. Whole-body gravity, initial
    energy, actuator work, elasticity, losses and training require separate terms.
14. **Intertwined Mechanisms.** Randomize a calibrated perturbation's direction
    and timing within a matched task and measure the pre-perturbation state.
    Compare early mechanical response, later correction, and changes across
    trials, with controlled feedback/load, washout and held-out transfer. Repeat
    with measured grip/contact conditions. This can distinguish predictions for
    prepared state, impedance, input gain and learning, while force/EMG/kinematic
    observations and uncertainty models constrain remaining ambiguity. Begin with
    instrumented slow tasks or controlled simulators where needed; simulation
    verifies equations, physical measurements validate human predictions.

## Local Validation in Progress

Two publication arithmetic tests failed against the original chapter editions;
the other independent mechanical checks passed. All17 now pass against the paired
rewrite. The new test file passes Ruff and was formatted with Black100 after its
first check identified one wrapping change. No production numerical utility was
added. Figure inventory now records28 illustrated chapters,31 LaTeX figures,
23 TikZ,8 included images,31 labels and9 Quarto figures; the unrelated22-figure
parity gap remains. Expectations were updated to these measured counts.

The first full book build (pdfLaTeX/BibTeX/makeindex/two further pdfLaTeX passes)
and selected root-config web render succeeded. All17 initial chapter pages were
visually inspected, including all14 exercises and answer guidance. The diagram's
initial outer learning arrows crossed its middle box; routing them around the
boxes repaired that. Two awkward print heading breaks, a one-line callout
continuation and an orphaned reference to an earlier draft were corrected.
Short TOC titles and explicit print-only line breaks preserve navigation.
All30 historical web heading/reference anchors are retained; the previous
generated `exercises:ex:ch26_exercises` print label is retained as an alias.
The final550-page book was rebuilt and all17 chapter pages (printed403–419,
physical431–447), the affected TOC/figure-list pages22/27 and bibliography
pages532/533/535/536/537/539 were inspected. The inherited `sec:sensitivity`
duplicate elsewhere in the book remains a whole-corpus consistency item; no
chapter26 citation/reference is undefined and its boxes/equations fit. Nelson
and Barto/Mahadevan are no longer cited by this chapter and therefore do not
appear in its rendered bibliography.

The full root suite passes4867, with29 skips,131 deselections and50 warnings in
253.89s; explicit src coverage is92.98%. Content lint passes130 with4 skips.
Ruff, Black100, strict mypy86 and title-case631 pass. Forty focused numerical
and figure checks passed before the final scanner repair; all64 affected checks
pass afterward. Static CI contracts initially passed33/34: the COR detector
matched the trailing `85%` inside the valid head-only `0.785%` gravity ratio.
Three new number-boundary regressions first hit a missing pytest import, then
properly failed for `0.785`, `180` and `1085` in both source formats. A numeric
left boundary repairs the detector; all24 parity tests and all34 static
contracts now pass. The original incorrect82% energy-ratio cases still fail
the detector as intended. No baseline or severity threshold was relaxed.

The first browser pass exposed pale bibliography text on a white appendix in
dark mode (computed text rgb221/225/231, background255/255/255). A chapter-only
transparent appendix background fixes it. The second pass typesets all113 math
expressions, including11 displays; all14 width/theme combinations (320 through
1920px) have zero document overflow or MathJax errors. Both themes have no
serious/critical axe violations; inherited moderate duplicate landmark labels
remain. All30 historical anchors are unique, both images load with alt text,
all internal fragments resolve, and each figure scrolls40px by ArrowRight.
Thirty-six targeted web captures and six math/figure right-edge captures were
inspected. One desktop capture caught a section's entrance animation; the final
capture pass waits for it to settle. Mobile inspection also showed inherited
equation shrinking; a scoped rule now preserves the surrounding text size and
lets long derivations scroll. The final math-size pass and protected delivery
remain at this checkpoint.

Render hooks changed only generated dates/formatting in three unrelated trust
registries; structural JSON comparison confirmed this before restoring those
own generated changes. Claim-audit evidence hashes were already current; the
claim/critique and audit inventory generators introduce no substantive changes.
Do not stage untracked source extracts, local renders or browser artifacts.

## Wrist Delivery Dependency

PR4304 remains protected and open at bcc0b6dc. CI34302378496 passed its Python,
JavaScript, static, HTML/CSS and ordinary browser tests. Its all-route verifier
found two newly published standalone HTML companions lacking canonical links,
navigation and theme state. These are
`/content/wrist-as-universal-joint/Wrist_Universal_Claude.html` and
`/src/tools/wrist_universal_joint/grip_angle_simulator.html`. Both return200,
have one heading, no overflow and no axe violations; the two unrelated
warn-only contrast findings did not cause the failure. Exact artifact10085985439
was downloaded and inspected. Repair the companion pages on the wrist branch,
keeping the verifier contract intact, then return to the saved brain branch.
Both codex leases were renewed through2026-09-09T05:42UTC. No wrist merge or
publication is claimed. Never switch, commit or push during local tests/build/QA.

### Final Chapter-Only Presentation Check

The final math-size render succeeds. All14 responsive/theme cases,113 equations,
internal fragments, image loading, axe serious/critical policy and two40px
figure keyboard checks pass again. Nine scrolling right-edge captures, the
settled desktop yips section and the rotor derivation in both phone themes were
inspected after the final CSS change. The preceding36 body and6 edge captures
remain the broader layout review; this is not a claim that every pixel of every
newly generated capture was inspected. Equation size now follows surrounding
text and both ends remain reachable. The single early faded section capture was
an entrance-animation timing artifact, not a persistent contrast defect.


## Protected-Main Replay and Wrist Publication, 2026-09-09

The saved brain checkpoint 2a5ec6fb was pushed with every hook passing. Remote
inspection then showed that PR #4304 had already merged as a11abdbf, after another
task changed the auxiliary HTML publication policy. That task removed the old
HTML guide from deployment and excluded content/src HTML from the Quarto page
manifest. The simulator remains linked as an auxiliary resource. This supersedes
the earlier instruction to repair an open wrist PR; no competing wrist repair
was made. The manifest no longer claims those auxiliary routes as Quarto pages.

Main deployment 34310520642 at descendant 19170f82 succeeded. Its exact live
artifact 10088805870 was downloaded and inspected: 956/956 checks, 239 routes,
zero failures, serious/critical axe findings, retries or transient responses.
Auxiliary simulator validation rests on the earlier direct browser checks,
not on the reduced page manifest. The wrist merge itself had a failed deploy;
the successful descendant contains the critique-link repair from PR #4305.

Only brain commit 2a5ec6fb was cherry-picked onto 19170f82, becoming 52f80227
on fix/4303-computational-brain-review. No force push or history replacement.
The replay passes 4,900 root tests, 29 skips, 131 deselections and 50 warnings
in 383.16 seconds. All 64 affected checks, 34 static contracts and the new site
link gate pass. The first direct link-checker invocation lacked the package
import path; invoking it as a module passes without changing its source.
No new scientific assertions or equation changes were introduced by the replay.
Both complete original swing-plane/launch editions were read while these
checks ran; their fixes belong to the next focused issue, not this PR.
