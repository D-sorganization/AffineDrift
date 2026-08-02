# Motion Capture — Systems, Accuracy, Patents, and Estimation Dossier

Compiled 2026-08-02 for `articles/technology-motion-capture.qmd`. Research done via
Europe PMC, Crossref, Semantic Scholar, PubMed and FreePatentsOnline APIs (Google Patents
returned HTTP 503 throughout). Grading: **[V]** verified from primary source;
**[S]** secondary-sourced; **[X]** claim that research contradicts.

---

## 1. Optical baseline and the real accuracy ceiling

| System              | Sensor    | Full-res fps | Windowed fps   | Stated 3D resolution |
| ------------------- | --------- | ------------ | -------------- | -------------------- |
| Qualisys Miqus M1   | 1216×800  | 250          | 650 @0.5MP     | 0.14 mm @10 m        |
| Qualisys Miqus M3   | 1824×1088 | 340          | 360 @1MP       | 0.11 mm @10 m        |
| Qualisys Miqus M5   | 2048×2048 | 180          | **1400 @1MP**  | 0.07 mm @10 m        |
| Vicon Valkyrie VK26 | 26.2 MP   | 150          | —              | not published        |
| Vicon Valkyrie VK8  | 8.0 MP    | 500          | —              | not published        |
| Vicon Valkyrie VK6  | 6.1 MP    | 720          | **up to 2000** | not published        |

