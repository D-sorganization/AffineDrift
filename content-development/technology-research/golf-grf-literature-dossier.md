# Golf Ground Reaction Force & Force-Measurement Dossier

Compiled 2026-08-02 as source material for `articles/technology-force-measurement.qmd`.
Every quantitative claim is traced to a source URL. Claims that could not be verified
against a primary source are flagged **[UNVERIFIED]**.

---

## 0. Keystone source: the 2026 systematic review

Watson A, Murray A, Ehlert A, Xu J, Williams S, Spiegelhalter A, Coughlan D, Turner A, Bishop C (2026). Ground Reaction Force and Centre of Pressure During the Golf Swing and Associations with Clubhead Speed and Skill Level: A Systematic Review. _Sports Medicine_ 56(5):1191–1212. doi:10.1007/s40279-025-02391-3. PMID: 41653371 — https://pubmed.ncbi.nlm.nih.gov/41653371/

- PRISMA 2020; 129 studies retrieved; **24 met inclusion criteria**.
- Newcastle-Ottawa: **all 24 scored 7 or 8 of 9** — the golf GRF literature is methodologically decent but small.
- **9 empirical investigations** showed moderate-to-strong CoP↔CHS or GRF↔CHS relationships.
- More skilled golfers "tended to exhibit higher GRF and superior CHS."
- Authors explicitly call for _"clearly defined methods for assessing force during the golf swing and universal terminology regarding GRF and CoP metrics."_

**[LIMITATION]** Full text paywalled; abstract verbatim only, not the effect-size tables.

---

## Part A — Golf GRF literature

### A.1 Barrentine et al. (1994) — the founding citation

Barrentine SW, Fleisig GS, Johnson H, Woolley TW (1994). Ground reaction forces and torques of professional and amateur golfers. In _Science and Golf II_, E & FN Spon. doi:10.4324/9780203474709-6

Direct access returned HTTP 403. Values recovered **secondhand** via Worsfold, Smith & Dyson (2008) — reliable secondary reporting, verify before publication.

Ground reaction torque about the vertical axis (free moment), artificial surface:

| Group                 | Back foot | Front foot |
| --------------------- | --------- | ---------- |
| All handicaps (range) | 17–26 Nm  | 17–26 Nm   |
| PGA + low handicap    | 17–18 Nm  | 23–26 Nm   |
| Driver, reported peak | 22 Nm     | 23 Nm      |

Source: https://www.jssm.org/volume07/iss3/cap/jssm-07-408.pdf (pp. 412–413)

Used **Fz% (vertical force ratio between feet)**; COP only for heel-to-toe analysis. Handicap split 0–15 / 15+ — coarser than Koenig/Williams (0–7, 8–14, 14+), which Ball identifies as a source of conflicting results.

### A.2 Koenig et al. (1993/1994)

Koenig G, Tamres M, Mann RW (1994). The biomechanics of the shoe-ground interaction in golf. In _Science and Golf II_.

