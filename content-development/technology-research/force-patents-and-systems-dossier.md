# Force Measurement — Patents, Commercial Systems, and Estimation Dossier

Compiled 2026-08-02 for `articles/technology-force-measurement.qmd`. Patent records
retrieved from FreePatentsOnline (Google Patents returned HTTP 503 throughout);
`patents.google.com` URLs are canonical constructions for reader convenience and were
not individually verified.

---

## 1. Commercial golf force / pressure systems

**The load-bearing distinction:** a pressure mat resolves only the _normal_ traction distribution across sensels. It can integrate to give total Fz and locate CoP, but is structurally incapable of resolving **shear (Fx, Fy)** or the **free moment (Tz)** — those require instrumented tangential load transfer (strain-gauged shear webs or multi-axis piezo elements).

### Swing Catalyst (Initial Force AS, Norway)

| Product                  | Measures                                                                                                              | Rate        | Specs                                       |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------- |
| **Balance Plate**        | **Pressure only.** Distribution, CoP, trace, heat map. No shear, no torque.                                           | **150 Hz**  | >2000 sensors; 98.6 × 50.5 × 2.2 cm; 5.9 kg |
| **Dual Pressure Plates** | **Pressure only.** Per-foot pressure, heat map, balance point speed, stance width.                                    | **130 Hz**  | 52 × 31.75 cm/plate; 2.5 kg each            |
| **Motion Plate**         | **Force + pressure.** Vertical force, **horizontal shear (Y-axis)**, **torque**                                       | **1000 Hz** | max vertical 10,000 N, max shear 5,000 N    |
| **Dual Motion Plates**   | **Force + pressure, per foot.** Shear (Y), vertical, **twisting force (free moment)**, 3D force vectors, per-foot CoP | **1000 Hz** | 50 × 60 × 9 cm                              |
| **Dual Force Plates**    | **True 6-axis. Fx, Fy, Fz, Mx, My, Mz**                                                                               | **1000 Hz** | combined 14,000 N; **$12,500 ex-tax**       |

Product pages: https://swingcatalyst.com/products

**Foundational patent — clearest public statement of the architecture.** **US 2011/0260890 A1, "Motion Analysis Apparatus," INITIAL FORCE AS, filed 6 Nov 2009** — https://www.freepatentsonline.com/y2011/0260890.html · https://patents.google.com/patent/US20110260890A1/en. Family EP2362803B1, WO2010/052468. Verbatim: _"a platform upon which the subject stands… force sensors arranged to measure forces exerted on the platform by the subject in three dimensions (along X, Y and Z axes) **and** a pressure sensitive mat arranged to collect pressure data relating to the position of each foot… software for determining… **torque and angular momentum around different axes, using both the force and pressure data**. In a golfing scenario, the apparatus can be used to analyze the motion of a subject whilst making a golf swing."_

> The pressure mat's role is _foot localisation_ — it supplies the moment arm; the 3D force sensors supply the force. **Neither alone yields per-foot torque.** This is the single best citation for the pressure-vs-force point.

### BodiTrak / XSENSOR

Capacitive pressure mapping. Both boditrak.com and boditraksports.com now fail TLS validation (certificates for unrelated domains), consistent with the brand folding into XSENSOR. **Acquisition unconfirmed from primary sources.**

XSENSOR patent estate (all normal-load-at-intersection sensing — **no shear channel anywhere**):

- **US 8,121,800** — "Capacitative node measurement in a capacitative matrix pressure inducer," filed 25 Apr 2007, issued 21 Feb 2012 — https://www.freepatentsonline.com/8121800.html
- **US 8,272,276** — "Dielectric textured elastomer in a pressure mapping system," filed 6 May 2009
- **US 8,544,336** — "Sealed conductive grid capacitive pressure sensor"
- **US 12,089,952** — "Foot sensor and other sensor pads," priority 28 Jul 2020, issued 17 Sep 2024
- Also US 8,893,561, US 9,404,818, US 9,320,665, US 9,486,160

### Other systems

