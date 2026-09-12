# Strokes-Gained Accounting and Individual Inference: Technical Review

## Review Scope and Authority

Governing issue #4358, under epic #4009 and corpus audit #4021. This review
covers the complete strokes-gained article, its bibliography companion, and
`critiques/strokes_gained_non_ergodic.md`. The original and revised sources
were read in full. The original article contained about 5,375 whitespace words.
No empirical golfer dataset was fitted and no textbook PDF changed.

The article's central question is how a change in a golfer's movement can change
scoring. The corrected chain is capabilities and feasible actions, impact and
launch, flight and ground interaction, shot-outcome distributions, continuation
policies and counted score. Each predictive link needs qualification. An exact
accounting identity is not evidence that a proposed practice intervention works.

## Findings and Disposition

| Finding                                                                                     | Severity | Saved Correction                                                                                                            |
| ------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| Opening denies one-for-one scoring changes despite its own telescoping identity             | High     | Fixed benchmark/start-state conditions, whole-round and category identities, explicit distinction from intervention effects |
| Penalties omitted and per-putt/per-round units confused                                     | High     | Counted transition costs, penalty example, denominator explanation                                                          |
| Descriptive regression asserted to satisfy Bellman optimality                               | High     | Separate policy evaluation and optimization; state sufficiency and persistent player identity                               |
| Worse putter asserted to have steeper distance slope                                        | High     | Exponential curves reverse slope ordering; three-player finite counterexample                                               |
| Mean proximity treated as a sufficient outcome description                                  | High     | Full distributions, Taylor conditions, equal-mean counterexample, precise mean-preserving-spread condition                  |
| Categories implicitly treated as independent causal contributions                           | High     | Approach/putting boundary transfer and within-putting cancellation                                                          |
| Observed contrasts called ATEs and pooled derivatives called average individual derivatives | High     | State-dependent composition weights and derivative term; intervention/identification conditions                             |
| Hierarchical model claimed to establish causality                                           | High     | Predictive pooling, validation, overlap, exchangeability, consistency and carryover limits                                  |
| Non-ergodicity, hidden states and risk neutrality treated as accounting requirements        | Medium   | Distinguish accounting, conditional means, sequential models and explicit decision objectives                               |
| Worse expected score described with wrong sign                                              | Medium   | Score is a cost; threshold example prefers a different action than mean-score minimization                                  |
| Affine mechanics claimed to supply validated coaching causality                             | High     | Specified states/inputs, activation/contact and identification limits; complete mechanics-to-score chain                    |
| Bibliography and editorial objections contain unsupported facts                             | Medium   | Four verified sources, withdrawn unverified metadata/graph claims, no invented universal sample threshold                   |

The directly linked critique is corrected in canonical source while its ledger
identity and `open` disposition remain unchanged. Generated trust annotations
are untouched. This review records corrected source arguments. Changing route review status
requires a separate commit binding this report and the reviewed sources to their
actual implementation revision; it does not close the governed critique.

## Derivation and Independent Checks

For fixed B with terminal value zero, `g_t = B(s_t) - c_t - B(s_(t+1))`; summing
gives B(s_0) - sum(c_t) for any intermediate B values. Across rounds,
delta E[G] = delta E[K] - delta E[C]. For an exhaustive partition, category
sums equal total G. No probabilistic model or optimality assumption is needed.

At a fixed approach start, with one approach and on-green continuation through
holing, expected approach SG is B(start)-1-E[B(X)] and expected putting SG is
E[B(X)-V_i(X)]. Their sum is B(start)-1-E[V_i(X)]. With unchanged continuation
skill and leave distributions P0/P1, define b_B=E0[B]-E1[B] and b_i=E0[V]-E1[V].
Then the mean category changes are b_B and b_i-b_B, totaling b_i. If the altered
shot itself is a lag putt, both contributions fall inside putting; the internal
benchmark cannot invalidate the whole-category identity.

Policy evaluation uses a fixed policy and a proper absorbing transition model:
V=c+PV, hence V=(I-P)^(-1)c. Minimization over available actions is additional.
The example P=[[0,1],[0,.25]], c=[1,1] gives V=[7/3,4/3]; an action costing one
and finishing from state 1 proves the evaluated policy is not optimal there.

For deterministic small delta, benefit is V(x)-V(x+delta), approximately
-V'(x)delta. For a coupled random shift delta(X), include the expectation of
the derivative product and the second-order term. A difference between levels
does not itself prove a difference between slopes or contrasts.

The two-putt illustration has V=2-p on positive distance, with a certain
finishing stroke after every miss. It is not a general putting transition model.
For p_A=exp(-.3x), p_B=exp(-1.2x), B has lower make probability everywhere x>0.
The slope magnitudes cross at log(4)/.9 = 1.5403270679 m. At .5 m they are
.258212393 and .658573963; at 3 m, .121970898 and .032788467. Finite benefits
from 2.5 to 2 m are .0764450834 and .0409308849 strokes. Thus worse putting
does not order proximity benefits.

