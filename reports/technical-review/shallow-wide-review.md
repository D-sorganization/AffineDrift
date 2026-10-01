# Shallow-Wide Latency and Synergy Review

Issue #4733 belongs to epic #4009. This review covers the complete canonical
Volume IV Chapter 4 source, both printed Python listings, its schematic and
exercises, and the bounded Chapter 4 summary on the book landing page. The
historical notebook remains a scaffold and has not received this numerical
review. Other chapters retain their previous scientific status.

## Argument and Corrections

The defensible thesis is conditional: reducing a computation's critical path
can help a delayed controller if it preserves task-relevant information and
policy accuracy. It does not establish a universal brain depth or an intrinsic
advantage of width. The chapter now connects new sensory information, retained
controller state, prediction, passive mechanics and actuator dynamics.

The response endpoint must be declared before allocating a timing budget.
EMG onset, force change and successful correction have different delays. The
serial toy budget subtracts fixed delays, floors the remaining stage count,
and recognizes an infeasible deadline. Parallel branches use the required
critical path; recurrent computation needs a finite unrolled interval and
initial state. Throughput is distinguished from input-to-output latency.

Anatomical cortical laminae are not sequential computational stages. Unsupported
universal synapse counts, region clocks, a one-millisecond minimum and the
unverified GPT-4 layer comparison were removed. The M1 qualification avoids
the opposite overstatement that motor cortex universally has no layer 4.

The original network listing declared an unused 50,000-parameter budget, but
actually constructed 21,960 and 62,010 parameters and used different output
activations. The corrected comparison uses 21,960 versus 21,958 parameters,
common hidden ReLU and linear output conventions, and expressly assumed stage
delays. Neither untrained output nor assigned delay establishes control quality
or measured speed. Equal parameter count does not imply equal expressiveness.

The hierarchy sum remains quadratic in the original dimension under its
declared square-map assumptions. It does not remove general exponential
approximation or sampling complexity. Equal-position/opposite-velocity states
provide a counterexample to indiscriminate compression. The cited sigmoid
approximation theorem supplies neither a feasible width nor a closed-loop
guarantee, and does not analyze the listing's ReLU network.

The EMG model is approximate and descriptive. Synchronous spatial factors and
time-varying templates are distinguished; electrical measurements are not
identified with muscle force or neural commands. Scale/permutation ambiguities,
model-order criteria, training versus held-out reconstruction, and causal
identification are explicit. The universal four-to-six/over-90% assertion is
replaced by the cited experiment's actual scope.

The NMF listing rejects invalid data and options, defines its uncentered score,
normalizes input scale, uses a local reproducible generator and explicitly
groups Gram products. Zero-data relative score is undefined; the score may be
negative and is not centered statistical R-squared. Synthetic channels have no
assigned muscle anatomy. A single seeded fit is not a model-selection study.

## Primary Reading Scopes

- **Katz and Miledi (1965), DOI 10.1098/rspb.1965.0016:** complete
  publisher-deposited Crossref abstract read and saved. The timing landmarks
  and temperature are retained in the chapter. Full paper was not read; no
  species detail is inferred from an unavailable methods section.
- **Yamawaki et al. (2014), DOI 10.7554/eLife.05422:** introduction, all
  Results narrative subsections, Discussion and Methods read in the official
  [Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4290446/fullTextXML).
  Scope is mouse forelimb M1. Figure pixels and supplements were not
  independently inspected; no human circuit-depth inference is made.
