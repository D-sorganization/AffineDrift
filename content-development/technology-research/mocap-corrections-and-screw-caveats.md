# Motion Capture — Corrections, Screw-Axis Caveats, and Golf Findings

Compiled 2026-08-02. Late-arriving dossier that **corrects several claims** and supplies the
strongest available counterweight to helical-axis advocacy. `✅` = verified to primary source.

---

## 1. The correction that matters most: screw representation is correct but NOT protective

The helical/screw description is frame-free and sequence-independent — that much is sound geometry.
**But the measurement problem is unsolved**, and the article must say so:

- **Woltring HJ (1985).** _Explanation, verification and application of helical-axis error propagation formulas._ _Hum Mov Sci_. **FHA direction error ∝ 1/φ and ∝ 1/(cluster radius)** — ill-conditioned as rotation angle → 0. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/0167945784900071)
- **Ancillao (2021)** — skin-marker instantaneous helical axis at the knee is off by **33 ± 8° in direction and 38 ± 11 mm in position** versus reference. **This is the sharpest available caveat: the invariance is real, the estimate from skin markers is not.**
- **Woltring HJ (1994).** _3-D attitude representation of human joints: a standardization proposal._ _J Biomech_ 27(12):1399–1414, DOI [10.1016/0021-9290(94)90191-0](<https://doi.org/10.1016/0021-9290(94)90191-0>) ✅ — **the paper that most directly supports the screw-theoretic thesis, and it is under-cited relative to the ISB recommendations that partially set it aside.** Woltring argued for it in 1994 and lost to Grood–Suntay on clinical familiarity, not correctness.
- **Woltring HJ (1991).** _Representation and calculation of 3-D joint movement._ _Hum Mov Sci_ 10(5):603–616, DOI [10.1016/0167-9457(91)90048-3](<https://doi.org/10.1016/0167-9457(91)90048-3>) ✅

> **Honest framing for the article: use screw representation for interpretation; be explicit that the estimation problem from skin markers is unsolved.** Golf transition — where angular velocity passes through small values — is exactly where the conditioning is worst.

**Nobody has applied a screw description to the club itself.** The two golf anchors are Vena et al. (2011, ISA sequence) and Kim (2025, pitch invariance, n=2).

---

## 2. Corrections to commonly repeated claims

| Claim                                         | Verdict                                                                                                                                              |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shaft deflection "~mm-scale"                  | **Wrong by an order of magnitude.** Nesbit measured **108.8 mm peak, 61.25 mm at impact**, predominantly in-plane                                    |
| Pelvis 500–700, thorax 700–900 °/s            | **Not supported for the downswing.** Peer-reviewed optical: **pelvis 415 °/s, thorax 552 °/s in downswing; thorax reaches 929 °/s only post-impact** |
| Arm >1000, hand/club >2000 °/s                | **No retrievable peer-reviewed citation. Do not publish without one**                                                                                |
| Impact ~0.45 ms                               | **Confirmed** ~400–500 µs, ~13 kN peak; **cite Penner's "<0.5 ms"** rather than a spuriously precise 0.45                                            |
| GEARS 360 fps / 0.2 mm                        | **Confirmed** (8 cameras, 1.7 MP, 360 fps, 34 markers) — **but 0.2 mm is a static/resolution figure, not dynamic clubhead accuracy**                 |
| K-Vest "3–4 sensors"                          | **4** (thorax, pelvis, lead upper arm, lead wrist); sample rate not published — only sourced figure is **120 Hz from the 2007 patent**               |
| Swing Catalyst uses Qualisys                  | **No evidence.** Ships its own markerless module with undisclosed partner                                                                            |
| 780 nm strobe                                 | **Legacy.** All current flagship spec sheets state **850 nm**                                                                                        |
| Abdel-Aziz & Karara date                      | **1971**, not 2015 (citation tools substitute the PE&RS reprint DOI)                                                                                 |
| Triggs et al. Bundle Adjustment               | **2000** per Crossref (LNCS), often miscited as 1999                                                                                                 |
| US5227985 as a Motion Analysis patent         | **Wrong** — University of Maryland (DeMenthon lineage). The foundational Motion Analysis patent is **US4656507**                                     |
| Sportsbox AI vs "Swing AI" litigation         | **No suit found; premise unsupported**                                                                                                               |
| TrackMan vs Foresight / Full Swing litigation | **No evidence found.** Do not state these companies have litigated against each other                                                                |

---

## 3. The X-factor finding that undercuts the construct

**Kwon et al. (2013)** — strongly confirms reference-frame dependence, **plus the harder result that X-factor parameters do not correlate with maximum clubhead velocity in skilled golfers at all.**

Supporting the same theme:

- **Bourgain**: X-factor magnitude **doubles** with landmark choice.
- **Kwon 2013**: significantly different values across **three computation methods**.
- **Phadke 2011** (Euler decomposition): elevation error <3° but **axial rotation error 24°**.
- **Reinschmidt 1997**: secondary-plane knee angle errors **63–70% of range**.
- **Polhemus Liberty golf study**: **ICC 0.0 on the longitudinal axis.**

---

## 4. Golf patents worth citing

- **US11504581 / US11583729** — _Systems and methods for integrating measurements captured during a golf swing_, **TaylorMade**. Claim 1 is an automated fitting kiosk combining an optical and a radar launch monitor, applying **technology-type-dependent offsets to align measurements across devices**. **This is the patent literature explicitly acknowledging inter-launch-monitor disagreement.** [Google Patents](https://patents.google.com/patent/US11504581B2/en)
- **US11107366** — **Acushnet/Titleist**: a wheeled gantry carrying a **2,000–6,000 fps camera** on chain-belt multi-axis positioners, repositioning to the golfer between shots rather than forcing them back to a fixed address position after divots.
- **US8616989** — **K-Motion** (K-Vest): body-mounted IMUs at **120 Hz**, kinetic efficiency index normalized 0–100, plus a prescription engine selecting corrective exercises. Continuations US9770658, US10456676, US10463958, US10569134, US10576373, US11000765, US11033776.
- **US9694267** — **Blast Motion**: _Swing analysis method using a swing plane reference frame_ — **transforms sensor trajectory into a swing-plane frame defined by the club longitudinal axis and the impact velocity vector.** A genuine frame-covariance argument in a consumer patent.
- **US10133919 / US10706273** — Blast Motion, _combining sensors with different measurement ranges_ — the dual-range gyro saturation solution.
- **US7324663** — Wintriss/Foresight: standalone smart camera recovering speed, trajectory, spin axis and rate by rotating/scaling/correlating image pairs, **using natural surface features so the ball need not be marked.** The ancestor of GC2/GCQuad.
- **US11875517** — Full Swing: camera ball tracking inferring impact point from the **deceleration signature**, mapping pixel to world by **inverse homography**.

### Litigation

**Max Out Golf LLC v. Cool Clubs / Worldwide Golf** (2015), asserting US8696497 and US7967695 — notable because it **targeted fitters as contributory infringers for using third-party launch monitors** (TrackMan; Foresight GC2/FSX). No reported resolution. **Wyoming IP Holdings v. TrackMan** (US8617671) dismissed under §101/Alice.

### Explicit negative findings

**GEARS Golf / Gears Sports / AMM: no US patents indexed under any of those assignee strings.** Do not assert a patent estate. Also zero results: Charnwood Dynamics/Codamotion, Peak Performance Technologies. **Uneekor**: none in the US/EP-weighted index — treat as "not verified," not "none exists" (a KIPO estate may exist).

---

## 5. Structural observations the patent record supports

1. **The optical-mocap core problem was solved twice, differently.** Motion Analysis (US4656507, 1984) reduced markers to edge-lists **in hardware**; Vicon/OMG (US8103055, 2008) solved the same centroiding problem **in software** twenty-four years later.
2. **Marker identity is the recurring battleground**, splitting into three still-live schools: temporal modulation (PhaseSpace US6324296), spatial uniqueness (Oxford Metrics US11662417), and sequential-then-simultaneous strobing (NDI US5828770).
3. **Golf-specific measurement never converged on mocap at all** — it split into radar (TrackMan), photometric ball/club imaging (Foresight), body-worn IMU (K-Motion, Blast), and monocular deep-learning pose (Sportsbox). **Sportsbox is the only one whose claims read on markerless 3D _body_ kinematics.**

---

## 6. The five theses this supports

1. **The error budget is inverted in most treatments.** STA (10–40 mm, ~5° against bone) ≫ landmark misidentification (6–25 mm) > joint-model assumptions (degrees) ≫ instrumental error (0.06–0.2 mm). **The exception that matters for golf: markers rigidly affixed to a club have no STA, so club kinematics genuinely can approach the hardware limit while body-segment kinematics cannot.**
2. **Primary-plane rotations survive; secondary rotations do not — across every modality.** Golf's entire vocabulary consists of secondary/transverse rotations. **That is the central irony of the field.**
3. **The screw representation is correct but not protective** (§1).
4. **Every degree of freedom you don't measure, you assume — and the assumption becomes the answer.** The reproducibility problem is an _analyst-degrees-of-freedom_ problem, not a hardware one.
5. **Golf sits precisely at the intersection of every failure mode**, and **no reference standard can measure a full swing** — DSX cannot fit or dose one, and every field-usable method is validated against optical mocap, which is itself ~5° from the bone.

---

## 7. Canonical citations confirmed

- **Spoor & Veldpaus (1980)**, _J Biomech_ 13(4):391–393, DOI [10.1016/0021-9290(80)90020-2](<https://doi.org/10.1016/0021-9290(80)90020-2>) ✅
- **Söderkvist & Wedin (1993)**, _J Biomech_ 26(12):1473–1477, DOI [10.1016/0021-9290(93)90098-Y](<https://doi.org/10.1016/0021-9290(93)90098-Y>) ✅ — the SVD/Procrustes pose estimator still default in every commercial package
- **Grood & Suntay (1983)**, _J Biomech Eng_ 105(2):136–144, DOI [10.1115/1.3138397](https://doi.org/10.1115/1.3138397) ✅
- **Lu & O'Connor (1999)**, _J Biomech_ 32(2):129–134, DOI [10.1016/S0021-9290(98)00158-4](<https://doi.org/10.1016/S0021-9290(98)00158-4>) ✅ — origin of global optimization/MKO
- **Ehrig et al. SCoRE (2006)** DOI [10.1016/j.jbiomech.2005.10.002](https://doi.org/10.1016/j.jbiomech.2005.10.002) ✅ and **SARA (2007)** DOI [10.1016/j.jbiomech.2006.10.026](https://doi.org/10.1016/j.jbiomech.2006.10.026) ✅ — **SARA is a screw-axis estimator dressed in least-squares clothing**
- **Cappozzo et al. (1995, 1996)** and the four-part _Gait & Posture_ 2005 STA review series ✅
- **Brainerd et al. XROMM (2010)**, DOI [10.1002/jez.589](https://doi.org/10.1002/jez.589) ✅
- **De Groote et al. (2008)**, Kalman smoothing, PMID 19026414 ✅
- **Zatsiorsky**, _Kinematics of Human Motion_ (1998) — **the most complete treatment of screw/helical axis methods in a biomechanics textbook**

---

## 8. Items requiring verification before publication

Vicon and Qualisys acceptable calibration residuals (both behind login/AccessDenied); OpenSim IK marker-error thresholds (Confluence 404 after migration — treat as heuristics regardless); Optotrak Certus and PhaseSpace specs (products retired, pages 404); DSX per-trial radiation dose; Woltring (1986) GCVSPL DOI and the 1990/1995 book chapters; VideoPose3D/MotionBERT absolute Human3.6M MPJPE; OpenPose/HRNet numeric COCO AP.