Via Ball 2006 thesis (https://vuir.vu.edu.au/1432/1/Ball.pdf): two force plates, measure = Fz%. N = 14, hcp 0–20. Fz% (0% = back foot, 100% = front) at successive events: **55 → 35 → 20**. Skill differences located at top of backswing, contra Wallace et al. (1990).

**Critique:** Worsfold et al. (2008) note "qualitative observational reports without descriptive statistics or statistical analyses (Koenig et al. 1994) can result in the basis of knowledge being anecdotal." The two most-cited foundational golf GRF papers are a paywalled conference chapter and a partly qualitative report.

### A.3 Worsfold, Smith & Dyson — shoes, GRF, free moment

**(a) Worsfold P, Smith NA, Dyson RJ (2008).** Low handicap golfers generate more torque at the shoe-natural grass interface when using a driver. _J Sports Sci Med_ 7(3):408–414 — https://www.jssm.org/volume07/iss3/cap/jssm-07-408.pdf

_Methods:_ 24 golfers (8 low 0–7; 8 medium 8–14; 8 high 15+); driver, 3-iron, 7-iron; 3 shoes. **Two Kistler 9851 covered with 30 mm natural grass turf, outdoors**, Kistler 9865 amps, **1000 Hz**. Torque as **Tzmax** (peak) and **torque generated** (max-to-min range).

|                          | Front foot         | Back foot    |
| ------------------------ | ------------------ | ------------ |
| Tzmax (all clubs)        | **17–19 Nm**       | **6–7 Nm**   |
| Torque generated (range) | **~40 Nm** (38–43) | **10–16 Nm** |

Driver, back-foot torque generated (Nm, mean ± SD):

| Shoe              | Low (0–7)      | Medium (8–14) | High (15+) |
| ----------------- | -------------- | ------------- | ---------- |
| Metal spike       | **18.2 ± 3.1** | 15.5 ± 4.7    | 14.2 ± 7.4 |
| Alternative spike | **15.8 ± 3.7** | 13.2 ± 3.1    | 11.0 ± 4.4 |
| Flat sole         | **14.4 ± 2.4** | 11.6 ± 4.0    | 11.9 ± 5.6 |

Low < medium/high p < 0.05 for all three shoes. **Front foot showed no handicap effect** (38.9–43.5 Nm) — the discriminating variable is the _trail_ foot.

_Vertical GRF_ (Worsfold et al. 2007, cited within): peak vGRF **lower** with driver (back **0.49 BW**, front **0.84 BW**) than 3-iron/7-iron (back **0.82 BW**, front **1.1 BW**). Weight transfer between feet peaks at **0.3–0.4 BW**.

> The driver's distinguishing kinetic signature is in **Tz (free moment)**, not **Fz** — precisely the component pressure mats cannot measure.

Mechanical shoe-traction (Worsfold et al. 2006a): metal vs alternative 7-spike on natural turf — forefoot linear traction +7%, forefoot **rotational traction +31%**, full-foot inward rotation +11%, outward +18%.

**(b) Worsfold P, Smith NA, Dyson RJ (2009).** Kinetic assessment of golf shoe outer sole design features. _J Sports Sci Med_ 8(4):607–615. PMC3761538 — https://pmc.ncbi.nlm.nih.gov/articles/PMC3761538/

18 golfers (hcp 12.4 ± 7.8), driver. **Two Kistler 9851 @ 1000 Hz**; **Footscan RS insoles @ 500 Hz**.

| Measure             | Metal            | Alternative | Flat             |
| ------------------- | ---------------- | ----------- | ---------------- |
| Back foot Tzmax     | 7.8 ± 1.6 Nm     | 7.2 ± 1.6   | 7.2 ± 1.5        |
| Back foot Tz range  | **14.8 ± 1.8\*** | 14.3 ± 1.9  | **13.2 ± 2.0\*** |
| Front foot Tzmax    | 20.8 ± 3.7       | 20.4 ± 4.3  | 19.7 ± 4.0       |
| Front foot Tz range | 38.1 ± 5.9       | 38.9 ± 5.5  | 39.2 ± 4.2       |

\* metal > flat p < 0.05. Fzmax no shoe differences. **COFxy** (requires shear — force plate only): back 0.607–0.654, front 0.608–0.634.

### A.4 Ball & Best — weight-transfer styles

- Ball KA, Best RJ (2007). Different centre of pressure patterns within the golf stroke I: Cluster analysis. _J Sports Sci_ 25(7):757–770. PMID 17454544
- Ball KA, Best RJ (2007). ...II: group-based analysis. _J Sports Sci_ 25(7):771–779. PMID 17454545
- Ball KA, Best R (2011). Golf styles and centre of pressure patterns when using different golf clubs. _J Sports Sci_ 29(6):587–590. PMID 21347969
- Ball K, Best R (2012). Centre of pressure patterns in the golf swing: individual-based analysis. _Sports Biomech_ 11(2):175–189. PMID 22900399
- Ball K (2006). PhD thesis, Victoria University — https://vuir.vu.edu.au/1432/1/Ball.pdf

_Instrumentation:_ two **AMTI** plates, Pro-Turf covered; **AMLAB 16-bit**; COP parallel to shot line as **CPy%** (0% = front-foot midpoint, 100% = back-foot midpoint) at **eight swing events**.

_Paper I:_ 62 golfers. Cluster analysis identified **two CPy% styles**:

- **Front Foot** (n = 39): even → back in backswing → forward early downswing → **continues to front foot through contact**.
- **Reverse** (n = 19): identical through early downswing, then **moves back toward trail foot through contact and follow-through**.

**Both styles occurred across all skill levels from professional to high handicap — neither is a technical error.** Pooling styles produces statistical cancellation, which Ball identifies as the root cause of decades of conflicting weight-transfer results.

_Paper II — correlates of club velocity, within style:_

- **Front Foot:** larger CP range and more rapid downswing CP movement → larger CHV.
- **Reverse:** CP further from back foot at late backswing, more rapid transfer _toward the back foot_ at contact → larger CHV.

Opposite-signed optimal strategies.

_Paper III:_ 46 golfers, driver/3-iron/7-iron. **96% used the same style across all clubs** — style is a stable individual trait. Reverse-style golfers positioned COP nearer the toes at contact.

_Paper IV:_ 5 golfers × 50 swings. Significant combinations **differed per golfer**. Most consistent: larger weight-transfer range → larger CHV (p < 0.05); all golfers showed ≥1 significant relationship with **rate** (p < 0.01).

_Thesis details:_ **CPy% and Fz% correlated r = 0.99, p < 0.001, N = 62** — for between-feet transfer, COP position and vertical-force ratio are effectively interchangeable. Back-foot vGRF at takeaway vs club velocity: **r = 0.45**. Minimum detectable effect given N: **r = 0.35**.

Historical Fz%/CP% values (0% = back foot):

| Study                  | Group              | Measure | Values                 |
| ---------------------- | ------------------ | ------- | ---------------------- |
| Richards et al. (1985) | Low hcp <10, N=10  | COV     | 28, 96, 17, 105        |
| Richards et al. (1985) | High hcp >20, N=10 | COV     | 22, 81, 15, 98         |
| Wallace et al. (1990)  | Low hcp, N=1       | CP%     | 63, 53, 27, 68, 82, 90 |
| Wallace et al. (1990)  | High hcp, N=1      | CP%     | 49, 42, 31, 47, 67, 77 |
| Koenig et al. (1993)   | hcp 0–20, N=14     | Fz%     | 55, 35, 20             |
| Robinson (1994)        | Professional, N=10 | Fz%     | 49                     |
| Robinson (1994)        | Amateur 0–20, N=20 | Fz%     | 58                     |

Williams & Cavanagh (1983), Mason et al. (1990, 1995), Barrentine et al. (1994), Neal (1998) **reported no numerical values at all**.

### A.5 COP vs COG

Smith AC, Roberts JR, Kong PW, Forrester SE (2017). Comparison of centre of gravity and centre of pressure patterns in the golf swing. _Eur J Sport Sci_ 17(2):168–178. PMID 27737623 — https://pubmed.ncbi.nlm.nih.gov/27737623/

22 low-handicap golfers. **Vicon + two Kistler plates.** PCA on COP and COG in ML and AP.

- **COP↔COG PC1: ML r = 0.90; AP r = 0.81** (p < .05).
- Clubhead velocity explained by three PCs = **74%** of variance; predictive PCs were **timing and rate of change of COP_ML near the downswing**, _not_ magnitude.

> **Rate and timing beat magnitude** — recurs across the literature. Rate metrics are far more sensitive to sample rate and filtering than peak magnitudes.

### A.6 Han et al. — the ground-reaction _moment_ paper

Han KH, Como C, Kim J, Lee S, Kim J, Kim DK, Kwon YH (2019). Effects of the golfer-ground interaction on clubhead speed in skilled male golfers. _Sports Biomech_ 18(2):115–134. PMID 31042142 — https://pubmed.ncbi.nlm.nih.gov/31042142/

- **N = 63 highly skilled males (hcp ≤ 3)** — by far the largest force-plate golf sample.
- Driver, 5-iron, pitching wedge. Optical mocap + force plates.
- Computed **three golfer-ground interaction moments**: GRF moments, **pivoting moments**, foot contact moments.
- **Primary moments: the GRF moment about the forward/backward axis, and the pivoting moment about the vertical axis** (the free moment).
- **Lead foot primarily generates the GRF moment; trail foot contributes more to the pivoting moment.**
- Maximum angular effort at the instant **"the lead arm becomes parallel to the ground"**; loading onto the lead foot there is critical to both peak moments.
- Decomposes moment into resultant horizontal force × moment arm — maps directly onto a wrench/screw treatment.

**[LIMITATION]** Full text paywalled; no numeric moment magnitudes or r values in abstract.

> Converges with Worsfold: trail foot is where torsional action is, and it is invisible to pressure mats.

### A.7 Nesbit — work and power

Nesbit SM, Serrano M (2005). Work and power analysis of the golf swing. _J Sports Sci Med_ 4(4):520–533. PMC3899668 — https://pmc.ncbi.nlm.nih.gov/articles/PMC3899668/

4 golfers — scratch (52.0 m/s CHV), 5-hcp (49.7), 13-hcp (46.3), 18-hcp F (42.1).

Total body work, downswing:

|                             | Scratch  | 5-hcp    | 13-hcp   | 18-hcp   |
| --------------------------- | -------- | -------- | -------- | -------- |
| Total work (Nm)             | **1452** | 1429     | 1105     | 878      |
| Core (back/hips) share      | 71.8%    | 72.2%    | 70.0%    | 68.7%    |
| Upper body share            | 24.7%    | 24.2%    | 26.2%    | 28.0%    |
| **Lower body (legs) share** | **3.6%** | **3.6%** | **3.8%** | **3.3%** |

Club model: peak power 3875/3005/2310/1720 W; max torque 42.1/36.8/24.6/24.0 Nm; max force 512/453/390/304 N; "efficiency" (club work / body work) 24.5%/20.2%/26.1%/26.8%.

Model validation: vertical GRF from full-body model vs force plate agreed to **max 7% difference**.

> **Two cautions.** (1) "Efficiency" is non-monotonic in skill — it does not mean what its name suggests. (2) Legs perform only **~3.3–3.8% of total body work**, yet 100% of the external wrench enters through the feet. GRF is the reaction to whole-body momentum change; attributing it to leg work is a category error.

Companion: Nesbit SM (2005). A three dimensional kinematic and kinetic study of the golf swing. _JSSM_ 4(4):499–519 — https://www.jssm.org/volume04/iss4/cap/jssm-04-499.pdf

### A.8 McNitt-Gray — impulse regulation

**[PARTIALLY VERIFIED — search-result summaries only]**

- 9 skilled golfers, 6-iron, three conditions (Normal, Rear Leg Up, Target Leg Up). Linear/angular impulse components from each leg as **resultant horizontal reaction force × moment arm**. **Net angular impulse did not change between conditions**; target-leg angular impulse greater in Target Leg Up — golfers redistribute impulse between legs to conserve the net.
- Skilled golfers manipulate GRF to control distance: **peak horizontal GRF reduced in lead leg by 5%** when reducing shot distance.
- Peterson & McNitt-Gray (2018): lower-extremity multi-joint control strategies during the swing.

### A.9 Force–time characteristics, RFD, clubhead speed

Leary BK et al. (2012). The relationship between isometric force-time curve characteristics and club head speed in recreational golfers. _J Strength Cond Res_ 26(10):2685–2697. PMID 22797001

- 12 recreational golfers (hcp 14.5 ± 7.3). CMJ, static jump, IMTP.
- Handicap vs average CHS **r = −0.52 (p = 0.04)**.
- **Force at 150 ms** vs average CHS **r = 0.46 (p = 0.07)**; maximal **r = 0.47 (p = 0.06)**.
- RFD 0–150 ms vs average CHS r = 0.38 (p = 0.11) — **not significant**.

> The authors' conclusion rests on r ≈ 0.46–0.47 at **p = 0.06–0.07 with n = 12** — _not statistically significant_. Frequently cited as though it established the RFD→CHS link. It did not.

Johansen MJ et al. (2023). _J Sports Sci_ 41(9):912–924. PMID 37585706 — 21 national-level males (hcp +1.1 ± 1.7). CHS correlated with IMTP MVC, isometric bench MVC, leg-press RFD, rotational trunk power, CMJ (**all P < 0.01**).

Johansen MJ et al. (2026). _Scand J Med Sci Sports_ 36(3):e70255. PMID 41815052 — 41 elite (22 M, 19 F) incl. PGA/LPGA:

|                           | Males r [95% CI]      | Females r [95% CI] |
| ------------------------- | --------------------- | ------------------ |
| Trunk rotation peak power | **0.89 [0.72; 0.96]** | 0.59 [0.16; 0.82]  |
| CMJ impulse / peak power  | 0.78 [0.53; 0.90]     | 0.67 [0.30; 0.87]  |
| IMTP peak force           | 0.75 [0.47; 0.90]     | —                  |

Shaw J et al. (2023). _J Sports Sci_ 41(19):1744–1752. PMID 38150377 — 64 youth. Peak power explained **79.4% (6-iron) / 82.4% (driver)** of CHS variance; **but maturity offset alone explained 78.4% / 71.3%** — a confound that swallows most of the effect.

**On "~200% bodyweight vertical GRF": [UNVERIFIED — likely unsupported].** No peer-reviewed primary source located. Conflicts with the only verified per-foot peaks — Worsfold et al. (2007): 0.49/0.84 BW driver, 0.82/1.1 BW irons. Swing Catalyst's own GRF article (https://swingcatalyst.com/resources/articles/ground-reaction-force) contains **no numerical values and no citations**.

### A.10 Impulse-based energy transfer

Rachnavy P et al. (2026). Foot–ground interaction and clubhead speed: impulse-based energy transfer as the key mechanism in the golf swing. _Front Sports Act Living_ 8:1790645. PMID 42052547 — https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2026.1790645/full (open access)

30 golfers (15 pro, 15 amateur). **Six Qualisys Oqus 7+ @ 200 Hz**, 42 markers, 14-segment 26-DOF model. **Kistler 9286BA @ 1500 Hz**. **Surasole Pro 8 insoles @ 20 Hz** (8 resistive sensors/insole).

CHS: pro 110.91 ± 4.12 vs amateur 91.97 ± 4.07 mph; **Cohen's d = 4.63**.

Hierarchical regression on CHS:

- Block 1 (COP + group): R² = 0.355. **Neither early-phase COP (p = 0.190) nor late-phase COP (p = 0.200) significant.**
- Block 2 (+ trunk sequencing): R² = 0.563.
- Block 3 (+ impulse-based energy transfer): **R² = 0.754**, ΔR² = 0.190 (p < 0.0001).

Serial mediation (5,000 bootstrap): total effect early-COP → CHS B = 0.72, p = 0.190 (n.s.); direct B = 0.21, p = 0.660 (n.s.); **indirect via impulse transfer B = 0.31, 95% CI [0.07, 0.63], p = 0.010**.

Group comparisons: trunk sequencing d = 3.19; impulse transfer d = 1.27; **early-phase COP d = 0.20 (n.s.); late-phase COP d = 0.10 (n.s.).**

> COP behaviour has **no direct effect** on CHS and **does not discriminate professionals from amateurs**. Its entire association is mediated through downstream impulse transfer: _"Ground reaction forces contribute to performance only to the extent that they are effectively transmitted through the musculoskeletal system."_

> Note the **20 Hz** insole: with a ~0.25–0.33 s downswing, that is ~5–7 samples across the entire downswing, against 1000–1500 Hz force plates in the same study.

### A.11 GRF variability and skill

Jones KM, Wallace ES, Otto SR (2024). The relationship between skill and ground reaction force variability in amateur golfers. _Sports Biomech_ 23(10):1625–1639. PMID 34455916 — https://pubmed.ncbi.nlm.nih.gov/34455916/

- **104 amateur golfers**, driver and 5-iron. PCA considering **all three GRF components together**.
- Higher skill → lower variability in **2 of 5 PCs (driver)**, **4 of 5 PCs (5-iron)**.
- **Intra-individual variability far below inter-individual variability** across all golfers.

> Empirical foundation for rejecting normative GRF templates.

### A.12 X-factor, kinetic sequence, GRF

Chu Y, Sell TC, Lephart SM (2010). _J Sports Sci_ 28(11):1251–1259. PMID 20845215 — **308 golfers**. Regression at four swing events accounted for **44–74% of ball-velocity variance**. Contributors: upper torso–pelvis separation (X-Factor), delayed arm/wrist release, trunk tilting, weight shifting.

Liu H et al. (2026). _Front Bioeng Biotechnol_ 14:1847830. PMID 42317237 — 16 low-hcp males, SPM{t}. Driver tilt angle smaller than 7-iron in all phases (p < 0.001).

Bourgain M et al. (2017). Contribution of vertical and horizontal components of ground reaction forces on global motor moment during a golf swing. _Comput Methods Biomech Biomed Engin_ 20(sup1):29–30. PMID 29088635 — **no abstract available**; the one paper explicitly quantifying how much of the driving moment comes from _shear_. Worth obtaining.

Ball-position chain-effect studies:

- Kim SE et al. (2021). _Sci Rep_ 11:2694. PMID 33514759 — 20 professionals, 5 ball positions in 2.14 cm increments. Weight-distribution effects appear at address, **disappear during backswing, reappear during downswing**.
- Kim SE et al. (2018). _J Sports Sci Med_ 17(4):589–598. PMID 30479527 — **a 2.14 cm ball-position change significantly alters left vertical GRF and COP AP position.**

### A.13 Screw theory in the golf swing

Kim W (2025). Pitch Invariance Reveals Skill-Specific Coordination in Human Movement: A Screw-Theoretic Reanalysis of Golf Swing Dynamics. _J Funct Morphol Kinesiol_ 10(3):315. PMID 40843846 — https://pubmed.ncbi.nlm.nih.gov/40843846/ (open access)

- Defines **pitch** as the ratio of linear to angular velocity along the **instantaneous screw axis**. Computes ISA trajectories and pitch from 3D marker data, **synchronised with vertical GRF**.
- **Proficient:** tightly bounded pitch oscillations ≈ **±0.0025 cm/rad**, aligned with a **single well-defined GRF peak**.
- **Novice:** irregular fluctuations **−0.025 to +0.01 cm/rad**, **asynchronous GRF with multiple peaks**.

**[MAJOR CAVEAT]** Reanalysis of a dataset with **exactly two golfers**. Hypothesis-generating, not established. Cite for the _framework_, flag the n.

---

## Part B — Commercial systems (INCOMPLETE)

### B.1 The pressure-vs-force distinction

A **force plate** resolves the complete 6-component wrench; COP is _derived_, and **free moment Tz** is recoverable.

A **pressure mat/insole** is an array of sensels measuring **normal stress only**:

- Fz (summed), COP (pressure-weighted centroid), pressure distribution / contact area
- **Fx, Fy (shear) — not measurable in principle**
- **Tz (free moment) — not measurable in principle**

This is a **dimensional** limitation, not an accuracy one. A scalar normal-stress field over a plane carries no information about tangential traction.

**Definitive citation, and it is a golf study:**

Joo SB, Oh SE, Mun JH (2016). Improving the ground reaction force prediction accuracy using one-axis plantar pressure: Expansion of input variable for neural network. _J Biomech_ 49(14):3153–3161. PMID 27515436 — https://pubmed.ncbi.nlm.nih.gov/27515436/

- States explicitly: **"only vertical force is directly calculable from plantar pressure."**
- Trains **wavelet neural networks** to _estimate_ 3-axis GRFs and 3-axis ground reaction moments from pressure.
- **Validated against force plates during golf swings in 80 subjects**, 5-fold CV.
- Accuracy: **r = 0.73–0.97** (accumulated pressure + opposite foot); **r = 0.83–0.98** (+ COP pattern).

### B.2 Pressure-based COP error

Bincalar AD, Freeman C, Schraefel MC (2025). _Sensors_ 25(5):1283. PMID 40096044 — piezoresistive mats: baseline **mean absolute COP error 17.37%** (8×8 layout); optimised geometry **5.47%**; adding footprint prior **3.93%** (a model-based correction, not raw improvement).

Cudejko T, Button K, Al-Amri M (2023). _Sci Rep_ 13:14946. PMID 37696840 — insoles vs plates: **AP COP comparable**; **ML COP consistently shorter**; **vGRF consistently lower**.

> The axis pressure systems measure worst (mediolateral) is the axis golf performance research depends on most (Smith et al. 2017).

Davidson JB et al. (2025). _Ergonomics_. PMID 40704489 — 39 participants, three-compartment insoles: **COP RMSE 1.7–3.4 cm**.

Brady K, Kiernan D (2020). _Gait Posture_ 82:96–99. PMID 32911097 — injected COP error in 3 mm increments; kinetic gait deviation index became **clinically significant at 9 mm and 12 mm**.

> Gait inverse dynamics degrades at **9–12 mm** COP error; validated pressure insoles show **17–34 mm** RMSE. Joint kinetics computed from pressure-derived COP in a golf swing operates well outside an error budget that gait already considers unreliable.

### B.3 Force plates used in the peer-reviewed golf literature

| System                                        | Sample rate | Study                       |
| --------------------------------------------- | ----------- | --------------------------- |
| **Kistler 9851** (×2), grass-covered, outdoor | 1000 Hz     | Worsfold 2008, 2009         |
| **Kistler 9286BA** (×2)                       | 1500 Hz     | Rachnavy 2026               |
| **Kistler** (×2) with Vicon                   | —           | Smith 2017                  |
| **AMTI** (×2), Pro-Turf; AMLAB 16-bit         | —           | Ball 2006, 2007, 2011, 2012 |
| **Bertec FP4060-07-1000**                     | 1000 Hz     | Castro 2018                 |
| **Footscan RS** insoles                       | 500 Hz      | Worsfold 2009               |
| **Surasole Pro 8** insoles                    | **20 Hz**   | Rachnavy 2026               |

### B.4 Swing Catalyst — verified only

Initial Force AS (Norway). https://swingcatalyst.com/resources/articles/ground-reaction-force

- The **3D Motion Plate** is stated to measure force "broken down in three dimensions: one vertical and two horizontal (right/left and toe/heel)."
- The page contains **no numerical force values**, **no timing data**, and **no citations to peer-reviewed work**.

A device measuring three orthogonal force components is a genuine force plate for Fx/Fy/Fz. **Not verified:** sensing technology, sample rate, whether it outputs moments (specifically Tz), accuracy specification. Swing Catalyst also markets a separate **pressure-based plate** — **do not conflate the two products.**

Patent leads (assignees/contents NOT verified): US 9492708, US 8678943, US 11458362, US 12214253.

### B.5 Unresearched

BodiTrak/BodiTrak2 (Vista Medical) specs and TPI relationship; TPI force-plate usage; Swing Catalyst Balance Plate specs; K-Vest/K-Motion, GEARS, Foresight, Trackman force integration; AMTI/Bertec/Kistler commercial specs; Sportsbox AI and video-based force estimation; **any direct validation of BodiTrak or Swing Catalyst against Kistler/AMTI/Bertec** (none located, but the search was truncated — do not claim none exists).

---

## Synthesis: strongest supported arguments

1. **The free moment is where golf's distinctive kinetics live, and pressure mats cannot measure it.** Worsfold (2008): driver produces _lower_ peak vGRF than irons but trail-foot torque discriminates handicap (18.2 vs 14.2 Nm). Han (2019, n=63) independently identifies the trail-foot pivoting moment as a primary moment correlating with CHS.
2. **"Pressure-derived force" is model output.** Joo et al. (2016): only vertical force is directly calculable; the rest needs neural networks achieving r = 0.73–0.98 on golf swings.
3. **The COP error budget is exceeded before inverse dynamics starts.** 9–12 mm matters in gait; insoles show 17–34 mm.
4. **There is no canonical GRF/COP pattern.** Two opposite styles across all skill levels with opposite-signed optimal strategies (Ball & Best); per-individual predictors (Ball 2012); intra ≪ inter-individual variability (Jones 2024, n=104).
5. **COP does not directly cause clubhead speed.** Rachnavy (2026): effects entirely mediated by impulse transfer; COP does not discriminate pro from amateur (d = 0.20, 0.10 n.s.) though CHS does (d = 4.63).
6. **GRF is not leg work.** Nesbit (2005): legs perform 3.3–3.8% of total body work while 100% of the external wrench passes through the feet.
7. **The field is asking for this.** Watson et al. (2026) explicitly recommend "clearly defined methods... and universal terminology regarding GRF and CoP metrics."

**Claims to avoid:** the "~200% bodyweight vGRF" figure (no primary source; conflicts with verified peaks) and framing Leary et al. (2012) as establishing an RFD→CHS link (r ≈ 0.46, p = 0.06–0.07, n = 12).

**Highest-value papers to acquire in full:** Han et al. 2019; Watson et al. 2026; Barrentine et al. 1994; Bourgain et al. 2017.
