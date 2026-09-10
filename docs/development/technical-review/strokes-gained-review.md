# Strokes-Gained Technical Review and Handoff

## Status and Scope

User-requested intermediate handoff, September 10, 2026. Governing issue #4358
is a native child of #4009 and contributes to #4021/#4059. Worktree:
`C:/Users/diete/Repositories/AffineDrift-technical-review`; branch
`fix/4358-strokes-gained-rigor`. The source rewrite is saved, not publication
ready. Full rendered review, trust-inventory reconciliation, protected delivery,
and the remaining corpus are unfinished. Do not mark the epic complete.

The complete original article (about 5,375 words), bibliography companion, and
linked critique were read. The replacement article is about 4,723 whitespace
tokens including markup; this is a content reconstruction, not a shortened
claim that all previous reasoning was correct. No empirical golfer dataset was
fitted. All quantitative examples are explicitly illustrative.

## Findings and Disposition

| Finding | Severity | Saved Correction |
|---|---|---|
| Opening denies one-for-one scoring changes despite its own telescoping identity | High | Fixed benchmark/start-state conditions, whole-round and category identities, explicit distinction from intervention effects |
| Penalties omitted and per-putt/per-round units confused | High | Counted transition costs, penalty example, denominator explanation |
| Descriptive regression asserted to satisfy Bellman optimality | High | Separate policy evaluation and optimization; state sufficiency and persistent player identity |
| Worse putter asserted to have steeper distance slope | High | Exponential curves reverse slope ordering; three-player finite counterexample |
| Mean proximity treated as a sufficient outcome description | High | Full distributions, Taylor conditions, equal-mean counterexample, precise mean-preserving-spread condition |
| Categories implicitly treated as independent causal contributions | High | Approach/putting boundary transfer and within-putting cancellation |
| Observed contrasts called ATEs and pooled derivatives called average individual derivatives | High | State-dependent composition weights and derivative term; intervention/identification conditions |
| Hierarchical model claimed to establish causality | High | Predictive pooling, validation, overlap, exchangeability, consistency and carryover limits |
| Non-ergodicity, hidden states and risk neutrality treated as accounting requirements | Medium | Distinguish accounting, conditional means, sequential models and explicit decision objectives |
| Worse expected score described with wrong sign | Medium | Score is a cost; threshold example prefers a different action than mean-score minimization |
| Affine mechanics claimed to supply validated coaching causality | High | Specified states/inputs, activation/contact and identification limits; complete mechanics-to-score chain |
| Bibliography and editorial objections contain unsupported facts | Medium | Four verified sources, withdrawn unverified metadata/graph claims, no invented universal sample threshold |

The directly linked critique is corrected in canonical source while its ledger
identity and `open` disposition remain unchanged. Generated trust annotations
are untouched. Both affected route inventory records remain `deferred`: this
checkpoint is not an evidence-backed adjudication or completed #4059 audit.

## Derivation and Independent Checks

For fixed B with terminal value zero, g_t = B(s_t) - c_t - B(s_(t+1)); summing
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

1. Broadie: publisher metadata confirms *Interfaces* 42(2),146–165 (2012),
   DOI 10.1287/inte.1120.0626. Author preprint dated April 8,2011; full Section 2
   and opening Section 3 through benchmark-estimation discussion were read.
   Its optimality approximation is explicitly acknowledged in the rewrite.
   No claim of whole-paper reading or current ShotLink specification validation.
2. Sutton/Barto: 2018 draft at
   `https://www.andrew.cmu.edu/course/10-703/textbook/BartoSutton.pdf` downloaded
   successfully (43,634,706 bytes). PDF pages 80–86, printed58–64, were read:
   full3.5 and opening3.6 through the partial last-page action-value discussion.
   Production artifacts are present; no empirical golf claim comes from it.
   Original author site timed out; CMU hosts the authors' primary text.
3. Gelman: `https://sites.stat.columbia.edu/gelman/research/published/multi2.pdf`,
   full technical text and reference list read, four-page paper, DOI
   10.1198/004017005000000661. Prediction and causal-coefficient limits apply;
   radon data are not used as golf evidence.
