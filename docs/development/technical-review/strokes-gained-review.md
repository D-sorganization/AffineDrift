# Strokes-Gained Technical Review and Handoff

## Status and Scope

Resumed September 12, 2026, under reopened #4358 (child of #4009;
corpus #4021 and applied routes #4059). Worktree:
`C:/Users/diete/Repositories/AffineDrift-technical-review`; branch
`fix/4358-strokes-delivery`, based on main
`59b4b84790d22e45d26e222a86d5ae260954b836`. Follow-up PR not created.
PR #4360 was converted to regular and merged as
`e19e3ff17fd6340ae05c9362fea7c7049d4bf089` before its recorded rendered review
and inventory reconciliation were complete. This follow-up finishes that work.
All future PRs must be regular, per the user's explicit instruction.
The overall corpus remains unfinished; do not mark the epic complete.

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
   acquire a new unique session/presence, and inspect the current branch/PR.
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
   Create a regular PR after verification, then use protected squash
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

Implementation c46453792a2fe87cd2c3ad382090e93ee0a78836 was first pushed in
PR #4360, subsequently converted to regular and merged. The first commit13e0a098 was normally replayed before first push onto
published main0c753400; the scoped article, critique, bibliography, numerical
builder and tests did not change, while merged peer impact/acoustics work was
preserved. Root/content checks above ran before replay; all14 focused tests
passed again afterward. Normal commit and push hooks passed. The first commit
attempt required only Prettier formatting of the bibliography companion.

The final documentation checkpoint is identified by SELF in AGENT_HANDOFF.
The issue lease and central presence were released successfully for takeover:
receipts5621007068 and5621008118, September10 at15:16:52Z. This is a complete
save-and-handoff operation, not completion of the scientific corpus review.
The outstanding rendered review and evidence work is now on the follow-up
branch; the historical merge did not prove it complete. The full goal remains active; no new agent was spawned.

## September 12 Follow-Up Decisions

Added the full immediate-cost, leave-distribution and continuation-value
intervention decomposition. Old/new costs 1/1.1, distributions (.5,.5)/(.75,.25)
and continuation values (1.5,2)/(1.3,1.9) give total costs 2.75/2.55 and a .20
benefit. Allocation at old skill gives -.10+.125+.175; reversing the order gives
-.10+.15+.15. Their .025 interaction is the combined benefit minus the isolated
benefits. This is model accounting, not causal identification. Added independent
checks for that identity and conditional Jensen's mean-preserving-spread condition;
17 focused tests passed after a recorded missing-function RED failure.

The article now states finite-mixture differentiability conditions and the
coupling E[Y|X]=X with convex V and existing expectations. Larger variance alone
is insufficient. No new empirical golfer claims or fitted data were introduced.

Rendered inspection found reference contrast failure in dark mode, math-only
headers reported as empty by axe, and expanded explanatory panels with zero
height because heading wrappers broke the shared sibling selector. Once opened,
white card backgrounds also failed dark-theme contrast. The scoped stylesheet
uses the reading background and the panel's actual aria-hidden state; table
headers now name the two players. Browser checks must verify actual panel height,
not merely aria-expanded. Full reading captures must reset horizontal scroll
positions after exercising wide tables.

Initial root run: 5,274 passed, 29 skipped, 132 deselected, 59 warnings,
coverage 79.30%; two root-hygiene failures were caused solely by the local
Playwright CLI output directory. Ruff and Black100 (703 files) passed. The exact
CI mypy command passed over 91 files; an earlier generic scripts-directory
invocation was invalid because that directory is excluded by configuration.
Content lint: 131 passed, 4 skipped. Title audit: 636 sources passed. CSS budget
passed via python -m scripts.check_styles_budget; direct-file invocation lacked
the package root and was corrected. Final browser and root-hygiene outcomes are
recorded below when complete.

The first actual-route gate had 28/28 HTTP200 and no inspection or axe failures,
but all records failed on Pandoc's blocked legacy polyfill. Production already
removes that script. Apply only strip_legacy_math_polyfill from the canonical
production module, not its destructive docs-pruning entry point, before rerunning.
Full manifest generation against this mixed local docs tree encounters old
nonpublic draft HTML without H1; the focused manifest uses canonical _page_record
for the two actual rendered routes and the production viewport contract.

## Completed Local Review, September 12

