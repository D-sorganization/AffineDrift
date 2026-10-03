# Validation-Program Source Dossier

Review #4847, epic #4009. Original and revised Chapter 11 read completely. Baseline `a4afe8cc9f573e29fe11f22bf79dae1e39ba4dc9`; no new acceptance is assigned to the other chapters. The source report records corrections and their boundaries.

## Pinned Program Authority

The private [Launch-Monitor-Flight-Model-Campaign repository](https://github.com/D-sorganization/Launch-Monitor-Flight-Model-Campaign/tree/8cd8ad04bf2904eedd0d8f10d2aa202e437e91fd) is the existing chapter's historical authority. Authorized GitHub reads retrieved the full paired-device protocol, both paired-device analysis modules, the qualification/model/capability manifests, both human-readable multisource reports, model-source aggregate metrics, the empty schedule/ledger and generated status. Raw copies are retained outside the public checkout. No restricted observed-shot table was retrieved; no upstream software or tests were changed or executed.

The public [Tools release-program description](https://github.com/D-sorganization/Tools/blob/main/docs/development/LAUNCH_MONITOR_RELEASE_PROGRAM.md) identified this authority. Its newer release pins were not substituted for the paper's historical snapshot. The public UpstreamDrift source-backed scoring contract at `fb4e6e41ac4980309e32dacceb957f4da02616b3` was inspected through ADR0035 and the complete `src/shared/python/launch_monitor/strokes_gained.py`. That reading supports retained exact-state, supported-domain and provenance/proxy boundaries, not independent evaluation of every baseline or current application release.

### Aggregate Reconciliation

The qualification manifest's exact-byte SHA-256 is `679856edb290111a0106c0cbcbd2b673f581fd6b0026409c4d643565b330709a`; the original chapter omitted one `c`. The model manifest independently references the correct value. Its own digest `b70935fb4209b3f3aa18c3129ae948c4e20da74536af4d88433e5f0875960ca7` and the capability digest `1906d19fcace3284ae99d9dd8de213a0e2dabe8c062e4d63edc06c98f7eaf92e` match the printed authority.

Pinned aggregates confirm 261,666 rows / 27 sources; 13,855 complete launch-input rows; available carry/lateral/descent/time counts 13,647 / 13,532 / 9,850 / 9,283; a strict cohort of 13,843 / 15 sources; and 96,901 predictions from seven configurations with zero execution failures. The human-readable model report specifies complete inputs plus at least one supported observed outcome. Individual outcome metrics have separate eligibility. ShotLink and vendor-labelled source counts and qualification/retired status match the existing prose.

The 224-row `results/v2/model/model_source_metrics.csv` hashes to `75075faaab63c8dc338b36aa3636eea60d2f6e89337b2b45e4d86571123ff3cf`, matching its manifest. Minimum carry RMSE across the seven configurations matches the published roundings: Blackmore n=8,860, 12.25593797708933 m, bias −4.093436574709416 m; R10 Ballantyne n=1,541, 7.1502999575714865 m, bias −4.721820116563979 m; R50 n=255, 10.237663384603147 m, bias +6.553662433553424 m. These are comparisons to reported source outcomes, not physical-reference accuracy or held-out model selection.

### Protocol Versus Implemented Analysis

The full protocol calls itself a structural template, explicitly not completed preregistration. Ball specification and numerical speed bands, hardware/reference choices, placement and calibration remain decisions to freeze. Its approximate one-endpoint mean-bias calculation produces 71 independent complete pairs and inflates expected attempts to 84 for 15% losses. The implementation separately requires 84 accepted observation sets in each of three cells. Preserve that operational requirement while identifying missing multiplicity, clustering and precision justification.

The validator requires at least two distinct commercial devices and exactly one reference, with shared trigger timestamp and recorded calibration status. It does not physically establish synchronization, traceability or independence. The descriptive analyzer groups by device/vendor/model, computes ordinary paired mean/SD and regression, uses an individual-pair bootstrap for mean bias, and names `1.96 s_D` a repeatability coefficient. No hierarchical model or interval for each agreement-limit endpoint appears in the inspected complete modules. The publication qualifies that label; it does not alter upstream software.

The schedule and ledger contain 252 rows each, with matching identifiers; their digests match the chapter. The status reports `confirmatory_ready=false`, 252 not-collected exclusions and zero analyzed pairs. Three robot-center outdoor club/speed cells are a subset of the broad desired program. A replacement/attempt policy must be versioned before collection to handle losses without overwriting failures. Nothing in this review closes or completes an external physical campaign.

## Statistical Sources and Independent Work

[Bland and Altman (2007)](https://www-users.york.ac.uk/~mb55/meas/bland2007.pdf), DOI `10.1080/10543400701329422`: all extracted text read, including metadata and references. Figure pixels not inspected; no example reanalysis. The source distinguishes repeated pairs for changing quantities, replicated fixed quantities, averages versus individual measurements, and variance/dependence assumptions. The new equal-block example is independently derived, not claimed to be the paper's fitted model.

[JCGM VIM3 precision](https://jcgm.bipm.org/vim/en/2.15.html), [repeatability conditions](https://jcgm.bipm.org/vim/en/2.20.html), [repeatability](https://jcgm.bipm.org/vim/en/2.21.html), and [calibration](https://jcgm.bipm.org/vim/en/2.39.html): those entries' definitions, notes and annotations read. No complete-standard review is claimed. The bibliography identifies the third-edition JCGM 200:2012 vocabulary and the annotated online material actually consulted.

Independent numerical work checks the normal-quantile planning calculation, identical-bias counterexample, error-covariance subtraction, equal-block covariance averaging, nonunique variance decompositions and the difference between mean precision and individual agreement. All data in those tests are manufactured. Raw source provenance remains distinct from a software test and from a collected physical observation.

## Publication Boundaries

The review adds two bibliography entries while preserving the original 88 entries, impact/radar chapter sources and existing acceptance records. The shared PDF changes are tracked explicitly. The revised Chapter 11 text, all six numbered equations, six rendered chapter pages, two new bibliography entries and impact/radar boundary pages have been read. No claim is made to have newly reviewed the remaining book's scientific content or visually inspected every page.

Four agy Gemini 3.8 Flash helper outputs were limited to public mechanical/editorial/supplied-metadata tasks and adjudicated in the source report. Private authority content was not delegated. Formal acceptance/source binding and remote delivery are recorded separately, after validation.
