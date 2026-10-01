# Patent Catalog Review Dossier — October 1, 2026

Issue #4766, within epic #4009. Review in progress; these receipts do not certify legal status or product performance.

## Evidence and Interpretation

The lead compared full source chapters with the captured index metadata and abstract comparisons. Selected first claims were read to distinguish disclosed embodiments from claim requirements. All source HTML and full text are retained in local QA; their hashes and bibliographic fields are recorded in [the committed source inventory](../../../reports/technical-review/patent-catalog-source-inventory.json). The [review report](../../../reports/technical-review/patent-catalog-review.md) records adjudication and outstanding work.

- US10850179B2 claim 1 identifies an axis projection, not an unrestricted full 3D axis.
- US5333874A uses rebound measurements and stored spin values; shared inventors do not establish Foresight ownership.
- US12544624B2 selects a spin candidate using trajectory, probable club and model probabilities.
- US11964188B2 estimates placement-dependent tracking errors; US9162132B2 concerns image-based recognition and shot detection. Neither should inherit an unrelated grouped description.
- US10775492B2 first claim uses delay ratios, receiver separation and receiver-plane conventions; an unconditional indoor-accuracy conclusion is unsupported.
- US6758759B2 and US7143639B2 illustrate why the camera count in an embodiment must not be presented as the minimum in every claim.
- The engineering validation questions are the review's synthesis, not patent-office performance findings.

## Retained Details and Cross-Chapter Consistency Checkpoint

Six additional supplied-text agy Gemini 3.8 Flash jobs are complete (38 patent jobs total): three retained-detail comparisons, one cross-book inventory, one camera-condition search comparison and one patch consistency review. The lead read the drafts and selected primary claims/description passages. The extra handoff-deduplication job belongs to geometry integration, not this patent count.

US11191998B2 claim 1 uses speed/angle-based estimates both to replace unavailable mark-derived spin and to correct available mark-derived spin. Chapter 7 now explains why that corrected output is not independent evidence for its input relationship. US12002222B2 distinguishes database-derived dynamic loft/backspin from motion-vector axis inference. The catalog also corrects golf-surface versus screen impact (US11875517B2), fixed-plane/image measurement versus unsupported simulator lifecycle labels (US8758103B2), and unconditional markerless/camera-count language (US11439886B2). US12263393B2 claim 1 concerns fix-line angle; claims 3/4 expressly add known geometry to the three-dimensional reconstruction.

Retain supported details: US11452911B2 describes range radar as an embodiment; US9958527B2 describes phase-comparison monopulse; US5471383A describes retroreflective material; US5501463A describes face orientation/contact location. Missing words in a first claim do not refute descriptions. US9333409B2's low-speed-camera passage states a motivating difficulty rather than a performance guarantee, so the table now describes candidate-trajectory processing. US9514379B2 likewise states the inference mechanism rather than a low-resolution capability promise.

The abstract, introduction, camera discussion, design guidance and implementation appendix now agree with Chapter 7's evidence boundaries. Removed blanket expiry dates, public-domain recipes, direct commercial lineage and automatic optical-accuracy claims from the identified passages. Camera count, visibility, calibration, geometric priors and model dependence are connected explicitly. These focused edits do not constitute full audits of the five additional sections. Their other hardware, numerical, vendor-comparison and performance statements still need the corpus review.

The final Flash review suggested explicit Creatz attribution and clearer phased optical headings; those clarity edits were accepted. Its claim that the word measured is inherently incompatible with calibrated reconstruction is too broad; the correction avoids an unconditional promised capability without declaring all calibrated measurements invalid. Its Tier 3 reference actually concerned Tier 4. No new patent fact was accepted solely from that draft.

Geometry main integration aab6c3999 is pushed to PR4765 and normally merged here as 7fcd86945. Its current-head static/Python/JS/link checks pass; E2E was still running at this checkpoint. Patent final per-entry adjudication, secondary-reference review, scientific binding and full regression remain pending. Corpus credit remains unchanged at 122 pending full-source audits plus whole-book consistency.

## Additional First-Claim Comparisons

Thirty-six more leading catalog entries have scoped lead dispositions in [the per-entry decision record](../../../reports/technical-review/patent-catalog-dispositions.json). The source hashes and exact table rows make the review reproducible. Twenty-two subjects were refined and14 retained; first-claim scope is not substituted for the full disclosure.