Separate far/near benchmark values (1.5,1.3) give approach gain .2. Player
values A=(1.2,1.1), B=(1.7,1.4), C=(1.8,1.75) give total benefits .1,.3,.05;
putting category changes -.1,+.1,-.15. For a lag putt beginning at B=2, moving
from continuation (B,V)=(1.5,1.7) to (1.3,1.4) changes first-putt SG by .2 and
continuation SG by .1; total putting gain and score benefit both equal .3.

Mean distance 2 can arise from a certain 2 or a 50/50 mixture of 1 and 3.
With continuation values [1.1,1.5,2.1], expected scores are 1.5 and 1.6.
Larger variance alone does not generally order expectations; the article uses
the more precise convex-function/mean-preserving-spread condition.

For pooled observational values B(s)=sum_i w_i(s)V_i_obs(s), differentiation
includes sum_i w_i'(s)V_i_obs(s). In the declared interval [1,2], VA=1+.1d,
VB=1.5+.2d and wA=.8-.2d. At d=1.5 the individual-slope part is .15 and the
composition part .13, giving .28. A finite-difference test checks the result.

The tournament example scores 4 certainly versus 3 with probability .6 and 7
with probability .4. Means are 4 and 4.6, while chance of scoring at most 3 is
0 and .6. This is a constructed objective comparison, not a psychological
claim. For two interventions, interaction benefit is
F(1,0)+F(0,1)-F(0,0)-F(1,1), obtained by subtracting the sum of isolated score
reductions from the combined reduction.

## Primary Sources Actually Read

1. Broadie: publisher metadata confirms _Interfaces_ 42(2), 146–165 (2012),
   DOI 10.1287/inte.1120.0626. Author preprint dated April 8, 2011; full Section 2
   and opening Section 3 through benchmark-estimation discussion were read.
   Its optimality approximation is explicitly acknowledged in the rewrite.
   No claim of whole-paper reading or current ShotLink specification validation.
2. Sutton/Barto: 2018 draft at
   `https://www.andrew.cmu.edu/course/10-703/textbook/BartoSutton.pdf` downloaded
   successfully (43,634,706 bytes). PDF pages 80–86, printed 58–64, were read:
   full 3.5 and opening 3.6 through the partial last-page action-value discussion.
   Production artifacts are present; no empirical golf claim comes from it.
   Original author site timed out; CMU hosts the authors' primary text.
3. Gelman: `https://sites.stat.columbia.edu/gelman/research/published/multi2.pdf`,
   full technical text and reference list read, four-page paper, DOI
   10.1198/004017005000000661. Prediction and causal-coefficient limits apply;
   radon data are not used as golf evidence.
4. Hernán/Robins: author page `https://miguelhernan.org/whatifbook` links
   `/s/hernanrobins_WhatIf_19aug26.pdf`. Download succeeded (11,315,465 bytes).
   PDF 37–44, printed 28–35, read completely: identification conditions,
   exchangeability, crossover/carryover Fine Point 3.2, positivity, and opening
   consistency/intervention-version discussion. Page 44 ends mid-discussion.
   Earlier Harvard URLs failed. Do not claim all Chapter 3 or whole-book reading.

The source PDFs remain local scratch and are not committed. Four bibliographic
entries are in `references/strokes-gained-rigor.bib`. Historical Broadie2014
and Peters2019 citation destinations remain spans, explicitly not evidence for
the new examples. All old heading IDs were preserved in source where known;
all 37 original article destinations and the four current citation entries were
subsequently verified in the rendered browser DOM.

## Joint Interventions and Attribution Conventions

The extension beyond proximity separates old/new mean immediate costs c0/c1,
next-state distributions P0/P1 and continuation functions V0/V1. Define
F_a=c_a+E_Pa[V_a]. Then

    F0-F1 = (c0-c1) + (E0[V0]-E1[V0]) + E1[V0-V1].

The identity follows by adding and subtracting E1[V0]. Evaluating the
redistribution at V1 instead allocates the interaction differently without
changing the sum. With costs 1/1.1, probabilities (.5,.5)/(.75,.25), and
values (1.5,2)/(1.3,1.9), costs fall 2.75→2.55. Allocations are
-.10+.125+.175=.20 or -.10+.15+.15=.20. The interaction is .025: the combined
benefit exceeds the sum of the two isolated benefits by that amount. Neither
allocation is an identified causal mediation effect merely because it is exact.

