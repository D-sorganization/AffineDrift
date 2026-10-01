# Measured Golfer Evidence Review — #4771

Full source review of companion Chapter 24 under epic #4009 and corpus #4021.
This checkpoint revises the chapter and its evidence diagram; publication
validation and exact committed-source binding remain pending. No new human
measurements, pooled systematic review, or simulation rerun is claimed.

## Scientific Decisions

1. **Correct the Review Attribution.** The 92-study systematic kinematics review is Bourgain et al. (2022), not McPhee et al.'s narrative review. Preserve both with distinct purposes and add the missing bibliography record. The human-study list is a selected register, not a systematic search performed by this project.
2. **Bound the EMG Findings.** Use Kao et al.'s canonical authorship (Jobe is a coauthor), selected four scapular muscles, and 15 competitive male participants without inventing electrode type from the abstract. Robinson et al. measured bilateral extensor carpi ulnaris, not all wrist muscles, in 15 subelite right-handed men. Nonsignificance does not establish irrelevance or equivalence; EMG is not force.
3. **Separate Sensor and Model Quantities.** Koike's calibrated strain-gauge handle reconstructs palm resultants under fixed-reference and negligible-handle-inertia assumptions. Choi/Park's single six-axis internal grip sensor supports inverse-dynamics estimates of separate hand and net joint loads. Their reported hand-torque ratio is model-derived; grip modification, fixed trial order, possible bypass, and foam/sponge balls limit interpretation.
4. **Retain Study and Mechanical Boundaries.** Zheng's observational skill comparisons do not justify copying a professional's technique or injury prevention. Han's force plates and computed ground-interaction moments support associations, not identified energy pathways. Betzler's bounded shaft comparison does not establish universal stiffness effects. Peak sequence, force magnitude, and activation timing are not interchangeable measurements of energy transfer.
5. **Explain Repeated-Measure Uncertainty.** Derive a balanced independent-participant random-intercept example with explicitly manufactured variances. Verify its mean variance from a full covariance matrix: 11/150 versus the false independent-swing estimate 2/150, design effect 5.5. The equivalent count 300/11 is neither independent people nor a degrees-of-freedom formula. More repeats reduce residual uncertainty but leave the between-person term at fixed participant count.
6. **Distinguish Statistical Targets.** Hierarchical estimation, prediction for unseen participants, prediction for a known participant's new session, and causal identification require different designs. Participant holdout is relevant to unseen-person generalization, not a universal requirement for every association estimate. Preprocessing/model selection must respect the split. Neither prediction nor a mixed model automatically supplies causal identification.
7. **Scope the Validation Gap and Integrate Channels.** Absence of a complete validation dataset is bounded to the evidence assembled in this project. Explain why ground/body/hand/shaft/EMG/launch observations need synchronized mechanical accounting and why not every narrower question needs every channel. Pressure does not replace a contact wrench; stationary ideal ground contact can exchange momentum without supplying work.
8. **Make Disagreement Diagnostic Without Overdiagnosis.** A persistent sign mismatch after frame/timing/uncertainty checks can refute the specified prediction. Matching mechanics does not validate anatomy. Motion/load disagreement admits multiple causes, rather than uniquely proving underconstraint or compensation. Frozen tests, explicit deviations, consent-compatible release, and synthetic-data labels keep the inference auditable.
9. **Replace the Certainty Pyramid.** Four equal-width panels distinguish observations, mechanical inference, anatomical inference, and prospective tests. More sensing can constrain explanations without uniquely identifying biology. Only make_human_evidence changes in the shared generator; existing asset names and chapter anchor remain stable.

## Sources and Verification Limits

Primary records were checked on 2026-10-01. New bibliography metadata was cross-checked against publisher DOI deposits through Crossref. Abstract-only access is not represented as full-paper review.

