# Bibliography: On the Limits of Strokes-Gained Inference

## Concept Map

- **Strokes Gained (SG)**: A metric measuring the quality of a shot relative to a benchmark population, mathematically equivalent to a difference in value functions.
- **Conditional Expectation**: The expected number of strokes to hole out given the current state ($E[H|S]$).
- **Value Function ($J(x)$)**: In dynamic programming, the expected cost-to-go from state $x$.
- **Ecological Fallacy**: The logical error of inferring individual-level correlations from group-level averages.
- **Heterogeneous Treatment Effects (HTE)**: The variation in the causal effect of an intervention (e.g., practice) across different individuals.
- **Dynamic Programming (DP)**: The mathematical framework for optimizing sequential decisions, underpinning the SG calculation.
- **Hierarchical Modeling**: A statistical approach (also known as multilevel modeling) that estimates individual parameters while pooling information from the population.
- **Average Treatment Effect (ATE)**: The mean effect of an intervention on a population, which may differ from the Conditional Individual Treatment Effect (CITE).
- **Markov Decision Process (MDP)**: A discrete-time stochastic control process providing the formal basis for golf state transitions.

## Bibliography

bibliography:

- id: Broadie2012
  title: Assessing Golfer Performance on the PGA TOUR
  authors: Mark Broadie
  year: 2012
  venue: Interfaces, 42(2), 146-165
  scholar_link: https://scholar.google.com/scholar?q=Broadie+Assessing+Golfer+Performance+on+the+PGA+TOUR+Interfaces
  clusters: [Golf Analytics, Operations Research]
  concepts: [Strokes Gained, ShotLink, Performance Measurement]
  related_ids: [Broadie2014, Connolly2012]
  references_out_ids: [Broadie2014, Connolly2012, Lewis2016]

- id: Broadie2014
  title: "Every Shot Counts: Using the Revolutionary Strokes Gained Approach to Improve Your Golf Performance and Strategy"
  authors: Mark Broadie
  year: 2014
  venue: Gotham Books
  scholar_link: https://scholar.google.com/scholar?q=Broadie+Every+Shot+Counts
  clusters: [Golf Analytics]
  concepts: [Strokes Gained, Strategy, Benchmarking]
  related_ids: [Broadie2012]

- id: Robinson1950
  title: Ecological Correlations and the Behavior of Individuals
  authors: W. S. Robinson
  year: 1950
  venue: American Sociological Review, 15(3), 351-357
  scholar_link: https://scholar.google.com/scholar?q=Robinson+Ecological+Correlations+and+the+Behavior+of+Individuals
  clusters: [Statistics, Sociology]
  concepts: [Ecological Fallacy, Aggregation Bias, Correlation]
  related_ids: [Gelman2006]
  references_out_ids: [Gelman2006, Pearl2009]

- id: Gelman2006
  title: Data Analysis Using Regression and Multilevel/Hierarchical Models
  authors: Andrew Gelman, Jennifer Hill
  year: 2006
  venue: Cambridge University Press
  scholar_link: https://scholar.google.com/scholar?q=Gelman+Hill+Data+Analysis+Using+Regression+and+Multilevel
  clusters: [Statistics, Bayesian Inference]
  concepts: [Hierarchical Modeling, Multilevel Models, Partial Pooling]
  related_ids: [Robinson1950, Pearl2009]
  references_out_ids: [StanSoftware, Pearl2009]

- id: Bellman1957
  title: Dynamic Programming
  authors: Richard Bellman
  year: 1957
  venue: Princeton University Press
  scholar_link: https://scholar.google.com/scholar?q=Bellman+Dynamic+Programming+1957
  clusters: [Control Theory, Optimization]
  concepts: [Dynamic Programming, Bellman Equation, Value Function]
  related_ids: [Puterman1994, Sutton2018]
  references_out_ids: [Puterman1994, Sutton2018, Bertsekas2012]

- id: Puterman1994
  title: "Markov Decision Processes: Discrete Stochastic Dynamic Programming"
  authors: Martin L. Puterman
  year: 1994
  venue: Wiley-Interscience
  scholar_link: https://scholar.google.com/scholar?q=Puterman+Markov+Decision+Processes
  clusters: [Operations Research, Optimization]
  concepts: [MDP, Policy Iteration, Value Iteration]
  related_ids: [Bellman1957]
  references_out_ids: [Sutton2018]

