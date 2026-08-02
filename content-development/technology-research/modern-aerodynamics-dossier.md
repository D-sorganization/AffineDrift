# Modern Golf Ball Aerodynamics — WSU Still-Air Data, CFD, and Published Coefficients

Compiled 2026-08-02. Fills the coefficient gaps left open in
[aerodynamics-models-gap-register.md](aerodynamics-models-gap-register.md).

---

## 1. THE ONE MODEL WITH PUBLISHED COEFFICIENTS

**Naruo, T., Mizota, T. & Shimozono, H. (2004)**, _Trans. JSME Series B_ **70**(697), 2371–2377,
[doi:10.1299/kikaib.70.2371](https://doi.org/10.1299/kikaib.70.2371) — ✅ **full text read**.

$$C_D(S) = 0.7510\,S^4 - 1.760\,S^3 + 1.098\,S^2 + 0.2148\,S + 0.2049$$
$$C_L(S) = -0.2158\,S^4 + 1.006\,S^3 - 1.644\,S^2 + 1.250\,S + 0.0616$$

Valid **S = 0.03–1.13, Re = 7.09×10⁴–1.25×10⁵**. Evaluated: S=0.1 → C_D 0.236, C_L 0.171;
S=0.2 → 0.279, 0.253; S=0.5 → 0.414, 0.343.

Method: 400 mm open-jet tunnel, U = 25–44 m/s, wire-driven ball to 167 rps; high-speed runs at
Salford to 80 m/s. Non-spinning **C_D ≈ 0.25–0.28 over Re = 4×10⁴–3×10⁵**, all three dimple
patterns indistinguishable.

> ⚠️ **Their central claim is the disputed one:** C_D and C_L collapse onto single curves in spin
> ratio and are **independent of Re** over the flight range. §3 below contradicts this directly.
> The model is convenient and self-consistent but rests on a premise later measurements reject.

**Naruo & Mizota (2014)**, _Procedia Engineering_ **72**, 780–785 — 🚩 gold OA but every route
403'd. The [JSME symposium twin](https://www.jstage.jst.go.jp/article/jsmeshd/2014/0/2014__B-29-1_/_pdf)
with the same data ✅ was read: deeper dimples (k/D 3.70×10⁻³) give C_L collapsing cleanly across
25–44 m/s; **shallower dimples (2.88×10⁻³) give higher C_L above 30 m/s but C_L collapses to
0.00–0.05 below 30 m/s** — and a real drive drops below 30 m/s just after apex, so the shallow
ball loses carry. Adding 252 "tiny" dimples between the large shallow ones removes the collapse.

---

## 2. ITR-class measured values for named balls

From **US 6,916,255 B2** (Aoyama & Jones, Acushnet, 2005), ballistic-screen indoor range:

| Ball                          | C_L @ Re 70k, SR 0.188 | C_L @ Re 180k, SR 0.110 | C_D @ 70k | C_D @ 180k |
| ----------------------------- | ---------------------- | ----------------------- | --------- | ---------- |
| Pinnacle Gold (USGA standard) | 0.216                  | 0.158                   | 0.276     | 0.225      |
| **Titleist Pro V1**           | 0.209                  | 0.168                   | 0.274     | 0.227      |
| HX Red                        | 0.215                  | 0.179                   | 0.282     | 0.228      |
| Rule 35 Red                   | 0.227                  | 0.177                   | 0.284     | 0.227      |

**USGA population ranges** (Quintavalla 2006, USGA Tech Report RB/cor2006-01,
[R&A-hosted PDF](https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/f6d83584-fe07-4a89-a9d4-78b764687baf/R201%20-%20Effect%20of%20Equipment%20on%20Distance%20Golf%20Balls%20App%20A.pdf)):
**C_L 0.125–0.30, C_D 0.22–0.32** over Ω = 0.05–0.2, Re ≈ 0.5–2×10⁵, with both **peaking near
Re ≈ 1×10⁵** and declining above.

**Editorial read:** these sit inside the still-air ranges. The three methods are **not in gross
conflict on modern balls** — disagreements are at the level of a few hundredths.

---

## 3. WSU still-air projectile method (Lyu / Kensrud / Smith)

| Paper                                                                                                                                                          | Access                     |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Lyu, Kensrud, Smith & Tosaya (2018), "Aerodynamics of Golf Balls in Still Air," _Proceedings_ **2**(6), 238, [doi](https://doi.org/10.3390/proceedings2060238) | OA ✅ read                 |
| Lyu, Kensrud & Smith (2020), "The reverse Magnus effect in golf balls," _Sports Eng._ **23**(1):3, [doi](https://doi.org/10.1007/s12283-020-0318-1)            | OA ✅ read                 |
| Kensrud & Smith (2018), _Proc IMechE Part P_ **232**(3), 255–263, [doi](https://doi.org/10.1177/1754337117740749)                                              | 🚩 **paywalled, NOT read** |
| Kensrud (2010), MS thesis WSU, [hdl:2376/105199](https://hdl.handle.net/2376/105199)                                                                           | ✅ read (127 pp.)          |

### Apparatus

Fire production balls through **stationary** air; speed decay → drag, vertical deflection → lift.
Eliminates support interference, blockage corrections, and scaled models.

- **Launcher:** bespoke **non-wheeled** pneumatic accelerator with a flexible tip carrying
  high-friction material on one side — avoids the dimple damage a wheeled machine inflicts.
- **Three speed sensors**, each = two vertical light gates **0.41 m** apart + one 45° gate for
  vertical position. Baseline **3.81 m**, short enough that coefficients are constant over it.
- Sensor heights within 0.025 m; total vertical drop ≤ 0.1 m.
- Spin verified by Phantom V711 at 2000 fps, **±15 rpm**.
- Range (golf): **18–91 m/s, 1500–4500 rpm**.

**Daily calibration — the elegant part:** a setup ball is fired with a **vertical spin axis**, so
no vertical Magnus force can exist; sensor positions are adjusted until measured
**C_L = 0.00 ± 0.01**. Drag sensors adjusted to within ±0.02 of initial.

Uncertainty: **U(C_D) = 0.005, U(C_L) = 0.0005**. Random error over 416 tests: σ(C_D) = 0.02,
σ(C_L) = 0.01. (Thesis-era was far cruder: U(C_D) = 0.05.)

### Results

- **Drag crisis onset Re ≈ 7×10⁴.** C_D falls **0.5 → 0.2 between Re 5×10⁴ and 7.5×10⁴**.
  Of eight sports balls tested the golf ball has **the most severe drag crisis of any**.
- **Minimum C_D = 0.17** vs Bearman & Harvey's 0.23 — a 26% difference. ⚠️ Kensrud attributes it
  to 50 years of ball development, **not** method error.
- Between-model C_D spread **>0.1 below Re 10⁵**, **<0.05 above**. Extremes: TP5X lowest, Wilson
  Staff Duo highest. Smooth-sphere control gave C_D = 0.50, agreeing with Achenbach.
- **C_L is non-linear in S**, fitted per ball with a 2nd-order polynomial; rotating drag needed
  **two** polynomial branches (50k<Re<100k, 75k<Re<200k). **Nothing collapses to one curve.**

### Reverse Magnus — the sharpest golf-specific dataset

| Quantity                                | Value                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Window                                  | **5×10⁴ < Re < 7×10⁴**, **750 < ω < 2250 rpm**                   |
| Titleist Pro V1 (circular, 352 dimples) | **C_L,min = −0.10**, negative over 0.09 < S < 0.15               |
| Bridgestone B330-RX (dual, 330)         | negative over 0.07 < S < 0.19                                    |
| Callaway ChromeSoft (hexagonal, 332)    | **C_L,min = −0.15**, negative over 0.08 < S < 0.21               |
| Local Re asymmetry                      | at Re 6×10⁴, 1500 rpm: bottom **6.9×10⁴**, top **5.1×10⁴**       |
| ∂C_D/∂Re vs C_L correlation             | **r² = 0.87** — steeper drag crisis ⇒ more severe reverse Magnus |

> **C_L differs by 0.05 (50%) between two production balls at identical Re and spin, purely from
> dimple pattern.** This is the strongest available argument that no single-parameter C_L(S)
> model can be right, and it is a direct measurement rather than an inference.

### Carry consequence

13 models, identical release (71.5 m/s, 6°, 3000 rpm, 4%/s decay): **carry spread 18 m** from
mean coefficient differences of only ~0.02. Longest: Bridgestone B330-RX and Kirkland 2017,
within 0.5 m — **neither from the high-price tier. Cost not correlated with distance.**

### Their stated position on wind tunnels

Tunnels control air speed well but struggle to support and spin the ball, need empirical blockage
corrections, and use **scaled models** — which cannot represent production balls because golf ball
behaviour is acutely sensitive to dimple shape and surface roughness. Both papers are careful:
this is **not** a claim tunnel data is wrong, only that still-air is closer to play.

⚠️ **Highest-value unretrieved item:** a search snippet from the paywalled Kensrud & Smith 2018
reads _"the still air drag coefficient of smooth balls was comparable to wind tunnel drag at
Re < 2×10⁵ and higher than wind tunnel results at Re > 2×10⁵."_ If genuine this is the most
direct still-air-vs-tunnel discrepancy statement in the corpus. **Unverified — obtain the paper.**

---

## 4. CFD

| Study                                                                                                                                                                                               | Conditions                         | Values                                                                                                                                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Smith, Beratlis, Balaras, Squires & Tsunoda (2010)**, _IJHFF_ **31**(3) 262–273, [doi](https://doi.org/10.1016/j.ijheatfluidflow.2010.01.002) ✅                                                  | non-rotating DNS                   | Re 2.5×10⁴: **C_D 0.47** (337M pts); Re 1.1×10⁵: **C_D 0.26** (1.2B pts). Separation ≈84° sub- vs ≈110° supercritical                                                                           |
| **Beratlis, Squires & Balaras (2012)**, _J. Turbulence_ **13**(15), [doi](https://doi.org/10.1080/14685248.2012.676182); free [TSFP-7](http://www.tsfp-conference.org/proceedings/2011/4d1p.pdf) ✅ | DNS, α = 0.126, ~300 dimples       | Re 1.7×10⁴: 0.454, +0.046; **4.5×10⁴: 0.362, −0.0411 (negative Magnus)**; 6.5×10⁴: 0.249, +0.120; 1.7×10⁵: 0.212, +0.0215                                                                       |
| **Li, Tsubokura & Tsunoda (2017)**, _FTaC_ **99**, 837–864, [doi](https://doi.org/10.1007/s10494-017-9859-1) ✅ OA                                                                                  | LES, real 392-dimple ball, Γ = 0.1 | Re 4.3×10⁴: 0.5059, 0.1498; **7.5×10⁴: 0.3168, −0.1367**; 1.1×10⁵: 0.2397, 0.1353. Critical Re ≈ 8×10⁴                                                                                          |
| **Crabill, Witherden & Jameson (2018)**, [arXiv:1806.00378](https://arxiv.org/abs/1806.00378) ✅                                                                                                    | high-order ILES, Re 150k, Γ = 0.15 | static C_D 0.2469 ± 0.005; spinning C_D 0.256 ± 0.010, **C_L 0.164 ± 0.021**. Transition from 4th dimple row (~31°), fully turbulent by 63°                                                     |
| **Kim & Choi (2014)**, _Proc IMechE P_, [doi](https://doi.org/10.1177/1754337114543860); free [TSFP-7](http://www.tsfp-conference.org/proceedings/2011/4d2p.pdf) ✅                                 | grooved vs dimpled, Re 0.5–2.7×10⁵ | grooved ≈50% drag reduction vs smooth; supercritically C_D 4–10% higher but C_L 10–27% higher than dimpled → **L/D 5–20% better**. Simulated carry: dimpled 230 m, grooved 215 m, smooth ~100 m |

**Fluctuating side force** (Li et al. 2017, Table 1): at critical Re = 7.5×10⁴ the side-force
**standard deviation (0.0426) exceeds its own mean (0.0386)** and is ~31% of mean lift magnitude.
Subcritically a rotating golf ball shows _larger_-amplitude lateral oscillation than a smooth
sphere; supercritically rotation stabilises it.

---

## 5. Dimple orientation relative to spin axis — a NEGATIVE finding

**No peer-reviewed study measures golf-ball C_D/C_L as a function of dimple-pattern orientation
relative to the spin axis** (poles-horizontal vs poles-vertical, parting-line effects). Systematic
Crossref/OpenAlex querying found nothing. Presumably proprietary to ball makers and the USGA R&TC.

🚩 **Treat any specific PH-vs-PV ΔC_L number as unsourced.**

Consistent with that, the **rules themselves carry no test**: USGA's own
[R32 history](https://www.usga.org/content/dam/usga/pdf/Equipment/R32%20-%20History%20of%20Equipment%20Rules.pdf)
records the symmetry standard adopted **1980** (⚠️ not 1981 as commonly cited — that is likely the
effective date) and **"the actual symmetry test is removed from the text of the Rules"** in
**1996**. Current Equipment Rules Part 4 §4 is a bare design-intent provision with no procedure
and no numeric tolerance.

The provoking product: **US 3,819,190** (Nepela & Holmstrom, 1974) — Polara, dimples concentrated
in an equatorial band with smooth poles. Contains **no quantitative side-force data**. Contrast
**US 4,560,168** (Aoyama, 1985), whose icosahedral layout is justified explicitly so "the ball
will always fly the same way no matter what the orientation."

**Closest verified golf proxy:** the 0.05 C_L difference between circular and hexagonal dimple
balls at matched Re and spin (§3).

**Cross-sport analogues** (best open orientation sweep): Shah & Mittal (2023), _Flow_ **3**:E16,
[doi](https://doi.org/10.1017/flo.2023.12) — cricket ball, seam angle 0–90° in 10° steps,
Re 0.45–3.40×10⁵, **side force reversing sign with Re at fixed orientation**, C_Z spanning ±0.3–0.4.
Also Watts & Sawyer (1975), [doi](https://doi.org/10.1119/1.10020) — the canonical statement that
nonsymmetric roughness gives a lateral force that changes as the surface rotates.

---

## 6. Brief corrections to circulated attributions

| Wrong                                     | Right                                                              |
| ----------------------------------------- | ------------------------------------------------------------------ |
| "Kiyoshi Naruo"                           | **Takeshi Naruo**                                                  |
| Naruo at Sumitomo / Bridgestone           | **Mizuno Corporation** (Mizota at Fukuoka Inst. Tech. is correct)  |
| "Kensei Aoki, Kogakuin"                   | **Katsumi Aoki, Tokai University**                                 |
| Chowdhury first author on RMIT drag paper | **Alam** is first author                                           |
| "Ayako Sakamoto"                          | **appears to be spurious — no such researcher in this literature** |
| USGA symmetry standard 1981               | **1980** per USGA's own R32                                        |

⚠️ **RMIT internal inconsistency:** Alam/Chowdhury 2011 reports min C_D ≈ 0.25; the
[2010 companion](https://people.eng.unimelb.edu.au/imarusic/proceedings/17/176_Paper.pdf) reports
≈0.20 with up to 40% spread between balls. **The two papers disagree on the minimum.**

---

## 7. Not verified

1. **Kensrud & Smith 2018** (_Proc IMechE_ 232:255) — paywalled; the still-air-vs-tunnel sentence
   above is from a search snippet only. **Highest-value target.**
2. **Bearman & Harvey's own tables, model scale, spin grid** — all figures secondary. The "2.5×
   scale" appears in Kensrud's thesis but was not confirmed against the original.
3. **Sakib & Smith (2020)**, _Exp. Fluids_ **61**:115 — paywalled, no OA location, **no coefficient
   values obtainable**. Method confirmed only (2-component PIV, separation-point diagnosis).
4. Naruo & Mizota 2014 _Procedia_; Choi et al. 2006; Ting 2002/2003; Aoyama's _Science and Golf_
   papers — citations confirmed, full text blocked.
5. No paper titled "The Aerodynamic Drag Crisis in Golf Balls" or "A comparison of laboratory and
   field testing of golf ball aerodynamics" exists under these authors. That content lives inside
   the papers above.