- **Cybenko (1989), DOI 10.1007/BF02551274:** Theorem 1, Lemma 1, Theorem 2
  and surrounding explanation read in the
  [original paper](https://papers.baulab.info/papers/Cybenko-1989.pdf).
  The chapter retains the compact-domain and continuous-sigmoid assumptions.
- **d'Avella and Bizzi (2005), DOI 10.1073/pnas.0500199102:** all six main
  PDF pages, tables and discussion read in the
  [author-hosted paper](https://web.mit.edu/bcs/bizzilab/publications/davella2005.pdf).
  Three frogs and thirteen hindlimb muscles; the two model families and
  reconstruction summaries are not generalized to human golf. Supplement was
  not independently read.
- **Tresch, Cheung and d'Avella (2006), DOI 10.1152/jn.00222.2005:** abstract,
  selected Methods (simulation, experimental data, algorithms and model order),
  real-data Results at journal pages 2208–2209, and Discussion recommendations
  read in the [author-hosted paper](https://web.mit.edu/ckcheung/www/ScientificResearch_files/TreschCheungDAvella_JNP2006.pdf).
  Other Results were not comprehensively read. The bibliography now includes
  the full title; the correction does not change the paper's identity or DOI.
- **Lee and Seung, NIPS 2000:** problem/objective, multiplicative updates,
  auxiliary-function argument and discussion read in the official seven-page
  [proceedings paper](https://proceedings.neurips.cc/paper_files/paper/2000/file/f9d1152547c0bde01830b7e8bd60024c-Paper.pdf).
  The bibliography uses the official proceedings year. No unique or globally
  optimal solution is promised for the demonstration.

Chao and Yang (2019) was consulted through part of Results only, and Boudkkazi
et al. (2011) through abstract/search material. Neither supplies a new chapter
claim. A delay relative to action-potential end must not be substituted for
onset-to-onset delay. These partial leads are not represented as full reviews.

## Adversarial and Numerical Review

Three supplied-text agy Gemini 3.8 Flash High passes inventoried original
claims/code and reviewed the corrected chapter. They used no tools, network,
edits or scientific authority. Lead adjudication accepted the parameter and
activation discrepancies, invalid-input defects, matrix-intermediate label,
obsolete-example reference and figure clarity issues.

Rejected or qualified suggestions included calling the valid finite geometric
sum erroneous, declaring uncentered reconstruction inherently invalid, imposing
a universal absence of M1 layer 4, treating the frog recordings as surface EMG,
and requiring rank not exceed channel count merely because a Gram matrix can
be singular. The multiplicative update does not invert that matrix;
overcompleteness does not establish the asserted numerical failure. It does
increase identification ambiguity. Return order W/C is declared explicitly,
with shapes and the reconstruction product; symmetric scale allocation is a
numerical convention, not a physiological unit assignment.

The original listings were executed before correction. Regression tests were
then run against them: 17 failed and six passed. After correction all 23 pass.
Tests execute the actual printed listings, check parameter counts and common
signed output, reject invalid inputs/options, reconstruct rank-one data over
scales 1e-120 to 1e120, check deterministic local randomness and one-iteration
return, and demonstrate factor-scaling and lost-velocity ambiguities. A final complex-input case exposed lossy conversion before validation; the
listing now rejects complex data explicitly, bringing the example suite to
24 checks. Seven additional audit tests retain the original audit identity and
reject invalid follow-up issue URLs. There was no human experiment or
trained-controller benchmark.

## Publication and Remaining Questions

The whole volume is rebuilt with existing repository sources in an isolated
scratch directory. Local latexmk could not start because its Perl engine is
absent; the installed pdflatex/BibTeX/makeindex tools were used in an explicit
halt-on-error multi-pass build instead. No forced compilation or dependency
installation was used. The PDF build and visual-review snapshot is recorded in
`shallow-wide-render-verification.json`. Later integrated repository and browser
checks are recorded separately in `shallow-wide-integration-validation.json`;
these do not expand the scientific review to the rest of the volume.

The prior book-route records are preserved in
`shallow-wide-prior-reviews.json`. The new chapter review must not replace
historical finding commits or claim fresh scientific review of routes affected
only by shared bibliography/audit metadata. Publication dependency changes and
unchanged inputs are recorded separately. A repository merge does not establish
successful live-site deployment.

Open empirical questions are deliberate: does a shorter measured critical path
improve performance after controlling information and actuator limits; which
state distinctions are necessary; how do prediction and passive mechanics
change the result; and what human perturbation evidence distinguishes the
candidate mechanisms? The exercises now operationalize those questions.