4. Hernán/Robins: author page `https://miguelhernan.org/whatifbook` links
   `/s/hernanrobins_WhatIf_19aug26.pdf`. Download succeeded (11,315,465 bytes).
   PDF37–44, printed28–35, read completely: identification conditions,
   exchangeability, crossover/carryover Fine Point3.2, positivity, and opening
   consistency/intervention-version discussion. Page44 ends mid-discussion.
   Earlier Harvard URLs failed. Do not claim all Chapter3 or whole-book reading.

The source PDFs remain local scratch and are not committed. Four bibliographic
entries are in `references/strokes-gained-rigor.bib`. Historical Broadie2014
and Peters2019 citation destinations remain spans, explicitly not evidence for
the new examples. All old heading IDs were preserved in source where known;
actual rendered destination verification remains pending.

## Validation at the Intermediate Checkpoint

- RED: new module absent (13 fixture errors) and original source lacks corrected
  accounting conditions (one assertion failure), captured in `strokes-red.log`.
- GREEN: 14 focused tests passed; independent numerical values and probability
  validation checked. Ruff and Black100 passed. JSON regeneration succeeded.
- Title audit: all636 sources pass. Root checkpoint:5,269 pass/29 skip/132 deselected/59 warnings, coverage79.29%;
  content lint131 pass/4 skip. All QA processes reaped before Git.
- No revised Quarto render, browser captures, axe/keyboard verification, citation
  rendering verification, or production route gate has run for this article.
  The existing local HTML is the old article. No PDF textbook changed.
- A combined delete/add apply_patch invocation was rejected before mutation;
  separate operations succeeded. No content was lost in the final saved source.

## Exact Continuation Plan

1. Read AGENT_HANDOFF and the governing issue; check central inbox and claim,
   acquire a new unique session/presence, and inspect the draft branch/PR.
2. Finish adversarial source reading and add any missing meaningful checks,
   especially full cost/continuation boundaries and stochastic-policy conditions.
3. Render article and critique via `render_selected.py` using the root config.
   Do not prune the root docs tree; it holds canonical review records.
4. Preserve all37 original article destinations from committed
   `strokes-original-ids.json`. Verify critique destinations and all four citation entries.
5. Adapt the local scratch `qa_forces_all_scroll.js` (or recreate equivalent
   browser checks if continuing in another clone) for the actual article/critique routes. The
   existing thresholds, expected text and IDs are Chapter4-specific. Check every
   expression/table at320/390/1440 and full light/dark responsive cases, keyboard
   scrolling, disclosures, all links and axe. Read all final full-page captures.
6. Complete root/content/static checks and actual-route production gate. Record
   failures honestly, then reconcile affected #4059/#4057 trust inventory records
   with genuinely completed review evidence; regenerate bound projections only
   through canonical tools. Do not silently close the governed critique.
7. Update single SPEC row, DL-#4358 and handoff. Sync current main with normal
   merge/rebase rules, preserving peer changes. Never mutate Git during local QA.
   Make the draft PR ready only after verification, then use protected squash
   delivery and verify the revision-matched live artifact before marking shipped.

## Corpus and Protected Work

Long remaining items include muscle-to-joint torques (~5,283 original words),
nullspace (~5,174), curiosity (~5,123), and the many indexed/partial sources in
`corpus-review-index.csv`. Five completely read DCR critiques are queued under
#4340. Corpus completion remains unproven. Keep immutable
`articles/proximal_distal_energy_transfer/`, bound DCR evidence, authority pins,
peer impact/acoustics #4253/#4255 and Chapter29, original checkout, and all peer
handoff/DL sections untouched.

## Committed Handoff Checkpoint

Implementation c46453792a2fe87cd2c3ad382090e93ee0a78836 is pushed in draft
PR #4360. The first commit13e0a098 was normally replayed before first push onto
published main0c753400; the scoped article, critique, bibliography, numerical
builder and tests did not change, while merged peer impact/acoustics work was
preserved. Root/content checks above ran before replay; all14 focused tests
passed again afterward. Normal commit and push hooks passed. The first commit
attempt required only Prettier formatting of the bibliography companion.

The final documentation checkpoint is identified by SELF in AGENT_HANDOFF.
The issue lease and central presence were released successfully for takeover:
receipts5621007068 and5621008118, September10 at15:16:52Z. This is a complete
save-and-handoff operation, not completion of the scientific corpus review.
Do not auto-merge draft4360 until its outstanding review and delivery work is
finished. The full goal remains active; no new agent was spawned.