Final source render and production-normalized actual-route gate pass: all 28
records HTTP200, with no console or inspection failures, no serious/critical axe
violations, and no retries. Article:154 expressions/18 displays; all37 old IDs and
four citation entries;126 expression/table cases and64 keyboard scrolls. Critique:
four expressions, six display cases and two keyboard scrolls. Seven widths in both
themes pass for each page. Expanded panel heights are checked, not inferred from
button attributes. Full article/critique source and overlapping reading captures
were inspected, including expanded editorial responses; final affected mobile math,
table edges, dark references and panels were inspected again.

The final gradient background defect was found visually after axe passed. Its
correction received a fresh14-case layout/axe and12-panel capture pass; only shared
moderate landmark-unique findings remain. Supplemental screenshot navigation once
timed out because the theme button was offscreen; scrolling to the top before
clicking resolved it. No product behavior was bypassed.

All QA workers are reaped and browser session strokes-review is closed. The CLI
output directory was safely moved within the worktree to
`docs/development/technical-review/strokes-cli-20260912`; all6 root-hygiene tests
then passed.17 focused tests passed again. Six unrelated test-generated outputs
were restored after JSON comparison proved only date/format changes. Production
preview on port8767 may remain idle; it is not an ongoing verification worker.

The immutable review report is `reports/technical-review/strokes-complete-review.md`;
local evidence summary is `strokes-render-verification.json`. Next: commit source,
report and handoff; use that actual SHA for both inventory reviews and corrected
findings, regenerate canonical evidence reports, then create a regular PR. Preserve
the governed critique's open status. Verify protected merge and live publication
before changing DL4358 to shipped. Continue the remaining corpus afterward.

## Evidence-Binding and Source-Mapping Correction

The first evidence reconciliation revealed two real boundary constraints. The
validator assumed every route had a .qmd source, rejecting the existing .md
critique. A failing regression demonstrated this; the resolver now follows public
manifest precedence (.qmd first, then an existing same-route .md). It still rejects
unrelated source paths and does not accept Markdown when a Quarto source exists.

The deployment-boundary test also correctly rejected evidence under docs/, which
is generated output. The numerical builder moved to
`scripts/build_strokes_gained_examples.py`; its exact numerical JSON and the browser
verification summary moved to `reports/technical-review/`. The focused test imports
the canonical script. No evidence exemption or pruning check was weakened. The
partition contract now explicitly accounts for the two completed strokes routes:
198 deferred and21 completed routes in that historical batch partition.

The full standalone DL validator additionally reports a pre-existing DL1595
missing-SHA entry alongside DL3903/3902; those peer entries remain untouched.
The repo-local shared checker path is absent, so the authoritative checker from
Repository_Management was used. The first commit's Prettier hook interpreted an
unquoted underscore formula as emphasis; it was corrected with inline code before
first push. Implementation checkpoint is7f88be5429b90428f1bb68639df56ae763f9ff57.

## Final Evidence Package Validation

The initial relocated-builder root run passed5279 tests at79.29% coverage.
Because the builder now falls under the maintained scripts coverage surface,
added boundary tests check invalid transition lengths/costs, nonabsorbing chains,
invalid interventions and mixture domains. An exact artifact-reproduction check
also exercises report generation. No mathematical outputs changed. Final root:
5297 passed,29 skipped,132 deselected,59 warnings;79.35% coverage, builder100%.
Log: `strokes-delivery-boundary-root.log`. Focused evidence/numerical suite57 pass.
Ruff/Black100 pass; configured mypy91 and stricter changed-module mypy2 pass.

Both route records alone changed among239 inventory records. Their evidence
survives production pruning. The reviewed article, critique and CSS bytes match
the render summary hashes. Normalize maintained text to LF before final digest
regeneration so committed bytes and Windows working bytes agree. Six unrelated
test outputs differ only by generated_on or newline/JSON formatting; restore only
those proven outputs after the completed QA process is reaped. All local checks
are complete; protected PR and revision-matched publication remain pending.

The first evidence commit hook reformatted the moved JSON. The numerical JSON
now has a scoped Prettier ignore because its generator/test owns exact bytes,
following the existing generated-report convention. Browser-summary and inventory
formatting were accepted and their digests regenerated. No checker was disabled.

Complete implementation commit: `e079999a136b5b8dc2c63c37f7c3989adb5603c0`. All declared evidence hashes were
independently recomputed from `git show` of that revision before updating the two
review_commit and four verification_commit fields. This separates immutable
implementation evidence from its later inventory reconciliation.