The chapter now explains shared radar-range dependence in US11619708B2 calibration, quality-weighted residual minimization in US12517218B2, and terrain-constrained camera depth in US12186643B2. These examples connect output coordinates and model assumptions to what an apparent agreement or three-dimensional display can actually establish. Single-radar and two-radar embodiments in US10379214B2 are both retained. The updated report records rejected draft diagnoses and remaining work.

## Institutional Sources

- [USPTO Patent Essentials](https://www.uspto.gov/patents/basics/essentials)
- [USPTO Kind Codes](https://www.uspto.gov/patents/search/authority-files/uspto-kind-codes)
- [TrackMan Marking Notice](https://www.trackman.com/legal/patents)
- [Uneekor Marking Notice](https://uneekor.com/en-us/legal/patents)
- [US12702912B2, Official Gazette](https://patentsgazette.uspto.gov/week32/OG/html/1549-2/US12702912-20260811.html): header and first claim inspected; Google mirror unavailable at capture.

- [Company license announcement, syndicated by Nasdaq](https://www.nasdaq.com/press-release/foresight-sports-and-uneekor-agree-license-foresight-sports-patents-related-portable): September 30, 2024, company-authored announcement; original Business Wire URL was unavailable to the browser. The announcement describes on-device screens and states that tracking/ball-flight algorithms were unchanged. It is not proof that one company adopted the other's spin algorithm.

## Publication Text Sources

The links below identify the publications used by the revised chapters. These are patent-text mirrors, not independent accuracy studies. A captured record or a listed link does not imply that every claim was reviewed.

- [EP1735637B1](https://patents.google.com/patent/EP1735637B1/en)
- [US10045008B2](https://patents.google.com/patent/US10045008B2/en)
- [US10052542B2](https://patents.google.com/patent/US10052542B2/en)
- [US10058733B2](https://patents.google.com/patent/US10058733B2/en)
- [US10247553B2](https://patents.google.com/patent/US10247553B2/en)
- [US10315093B2](https://patents.google.com/patent/US10315093B2/en)
- [US10338209B2](https://patents.google.com/patent/US10338209B2/en)
- [US10338212B2](https://patents.google.com/patent/US10338212B2/en)
- [US10379214B2](https://patents.google.com/patent/US10379214B2/en)
- [US10393870B2](https://patents.google.com/patent/US10393870B2/en)
- [US10441863B2](https://patents.google.com/patent/US10441863B2/en)
- [US10444339B2](https://patents.google.com/patent/US10444339B2/en)
- [US10471328B2](https://patents.google.com/patent/US10471328B2/en)
- [US10473778B2](https://patents.google.com/patent/US10473778B2/en)
- [US10587797B2](https://patents.google.com/patent/US10587797B2/en)
- [US10596416B2](https://patents.google.com/patent/US10596416B2/en)
- [US10605910B2](https://patents.google.com/patent/US10605910B2/en)
- [US10639537B2](https://patents.google.com/patent/US10639537B2/en)
- [US10668350B2](https://patents.google.com/patent/US10668350B2/en)
- [US10690764B2](https://patents.google.com/patent/US10690764B2/en)
- [US10775492B2](https://patents.google.com/patent/US10775492B2/en)
- [US10776929B2](https://patents.google.com/patent/US10776929B2/en)
- [US10850179B2](https://patents.google.com/patent/US10850179B2/en)
- [US10898757B1](https://patents.google.com/patent/US10898757B1/en)
- [US10935657B2](https://patents.google.com/patent/US10935657B2/en)
- [US10953303B2](https://patents.google.com/patent/US10953303B2/en)
- [US10962635B2](https://patents.google.com/patent/US10962635B2/en)
- [US10989791B2](https://patents.google.com/patent/US10989791B2/en)
- [US11016188B2](https://patents.google.com/patent/US11016188B2/en)
- [US11033826B2](https://patents.google.com/patent/US11033826B2/en)
- [US11079483B2](https://patents.google.com/patent/US11079483B2/en)
- [US11086005B2](https://patents.google.com/patent/US11086005B2/en)
- [US11086008B2](https://patents.google.com/patent/US11086008B2/en)
- [US11135495B2](https://patents.google.com/patent/US11135495B2/en)
- [US11143754B2](https://patents.google.com/patent/US11143754B2/en)
- [US11170513B2](https://patents.google.com/patent/US11170513B2/en)
- [US11191998B2](https://patents.google.com/patent/US11191998B2/en)
- [US11285367B2](https://patents.google.com/patent/US11285367B2/en)
- [US11291902B2](https://patents.google.com/patent/US11291902B2/en)
- [US11311789B2](https://patents.google.com/patent/US11311789B2/en)
- [US11335013B2](https://patents.google.com/patent/US11335013B2/en)
- [US11351436B2](https://patents.google.com/patent/US11351436B2/en)
- [US11364428B2](https://patents.google.com/patent/US11364428B2/en)
- [US11439886B2](https://patents.google.com/patent/US11439886B2/en)
- [US11446546B2](https://patents.google.com/patent/US11446546B2/en)
- [US11452911B2](https://patents.google.com/patent/US11452911B2/en)
- [US11504582B2](https://patents.google.com/patent/US11504582B2/en)
- [US11513208B2](https://patents.google.com/patent/US11513208B2/en)
- [US11557044B2](https://patents.google.com/patent/US11557044B2/en)
- [US11565166B2](https://patents.google.com/patent/US11565166B2/en)
- [US11573082B2](https://patents.google.com/patent/US11573082B2/en)
- [US11612801B2](https://patents.google.com/patent/US11612801B2/en)
- [US11619708B2](https://patents.google.com/patent/US11619708B2/en)
- [US11619731B2](https://patents.google.com/patent/US11619731B2/en)
- [US11644562B2](https://patents.google.com/patent/US11644562B2/en)
- [US11673029B2](https://patents.google.com/patent/US11673029B2/en)
- [US11697046B2](https://patents.google.com/patent/US11697046B2/en)
- [US11747461B2](https://patents.google.com/patent/US11747461B2/en)
- [US11748985B2](https://patents.google.com/patent/US11748985B2/en)
- [US11771957B1](https://patents.google.com/patent/US11771957B1/en)
- [US11815618B2](https://patents.google.com/patent/US11815618B2/en)
- [US11828867B2](https://patents.google.com/patent/US11828867B2/en)
- [US11844990B2](https://patents.google.com/patent/US11844990B2/en)
- [US11875517B2](https://patents.google.com/patent/US11875517B2/en)
- [US11883716B2](https://patents.google.com/patent/US11883716B2/en)
- [US11921190B2](https://patents.google.com/patent/US11921190B2/en)
- [US11938375B2](https://patents.google.com/patent/US11938375B2/en)
- [US11946997B2](https://patents.google.com/patent/US11946997B2/en)
- [US11951372B2](https://patents.google.com/patent/US11951372B2/en)
- [US11964188B2](https://patents.google.com/patent/US11964188B2/en)
- [US11986698B2](https://patents.google.com/patent/US11986698B2/en)
- [US11995846B2](https://patents.google.com/patent/US11995846B2/en)
- [US12002222B2](https://patents.google.com/patent/US12002222B2/en)
- [US12008770B2](https://patents.google.com/patent/US12008770B2/en)
- [US12036465B2](https://patents.google.com/patent/US12036465B2/en)
- [US12042698B2](https://patents.google.com/patent/US12042698B2/en)
- [US12067775B2](https://patents.google.com/patent/US12067775B2/en)
- [US12105184B2](https://patents.google.com/patent/US12105184B2/en)
- [US12109473B2](https://patents.google.com/patent/US12109473B2/en)
- [US12121771B2](https://patents.google.com/patent/US12121771B2/en)
- [US12128275B2](https://patents.google.com/patent/US12128275B2/en)
- [US12158517B1](https://patents.google.com/patent/US12158517B1/en)
- [US12169941B1](https://patents.google.com/patent/US12169941B1/en)
- [US12179068B2](https://patents.google.com/patent/US12179068B2/en)
- [US12186643B2](https://patents.google.com/patent/US12186643B2/en)
- [US12206977B2](https://patents.google.com/patent/US12206977B2/en)
- [US12253622B2](https://patents.google.com/patent/US12253622B2/en)
- [US12263393B2](https://patents.google.com/patent/US12263393B2/en)
- [US12298326B2](https://patents.google.com/patent/US12298326B2/en)
- [US12322122B2](https://patents.google.com/patent/US12322122B2/en)
- [US12330020B2](https://patents.google.com/patent/US12330020B2/en)
- [US12354282B2](https://patents.google.com/patent/US12354282B2/en)
- [US12361570B2](https://patents.google.com/patent/US12361570B2/en)
- [US12478849B2](https://patents.google.com/patent/US12478849B2/en)
- [US12515116B2](https://patents.google.com/patent/US12515116B2/en)
- [US12517218B2](https://patents.google.com/patent/US12517218B2/en)
- [US12528005B2](https://patents.google.com/patent/US12528005B2/en)
- [US12539454B2](https://patents.google.com/patent/US12539454B2/en)
- [US12544624B2](https://patents.google.com/patent/US12544624B2/en)
- [US12548194B2](https://patents.google.com/patent/US12548194B2/en)
- [US12586211B2](https://patents.google.com/patent/US12586211B2/en)
- [US12586248B2](https://patents.google.com/patent/US12586248B2/en)
- [US12594460B2](https://patents.google.com/patent/US12594460B2/en)
- [US12599828B2](https://patents.google.com/patent/US12599828B2/en)
- [US12605593B2](https://patents.google.com/patent/US12605593B2/en)
- [US12616891B2](https://patents.google.com/patent/US12616891B2/en)
- [US12618962B2](https://patents.google.com/patent/US12618962B2/en)
- [US20160306036A1](https://patents.google.com/patent/US20160306036A1/en)
- [US20180239012A1](https://patents.google.com/patent/US20180239012A1/en)
- [US20210299540A1](https://patents.google.com/patent/US20210299540A1/en)
- [US20230065614A1](https://patents.google.com/patent/US20230065614A1/en)
- [US20230070986A1](https://patents.google.com/patent/US20230070986A1/en)
- [US20230347209A1](https://patents.google.com/patent/US20230347209A1/en)
- [US20230364468A1](https://patents.google.com/patent/US20230364468A1/en)
- [US4136387A](https://patents.google.com/patent/US4136387A/en)
- [US5333874A](https://patents.google.com/patent/US5333874A/en)
- [US5471383A](https://patents.google.com/patent/US5471383A/en)
- [US5501463A](https://patents.google.com/patent/US5501463A/en)
- [US6079269A](https://patents.google.com/patent/US6079269A/en)
- [US6186002B1](https://patents.google.com/patent/US6186002B1/en)
- [US6241622B1](https://patents.google.com/patent/US6241622B1/en)
- [US6500073B1](https://patents.google.com/patent/US6500073B1/en)
- [US6533674B1](https://patents.google.com/patent/US6533674B1/en)
- [US6616543B1](https://patents.google.com/patent/US6616543B1/en)
- [US6758759B2](https://patents.google.com/patent/US6758759B2/en)
- [US6898971B2](https://patents.google.com/patent/US6898971B2/en)
- [US7086955B2](https://patents.google.com/patent/US7086955B2/en)
- [US7143639B2](https://patents.google.com/patent/US7143639B2/en)
- [US7209576B2](https://patents.google.com/patent/US7209576B2/en)
- [US7292711B2](https://patents.google.com/patent/US7292711B2/en)
- [US7324663B2](https://patents.google.com/patent/US7324663B2/en)
- [US7395696B2](https://patents.google.com/patent/US7395696B2/en)
- [US7467060B2](https://patents.google.com/patent/US7467060B2/en)
- [US7497780B2](https://patents.google.com/patent/US7497780B2/en)
- [US7540500B2](https://patents.google.com/patent/US7540500B2/en)
- [US7641565B2](https://patents.google.com/patent/US7641565B2/en)
- [US8007367B2](https://patents.google.com/patent/US8007367B2/en)
- [US8077917B2](https://patents.google.com/patent/US8077917B2/en)
- [US8085188B2](https://patents.google.com/patent/US8085188B2/en)
- [US8189857B2](https://patents.google.com/patent/US8189857B2/en)
- [US8414408B2](https://patents.google.com/patent/US8414408B2/en)
- [US8500568B2](https://patents.google.com/patent/US8500568B2/en)
- [US8556267B2](https://patents.google.com/patent/US8556267B2/en)
- [US8647214B2](https://patents.google.com/patent/US8647214B2/en)
- [US8758103B2](https://patents.google.com/patent/US8758103B2/en)
- [US8834284B2](https://patents.google.com/patent/US8834284B2/en)
- [US8845442B2](https://patents.google.com/patent/US8845442B2/en)
- [US8912945B2](https://patents.google.com/patent/US8912945B2/en)
- [US8926416B2](https://patents.google.com/patent/US8926416B2/en)
- [US8951138B2](https://patents.google.com/patent/US8951138B2/en)
- [US9036864B2](https://patents.google.com/patent/US9036864B2/en)
- [US9162132B2](https://patents.google.com/patent/US9162132B2/en)
- [US9242158B2](https://patents.google.com/patent/US9242158B2/en)
- [US9333409B2](https://patents.google.com/patent/US9333409B2/en)
- [US9333412B2](https://patents.google.com/patent/US9333412B2/en)
- [US9448067B2](https://patents.google.com/patent/US9448067B2/en)
- [US9514379B2](https://patents.google.com/patent/US9514379B2/en)
- [US9605960B2](https://patents.google.com/patent/US9605960B2/en)
- [US9616346B2](https://patents.google.com/patent/US9616346B2/en)
- [US9645235B2](https://patents.google.com/patent/US9645235B2/en)
- [US9737757B1](https://patents.google.com/patent/US9737757B1/en)
- [US9752875B2](https://patents.google.com/patent/US9752875B2/en)
- [US9855481B2](https://patents.google.com/patent/US9855481B2/en)
- [US9857459B2](https://patents.google.com/patent/US9857459B2/en)
- [US9868044B2](https://patents.google.com/patent/US9868044B2/en)
- [US9955126B2](https://patents.google.com/patent/US9955126B2/en)
- [US9958527B2](https://patents.google.com/patent/US9958527B2/en)
- [WO2003032006A1](https://patents.google.com/patent/WO2003032006A1/en)

## Remaining Leading Entries — October 1, 2026

The lead reviewed the remaining42 abstracts and first claims, with targeted description checks for image features, unsynchronized cameras, antenna geometry and brightness compensation. There are now118 selected first-claim reads and no pending leading-entry reads. The consolidated disposition file contains78 records from the two disposition checkpoints:47 refined subjects and31 retained subjects. Earlier selected reviews remain documented in the preceding checkpoints; these counts do not imply an all-claims legal review.

Twenty-five additional subjects were refined and17 retained. The significant corrections distinguish air-density-derived effective altitude from environment-robust tracking (US11573082B2), radar-timed capture from generic sensor fusion (US9955126B2), surface features from mandatory applied markers (US11170513B2), and an image-size database from unrestricted single-camera depth reconstruction (US9605960B2). US11747461B2 retains its expressly disclosed camera/radar association while distinguishing its radar-track first claim. US20230364468A1 expressly separates the ball-image and swing-radar representations rather than integrating their positions.

Retained details are source-supported: US9448067B2 describes unsynchronized cameras, US10587797B2 connects brightness compensation to spin marks, US11311789B2 describes non-uniform antennas, and US8414408B2 describes ball return. Missing words in claim1 alone do not refute those embodiments. US9737757B1's first claim uses two camera-defined planes; its abstract's ground-plane example is not a universal camera-count requirement.

The new chapter discussion connects synthesized timing, launch-origin association, prediction-conditioned track selection and environmental inference to golf-swing interpretation. Interpolated frames are not additional exposures; selection using a predicted trajectory conditions the resulting agreement; shared aerodynamic-model error can persist across multiple trajectory-derived wind estimates; density-equivalent altitude does not encode the entire atmosphere.

Six supplied-text comparisons were dispatched through agy CLI gemini-3.8-flash-high, in two waves of three. All ended with provider HTTP500 or503 errors and returned no review. They are recorded as failed attempts, not added to the47 completed patent support jobs. The lead completed these42 source comparisons and decisions directly. The final secondary-reference review, combined scientific binding, full regression and regular PR remain pending; corpus credit remains122 pending full-source audits plus whole-book consistency.