- id: Pearl2009
  title: "Causality: Models, Reasoning, and Inference"
  authors: Judea Pearl
  year: 2009
  venue: Cambridge University Press
  scholar_link: https://scholar.google.com/scholar?q=Pearl+Causality+Models+Reasoning+and+Inference
  clusters: [Causal Inference, AI]
  concepts: [Causal Calculus, Counterfactuals, Structural Equation Models]
  related_ids: [Gelman2006, Morgan2014]
  references_out_ids: [Morgan2014]

- id: Sutton2018
  title: "Reinforcement Learning: An Introduction"
  authors: Richard S. Sutton, Andrew G. Barto
  year: 2018
  venue: MIT Press
  scholar_link: https://scholar.google.com/scholar?q=Sutton+Barto+Reinforcement+Learning+An+Introduction
  clusters: [Machine Learning, Control Theory]
  concepts: [Value Function, Temporal Difference, Policy Gradient]
  related_ids: [Bellman1957]

- id: Connolly2012
  title: Skill, Luck, and Streaky Play on the PGA Tour
  authors: Robert A. Connolly, Richard J. Rendleman Jr
  year: 2012
  venue: Journal of the American Statistical Association
  scholar_link: https://scholar.google.com/scholar?q=Connolly+Rendleman+Skill+Luck+and+Streaky+Play+on+the+PGA+Tour
  clusters: [Golf Analytics, Statistics]
  concepts: [Variance Decomposition, Skill vs Luck]
  related_ids: [Broadie2012]

- id: Lewis2016
  title: Optimal Strategy in Golf
  authors: Mark Broadie, A. J. Lewis (verify authorship context)
  year: 2016
  venue: International Journal of Golf Science (Query)
  scholar_link: https://scholar.google.com/scholar?q=Optimal+Strategy+in+Golf
  clusters: [Golf Analytics]
  concepts: [Strategy, Risk Management]
  related_ids: [Broadie2012]

- id: Morgan2014
  title: "Counterfactuals and Causal Inference: Methods and Principles for Social Research"
  authors: Stephen L. Morgan, Christopher Winship
  year: 2014
  venue: Cambridge University Press
  scholar_link: https://scholar.google.com/scholar?q=Morgan+Winship+Counterfactuals+and+Causal+Inference
  clusters: [Causal Inference, Sociology]
  concepts: [Counterfactuals, Selection Bias, Treatment Effects]
  related_ids: [Pearl2009]

- id: Bertsekas2012
  title: Dynamic Programming and Optimal Control
  authors: Dimitri P. Bertsekas
  year: 2012
  venue: Athena Scientific
  scholar_link: https://scholar.google.com/scholar?q=Bertsekas+Dynamic+Programming+and+Optimal+Control
  clusters: [Control Theory, Optimization]
  concepts: [Optimal Control, DP, Approximate DP]
  related_ids: [Bellman1957]

- id: StanSoftware
  title: "Stan: A Probabilistic Programming Language"
  authors: Stan Development Team
  year: 2024
  venue: Software
  scholar_link: https://scholar.google.com/scholar?q=Stan+A+Probabilistic+Programming+Language
  clusters: [Software, Statistics]
  concepts: [Bayesian Inference, MCMC, HMC]
  related_ids: [Gelman2006]

- id: PyMC
  title: "PyMC: Probabilistic Programming in Python"
  authors: PyMC Developers
  year: 2024
  venue: Software
  scholar_link: https://scholar.google.com/scholar?q=PyMC+Probabilistic+Programming+in+Python
  clusters: [Software, Statistics]
  concepts: [Bayesian Inference, Probabilistic Programming]
  related_ids: [Gelman2006]

- id: DataGolf
  title: Data Golf
  authors: Matt Courchene, Will Courchene
  year: 2024
  venue: Website / Analytics Platform
  scholar_link: https://scholar.google.com/scholar?q=Data+Golf+analytics
  clusters: [Golf Analytics, Data Science]
  concepts: [Strokes Gained, Predictive Modeling]
  related_ids: [Broadie2012]

