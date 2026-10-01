# Radar Screw-Kinematics Review Dossier

Issue [#4717](https://github.com/D-sorganization/AffineDrift/issues/4717), epic #4009. Complete Appendix E read and corrected; adjacent chapters were inspected only to resolve definitions, references, and build dependencies. This dossier records research provenance. It does not qualify the entire book, a hardware implementation, or human measurements.

## Primary Evidence and Read Scope

- [https://link.springer.com/article/10.1007/s12283-010-0058-8](https://link.springer.com/article/10.1007/s12283-010-0058-8): Publisher metadata, abstract, visible Appendix 1 through displayed equation 8; no subscription main text accessed. Part 1 metadata is 2011, volume13 pages105-123. Abstract addresses pelvis/shoulders/left arm, not club-radar estimator.
- [https://link.springer.com/article/10.1007/s12283-010-0059-7](https://link.springer.com/article/10.1007/s12283-010-0059-7): Publisher metadata and complete abstract; no subscription main text accessed. Reports expected sequencing in two of five subjects, not universal golfer behavior.
- [https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-2-twists-part-2-of-2/](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-2-twists-part-2-of-2/): Complete short transcript: adjoint frame conversion, body T^-1 Tdot and spatial Tdot T^-1 matrix definitions.
- [https://www.cds.caltech.edu/~murray/mlswiki/index.php?title=Main_Page](https://www.cds.caltech.edu/~murray/mlswiki/index.php?title=Main_Page): Author archive text including 20Jan2020 statement withdrawing online book PDF; do not promise current free availability.
- [https://www.ti.com/lit/ds/symlink/iwr6843.pdf](https://www.ti.com/lit/ds/symlink/iwr6843.pdf): Rev F April2025; device comparison p5, RF/ADC/ramp specifications p32, transmit/receive subsystem p60; not entire 90-page datasheet.
- [https://www.ti.com/lit/an/swra553a/swra553a.pdf](https://www.ti.com/lit/an/swra553a/swra553a.pdf): Rev A February2020; sections2 through5 (pp3-10): range/velocity/array/timing formulas and settling/ADC caveats. Not a device-qualified firmware example.
- [https://www.ti.com/lit/an/swra554a/swra554a.pdf](https://www.ti.com/lit/an/swra554a/swra554a.pdf): Rev A July2018; sections2-4 pp2-7, especially p6 TDM schedule and required Doppler phase correction before angle estimation.
- [https://rfbeam.ch/download/k-ld7-datasheet/](https://rfbeam.ch/download/k-ld7-datasheet/): Rev B March2021; characteristics p2; speed/distance/angle p6; speed-range settings/table4 p11. Downloaded public PDF; no login or access workaround.
- [https://omnipresense.com/wp-content/uploads/2024/01/OPS243-Product-Brief_004-F.pdf](https://omnipresense.com/wp-content/uploads/2024/01/OPS243-Product-Brief_004-F.pdf): Complete two-page product brief including A vs C model table.
- [https://www.trackman.com/blog/40-trackman-parameters](https://www.trackman.com/blog/40-trackman-parameters): Full-swing definitions: point, event time, face and plane parameters; not independent validation.
- [https://www.trackman.com/blog/what-is-club-speed](https://www.trackman.com/blog/what-is-club-speed): Technical definition, geometric center immediately before contact.
- [https://www.trackman.com/blog/club-data-definitions](https://www.trackman.com/blog/club-data-definitions): Reference-point and pre-impact-data/event-time explanation; this dated article is not an algorithm disclosure.

The older Murray archive is an availability notice, not access to the full textbook. Vena's publisher preview is not a full-paper read. Vendor definitions are product documentation, not independent accuracy validation. Earlier reviewed article `articles/technology-launch-monitors.qmd` and report `docs/development/technical-review/launch-monitors-review.md` (#4309) already establish the general rank/frame cautions; this review reconciles the appendix with that earlier work without taking new credit for it.

## Independent Derivations and Checks

The single-origin factorization is derived from p_i parallel to u_i and independently checked by the existing random-feature nullspace tests. In linear-first coordinates, A = U[I, [p_O]\_cross], so its rank is at most three. A simultaneous change delta_v = delta_omega cross p_O is invisible. Separate monostatic station examples reach ranks three, five, and six for one, two, and three suitably placed stations; this is not a claim about every MIMO channel geometry.

The body/spatial conversion and screw-axis velocity identity are checked independently by the existing SE(3) tests. The new smooth-history counterexample applies a constant rotation about the radar to both the positions and velocities: all radial histories are unchanged, though angle observations can distinguish the trajectories. This example does not assert ambiguity after those additional observations or a calibrated pose anchor are imposed.

New numerical checks distinguish same-transmitter timing (one versus three transmitters), range-bin migration, and face-normal azimuth rate. At lambda=5 mm, adjacent-chirp interval=25 microseconds, and 128 repeats per transmitter, the single-TX limit/bin/time are 50 m/s, .78125 m/s, 3.2 ms; three-TX TDM gives 16.6667 m/s, .2604167 m/s, 9.6 ms. The original 3.2-ms window allows .16 m radial travel at 50 m/s, or 4.2667 nominal 3.75-cm bins. A 4-GHz ramp at the specified 250 MHz/microsecond maximum needs at least 16 microseconds, exceeding the <8.333-microsecond adjacent-chirp interval needed for unambiguous >50 m/s three-TX TDM at the illustrative wavelength, even before idle time. These calculations do not rule out validated ambiguity-resolution or alternative multiplexing schemes.

A face normal (.8,0,.6) with omega=(3,4,5) rad/s has mathematical horizontal-azimuth rate 2.75 rad/s; its component about a vertical shaft is 5 rad/s. An independent finite rotation verifies the derivative. The manuscript separately defines right-positive golfer-facing path/face conventions in a right-handed target basis.

## Delegation and Scope Control

Two Gemini 3.8 Flash inventories ran through agy CLI with supplied text only, without tools, file edits, or network. Lead independently accepted ordering, coordinate, and inverse-covariance flags. Logging a diagnostic per-frame fit and feeding raw observations to a smoother is not itself contradictory; the actual problem was unsupported observability and uncertainty. Proposed validation is not rejected merely for being a proposal, but remains explicitly unexecuted.

The historical research outline contains further claims requiring complete review. Only a leading qualification notice is changed here; its original body is retained byte-for-byte. [#4719](https://github.com/D-sorganization/AffineDrift/issues/4719) is a native child of epic #4009 and records that remaining scope. No hardware trial is silently closed or represented as completed.
