# Radar Review Preparation

Queued issue [#4831](https://github.com/D-sorganization/AffineDrift/issues/4831), epic #4009 / corpus #4021. No implementation lease, source edits, acceptance or corpus credit. Full current `articles/Launch_Monitor_Technology_Review/sections/04-radar-systems.tex` read at checkpoint `542f03e0b6f095f34cb20ddcfed54f6c1dcf523b`; relevant bibliography entries and parent document inputs inspected. This is one of the longest remaining pending sources (2,002 indexed words). Finish current PR delivery before starting implementation.

## Lead Review Direction

The chapter needs a measurement-to-inference chain: signal and geometry assumptions, observability, estimation uncertainty, device implementation and empirical validation. Treat these separately. A phase equation does not guarantee a unique angle; a Doppler spectrum does not guarantee an identifiable spin fundamental; trajectory fitting does not guarantee a unique well-conditioned axis; a vendor label or patent is not independent accuracy evidence.

The issue records six scoped findings. Additional research should verify the actual band/range claims, coherent processing assumptions, K-LD7 data interface, Full Swing patent architecture, product generation and mode definitions, and cited validation conditions. Do not repeat its universal claims about all vendors or all studies. A one-time calibration is not proof that software, drift, multipath or target association cease to matter. The chapter's universal 24 GHz range limitation conflicts with its own later long-range 24 GHz example.

## Flash Adjudication

One supplied-text agy CLI `gemini-3.8-flash-high` inventory was read and adjudicated. Raw output remains local as `radar-inventory-flash.txt`. No tools, canonical editing, issue claims or publication authority were delegated.

- Accept phase-branch, aspect-angle, harmonic-number, inference-conditioning and product-mode questions.
- Reject a universal impossibility claim for trajectory-based axis inference. A rank-two homogeneous system in three dimensions has a one-dimensional nullspace; unit normalization identifies an axis up to sign. Rank-one rows leave a plane. Changing airspeed directions can add information if a constant spin vector and an adequate force model are justified. Instantaneous gyro-spin blindness alone does not establish non-identifiability over every trajectory.
- Reject the alleged single-module 3D contradiction: the source explicitly proposes separate vertical and horizontal angle modules. Their synchronization, coordinate registration, target association and sensing baselines still need treatment.
- A feature radius can mean distance from the rotation axis; it need not equal the ball radius. The missing line-of-sight projection is the sound criticism, not a universal equator requirement.
- A large baseline can be usable over a restricted field of view or with ambiguity resolution. The half-wavelength criterion is not an unconditional ban on larger baselines; even the endpoint convention matters.
- A local empirical linear loft model is possible with a stated domain. Reject the helper's blanket impossibility claim and unverified club-specific weighting numbers.
- Indoor device operation does not itself prove measured spin. Garmin's standard-ball thresholds are documented; the missing RCT mode qualification is the concrete finding.
- A named vendor statement in a forum can be evidence of that dated statement if authenticated. It cannot automatically establish the deployed algorithm in every newer product.

## Primary Reading Limits

Garmin's general R10 accuracy page was available in indexed primary text at `https://support.garmin.com/id-ID/?faq=kj37CgzvwM98hC9WPrIQm5`. The separately indexed RCT support page describes indoor spin measurement, but direct retrieval of `https://support.garmin.com/en-US/?faq=COFCXdRAJv2m8r9MBtLrf8` and its French-Canadian version returned mostly navigation. Record that limitation and obtain complete current instructions before accepting setup details.

Rapsodo's current product FAQ distinguishes optical RPT support for MLM2PRO from radar RCT support for MLM: `https://rapsodo.com/products/titleist-2025-pro-v1x-golf-balls-w-rpt`. Relevant FAQ passages were read. Other vendor pages contain stale or internally inconsistent purchase/compatibility wording; do not infer firmware history from them. This reading establishes the product distinction, not an independent accuracy result.

TrackMan's April 2020 OERT article body was read at `https://www.trackman.com/blog/two-radars-one-camera-zero-doubt`. It describes synchronized sensing, 40 kHz sampling, silhouette tracking and a stated pickup rate. These are dated vendor claims, not proof of the full current proprietary algorithm or a universal radar limitation. Selected club-data definition passages at `https://www.trackman.com/blog/club-data-definitions` distinguish impact-location orientation and impact timing from a geometric-center description.

Selected spin/trajectory description passages of US8845442B2 and selected time-delay description passages of US10775492B2 were read as technical disclosures. No full patent, legal-status, claim-scope or implementation validation was performed. The latter's dimensional and algebraic discrepancy is detailed in #4831. US9958527B2 and US11311789B2 were located but their mechanisms have not yet been read in full. Do not upgrade a located source to reviewed evidence.

## Preliminary Arithmetic

Local `radar-preliminary-arithmetic.json` contains manufactured checks: 24.125 GHz gives 71.9487079291 Hz per mph using exact SI light speed; 10.5 GHz gives 31.3144635547. The unequal-baseline ratio discrepancy yields 66.5868 degrees versus the specified 30 degrees. Rank-one and rank-two nullspace examples illustrate the corrected inference argument. These are arithmetic checks, not a radar simulation, validation study or tested replacement for a patented method.

Next: after current PR delivery frees implementation capacity, check the issue claim, obtain a lease, review the remaining primary sources and add independent tests for the actual corrections. Preserve the accepted ideomotor records and all other corpus findings.
