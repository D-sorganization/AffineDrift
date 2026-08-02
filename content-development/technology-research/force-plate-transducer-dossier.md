# Force Plate Technology — Transducer and Specification Dossier

Compiled 2026-08-02 as source material for `articles/technology-force-measurement.qmd`.

**Sourcing caveat:** Kistler _product_ pages (9260AA/9260BA/9287/9667AA) were serving 302 redirects to `maint.kistler.com` during research, so Kistler numeric datasheet values (pC/N sensitivities, natural frequencies, crosstalk %) are **not verified**. Kistler content below comes from their technology/glossary pages.

---

## 1. Transducer physics

### 1.1 Strain-gauge plates (AMTI, Bertec)

Bertec: "Each force plate consists of precision-engineered, strain gage load transducers that precisely measure six components: three orthogonal forces and the moments about each axis." Built-in **16-bit digital gain amplifier and signal conditioning**, "which make the use of calibration matrices obsolete" — the plate ships pre-linearized ([FP4060-10-TM datasheet](https://www.bertec.com/s/FP4060-10_v9.pdf); [FP4060-05-PT](https://www.bertec.com/s/FP4060-05-PT_v12.pdf)).

AMTI Optima-SC: **"Six 4-arm strain gage bridges (350 Ω minimum)"**, excitation software-selectable **2.5 / 5 / 10 VDC**, gain **500 / 1000 / 2000 / 4000**, per-channel auto-zero ([AMTI Optima-SC](https://www.amti.biz/product/optima-sc/)). Four-arm bridges give first-order cancellation of thermal-expansion and excitation-voltage drift — why strain gauge is the DC-stable choice.

Kistler's own comparison: strain-gauge bodies are "rather soft" with "low natural frequency" because signal amplitude depends on elastic deformation; piezo bodies are "extremely rigid structures featuring high natural frequencies." Strain gauge is "very long-term stable" with temperature compensation "through electrical bridge circuit adjustment"; piezo is "far more subjected to temperature changes" ([Kistler: piezo vs strain gauge](https://www.kistler.com/US/en/piezo-vs.-strain-gauge/C00000145)).

**Accuracy numbers:**

- Bertec (all sampled models): **Linearity 0.2 %FSO**, **Accuracy error Fz 0.2 %AL**, **Fx,Fy 0.2 %AL**, **Crosstalk Fx,Fy 0.1 %AL**, **Crosstalk Fz 0.1 %AL**, **COP accuracy error 0.8 mm**. Static resolution Fz **±0.4 N** p-p noise; digitization 0.2–0.4 N/LSB.
- AMTI **HPS** series: **accuracy ±0.1 % of applied load**, **crosstalk ±0.05 %AL**, **COP < 0.008 in (≈0.2 mm)**, **hysteresis < 0.5 %FSO** — all qualified "minimum 50 lb applied" ([HPS400600](https://www.amti.biz/product/hps400600/), [HPS464508](https://www.amti.biz/product/hps464508/)).
- AMTI **BMS** (mid-tier): **accuracy ±0.5 %AL**, **crosstalk ±0.2 %AL**, **COP < 0.5 mm** ([BMS400600](https://www.amti.biz/product/bms400600/)). HPS vs BMS = 5× accuracy and 4× crosstalk difference **from the same vendor and same physics** — the delta is calibration density and electronics, not transducer type.
- AMTI instrumented treadmill: linearity and hysteresis ±0.2 %FSO.

**Crosstalk semantics:** Bertec defines it as "for Crosstalk Fx, Fy, the Applied Load is an Fz load; for Crosstalk Fz, the Applied Load is an Fx, Fy load." So 0.1 %AL under a 2000 N vertical peak = **~2 N of phantom shear**.

**Third technology:** AMTI AccuGait-O balance plate uses **Hall Effect sensing elements**, Fz 1334 N, Fx/Fy 445 N, 10–1000 Hz ([AccuGait-O](https://www.amti.biz/product/accugait-o/)).

### 1.2 Piezoelectric plates (Kistler)

"A force plate is a measuring platform with a piezoelectric force sensor in every corner." Force "is applied via a cover plate to four 3-component force sensors, installed **under high pretension**. Each sensor contains three quartz plate pairs — one measuring vertical pressure and two measuring shear forces horizontally" ([Kistler 3D force plate](https://www.kistler.com/US/en/3d-force-plate/C00000090)). Four sensors × 3 axes = 12 crystal stacks, bussed into **8 output channels** (Fx12, Fx34, Fy14, Fy23, Fz1..Fz4) — the practical difference from AMTI/Bertec's 6-channel output, and why Kistler plates require the software to know plate geometry (a, b) to form Mx/My.

"Electrical charges produced in the piezocrystal are proportional to the force applied," read by a charge amplifier. Quartz "is not pyroelectric and is therefore resistant to temperature fluctuations." Piezo offers "an extremely broad measuring range, overload protection and marked long-term stability – lasting decades" ([Kistler piezoelectric effect](https://www.kistler.com/US/en/piezoelectric-effect/C00000136)).

**DC drift:** the charge amplifier is "a charge converter that converts very low charge signals... to proportional voltage signals." Amplifier-selection criteria include **"measurement with zero point reference (quasi-static) or purely dynamic (high-pass behavior)"** — the time-constant (Long/Medium/Short) mode selection ([Kistler charge amplifiers](https://www.kistler.com/US/en/charge-amplifiers/C00000100)). Kistler concedes piezo shows "very small, constant linear drift" that "becomes problematic when measuring smaller forces."

**Engineering framing:** the charge amp integrator has finite feedback resistance R_f and capacitance C_f; τ = R_f·C_f. Long-τ preserves quasi-static content but lets leakage-current offset accumulate (hence mandatory reset/operate zeroing before each trial); Short-τ kills drift but high-passes, destroying the DC baseline needed for impulse–momentum integration. **Golf consequence:** a swing sequence spans several seconds of quasi-static loading; a piezo plate left in Operate through a 30-swing session without re-zero accumulates baseline offset that corrupts COP.

**Kistler digital plates:** **24-bit per channel**, PTP sync "within microseconds," **up to 16 plates daisy-chained**, 100 m cable, lines **9667AA** and **9260BA** ([Kistler digital force plate technology](https://www.kistler.com/US/en/digital-force-plate-technology/C00000167)). AMTI Epsilon: **2000 Hz digital output**, "10× lower signal noise," milli-Newton resolution, 50+ plates ([AMTI Epsilon](https://www.amti.biz/epsilon-force-plate-systems/)).

### 1.3 Capacitive

Dominant in **pressure** platforms rather than 6-axis plates — novel emed uses "calibrated capacitive sensors" ([novel emed](https://novel.de/products/emed/)). Giacomozzi's bench comparison of five commercial pressure devices: **capacitive elastomer-based lowest error (RMSE < 0.5 %)**, capacitive air-based < 5 %, resistive (Tekscan) < 2.5 % but "required complex calibration procedures" ([Giacomozzi 2010, PMID 20399101](https://pubmed.ncbi.nlm.nih.gov/20399101/)).

---

## 2. Pressure mats and insoles

| System                    | Tech       | Sensels            | Density         | Range                 | Rate         | Error                                                                     |
| ------------------------- | ---------- | ------------------ | --------------- | --------------------- | ------------ | ------------------------------------------------------------------------- |
| novel **pedar** insole    | capacitive | 99/insole, max 256 | —               | 15–600 or 30–1200 kPa | up to 400 Hz | resolution 2.5/5 kPa; **hysteresis < 7 %**; offset temp drift < 0.5 kPa/K |
| novel **emed-s** platform | capacitive | 6912               | **4/cm²**       | 10–1270 kPa           | 120 Hz       | ±5 %                                                                      |
| novel **emed-xl**         | capacitive | 25 344             | 4/cm²           | 10–1270 kPa           | 100 Hz       | ±5 %                                                                      |
| **XSENSOR** Insoles Pro   | —          | 235/220/109        | 7–13.4 mm pitch | 0.7–88.3 N/cm²        | up to 150 Hz | **±5 % full-scale**                                                       |
| **Tekscan F-Scan** 3010   | resistive  | —                  | —               | —                     | up to 500 Hz | not published                                                             |

Sources: [novel pedar](https://novel.de/products/pedar/), [novel emed](https://novel.de/products/emed/), [XSENSOR](https://www.xsensor.com/solutions-and-platform/human-performance/gait-motion-insoles), [Tekscan F-Scan](https://www.tekscan.com/products-solutions/systems/f-scan-system).

An **insole is roughly two orders of magnitude coarser than a lab platform**. pedar insoles are individually calibrated on the **trublu** device; XSENSOR relies on **factory calibration**.

**Reliability:** Hafer et al. compared two emed-x and two MatScan units across 22 adults: all intra-platform correlations > 0.70; **five trials sufficed** ([PMID 23454044](https://pubmed.ncbi.nlm.nih.gov/23454044/)). Also [Patrick & Donovan 2018, PMID 28927350](https://pubmed.ncbi.nlm.nih.gov/28927350/); [Zammit 2010, PMID 20565812](https://pubmed.ncbi.nlm.nih.gov/20565812/); [Blades 2023, PMID 36850951](https://pubmed.ncbi.nlm.nih.gov/36850951/).

**The vertical-only limitation:** a sensel responds only to the normal component of traction, returning a scalar field p(x,y,t). You can integrate vertical force and COP — nothing else. Stief & Peikenkamp: "other forms of stress, such as bending, torsional and shear loadings, cannot be detected in shoes during day-to-day activities" ([PMID 26357526](https://pubmed.ncbi.nlm.nih.gov/26357526/)). See also [Spooner 2010, PMID 21084541](https://pubmed.ncbi.nlm.nih.gov/21084541/).

**Golf consequence:** Han/Kwon's 63-golfer study found "the lead foot was responsible for generating the GRF moment, while the trail foot contributed to the pivoting moment more" ([PMID 31042142](https://pubmed.ncbi.nlm.nih.gov/31042142/)). **A pressure mat cannot measure a pivoting moment at all.**

**Commercial illustration:** Swing Catalyst sells **Dual Force Plates** — "6-axis force plates," Fx/Fy/Fz/Mx/My/Mz, **1000 Hz**, 14 000 N combined capacity — and separately **Dual Pressure Plates** at **130 Hz**, returning pressure distribution, heat maps, stance width and balance-point speed, with **no force or moment components listed** ([dual force plates](https://swingcatalyst.com/products/dual-force-plates); [dual pressure plates](https://swingcatalyst.com/products/dual-pressure-plates)). Same vendor, ~8× sample-rate gap, categorical difference in measurand.

---

## 3. Force plate outputs

Six components at the plate origin: Fx, Fy, Fz, Mx, My, Mz. Bertec capacity asymmetry: Fz 5000/10 000 N but **Fx,Fy only half that (2500/5000 N)**; moments Mx 1500, My 1000, Mz 750 N·m for the 5 kN plate. **Shear channels saturate first.**

COP with sensor offset z₀ below the surface:

- COPx = (−My − Fx·z₀) / Fz
- COPy = ( Mx − Fy·z₀) / Fz

**COP error at low Fz:** σ_COP ≈ ε_M/Fz + COP·ε_F/Fz — a **1/Fz** blow-up. Chockalingam et al., testing two strain-gauge platforms with dynamic loads, found accuracy degrades toward plate edges and derived: **"the minimum vertical force threshold might be up to 113 N in order to estimate the centre of pressure within a distance with a S.D. of 0.3 cm"** ([PMID 12443947](https://pubmed.ncbi.nlm.nih.gov/12443947/)). Vendor specs carry load floors for the same reason (AMTI: "minimum 50 lb applied" ≈ 222 N).

**Validation method matters:** Middleton et al. showed single-point loading overstates COP error versus distributed two-block loading — "evaluating centre of pressure accuracy by applying force through a single point overestimates the errors inherent in human stabilometry research" ([PMID 10521614](https://pubmed.ncbi.nlm.nih.gov/10521614/)).

**Free moment Tz:** after COP is located, Mx and My are consumed by the force-offset transformation and go to zero at the COP; **Mz does not**. The residual is the free moment — the only pure couple the foot–ground interface transmits, not derivable from any pressure distribution. Literature: [Begue 2018, PMID 29804814](https://pubmed.ncbi.nlm.nih.gov/29804814/); [Yang 2014, PMID 24732724](https://pubmed.ncbi.nlm.nih.gov/24732724/); [PMID 32158716](https://pubmed.ncbi.nlm.nih.gov/32158716/); [Mahoney 2025, PMID 40991584](https://pubmed.ncbi.nlm.nih.gov/40991584/).

**COP ≠ COM:** posture "can be controlled by accelerating the Center of Mass through shifting the center of pressure within the base of support" — COP is the _control variable_ driving COM ([van den Bogaart 2022, PMID 35123153](https://pubmed.ncbi.nlm.nih.gov/35123153/)). Michaud et al.: immobilizing COM in standing _increased_ COP variability ([PMID 33719906](https://pubmed.ncbi.nlm.nih.gov/33719906/)).

---

## 4. Natural frequency — the spec that constrains golf/impact work

| Plate                                        | Fx     | Fy        | Fz               |
| -------------------------------------------- | ------ | --------- | ---------------- |
| Bertec FP4060-05-PT-1000 (portable, 5 cm)    | 120 Hz | **75 Hz** | 120 Hz           |
| Bertec FP4060-05-PT-2000                     | 160 Hz | 110 Hz    | 160 Hz           |
| Bertec FP4060-10-TM (fixed, 10 cm)           | 325 Hz | 325 Hz    | **>500 Hz**      |
| Bertec FP6090-15-TM (fixed, 15 cm, 60×90)    | 240 Hz | 230 Hz    | 400 Hz           |
| AMTI HPS400600 (1000 lb, standard)           | 310 Hz | 310 Hz    | 370 Hz           |
| AMTI HPS400600 (1000 lb, **high-frequency**) | 480 Hz | 480 Hz    | **720 Hz**       |
| AMTI HPS400600 (2000 lb, HF)                 | 570 Hz | 570 Hz    | 730 Hz           |
| AMTI HPS464508 (standard)                    | 390 Hz | 390 Hz    | 510 Hz           |
| AMTI HPS464508 (HF)                          | —      | —         | **up to 960 Hz** |
| AMTI BMS400600 (4000 lb, standard)           | 450 Hz | 450 Hz    | 410 Hz           |
| AMTI Tandem treadmill — installed plate      | 300 Hz | 300 Hz    | —                |
| AMTI Tandem treadmill — **structure**        | —      | —         | **120 Hz**       |

**Three lessons:** (1) **Portable plates are the weak link** — the Bertec 5 cm portable's Fy natural frequency is **75 Hz**, inside the band of interest for impact or rapid transition, and portables are what gets carried to a driving range. (2) **Larger plate = lower f_n**. (3) **The mounting structure, not the transducer, can be the limit** — AMTI's treadmill quotes plate f*n 300 Hz but \_structure* f_n **120 Hz**.

### Amplifier / acquisition

- **AMTI Gen-5:** gains 500/1000/2000/4000; **digital resolution 14 bit**; anti-alias **1000 Hz low-pass 2-pole Butterworth**; sample rate **max 2000 Hz/channel** ([Gen-5](https://www.amti.biz/product/gen-5/)).
- **AMTI Optima-SC:** sample rate 10–1200 Hz/channel; sync via Genlock/external trigger/internal clock; 0–52 °C indoor only.
- **Bertec:** internal 16-bit amp; **1000 Hz internal sampling**; 100 m cable runs.
- **Kistler digital:** 24-bit/channel, PTP microsecond sync.

Note the anti-alias filter is fixed at 1000 Hz on AMTI conditioners — sampling at 2000 Hz gives exactly Nyquist with a 2-pole rolloff. Thin for genuine impact work.

**Environment:** AMTI plates −18 to 52 °C. novel pedar offset temperature drift **< 0.5 kPa/K**.

---

## 5. Calibration and verification

**Factory:** AMTI Optima verified by **up to 4000 measurements across the platform surface**, multiple loads at **~400 locations**, positioning accuracy **0.005 mm**, NIST-traceable. Claims: COP typically <0.2 mm, crosstalk ±0.05 %AL, accuracy ±0.1 %AL ([Optima technology](https://www.amti.biz/optima-technology/)).

**In-situ recalibration literature:**

- **List et al. (2017)**, 12 years across six plates: in-situ correction "reduced the root mean square errors by up to approximately 60 % compared to the manufacturers calculation." Recommendation: **recalibrate after remounting, and at minimum every 5 years**; remounting caused larger coefficient changes than gradual aging ([PMID 28763716](https://pubmed.ncbi.nlm.nih.gov/28763716/)).
- **Chockalingam et al. (2002)**: "Do strain gauge force platforms need in situ correction?" — yes ([PMID 12443947](https://pubmed.ncbi.nlm.nih.gov/12443947/)).
- **Cedraro, Cappello & Chiari (2009)**: portable in-situ re-calibration system ([PMID 19111467](https://pubmed.ncbi.nlm.nih.gov/19111467/)).
- **Hsieh et al. (2011)**: in-situ static and dynamic calibration device ([PMID 21458995](https://pubmed.ncbi.nlm.nih.gov/21458995/)).
- **Koehler, Dhaher & Hansen (2014)**: portable 6-DOF load cell cross-validation ([PMID 24612723](https://pubmed.ncbi.nlm.nih.gov/24612723/)).

**Verification protocol:** (a) unloaded baseline drift over intended trial duration; (b) known dead-weight at a surveyed ≥3×3 grid including near-edge; (c) shear verification via pulley/known-angle load — the only way to see crosstalk; (d) impulse check with known mass, verify ∫F dt; (e) re-verify after **any** remounting.

---

## 6. Treadmills, 6-axis F/T, instrumented grips

### Instrumented treadmills

- **Bertec FIT5 dual belt:** two independent belts 1.75 × 0.5 m each; **Fx, Fy 2500 N and Fz 5000 N per belt**; speed 0–11.5 m/s; acceleration 0–25 m/s²; 6-component output per belt at **1000 Hz** ([Bertec treadmills](https://www.bertec.com/products/instrumented-treadmills)).
- **AMTI Tandem:** Fz **8800 N**, Fx/Fy 4500 N; **3 mm clearance between belts**; speed to 20 km/h; linearity/hysteresis ±0.2 %FSO; plate f_n 300 Hz but structure f_n **120 Hz** ([AMTI Tandem](https://www.amti.biz/product/tandem-instrumented-treadmill/)). AMTI also lists a **mobile instrumented pitching mound with three embedded Optima-BMS plates** — closest analogue to a golf-specific ground-interaction rig.

**Validation:** Fortune et al. validated dynamic COP on an AMTI treadmill using 68.0/102.1/136.1 kg loads at 0.5/0.75/1.0 m/s. Static COP error "similar to that of the ground-embedded force plates," but **"COP error appeared to vary systematically with weight and velocity and in the case of anteroposterior COP error, shear force"** ([PMID 28161106](https://pubmed.ncbi.nlm.nih.gov/28161106/)) — a crosstalk signature, the most citable caution about treadmill kinetics. Also [Tesio & Rota 2008, PMID 18388556](https://pubmed.ncbi.nlm.nih.gov/18388556/); [Dimiskovski 2017, PMID 28069392](https://pubmed.ncbi.nlm.nih.gov/28069392/).

### 6-axis F/T sensors (ATI)

ATI uses **silicon strain gauges** in a monolithic body, "a signal 75 times stronger than conventional foil gages," and withstands "overload of five to twenty times [the] sensing range" ([ATI F/T](https://www.ati-ia.com/products/ft/ft_productDesc.aspx)).

| Model        | Fx, Fy (±N) | Fz (±N) | Tx, Ty (±N·m) |
| ------------ | ----------- | ------- | ------------- |
| Axia80-M8    | 150         | 470     | 8             |
| Axia80-M20   | 500         | 900     | 20            |
| Axia90-M50   | 1000        | 2000    | 50            |
| Axia130-M125 | 2000        | 4000    | 125           |
| Axia130-M300 | 4000        | 6000    | 300           |

Same Wheatstone principle as a force plate, but silicon's piezoresistive gauge factor (~100+) vs foil constantan (~2) explains the 75× signal — why a 50 mm puck resolves what a 600 mm plate needs a compliant spring body to achieve, and why it fits inside a club handle.

### Instrumented golf grips

**Choi & Park (2020)** built a golf club with "a six-axis force-torque sensor connected to a custom-made axially separated grip," measuring internal forces from _both hands independently_ in nine professionals, plus 3D inverse dynamics for wrist/elbow/shoulder loads. **Right hand applied ~3× the torque of the left**; "the joint force and torque of the left arm tended to precede that of the right arm"; right-arm peak forces occurred around impact; "heuristic estimation methods based on club kinematics showed fair approximation" versus direct measurement ([_Sensors_, PMID 32630024](https://pubmed.ncbi.nlm.nih.gov/32630024/)).

**6-axis at the hands + 6-axis under each foot = a complete external-kinetics boundary condition for the golfer.** Pressure mats supply neither end.

### Supporting golf kinetics

- [Han et al. 2019, PMID 31042142](https://pubmed.ncbi.nlm.nih.gov/31042142/)
- [McHugh et al. 2024, _JSCR_: five metrics explained **85 % of ball-velocity variance**, one being **peak lead-foot GRF**; unskilled golfers showed delayed timing to peak lead-foot GRF, PMID 38088880](https://pubmed.ncbi.nlm.nih.gov/38088880/)
- [Hume, Keogh & Reid 2005, PMID 15896091](https://pubmed.ncbi.nlm.nih.gov/15896091/)
- [Li et al. 2026, predicting 3D GRF in the golf swing from IMUs via deep learning, PMID 41892082](https://pubmed.ncbi.nlm.nih.gov/41892082/)

---

## Gaps before publication

1. **Kistler numeric specs unverified** — product pages were down; sensitivities, ranges, natural frequencies, crosstalk need retrieval.
2. **Charge-amplifier Long/Medium/Short τ values** live in the 5233A/9865 manuals, not fetched.
3. **Tekscan** publishes almost nothing quantitative; Giacomozzi's RMSE < 2.5 % is the best sourced figure.
4. **BodiTrak** unreachable (TLS certificate errors on both domains).
5. **Kwon's GRF Systems** page (canonical COP-equation reference, ISB-indexed) failed on a self-signed certificate.
