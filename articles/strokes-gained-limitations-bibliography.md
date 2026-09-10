# Bibliography: On the Limits of Strokes-Gained Inference

## Scope and Evidence

This companion supports the revised `strokes-gained-limitations.qmd`. It is a
source guide, not a citation network. The previous list included unverified
authorship, dates, and supposed reference edges; those assertions are withdrawn.
The numerical counterexamples are independently constructed and reproducible in
`docs/development/technical-review/build_strokes_gained_examples.py`.

## Concept Map

| Concept                     | Meaning and Boundary                                                                                                    |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Strokes-Gained Accounting   | A benchmark difference minus counted cost; it telescopes for complete, consistently recorded sequences.                 |
| Conditional Mean            | A prediction under a specified observed-data distribution; not automatically an intervention response.                  |
| Policy Value                | Expected remaining cost under a specified player transition model and continuation policy.                              |
| Optimal Value               | The best achievable value for the stated dynamics, feasible actions, and objective.                                     |
| Category Boundary           | A state value that transfers credit between adjacent categories and cancels in their total.                             |
| Heterogeneity and Selection | Players can have different continuation functions, and their weights in pooled data can depend on state.                |
| Causal Effect               | A contrast between defined interventions, requiring an identification argument.                                         |
| Partial Pooling             | A method for sharing information across players; predictive benefits require validation and do not establish causality. |
| Time Variation              | A forecasting issue distinct from both population heterogeneity and algebraic score reconciliation.                     |

## Verified Core References

1. **Broadie, Mark (2012).** “Assessing Golfer Performance on the PGA TOUR.”
   _Interfaces_ 42(2), 146–165.
   [Published record](https://doi.org/10.1287/inte.1120.0626).
   [Author's April 8, 2011 preprint](https://www.columbia.edu/~mnb2/broadie/Assets/strokes_gained_pga_broadie_20110408.pdf).
   Section 2 defines SG and proves additivity; its closing discussion explicitly
   introduces a near-optimal-play approximation. The opening of Section 3
   explains averaging over unobserved conditions. Neither fact establishes an
   individual practice effect. The publication year is 2012; 2011 dates the
   linked preprint.

2. **Sutton, Richard S., and Andrew G. Barto (2018).**
   _Reinforcement Learning: An Introduction_, second edition. MIT Press.
   [Publisher](https://mitpress.mit.edu/9780262039246/reinforcement-learning/).
   [CMU-hosted 2018 draft](https://www.andrew.cmu.edu/course/10-703/textbook/BartoSutton.pdf).
   Section 3.5 and the opening of Section 3.6 distinguish policy evaluation
   from optimal control. PDF pages 80–86 were read; the last page stops partway
   through Section 3.6. The draft has visible production artifacts. Its golf
   example is illustrative, not a calibrated performance dataset.

3. **Gelman, Andrew (2006).** “Multilevel (Hierarchical) Modeling: What It Can
   and Cannot Do.” _Technometrics_ 48(3), 432–435.
   [Full author-hosted paper](https://sites.stat.columbia.edu/gelman/research/published/multi2.pdf).
   DOI: 10.1198/004017005000000661. The full technical text and reference list
   were read. Its example explains predictive pooling and the risk of a causal
   interpretation of observational coefficients; it is not a golf study.

4. **Hernán, Miguel A., and James M. Robins (2020).**
   _Causal Inference: What If_. Chapman & Hall/CRC.
   [Author's maintained book page](https://miguelhernan.org/whatifbook).
   The online edition linked during this review is dated August 19, 2026.
   Chapter 3 supplies the intervention, exchangeability, positivity, and
   consistency framework. Consult the derivation audit for exact reading
   coverage. A citation to this framework is not empirical evidence that a golf
   intervention works.

## Reading Paths

### Accounting and Decisions

Read Broadie's Section 2 alongside the article's complete-hole and category
examples. Then compare policy evaluation and optimality in Sutton and Barto.
Check which state, policy, and cost convention each equation uses.

### Prediction and Intervention

Read Gelman's prediction and causal-inference sections, then the identification
conditions in Hernán and Robins. Ask which data support a player's predictive
surface and which assumptions support changing an action or practice protocol.

## Withdrawn Inferences

The former generic “Optimal Strategy in Golf” entry had unresolved authorship
and publication metadata and is not retained as a source. The former
Connolly/Rendleman year and venue, broad software descriptions, and graph edges
were not verified and are not asserted here. Pearl's _Causality_ is not _The
Book of Why_. Economic ergodicity and general motor-control references did not
establish that SG accounting assumes stationary skill, fully observed states,
or risk-neutral behavior. Their removal narrows evidentiary claims; it does not
assert that these wider literatures are irrelevant to golf research.