- **TPI** is a **certification and education body, not a hardware manufacturer.** mytpi.com makes no mention of specific force/pressure technology. Do not describe "TPI mats" as a product.
- **K-Vest / K-Motion** is **inertial kinematics, not kinetics** — body-worn IMUs reporting segment orientations, rotational velocities, kinematic sequence. **Measures no force and no pressure.** Manufacturer domains now resolve to unrelated businesses; specs unverified.
- **GEARS** (https://www.gearssports.com/) is **full-body optical motion capture** — "500+ frames per capture," "50+ metrics." A kinematic instrument; no vendor documentation of force output or inverse-dynamics methodology. **Do not assert GEARS computes kinetics.**

### Reference force plates

| Vendor      | Technology                                                                                                           | Notes                                                                                                 |
| ----------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **AMTI**    | Strain gauge — built the **first commercially available strain gauge force plate**, 1976, Boston Children's Hospital | Optima-SC: max 1200 Hz/channel, 16-bit DSP / 14-bit resolution, 1000 Hz 2-pole Butterworth anti-alias |
| **Bertec**  | Strain gauge, custom electronics                                                                                     | 6 components internally sampled at **1000 Hz**                                                        |
| **Kistler** | **Piezoelectric quartz.** Founded 1959, Winterthur; built on Walter P. Kistler's 1950 charge-amplifier patent        | 8 raw charge outputs → 6 components; 9286-series standard for sports biomechanics                     |

> **Practical implication:** a golf swing compresses meaningful kinetics into a 0.2–0.3 s downswing with skill-discriminating torque differences of ~2–3 N·m. A 130–150 Hz pressure mat gives ~26–45 samples across the downswing and no torque channel. A 1000–1500 Hz force plate gives 200–450 samples plus Tz. These answer different questions and should never be pooled without stratification.

---

## 2. Patents

### 2.1 Kistler (piezoelectric)

| Number           | Title                                                                   | Filed       | Granted    | Notes                                                                                                                                                                                                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------- | ----------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 4,974,454** | Force transducers for fitting in force plates                           | 20 Apr 1989 | 4 Dec 1990 | Radial mounting flange allows insertion into the base plate after signal-line connection, then welding/brazing — _"the transducer with its signal lines thus becomes an integral part of the base plate and is sealed completely against outside influences."_ https://www.freepatentsonline.com/4974454.html |
| **US 4,009,447** | Amplifier arrangement with zeroing device for piezoelectric transducers | —           | —          | Charge-amplifier drift compensation — the enabling technology for quasi-static piezo measurement                                                                                                                                                                                                              |
| **EP 0342253**   | Mounting of a force transducer in a measuring platform                  | —           | —          |                                                                                                                                                                                                                                                                                                               |
| **EP 0360923**   | Measuring platform                                                      | —           | —          |                                                                                                                                                                                                                                                                                                               |
| **DE 2637952**   | Force measuring element for forming a force measuring platform          | —           | —          | Early foundational filing                                                                                                                                                                                                                                                                                     |

### 2.2 AMTI (strain gauge)

| Number            | Title                                                                                          | Filed           | Granted         | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------- | --------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 4,493,220**  | **Force measuring platform and load cell therefor using strain gages to measure shear forces** | **23 Nov 1982** | **15 Jan 1985** | The foundational AMTI patent. _"A top plate 12 is supported on tubular load cells 16. The load cells have strain gages to measure the strain due to the **horizontal shear forces**. The 'shear' strain gages also measure **moments about the Z axis** when properly placed in a bridge circuit."_ **The cleanest statement in the patent literature of why a force plate can measure shear and free moment and a pressure mat cannot.** https://www.freepatentsonline.com/4493220.html |
| **US 4,398,429**  | Force platform construction and method of operating same                                       | —               | —               | Earlier construction patent                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **US 5,400,661**  | Multi-axis force platform                                                                      | —               | —               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **US 5,814,740**  | Multi-axis force platform                                                                      | 24 Mar 1995     | 29 Sep 1998     | Slotted rigid block forming deflectable beams; **magnetic sensors** — a departure from strain gauges                                                                                                                                                                                                                                                                                                                                                                                     |
| **US 9,255,859**  | Force platform system                                                                          | 14 Oct 2011     | 9 Feb 2016      | Platforms self-identify by force-signal sequence; nonvolatile calibration memory. **Directly relevant to dual-plate golf setups**                                                                                                                                                                                                                                                                                                                                                        |
| **US 9,459,173**  | System and method for three dimensional calibration of force plates                            | —               | —               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **US 10,704,973** | Data acquisition device and method of timing data sampling                                     | —               | —               | Sync/timing                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

### 2.3 Bertec — inventor Necip Berme

The most prolific individual inventor in the field; 50+ patents.

| Number              | Title                                                                          | Filed                                | Granted     | Notes                                                                                                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------ | ------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 6,295,878**    | Particular strain gage orientation for a six component load measurement device | 13 Dec 1999                          | 2 Oct 2001  | Six gauges on a tubular element; first set ≤60° from long axis, second 45–120° to the first                                                                                                       |
| **US 6,354,155**    | Multi-component force and moment measuring platform and load transducer        | 2 Jun 1999                           | 12 Mar 2002 | _"each cell measures all force and moment components (Fx, Fy, Fz, Mx, My, Mz)"_; **plates can be tiled into arrays** — the architectural basis for dual/multi-plate installations                 |
| **US 8,544,347**    | Force measurement system having a plurality of measurement surfaces            | 11 Jan 2012                          | 1 Oct 2013  | Two surfaces separated by a gap, each on its own load cell, **plus a third load cell measuring load transferred _between_ them** — explicit hardware attack on the dual-surface partition problem |
| **US 11,790,536**   | **Swing analysis system**                                                      | 3 Oct 2022; priority **11 Oct 2019** | 17 Oct 2023 | Bertec's golf patent: motion capture of body segments plus head/face, hand/fingers and the manipulated object                                                                                     |
| **US 10,126,186**   | Load transducer correcting measurement errors in output forces/moments         | —                                    | —           | Crosstalk correction                                                                                                                                                                              |
| **US 2012/0271565** | Force Measurement System Having Inertial Compensation                          | —                                    | —           | The instrumented-treadmill/moving-plate problem                                                                                                                                                   |
| **US 11,705,244**   | Force and/or motion measurement system that includes at least one camera       | —                                    | —           | Optical + force fusion                                                                                                                                                                            |

### 2.4 Tekscan (piezoresistive)

| Number           | Title                                                                 | Filed       | Granted     | Notes                                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------- | ----------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 4,856,993** | Pressure and contact sensor system for measuring dental occlusion     | 2 Oct 1987  | 15 Aug 1989 | **The founding Tekscan patent.** Orthogonal electrode sets on flexible sheets separated by _"a thin, pressure-sensitive resistive coating such as molybdenum disulphide"_ |
| **US 5,033,291** | **Flexible tactile sensor for measuring foot pressure distributions** | 11 Dec 1989 | 23 Jul 1991 | The F-Scan ancestor; perimeter trimmable for custom foot shapes                                                                                                           |
| **US 6,032,542** | Prepressured force/pressure sensor                                    | 22 Jun 1998 | 7 Mar 2000  | Evacuated airtight seal so **atmospheric pressure supplies controlled preload** — addressing low-load nonlinearity                                                        |

> Every Tekscan sensel is a resistance varying with _normal_ load at an electrode intersection. **No shear channel exists.**

### 2.5 Novel GmbH / pedar / emed — Peter Seitz

| Number           | Title                                                                  | Filed       | Granted    | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ---------------- | ---------------------------------------------------------------------- | ----------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 4,836,033** | **Capacitive measuring assembly for determining forces and pressures** | 30 Sep 1987 | 6 Jun 1989 | Inventor Peter Seitz. _"The main surface being movable **both perpendicular and parallel** relative to the remaining surfaces so that… there can be measured or eliminated **both the forces that act perpendicularly**… **and the forces that act parallel with the capacitor surfaces**."_ **One of very few pressure-sensor patents claiming shear sensing** — the exception proving the rule, though commercial pedar/emed report normal pressure only. https://www.freepatentsonline.com/4836033.html |

### 2.6 Golf-specific force patents

| Number              | Title                                                                         | Applicant         | Filed                           | Notes                                                                                                         |
| ------------------- | ----------------------------------------------------------------------------- | ----------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **US 2011/0260890** | Motion Analysis Apparatus                                                     | Initial Force AS  | 6 Nov 2009                      | See §1                                                                                                        |
| **US 11,944,891**   | Selection of a sports club, racket or bat using ground pressure forces        | Swing Balance LLC | 15 Nov 2021, granted 2 Apr 2024 | Club-fitting from a pressure mat; computes a "load factor" for club selection                                 |
| **US 11,504,581**   | Systems and methods for integrating measurements captured during a golf swing | **TaylorMade**    | priority 6 Sep 2019             | Multi-device sensor fusion; selects most accurate readings across heterogeneous sensors. Family US 11,583,729 |

### 2.7 Instrumented treadmills

| Number            | Title                       | Assignee      | Filed                | Granted     | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------- | --------------------------- | ------------- | -------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US 6,878,100**  | **Force sensing treadmill** | **U.S. Army** | 21 Mar 2003          | 12 Apr 2005 | The canonical split-belt design: _"a pair of treadmills mounted in tandem, each on its own independent force platform… separated by a minimal gap, provides a plurality of signals representing **forces in the x-axis, y-axis, and z-axis, and torques about these three axes** enabling separate information to be collected from the left and right foot… the entire time that either foot is in contact with the belt."_ **The hardware answer to double-support indeterminacy.** |
| **US 12,629,558** | Treadmill with force plate  | TECHNOGYM     | priority 20 Feb 2023 | 19 May 2026 | Load cells beneath each side                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

### 2.8 Smart shoes — Nike and Adidas

**Honest finding: neither estate is primarily about force measurement.**

- **Nike:** searches return predominantly the **autolacing motor** family (US 11,819,087, US 12,685,369) — force-_directing_ structures routing actuator load, **not measurement patents**. Also US 8,535,169 "Golf ball with indicia to indicate imparted shear force" — a _ball-marking_ patent, easy to miscite.
- **Adidas:** the **miCoach / Portable Fitness Monitoring** family (US 8,033,959, US 8,715,139, US 9,077,465, US 11,376,468…). Closest to golf-relevant: **US 2020/0146397 / EP 3649883** "Individual Traction Profiles for Footwear" — traction being exactly the torque-transmission variable Worsfold identified.
- The Adidas_1 microprocessor shoe (2005) and Nike Adapt platform are actuation/adaptive-cushioning systems, **not measurement instruments**. No golf-shoe-specific force-sensing patent found from either brand.

---

## 3. GRF estimation without force plates

### 3.1 Kinematics-only Newton-Euler

**Ren L, Jones RK, Howard D (2008).** Whole body inverse dynamics over a complete gait cycle based only on measured kinematics. _J Biomech_ 41(12):2750–2759. PMID 18672243 — https://pubmed.ncbi.nlm.nih.gov/18672243/

Introduced the **Smooth Transition Assumption (STA)** to resolve double-support indeterminacy: trailing-limb vertical GRF decays smoothly to zero while the leading limb's rises. Findings: reasonably accurate in the sagittal plane, poorer in other planes; optimal filtering at **4.5 Hz**; _"errors in the mass properties of body segments can play a crucial role."_

### 3.2 IMU-based

**Karatsidis A et al. (2017).** Estimation of Ground Reaction Forces and Moments During Gait Using Only Inertial Motion Capture. _Sensors_ 17(1):75. PMID 28042857 — https://pubmed.ncbi.nlm.nih.gov/28042857/

| Component          | ρ         | relative RMSE |
| ------------------ | --------- | ------------- |
| **Vertical force** | **0.992** | **5.3%**      |
| Anterior force     | 0.965     | 9.4%          |
| Sagittal moment    | 0.933     | 12.4%         |
| Lateral force      | 0.862     | 13.1%         |
| Transverse moment  | 0.826     | 18.2%         |
| **Frontal moment** | **0.710** | **29.6%**     |

> **The gradient:** vertical force nearly solved; frontal-plane moment barely usable. The ordering vertical ≫ anteroposterior > mediolateral ≫ moments recurs in every study.

### 3.3 Machine learning — the golf result

**Li J, Wei R, Xie Q, Wu C, Kim YH (2026).** Prediction of Three-Dimensional Ground Reaction Forces in the Golf Swing Using Wearable IMUs and Biomimetic Deep Learning Models. _Biomimetics_ 11(3):159. PMID 41892082 — https://pubmed.ncbi.nlm.nih.gov/41892082/

Bilateral hip/knee/ankle angles from IMUs → 3D GRF. Best model **TCN-BiGRU**: **R² = 0.94 ± 0.02**, MRE = 0.044, NRMSE = 0.064. _"The full bilateral lower-limb configuration yielded the best overall performance, whereas using only the lead leg provided a cost-efficient alternative."_ **Vertical components again most reliable.**

---

## 4. Inverse dynamics with force plates

### 4.1 Bottom-up vs top-down

**Bottom-up** starts at the foot with measured GRF/CoP/free moment, works proximally; boundary condition is _measured_, but error grows proximally — the hip moment is least reliable. **Top-down** starts at a free distal end with known load, requires no force plate; error accumulates toward the foot.

### 4.2 Residual forces and moments

With both a measured GRF and a full kinematic model, the system is **over-determined**; the discrepancy is absorbed by a fictitious 6-DOF **residual actuator** at the pelvis. Sources in rough order of magnitude: BSIP error, soft tissue artefact, marker noise and double differentiation, **force-plate/mocap spatial misalignment and time sync error**, model simplification.

OpenSim's **Residual Reduction Algorithm (RRA)** adjusts torso CoM and kinematics within tolerance. The commonly cited rule of thumb — residual forces below ~5% of peak external force, residual moments below ~1% of (peak external force × model height) — **should be verified against current OpenSim documentation** (Confluence wiki migrated; deep links 404).

### 4.3 Double-support indeterminacy — the golf-critical problem

A single plate measures the _net_ wrench of everything touching it. Two feet on one plate: 12 unknowns (two 6-component wrenches), 6 equations. **Under-determined by 6.**

**Why golf is worse than gait:** in walking, double support is ~20% of the cycle and STA models a rolling transfer. **In golf both feet are on the ground for essentially the entire swing**, and the whole phenomenon of interest — Front Foot/Reverse styles, the lead-foot-GRF-moment / trail-foot-pivoting-moment division, inter-leg angular impulse coordination — _is_ the per-foot partition.

Solutions in descending rigour:

1. **Two independent plates, one per foot.** Fully determined. The only method recovering per-foot shear and free moment.
2. **Pressure mat spanning both feet partitioning a single plate's net force.** Partitions Fz and CoP exactly; **does not partition shear or free moment.** Exactly the Initial Force architecture and exactly its limit.
3. **Optimisation-based decomposition** — unique answer, but an artefact of the chosen cost function.
4. **Smooth Transition Assumption** — **invalid for golf**; there is no rolling transfer between limbs.

### 4.4 Golf-specific challenges

**Closed kinematic chain:** both hands grip the club, forming a loop. Nesbit & Serrano handle this with two separate models to avoid propagating through the closed loop. **High rates, short duration:** kinematic sampling at 110–200 Hz gives 22–90 frames across the downswing — sparse for double differentiation.

---

## 5. Books and standards

- **Winter DA.** _Biomechanics and Motor Control of Human Movement_, 4th ed., Wiley 2009. ISBN 9780470398180. Source for BSIP regression tables, link-segment inverse dynamics, residual analysis for filter cutoff selection, and the force platform chapter.
- **Zatsiorsky VM.** _Kinetics of Human Motion_, Human Kinetics 2002. The most rigorous treatment of forces and moments as **screws/wrenches**, joint force vs joint moment decomposition, and indeterminacy problems.
- **de Leva P (1996).** Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters. _J Biomech_ 29(9):1223–1230. PMID 8872282 — **the single most-cited BSIP source in modern motion analysis.** Population caveat: young adult Caucasian subjects.
- **Robertson DGE et al.** _Research Methods in Biomechanics_, 2nd ed., Human Kinetics 2014. **Chapter 4 (Forces and Their Measurement) is the best textbook treatment of force plate construction, calibration, CoP computation and free-moment extraction.**
- **Nigg BM, Herzog W (eds.).** _Biomechanics of the Musculo-skeletal System_, Wiley. Strongest on the shoe-surface interface.

### ISB standards

| Citation                                                                                                                                                   | Details                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **Wu G, Cavanagh PR (1995).** ISB recommendations for standardization in the reporting of kinematic data. _J Biomech_ 28(10):1257–1261. PMID 8550644       | Global reference frame conventions        |
| **Wu G et al. (2002).** ISB recommendation on definitions of joint coordinate system — Part I: ankle, hip, spine. _J Biomech_ 35(4):543–548. PMID 11934426 | Lower-limb JCS definitions                |
| **Wu G et al. (2005).** Part II: shoulder, elbow, wrist, hand. _J Biomech_ 38(5):981–992. PMID 15844264                                                    | Essential for the closed upper-limb chain |

### Force metrology

General standards are **ISO 376** and **OIML R 60**. **There is no ISO or ASTM standard specifically governing biomechanical force platform performance or in-situ verification** — a genuine, citable gap, which is why the verification literature exists as ad hoc academic practice.

### Sampling and filtering

- **1000 Hz is the de facto standard** for force plate acquisition. Force is typically sampled 5–10× faster than kinematics (110–200 Hz in golf studies); misalignment is a leading source of residual moments.
- **Cutoff selection is task-specific and consequential.** Ren et al. found 4.5 Hz optimal for kinematics-driven whole-body inverse dynamics in gait.
- **Golf-specific warning:** the free moment Tz is a small signal (6–19 N·m) riding on large forces, and is the most filter-sensitive channel. **Over-filtering erases exactly the skill-discriminating trail-foot torque differences** (15.8 vs 18.2 N·m).

---

## 6. Additional golf kinetics results

- **McNitt-Gray JL et al. (2013).** Regulation of reaction forces during the golf swing. _Sports Biomech_ 12(2):121–131. PMID 23898685. n=12, 6-iron, **1200 Hz** dual plates. Skilled players **regulate shot distance by scaling the magnitude of the resultant horizontal reaction force with minimal modification of force _direction_** — peak lead-leg horizontal force **5% less (p<0.05)** for reduced distance. **Direction-invariant, magnitude-scaled control.**
- **Peterson TJ, Wilcox RR, McNitt-Gray JL (2016).** Angular Impulse and Balance Regulation During the Golf Swing. _J Appl Biomech_ 32(4):342–349. PMID 26958870. **Net angular impulse from both legs greater with driver than 6-iron.** Balance constraint: **linear impulse perpendicular to the target line remained near zero.**
- **Peterson TJ, McNitt-Gray JL (2019).** Modified address positions. _J Appl Biomech_ 35(1):25–31. PMID 30080427. **Total angular impulse conserved across conditions.**
- **Peterson & McNitt-Gray (2018).** _J Biomech_ 77:26–33. PMID 29945785. _"The majority of the 3D support moment was produced by NJMs about an axis perpendicular to the leg planes"_ — legs behave largely as planar linkages inside a rotational task.
- **Wells JET et al. (2018).** _J Sports Sci_ 36(16):1847–1851. PMID 29300147. n=27 category-1 golfers: **CMJ positive impulse r = 0.788** (p<0.001) ≫ peak force r = 0.482 > **RFD 0–200 ms r = 0.398**, RFD 0–150 ms r = 0.343.
- **Wells JET et al. (2019).** _J Sports Sci_ 37(12):1381–1386. PMID 30572804. n=31 European Challenge Tour. _"CMJ PI was the only significant variable, accounting for 37.9% of the variance."_ RFD did not survive.
- **Wells JET et al. (2020).** vGRF asymmetry. _JSCR_. PMID 31136544. n=50, handicap ≤5. **No significant relationship (r = −0.14 to 0.22)** between clubhead velocity and any vGRF asymmetry measure.
- **Jones KM, Wallace ES, Otto SR (2023).** _J Sports Sci_ 41(4):342–349. PMID 37149899. n=104. **The required caveat to Ball & Best:** PCA showed _"clusters were not well separated and provided support for a multidimensional continuum"_; continuous classification predicts handicap and clubhead velocity better than discrete styles.
- **Lynn SK, Noffal GJ (2010).** Frontal plane knee moments in golf. _JSSM_ 9(2):275–281. **Peak valgus just before contact; peak varus just after.** External lead-foot rotation reduced post-contact varus (t = −3.51, p = 0.01). Golf adduction moments **9–33% larger** than walking/stair ascent, within 5–8% of drop-jump landing.
- **You Y et al. (2023).** _Applied Sciences_ 13(12):7209. Systematic review + meta-analysis, **7 studies, n = 422**. Lead-foot vertical GRF consistently exceeded trail-foot across all clubs.

---

## Open gaps and verification flags

- **Paywalled r values:** Ball & Best 2007 Part II, Chu 2010 β coefficients, Han 2019, Peterson 2016, Johansen 2023.
- **Watson et al. 2026 results tables** — Springer authentication wall.
- **Barrentine and Koenig primary proceedings** — only via Worsfold's discussion.
- **OpenSim RRA residual threshold table** — Confluence migrated; verify current values.
- **BodiTrak/XSENSOR acquisition** — unconfirmed from primary sources.
- **BodiTrak/Vista Medical patent family** — could not be isolated; FPO "Vista Medical" hits are a different company.
- **TPI hardware endorsement** — no evidence on mytpi.com.
- **GEARS kinetics** — no vendor documentation of force output.
- **ISO 376 / OIML R 60** edition and scope — iso.org returned 403.