- Bourgain et al.: publisher/search-extracted abstract, methods, and results describing 92 studies and heterogeneous methods. https://www.mdpi.com/2075-4663/10/6/91 ; DOI 10.3390/sports10060091. Direct follow-up access returned rate limiting/captcha.
- Kao et al.: primary PubMed abstract, 15 competitive men and bilateral four-muscle scapular EMG/cinematography. https://pubmed.ncbi.nlm.nih.gov/7726345/ . No electrode-type claim from this scope.
- Robinson et al.: primary PubMed abstract and DOI metadata. https://pubmed.ncbi.nlm.nih.gov/37983261/ . ECU-specific measurements and nonsignificant reported association; no new full-paper reading claimed.
- Koike et al.: complete four-page primary conference PDF, methods and results. https://ojs.ub.uni-konstanz.de/cpa/article/view/6828/6125 . The paper's inference from axial-force magnitude to speed contribution is not adopted without a dynamical or power calculation.
- Choi/Park: primary full-text XML through Europe PMC; complete Methods, Discussion, embedded results/equations and captions read. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7374515/fullTextXML . Instrument/model distinction, nine participants, fixed order, inertia and grip limitations checked. Published equations were read, not reimplemented. The historical shared key koike2020 is retained to avoid unrelated citation renaming.
- Zheng et al.: complete primary abstract. https://pubmed.ncbi.nlm.nih.gov/18004680/ . This is the professional/amateur paper, distinct from the male/female professional study.
- Han et al.: primary abstract. https://pubmed.ncbi.nlm.nih.gov/31042142/ . Ground-interaction moments, not a new joint-moment or causal-work decomposition.
- Betzler et al.: primary abstract. https://pubmed.ncbi.nlm.nih.gov/22900403/ . Twenty golfers and bounded shaft comparison; no unspecified demographic or raw-data access claim.
- Hume et al.: primary review abstract. https://pubmed.ncbi.nlm.nih.gov/15896091/ . Broad context only; not adopted as proof of fixed-hub, optimal-angle, or angular-momentum-conservation prescriptions.
- Lazic: primary methodological discussion of nested observations, variance components and pseudoreplication. https://link.springer.com/article/10.1186/1471-2202-11-5 . Methodology, not measured golf variance. The example is independently derived; the precise diminishing benefit of repeat observations is stated rather than adopting an absolute claim that repeats never improve population-mean precision.

## Delegation and Adjudication

Eight supplied-text agy CLI gemini-3.8-flash-high jobs completed: claim inventory,
test drafting, grip methods extraction, grip discussion extraction, register
draft, figure draft, adversarial review, and PR description drafting. Lead review
corrected these draft errors: Han's ground moments are not joint/body moments;
the Choi/Park ratio is not directly sensed at two hands; 350 g is grip mass,
not complete club mass; small longitudinal inertia is not automatically zero;
the secondary assertion that Koike only measured three components was not
inherited over its primary methods. The figure draft's repeated tiny banners
were replaced by one readable note. Unspecified p-values, data availability,
and fine-wire/surface electrode details were not invented.

## Verification at This Checkpoint

Three independent covariance fixtures pass; the two source contracts fail
before correction and pass afterward (five total). All 653 source-title checks
pass. PDF/HTML publication checks, regression, prior-evidence carry-forward,
and exact Git-blob binding remain required. The previous route contains 87
findings; none is superseded merely because this chapter changes. Corpus credit
remains 119 pending until validated binding.

The adversarial review prompted precise power-versus-work wording and variance-of-grand-mean terminology. Rejected suggestions: the citation key does not determine displayed authors (koike2020 contains Choi/Park metadata); the companion hierarchy filter intentionally handles chapter headings; a pinned provider source is deliberate; an electrode type supplied without primary evidence is not adopted. The reader-facing abstract-access aside was removed while its honest audit limitation remains here.

Publication checkpoint:223-page PDF/HTML and canonical/public parity pass; all Chapter24 pages164–170 plus boundary163/171 visually inspected. The figure was subsequently enlarged and its PDF/mobile render rechecked. Four viewport/theme checks pass with zero serious/critical axe findings. Nineteen math containers, two displays, no MathJax errors/unrendered nodes/page overflow at390/1440. All12 publication gates,48 targeted tests,Ruff,Black840,and CI-scoped mypy94 pass. Full regression, integration and final binding remain.

The PR wording draft incorrectly called all87 historical audit findings empirical and conflated19 math containers with two display equations; both were corrected in lead review. Integrated PR4770 head3d7f4eb/peer main37fa19fef, preserving scientific fields from both parent ledgers. Combined PDF and HTML regenerated. Source checkpoint947ad2373 remains in history.