For dispersion, a coupling with E[Y|X]=X and convex V gives
E[V(Y)|X]≥V(X), provided the expectations exist. Averaging proves the value
ordering. A greater variance alone is not this condition. The independent test
uses X=(1.5,2.5) and conditional Y=(1,2)/(2,3), with V(d)=1+.1d²; the increase
is .025. The derivative mixture formula is explicitly scoped to differentiable
weights and values along a scalar coordinate in a finite player mixture.

## Uncertainty and Falsifiers

The telescoping result is algebraic under the stated cost and boundary
conventions. Missing transitions, terminal-state errors, penalties omitted from
cost, or inconsistent benchmark versions invalidate the intended reconciliation;
no amount of regression fit repairs those records. The executable penalty
counterexample deliberately demonstrates the failure when one cost is omitted.

The constructed slope and equal-mean examples disprove universal claims. They
do not estimate how frequently those reversals occur in golfers. Empirical
recommendations would require support over relevant states, held-out calibration,
credible intervention comparisons, time and carryover controls, and a stated
score or tournament objective. A personalized model performing worse than a
common benchmark on relevant future outcomes defeats the claim that its extra
complexity helps that predictive task.

A mechanics-to-score proposal should specify a feasible input change, measurable
launch and dispersion predictions, the continuation model and the predicted
score contrast. Failure of any measured transition, lack of transport to the
intended golfer, or scoring discrepancies beyond declared uncertainty challenges
the proposal. Identifying model parameters, fitting observed motion or assigning
an acceleration contribution alone does not establish a coaching effect.

## Audience Framing and Critique Disposition

The abstract and explanatory panels distinguish description, prediction and
causal inference. Editorial objections are identified as editorial, not quotations
from researchers. The references name exactly which primary passages were read;
no whole-book or current-provider-specification claim is inferred from them.
The linked critique explicitly withdraws false accounting premises while retaining
its stable identity, medium severity and governed open status. The remaining
model-validation concern is not disguised as evidence that score totals stop
adding up. Generated trust annotations and the critique ledger were not edited.

## Presentation and Verification

The numerical builder and JSON are reproducible, with 35 focused tests covering
penalties, category cancellation, proper policy evaluation, slope reversals,
state-dependent composition, full distributions, joint interventions and objective
changes. The follow-up extension had a missing-function RED failure before GREEN.

The review found and corrected dark reference contrast, math-only table headers,
expanded panels clipped to zero height by a shared CSS sibling selector, and
dark card/label contrast. The article's scoped stylesheet preserves semantic
heading wrappers and uses actual aria-hidden state and theme colors. A browser
check of aria-expanded alone was insufficient and was strengthened to measure
panel height. The linked critique's five full reading captures were read; its
four expressions and original destinations were verified.

Root tests pass 5,297 cases with 29 skipped, 132 deselected, 59 warnings and
79.35% coverage. The numerical builder has 100% statement coverage; boundary
checks reject malformed counted transitions, invalid costs, nonabsorbing policies
and out-of-domain mixtures. The stored numerical artifact reproduces exactly.
The combined numerical, source-mapping, inventory and deployment-boundary suite
passes 57 cases. An earlier run exposed Playwright scratch output at the root;
closing the browser and relocating its output resolved both hygiene failures.
Ruff, Black100 over 705 files, configured CI mypy over 91 files and stricter
mypy over both changed implementation modules pass. The title audit of 636
sources and content lint (131 passed, 4 skipped) also passed.

Final article checks verified 154 expressions, 18 displays, all 37 original IDs,
four bibliography entries, 126 expression/table cases and 64 keyboard scrolls.
The critique verified four expressions, six display cases and two keyboard
scrolls. Both pages passed seven widths in both themes. The 28 article reading
captures cover the expanded explanations; five critique captures cover its full
text. Source and full reading captures were inspected, with additional inspection
of final affected equations, table edges, panels and dark references. The final
panel-gradient correction received a fresh 14-case layout/axe check and 12 panel
captures. Wide equations retain normal text size and remain keyboard-scrollable.

The full scan retains only shared moderate landmark-unique warnings. Automated
contrast scanning missed a pale takeaway on a light gradient; visual review
caught it and the final panel background fixes it. No serious/critical axe finding
remains. Axe's own font preload probes generated CSP console noise; these are
recorded separately from the production-style verifier, whose final 28 records
all have HTTP 200, no console or inspection failures, no serious/critical axe
findings, and no retries. Raw Quarto output receives the existing production
polyfill transform before that gate; no console error was suppressed.

`reports/technical-review/strokes-render-verification.json` preserves the
source hashes and case summaries. Numerical inputs and outputs are in the adjacent
`strokes-gained-numerics.json`; `python -m scripts.build_strokes_gained_examples` and the focused test module reproduce them.
The complete failure/recovery history and exact reproduction commands are retained
in `docs/development/technical-review/strokes-gained-review.md`. These are local
review results. A protected merge and revision-matched live deployment remain
separate requirements for a publication claim.