Vicon publishes no numeric accuracy figure; Qualisys does. Lab accuracy protocol: Eichelberger et al., _J Biomech_ 2016;49:2085-2088, [DOI](https://doi.org/10.1016/j.jbiomech.2016.05.007) **[V]**.

### Soft tissue artefact — the actual ceiling **[V]**

- **Fiorentino et al. 2017**, _Gait Posture_, [DOI](https://doi.org/10.1016/j.gaitpost.2017.03.033): mean skin-marker STA **0.3–5.4 cm**; hip angle errors 1.9° extension, 0.6° adduction, **5.8° internal rotation**; internal-external rotation ROM **reduced by up to 21.8°**.
- **Fiorentino et al. 2016**, [DOI](https://doi.org/10.1016/j.gaitpost.2016.09.011): hip joint centre error **16.6 ± 8.4 mm** (skin markers) vs 11.7 ± 11.0 mm (fluoroscopy).
- **Yoshida et al. 2022**, _Sensors_, [DOI](https://doi.org/10.3390/s22176502): scapular skin-marker median movement — acromial angle **30.4 mm**, root of scapular spine **53.1 mm**, inferior angle **70.0 mm**. Directly relevant to golf.
- **Xi et al. 2022**, [DOI](https://doi.org/10.3389/fbioe.2022.960063): lumbar STA L4-L5 **13.5 ± 6.5 mm** in flexion.
- **Roach et al. 2021**, [DOI](https://doi.org/10.1016/j.gaitpost.2021.02.004): skin markers underestimated ankle angles by up to **7.26°**, overestimated midfoot by **9.01°**.
- **Leardini, Chiari, Della Croce, Cappozzo 2005**, [PMID 15639400](https://pubmed.ncbi.nlm.nih.gov/15639400/): **STA frequency content overlaps true bone motion, so it cannot be filtered out**; in vivo only flexion/extension is reliably measurable from skin markers.

> A 0.07 mm camera feeding a marker set with 30–70 mm of skin motion is precision without accuracy.

---

## 2. Inertial systems

**Hardware:** Xsens/Movella MVN Awinda — up to 60 Hz full-body streaming, ~30 ms latency, 50 m range, up to 17 sensors **[V]**. APDM (now Clario) Opal V2R — up to 128 Hz, ~12 h streaming, raw-data access **[V]**. Noraxon myoMOTION now Ultium Motion.

> ⚠️ Gyro full-scale ranges and accuracy figures for all three vendors are behind gated knowledge bases. **Do not publish per-product dps or accuracy numbers without pulling the current datasheet.**

**Fusion algorithms:**

- **Mahony et al. 2008**, _IEEE TAC_ 53(5):1203-1218, [DOI](https://doi.org/10.1109/TAC.2008.923738) — rigorous SO(3) complementary filter; PI correction torque on rotation error, integral term estimating gyro bias. **[V]**
- **Madgwick, Harrison, Vaidyanathan 2011**, _IEEE ICORR_, [DOI](https://doi.org/10.1109/ICORR.2011.5975346) **[V]**. Note the modern xioTechnologies/Fusion library implements the **revised thesis chapter-7 algorithm, not the famous chapter-3 gradient-descent one** — a distinction almost universally missed.
- **VQF — Laidig & Seel 2023**, _Information Fusion_ 91:187-204, [DOI](https://doi.org/10.1016/j.inffus.2022.10.014): average RMSE **2.9°** vs **5.3–16.7°** for prior methods with one fixed parameter set. **[V]**

**The math:** orientation propagates via q̇ = ½ q ⊗ [0, ω] — exact for orientation _change_, no absolute reference, so gyro bias integrates into unbounded drift. The accelerometer supplies absolute inclination for only **two** of three rotational DOF and is corrupted by linear acceleration (a first-order problem in a downswing). The magnetometer supplies heading only if the local field is undistorted.

**Drift:** MEMS gyro error decomposes via Allan variance into angle random walk (°/√h) and bias instability (°/h); representative range 0.57 °/h down to 0.027 °/h across MEMS grades **[V]**. **Heading drift is unbounded** without magnetometer/GNSS/kinematic constraint.

**Magnetometer-free joint-constraint tracking** is the most promising route for golf (the club is a large ferromagnetic/conductive disturbance): Laidig, Weygers, Seel, _Sensors_ 2022, [PMID 36560219](https://pubmed.ncbi.nlm.nih.gov/36560219/) **[V]**.

**Sensor-to-segment calibration:** Picerno, Cereatti, Cappozzo 2006, [DOI](https://doi.org/10.1016/j.gaitpost.2006.09.040) **[V]**. Zhang et al. 2013, [PMID 23893094](https://pubmed.ncbi.nlm.nih.gov/23893094/): CMC > 0.96 in flexion/extension but markedly worse in ab/adduction and internal/external rotation, attributed explicitly to differing anatomical-frame definitions.

### Validation vs optical **[V]**

| Study                                                                      | System / task                                 | Result                                                                                         |
| -------------------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Zhang 2013                                                                 | Xsens vs Optotrak, gait/stairs                | Flex/ext **CMC > 0.96**; transverse much worse                                                 |
| Al-Amri 2018, [DOI](https://doi.org/10.3390/s18030719)                     | Xsens vs Vicon, walk/squat/jump               | Sagittal excellent; **within-day reliability degrades to poor during jumping**                 |
| Nijmeijer 2023, [PMID 37210922](https://pubmed.ncbi.nlm.nih.gov/37210922/) | Xsens vs Vicon, jump-landing/COD              | Sagittal **XCORR > 0.92**; "highly variable" in transverse and frontal                         |
| **Brice 2020**, [PMID 31512552](https://pubmed.ncbi.nlm.nih.gov/31512552/) | IMU vs optoelectronic, dynamic torso rotation | Absolute orientation RMSE **1–7%**; **thorax-pelvis relative angle RMSE 4–57%**                |
| Morrow 2017, [PMID 27918696](https://pubmed.ncbi.nlm.nih.gov/27918696/)    | IMU vs lab mocap, upper body                  | Trunk flex/ext **1.6 ± 1.1°**; shoulder elevation **6.8 ± 2.7°**; elbow flexion **8.2 ± 2.8°** |
| Goreham 2022, [PMID 35217243](https://pubmed.ncbi.nlm.nih.gov/35217243/)   | Low-cost Notch IMU                            | **0.10 ± 3.11°** to **44.95 ± 3.50°**; authors do **not** recommend the device                 |

> **Brice 2020 is the key golf entry:** single-segment orientation accuracy (1–7%) does not survive differencing into a relative thorax-pelvis angle (4–57%) — and thorax-pelvis separation _is_ the X-factor.

**Golf-specific:** Kim SE et al., _Sensors_ 2023;23(20):8433, [DOI](https://doi.org/10.3390/s23208433), n=36: **ICC 0.91–1.00**, Pearson **r 0.92–1.00**, Bland-Altman absolute mean differences **0.61–1.67°** **[V]**. Note the tension with Brice 2020 — worth discussing rather than glossing.

**Where IMU degrades:** (1) transverse plane consistently across every study; (2) high acceleration, invalidating the accelerometer gravity reference; (3) STA is _not_ solved by going inertial; (4) consumer hardware does not generalise from research-grade results.

---

## 3. Electromagnetic and high-speed video

### Polhemus specs — from the [primary datasheet PDF](https://files.polhemus.com/production/downloads/Technical_Comparison_Chart_with_VIPER.pdf) **[V]**

| Product       | Update rate       | Latency | Static pos. RMS | Static orient. RMS |
| ------------- | ----------------- | ------- | --------------- | ------------------ |
| Viper         | 240–960 Hz/sensor | 1–3 ms  | **0.38 mm**     | **0.10°**          |
| Fastrak       | 120 Hz ÷ #sensors | 4 ms    | 0.76 mm         | 0.15°              |
| Liberty       | 240 Hz/sensor     | 3.5 ms  | 0.76 mm         | 0.15°              |
| Patriot       | 60 Hz/sensor      | 18.5 ms | 1.52 mm         | 0.40°              |
| G4 (wireless) | 120 Hz/sensor     | <10 ms  | 2.0 mm          | 0.50°              |

Ascension products now sold by NDI as 3D Guidance and Aurora.

**Metal interference — corrected citation:** Milne AD, Chess DG, Johnson JA, King GJW, _J Biomech_ 1996;29:791-793, [DOI](<https://doi.org/10.1016/0021-9290(96)83335-5>) **[V via Crossref]**. Two physically distinct mechanisms often conflated: **eddy-current distortion** in non-ferrous conductors (what pulsed-DC mitigates) and **ferromagnetic distortion** in steel/iron — **pulsed-DC does not help here**.

**Golf EM decline drivers:** the implement itself is the distorter (steel/titanium clubheads, force plates, rebar); 10–20 ft tethers constrain a swing; sample rates lost to high-speed optical.

### High-speed video: blur is governed by exposure, not frame rate

Blur = v × t_exposure. At 45 m/s:

| Exposure | Blur    |
| -------- | ------- |
| 1 ms     | 45 mm   |
| 100 µs   | 4.5 mm  |
| 50 µs    | 2.25 mm |
| 22 µs    | 1.0 mm  |

Edgertronic SC1 supports 1/200,000 s → **0.23 mm blur at 45 m/s** **[V]**. The corollary is a brutal lighting budget. **Rolling vs global shutter** matters enormously — rolling shutter skews a 45 m/s clubhead within a single frame.

---

## 4. Biplanar videoradiography — the benchmark

**Method:** two calibrated X-ray source/detector pairs at 100–1000+ Hz. Marker-based descends from Roentgen Stereophotogrammetric Analysis (Selvik 1974). **Model-based tracking** generates digitally reconstructed radiographs from a CT-derived bone model and iteratively adjusts the model's 6-DOF pose until the DRR matches both radiographs.

| Study                                                                                | Joint / task              | Accuracy                                              |
| ------------------------------------------------------------------------------------ | ------------------------- | ----------------------------------------------------- |
| Brainerd et al. 2010, [PMID 20095029](https://pubmed.ncbi.nlm.nih.gov/20095029/)     | XROMM marker precision    | **±0.046 mm** optimal, ±0.084 mm in vivo              |
| Bey et al. 2006, [PMC3072582](https://pmc.ncbi.nlm.nih.gov/articles/PMC3072582/)     | Shoulder MBT              | RMS translation **<0.385 mm**, rotation 0.25–0.47°    |
| Bey et al. 2008, [PMC2538511](https://pmc.ncbi.nlm.nih.gov/articles/PMC2538511/)     | Patellofemoral            | Translation **<0.395 mm**, rotation 0.86–0.88°        |
| Anderst et al. 2008, [PMC2668117](https://pmc.ncbi.nlm.nih.gov/articles/PMC2668117/) | Tibiofemoral, **running** | 1.75±0.61° (FE), 1.44±1.23° (IE); 0.69±0.46 mm (ML)   |
| Akhbari et al. 2019, [PMC6612458](https://pmc.ncbi.nlm.nih.gov/articles/PMC6612458/) | Wrist                     | Translation bias **<0.1 mm**, rotation bias **<0.1°** |

> Against §1's 10–70 mm STA figures, DSX is **two to three orders of magnitude** tighter. That gap, not the frame rate, is the gold-standard argument.

**Radiation:** ~**0.03 mSv/second** for upper-extremity biplane **[V]**, plus a CT scan for MBT. Field of view tens of cm.

**Labs/software:** Brown XROMM, Pittsburgh Biodynamics Lab, Henry Ford (Bey). Autoscoper (open-source), XMALab. **C-Motion ceased DSX Suite development and support in December 2024** — material for anyone planning a build **[V]**.

**Golf: no peer-reviewed golf-swing biplanar videoradiography study exists.** A genuine, publishable gap.

---

## 5. Emerging sensing

**Depth cameras:** Azure Kinect DK — 1MP ToF + 12MP RGB, 32-joint SDK, **every depth mode caps at 30 fps** **[V]**. Jo et al. 2022, [PMC9785788](https://pmc.ncbi.nlm.nih.gov/articles/PMC9785788/): ICC **0.90–0.92** for visible segments, **0.53–0.66** under self-occlusion. At 30 fps the entire downswing-impact-follow-through window (~120–150 ms) spans **3–5 frames** — viable for gait, not golf.

**LiDAR:** Apple ARKit ~±1 cm on discrete objects, degrading to 10–20 cm at room scale. **No peer-reviewed validation for human motion capture** located.

**mmWave radar:** RF-Pose3D (SIGCOMM 2018) per-keypoint error **4.2/4.0/4.9 cm**; mmMesh (MobiSys 2021) **2.47 cm** average vertex error **[V]**. Works through occlusion, privacy-preserving. Centimetre error rules it out as a reference, not as a screening modality.

**Event cameras:** iniVation DAVIS346 at 120 dB dynamic range, **1 µs** temporal resolution. **No fixed exposure window means no motion blur** — structurally the right answer to the blur/lighting tradeoff. DHP19 (CVPR-W 2019) is the reference human-pose dataset. Production sport-biomechanics validation does not yet exist.

**Markerless video — the practical bridge.** All three leading pipelines converge on the same architecture (commodity RGB → 2D deep-learning detection → multi-view triangulation → OpenSim-constrained IK):

- **Theia3D** — Kanko et al., _J Biomech_ 2021;127:110665, [DOI](https://doi.org/10.1016/j.jbiomech.2021.110665) **[V]**; running kinematics _J Appl Biomech_ 2024, [DOI](https://doi.org/10.1123/jab.2023-0069). Joint-centre RMS below 2.5 cm for most joints (~3.6 cm worst) **[S]**.
- **OpenCap** — Uhlrich et al., _PLoS Comput Biol_: ≥2 smartphones at 60 Hz, HRNet + triangulation + 33-DOF OpenSim IK. Mean absolute joint-angle error **4.5°** (1.7–10.2° RMSE by joint); marker position ~32 mm; GRF error 6.2% BW **[V]**.
- **Pose2Sim** — Pagnon, Domalain, Reveret, _Sensors_ 2022;22(7):2712 **[V]**.

> The honest framing: these report **4–10° joint-angle RMSE**, _comparable to marker-based mocap's own STA-driven error_. The argument for markerless is not that it beats markers but that both are dominated by the same soft-tissue noise floor.

---

## 6. Golf specifics

**GEARS Golf — verified [V]:** **8 cameras at 1.7 MP, 360 fps**, claimed resolution **0.2 mm**, snap-on club mounts tracking grip and clubhead, **shaft deflection measured**, ball detection for impact location. Records "over 600 images per swing."

> ⚠️ **Correction:** the GEARS homepage advertises "500+" which reads as frame rate but is **frames per capture**, not fps. The golf product page gives the actual **360 fps**.

**Sportsbox AI [V]:** single smartphone, >30 keypoints. **The site states no frame rate, no accuracy figure, and cites no validation study.** A targeted Europe PMC search returned nothing. Combined with holding only pending PCT applications, a notable evidence gap for a product marketed on measurement accuracy.

**Swing Catalyst [V]:** now sells a **Markerless Motion Capture add-on** — evidence the markerless transition has reached commercial golf. No sampling rates published.

**AMM:** amm3d.com shows only "Launching Soon."

### Clubhead displacement per frame at 45 m/s

| Rate           | Δt      | Travel/frame |
| -------------- | ------- | ------------ |
| 240 Hz         | 4.17 ms | **18.8 cm**  |
| 360 Hz (GEARS) | 2.78 ms | **12.5 cm**  |
| 1000 Hz        | 1.00 ms | 4.5 cm       |
| 2000 Hz        | 0.50 ms | 2.25 cm      |
| 10,000 Hz      | 0.10 ms | 4.5 mm       |

Club-ball contact lasts ~0.4–0.5 ms — **shorter than a single 360 Hz frame interval; impact is invisible and must be inferred.** ⚠️ The 0.4–0.5 ms figure returned **no peer-reviewed source**; treat as **[S]**.

### Segment angular velocities — the brief's premise corrected **[X]**

Zhou JY et al., _Front Sports Act Living_ 2022, [DOI](https://doi.org/10.3389/fspor.2022.986281), [PMC9816382](https://pmc.ncbi.nlm.nih.gov/articles/PMC9816382/). Motion Analysis 8-camera at **240 Hz**, 11 pro + 5 amateur **[V]**:

| Phase          | Pelvis (°/s)     | Upper torso (°/s) | X-prime (°/s)  |
| -------------- | ---------------- | ----------------- | -------------- |
| Downswing      | **415.2 ± 32.9** | **551.7 ± 47.6**  | −183.4 ± 41.4  |
| Impact         | 288.8 ± 70.9     | 458.5 ± 73.0      | −170.3 ± 63.0  |
| Follow-through | 309.8 ± 42.1     | **929.2 ± 185.1** | −729.4 ± 160.8 |

> **Pelvis and thorax peak at 400–900 °/s, not 2000+ °/s.** No source for a 2000 °/s _body segment_ value was found. The high-frame-rate argument rests soundly on clubhead **linear** velocity instead.

Note the methodological point: a 2-marker-per-segment model (ASIS pair, acromion pair) cannot resolve full 3D segment orientation.

**Club tracking:** MacKenzie et al., _J Sports Sci_ 2018, [DOI](https://doi.org/10.1080/02640414.2018.1479133); MacKenzie & Boucher 2017, [DOI](https://doi.org/10.1080/02640414.2016.1157262); Umek et al., _Sensors_ 2017;17(4):916, [DOI](https://doi.org/10.3390/s17040916) — strain gauges validated against Qualisys **[V]**.

### X-factor and kinematic sequence

⚠️ **Cheetham's X-factor stretch chapter (_Science and Golf IV_, ~2002) is NOT DOI-registered** — Crossref has no record. Cite as a book chapter; **do not fabricate a DOI**. Verifiable alternative: Lynn SK et al., _Int J Golf Sci_ 2013;2:116-125, [DOI](https://doi.org/10.1123/ijgs.2013-0011) **[V]**.

**Is proximal-to-distal universal? The evidence says no [V]:**

- **McGuire TG et al., _Sports Biomech_ 2024**, [DOI](https://doi.org/10.1080/14763141.2024.2423282): golf short game showed "**irregular patterns across all distances**," only "**partial proximal-to-distal pattern at best**."
- **Scarborough et al.**, [PMC8459924](https://pmc.ncbi.nlm.nih.gov/articles/PMC8459924/): **eleven distinct curveball kinematic sequences**, **49% showing altered distal segment sequencing**.
- **Wukelic et al., _J Appl Biomech_ 2024**, [DOI](https://doi.org/10.1123/jab.2023-0167): trained players maintained consistent P-to-D; untrained youth did not — **sequence consistency is a trained outcome, not a biomechanical law.**

Honest framing: X-factor is empirically useful and reproducible _within_ a protocol, while cross-study comparability is undermined by definitional and timing heterogeneity.

### Screw-axis approaches

Vena Part 1/2 verified via Crossref (_Sports Engineering_ 2011;13:105-123 and 125-133) — **17 and 15 citations after 15 years, itself informative: the screw-axis approach has not displaced Euler-based practice.** Abstracts publisher-elided.

Kim W (2025), [DOI](https://doi.org/10.3390/jfmk10030315), [PMC12371979](https://pmc.ncbi.nlm.nih.gov/articles/PMC12371979/) — read in full **[V]**. ISA extracted by SVD alignment of consecutive frames; pitch h = (v·ω)/(ω·ω). Qualisys Oqus-300 at 300 Hz, 24 markers + 4 clusters, Kistler plate, downswing only. Proficient pitch bounded within **±0.0025 cm/rad**; novice **−0.025 to +0.01 cm/rad**. ⚠️ **n = 2**, and subject characteristics appear **internally inconsistent** (the "proficient" golfer is handicap 32 with 1 year experience; the "novice" is handicap 8 with 15 years).

**Why screw representations avoid Euler pathology, and the counterweight:** Chasles' theorem gives coordinate-frame-independent invariants — no ordered sequence, no gimbal singularity. But **Woltring's work on finite-helical-axis error sensitivity** shows FHA direction becomes ill-conditioned at small rotation angles — precisely where a golf swing spends its transition. Kim's paper does not address this conditioning issue.

---

## 7. Patents

### Foundational tracking

| No.                                                           | Title                                                                                        | Assignee      | Filed      | Granted    | Method                                                                                                                                                                    |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------- | ---------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [US3983474A](https://patents.google.com/patent/US3983474A/en) | Tracking and determining orientation of object using coordinate transformation means         | **Polhemus**  | 1975-02-21 | 1976-09-28 | **[V]** EM field **nutating about a pointing vector**; three orthogonal radiating + three sensing coils. The foundational AC magnetic tracker. Expired.                   |
| [US4849692A](https://patents.google.com/patent/US4849692A/en) | Device for measuring position/orientation in presence of metals utilizing DC magnetic fields | **Ascension** | 1986-10-09 | 1989-07-18 | **[V]** Pulsed DC: measure Earth field with transmitter off, energize axes sequentially, subtract. Explicitly enables operation near conductors. The eddy-current answer. |

### Optical

| No.                                                               | Title                                                                       | Assignee        | Granted | Method                                                                                                                                        |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------- | --------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| [US6324296B1](https://patents.google.com/patent/US6324296B1/en)   | Distributed-processing motion tracking, individually modulated light points | PhaseSpace      | 2001    | Active IR LEDs with unique pulse sequences encoding persistent ID — eliminates the marker-swap problem                                        |
| [US6437820B1](https://patents.google.com/patent/US6437820B1/en)   | Motion analysis system                                                      | Qualisys        | 2002    | Markers respond to optical trigger with coded on/off sequences                                                                                |
| [US6415043B1](https://patents.google.com/patent/US6415043B1/en)   | Determining the position of an object                                       | Qualisys        | 2002    | Single-camera 3D from known marker size vs measured image size                                                                                |
| [US8103055B2](https://patents.google.com/patent/US8103055B2/en)   | Detection of blobs in images                                                | OMG plc (Vicon) | 2012    | Ray-casting centroid refinement — Vicon's camera-side 2D detection core                                                                       |
| [US10375288B2](https://patents.google.com/patent/US10375288B2/en) | Motion capture system                                                       | Oxford Metrics  | 2019    | Cameras with onboard accelerometers/temperature sensors; reprioritizes processing by detected vibration, times recalibration to thermal drift |
| [US11662417B2](https://patents.google.com/patent/US11662417B2/en) | Active marker device                                                        | Oxford Metrics  | 2023    | LED patterns distinguishable under arbitrary rotation — spatial rather than temporal ID coding                                                |
| [US7643158B2](https://patents.google.com/patent/US7643158B2/en)   | Synchronizing multiple devices                                              | Motion Analysis | 2010    | Time/frequency-division sync of ≥4 imaging devices                                                                                            |
| [US9019349B2](https://patents.google.com/patent/US9019349B2/en)   | Automated collective camera calibration                                     | NaturalPoint    | 2015    | Switchable IR-filter modes self-calibrating from a moved reference marker                                                                     |

### Inertial

| No.                                                               | Title                                    | Assignee | Granted | Method                                                                                                                                                              |
| ----------------------------------------------------------------- | ---------------------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [EP1970005B1](https://patents.google.com/patent/EP1970005B1/en)   | Motion tracking using a calibration unit | Xsens    | 2012    | Derives segment lengths **and** sensor-to-segment offsets by statistical fitting against skeletal and mechanical constraints — **without requiring a rigid N-pose** |
| [US12034909B2](https://patents.google.com/patent/US12034909B2/en) | Any pose motion capture calibration      | Movella  | 2024    | Extends calibration to any starting pose by fusing IMU data with camera imagery of visual markers                                                                   |

### Golf and markerless

| No.                                                                                   | Title                                             | Assignee                       | Granted                                 | Method                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------ | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [US8616989B2](https://patents.google.com/patent/US8616989B2/en)                       | Athletic motion analysis and instruction          | **K-Motion Interactive**       | 2013                                    | K-Vest's foundational patent. Body-mounted inertial sensors → swing metrics, colour-coded "cages" showing deviation from ideal limits, and **automatic prescription of a training-drill regimen**. Claims cover sensor-to-prescription, not just capture. Continuations: US9770658, US10456676, US10463958, US10569134, US10576373, US11000765, US11033776 |
| [US8471848B2](https://patents.google.com/patent/US8471848B2/en)                       | Tracking three dimensional objects                | Organic Motion                 | 2013                                    | Volumetric markerless: shape-from-silhouette onto virtual 2D slices, fit to a virtual skeleton                                                                                                                                                                                                                                                             |
| [EP3449463A1](https://patents.google.com/patent/EP3449463A1/en)                       | Motion analysis of thermally distinct objects     | Simi Reality Motion            | pub. 2019                               | **Thermographic** markerless segmentation — subjects separated by heat signature                                                                                                                                                                                                                                                                           |
| [US20130190098A1](https://patents.google.com/patent/US20130190098A1/en)               | Golf club head measurement system                 | WAWGD dba **Foresight Sports** | application (EP2815384B1 granted)       | Stereoscopic cameras + fiducial markers on the club face → orientation, path, impact location                                                                                                                                                                                                                                                              |
| US2026/0143244 etc.                                                                   | Markerless motion capture                         | **Theia Markerless**           | **applications only — no grant**        | —                                                                                                                                                                                                                                                                                                                                                          |
| [WO2023205423A1](https://patents.google.com/patent/WO2023205423A1/en), WO2022251680A1 | Monocular pose estimation; biomechanical analysis | **Sportsbox AI**               | **PCT applications only — no US grant** | —                                                                                                                                                                                                                                                                                                                                                          |

### Structural findings

- **GEARS: no patents found under any corporate-name assignee search** — a genuine negative finding, suggesting licensed or off-the-shelf optical tracking rather than owned foundational IP.
- **Theia Markerless and Sportsbox AI hold no granted patents** — only pending applications.
- **Why markerless exploded:** not "a foundational patent expired," but that the foundational IP of the _hardware_ generation is now expired or narrow, **while the new wave's enabling technology — deep-learning pose estimation — is open general-purpose computer-vision research rather than patented hardware.** The absence of granted patents at Theia and Sportsbox is direct evidence.
- ⚠️ **Not researched:** mocap patent litigation. Do not assert none occurred.

---

## 8. Advanced estimation

**Filtering:** differentiation multiplies Fourier components by |jω|ⁿ. Winter's residual analysis and zero-lag dual-pass Butterworth remain standard. Woltring's **GCVSPL** (quintic smoothing spline, smoothing parameter by generalized cross-validation) smooths and differentiates simultaneously without manual cutoff selection — _Adv Eng Software_ 1986;8:104-113, [DOI](<https://doi.org/10.1016/0141-1195(86)90098-7>) **[V]**. Savitzky-Golay 1964, [DOI](https://doi.org/10.1021/ac60214a047) **[V]**.

Useful modern datapoint on **sampling rate ≠ usable bandwidth**: Carretier et al., _Sensors_ 2026, [DOI](https://doi.org/10.3390/s26020662) — appropriate cutoffs of **13 Hz for video but 39 Hz for IMU** channels in the same trial **[V]**.

**Kalman smoothing — the key applied paper:** De Groote F, De Laet T, Jonkers I, De Schutter J, "Kalman smoothing improves the estimation of joint kinematics and kinetics in marker-based human gait analysis," _J Biomech_ 2008;41(16):3390-3398, [DOI](https://doi.org/10.1016/j.jbiomech.2008.09.035) **[V]** — 10-segment 21-DOF model; **joint-position errors reduced >50%**, **joint-moment errors reduced >35%** vs global optimization and causal Kalman filtering.

Multibody EKF/UKF: Cuadrado 2012, Naets 2014, Torres-Moreno 2016. Recent: Kortelainen et al., _Ann Biomed Eng_ 2025, [DOI](https://doi.org/10.1007/s10439-025-03807-x) — adaptive unscented Kalman smoother for IMU data in OpenSim **[V]**.

**Dynamic consistency:** OpenSim RRA (Thelen & Anderson 2006, [DOI](https://doi.org/10.1016/j.jbiomech.2005.02.010)). Best modern benchmark: **Fox AS, _R Soc Open Sci_ 2024;11(5), [DOI](https://doi.org/10.1098/rsos.231909)** — compares RRA, MocoTrack and AddBiomechanics on running; **MocoTrack best at driving residuals to near-zero, at the cost of substantially longer computation** **[V]**.

**OpenSim Moco:** Dembia et al., _PLOS Comput Biol_ 2020;16(12):e1008493, [DOI](https://doi.org/10.1371/journal.pcbi.1008493) **[V]**. Direct collocation enforcing dynamic consistency by construction; supports tracking and **predictive** modes. Verified runtimes: predictive squat-to-stand ~3 min; walking tracking ~3.5 min; tracking with foot-ground contact **~130 min**. ⚠️ **No golf-specific Moco application found.**

**Uncertainty quantification — with numbers:**

- **Myers, Laz, Shelburne, Davidson**, _Ann Biomed Eng_ 2015;43(5), [DOI](https://doi.org/10.1007/s10439-014-1181-7) **[V]**: probabilistic OpenSim framework; combined uncertainty bounds **2.7–6.4° in joint kinematics, 2.7–8.1 N·m in joint moments, 35.8–130.8 N in muscle forces.**
- **Stagni, Leardini, Cappozzo, Benedetti, Cappello**, _J Biomech_ 2000, [DOI](<https://doi.org/10.1016/s0021-9290(00)00093-2>) **[V]**: a **30 mm anterior** hip-joint-centre mislocation → **~−22%** error in the flexion/extension moment; 30 mm lateral → ~−15%. **Read alongside the 16.6 ± 8.4 mm skin-marker HJC error, this is the most compelling UQ argument available.**

**Inverse kinematics:** Lu TW, O'Connor JJ, _J Biomech_ 1999;32(2):129-134, [DOI](<https://doi.org/10.1016/s0021-9290(98)00158-4>) **[V]**. Important nuance: Pomarat et al., _J Biomech_ 2023, [DOI](https://doi.org/10.1016/j.jbiomech.2023.111514) **[V]** — adding joint kinematic constraints can, in some model configurations, **increase** intersegmental moment error. **MKO is not a universal improvement.**

⚠️ **No peer-reviewed golf-specific sampling-rate recommendation exists.** Verified anchors from published golf studies: Liu et al. 2025 — **250 Hz** mocap with **1000 Hz** force plate; Zhou 2022 — **240 Hz**; Kim 2025 — **300 Hz**; GEARS — **360 fps**.

---

## 9. Corrections and do-not-publish-without-verifying

**Three claims contradicted or unsupported:**

1. **"2000+ °/s segment rotation"** — verified values are pelvis **415 °/s**, upper torso **552 °/s** in the downswing. No source for a 2000 °/s _body segment_ value found.
2. **"GEARS ~500 Hz"** — GEARS is **360 fps**; "500+" is frames _per capture_.
3. **Kinematic sequence as a universal proximal-to-distal law** — contradicted by McGuire 2024, Scarborough, and Wukelic 2024.

**Unverifiable — do not fabricate:** Cheetham's X-factor stretch chapter has no DOI; Vena Part 1/2 abstracts are publisher-elided; club-ball contact duration (~0.4–0.5 ms) has no peer-reviewed source; inventor names on all patents in §7.

**Gated:** Xsens/Noraxon/Clario gyro-range datasheets; Milne 1996 distance-vs-error curves; Pose2Sim precise RMSE.

**Genuine negative findings:** no golf-swing biplanar videoradiography study; no independent published validation of Sportsbox AI; no granted patents for Theia, Sportsbox, or GEARS; no golf-specific Moco or PINN application.