- id: ShotLink
  title: ShotLink Intelligence
  authors: PGA TOUR
  year: 2024
  venue: Dataset
  scholar_link: https://scholar.google.com/scholar?q=ShotLink+Intelligence+PGA+TOUR
  clusters: [Golf Analytics, Data]
  concepts: [Shot Tracking, Laser Measurement]
  related_ids: [Broadie2012]

- id: Hastie2009
  title: "The Elements of Statistical Learning"
  authors: Trevor Hastie, Robert Tibshirani, Jerome Friedman
  year: 2009
  venue: Springer
  scholar_link: https://scholar.google.com/scholar?q=Hastie+Elements+of+Statistical+Learning
  clusters: [Machine Learning, Statistics]
  concepts: [Regression, Classification, Model Selection]
  related_ids: [Gelman2006]

- id: Taleb2020
  title: "Statistical Consequences of Fat Tails: Real World Preasymptotics, Epistemology, and Applications"
  authors: Nassim Nicholas Taleb
  year: 2020
  venue: STEM Academic Press
  scholar_link: https://scholar.google.com/scholar?q=Taleb+Statistical+Consequences+of+Fat+Tails
  clusters: [Statistics, Risk]
  concepts: [Ergodicity, Fat Tails, Time Average vs Ensemble Average]
  related_ids: [Gelman2006]
  references_out_ids: [Gelman2006]

- id: Kahneman1979
  title: "Prospect Theory: An Analysis of Decision under Risk"
  authors: Daniel Kahneman, Amos Tversky
  year: 1979
  venue: Econometrica, 47(2), 263-291
  scholar_link: https://scholar.google.com/scholar?q=Kahneman+Tversky+Prospect+Theory
  clusters: [Behavioral Economics, Psychology]
  concepts: [Loss Aversion, Risk Sensitivity, Reference Dependence]
  related_ids: [Todorov2002]
  references_out_ids: [Todorov2002]

- id: Todorov2002
  title: "Optimal Feedback Control as a Theory of Motor Coordination"
  authors: Emanuel Todorov, Michael I. Jordan
  year: 2002
  venue: Nature Neuroscience, 5(11), 1226-1235
  scholar_link: https://scholar.google.com/scholar?q=Todorov+Jordan+Optimal+Feedback+Control
  clusters: [Motor Control, Neuroscience]
  concepts: [Optimal Control, Risk Sensitivity, Feedback]
  related_ids: [Bellman1957]
  references_out_ids: [Bellman1957, Sutton2018]

## Reading Paths

### Path 1: Fast Ramp (The "What" and "Why")

1.  **Broadie2012**: The foundational paper establishing Strokes Gained as the industry standard.
2.  **Broadie2014**: The accessible book-length treatment explaining the implications for strategy.
3.  **Robinson1950**: A classic warning about the "Ecological Fallacy"—inferring individual traits from group averages.
4.  **Gelman2006**: The definitive guide to fixing heterogeneity issues using Hierarchical (Multilevel) Modeling.
5.  **DataGolf**: Modern, practical application of advanced golf analytics.

### Path 2: Deep Technical (The Theory)

1.  **Bellman1957**: The mathematical origin of the value functions used in Strokes Gained.
2.  **Puterman1994**: A rigorous treatment of Markov Decision Processes (MDPs), the formal model of golf.
3.  **Pearl2009**: The "Book of Why"—essential for distinguishing statistical correlation from causal impact.
4.  **Morgan2014**: Advanced methods for estimating causal effects when experiments (randomized trials) are impossible.
5.  **Connolly2012**: Statistical decomposition of variance in golf scores (luck vs. skill).
6.  **Sutton2018**: The modern "Reinforcement Learning" view of value functions and prediction.
7.  **Bertsekas2012**: Comprehensive reference for Dynamic Programming and Optimal Control.
8.  **Hastie2009**: Standard reference for the statistical learning techniques used to build these models.

### Path 3: Implementation (Tools & Data)

1.  **StanSoftware**: The gold standard for implementing the Hierarchical Models recommended in the article.
2.  **PyMC**: Python-based probabilistic programming for Bayesian inference.
3.  **ShotLink**: The PGA Tour's laser-measured dataset (reference concept).
4.  **DataGolf**: Example of high-quality public implementation of these metrics.
5.  **R-INLA**: Integrated Nested Laplace Approximations (fast alternative to MCMC for hierarchical models).
