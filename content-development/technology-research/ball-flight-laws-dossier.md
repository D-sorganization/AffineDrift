# Ball Flight Laws — Research Dossier

Compiled 2026-08-02. Both PING papers were retrieved as PDFs and parsed locally — full text
confirmed first-hand, not summarised from abstracts.

---

## HEADLINE FINDING — the 85/15 rule is misstated throughout the golf literature

**The only peer-reviewed measurement of it does not confirm 85%.** PING measured **76% ± 8%**
for driver _horizontal_ launch. The 83–87% figures that circulate are **_vertical_-plane
numbers.** This conflation is the single most citable problem in the ball-flight-law literature,
and it propagates into essentially every coaching source.

---

## 1. Old vs new laws — the correction, properly sourced

**The 85/15 statement, verbatim** — Fredrik Tuxen (TrackMan CTO), _TrackMan News #4_,
**January 2009**, "Secret of the Straight Shot":

> "The horizontal launch angle is determined by only two parameters, the club path and the
> face angle. As a rule of thumb, the horizontal launch angle is 15% determined by the club
> path and 85% determined by the face angle."

Worked example: path +6.7°, face −1° → HLA 0°. Check: 0.85(−1) + 0.15(6.7) = +0.16 ≈ 0. ✅

Same source, rejecting the old laws: _"According to the 'old' ball flight laws, the initial
direction of the ball (HLA) is 100% dictated by the club path. All the scientific people in the
golf industry know that this is very wrong."_

**D-plane, TrackMan's own definition**, _TrackMan News #5_, July 2009: _"the wedge-shaped plane
between two 3-dimensional directions: 1) clubhead direction at impact which is described by
attack angle and club path and 2) clubface orientation at impact which is described by dynamic
loft and face angle."_

### The crucial historical correction — it was a testing failure, not a textbook failure

Wood et al. (2018), **peer-reviewed**, state it plainly:

> "The PGA Teaching Manual [Wiren, 1990] … indicated that initial ball direction is more toward
> face angle than club path. However, due to a misunderstanding of the material, the PGA test
> for many years required candidates to state that the initial direction of the ball is equal
> to the club path. This likely contributed to the topic of the ball's initial direction being
> widely debated among golf teachers in recent years."

[doi:10.3390/proceedings2060249](https://doi.org/10.3390/proceedings2060249). **This is the
best-sourced sentence available on the controversy — a peer-reviewed claim, not a blog claim.**
The manual was right; the exam was wrong.

Reinforcing it, Henrikson et al. 2020 §1 note that **both Cochran & Stobbs (1968) and TrackMan
(via Dewhurst) are cited as quantified data sources** in 2020 peer review. **Correct oblique-impact
data was in print in 1968.** The instructional world's error was one of _transmission_, not of
available science.

---

## 2. Jorgensen's D-plane

T.P. Jorgensen, _The Physics of Golf_, Springer (1994; 2nd ed. 1999). "D" = **descriptive
plane**. Geometry: the plane containing the **club-face normal** and the **clubhead velocity
vector** just before impact; initial flight lies in that plane and the spin axis is normal to it.
Detail is in the book's **Technical Appendix, Section 3**.

What he actually claimed, per peer review (Wood et al. 2018): _"Jorgensen derived equations to
determine the ball's **vertical** launch angle and an example for some typical golf club and ball
parameters, yielding an initial direction just over 80% towards the dynamic loft."_
**A vertical-plane derivation with a worked example — not a general horizontal 85/15 law.**

Documented critiques ([The Swing Engineer](https://www.theswingengineer.com/problems_d_plane.html)):
the D-plane is defined only for centred strikes; Jorgensen never specifies _when_ "just before
impact" is, though both vectors rotate through the ~0.5 ms contact; practitioners assume a
straight-line path tangent he never asserted.

⚠️ Jorgensen's text could not be obtained (not in full view on Google Books, HathiTrust, or
archive.org). Only the peer-reviewed characterisation above is safe to cite.

---

## 3. THE MEASURED NUMBERS — Wood, Henrikson & Broadie (PING), 2018

_Proceedings_ **2**(6):249, 12th ISEA Conf., Brisbane —
[doi:10.3390/proceedings2060249](https://doi.org/10.3390/proceedings2060249)

**Methods:** 157 right-handed golfers (hcp 10.1 ± 10.0), 8-camera Vicon T40S @ **720 fps** +
Foresight GC2; **731 driver, 745 7-iron, 99 wedge** shots; filtered to strikes within **0.25″**
of face centre and **≥1.5°** face-to-path. Plus a **PING Man robot** 7-iron test, 41 m/s, five
face settings 0–8° open, Phantom camera @ **9000 fps** overhead via mirror.

| Measure                                       | Driver              | 7-iron               | Wedge               |
| --------------------------------------------- | ------------------- | -------------------- | ------------------- |
| **Vertical** launch ratio toward dynamic loft | 83% ± 8% (n=137)    | 81% ± 5% (n=252)     | 72% ± 6% (n=36)     |
| **Horizontal** launch toward face angle       | **76% ± 8%** (n=89) | **69% ± 3%** (n=172) | **61% ± 7%** (n=28) |
| Robot, horizontal toward face angle           | —                   | **63% ± 4%** (n=15)  | —                   |

Robot regression R² = 0.986, slope 0.63. Resolution: 1 px = 0.30° face angle, 0.15° launch angle.
Conclusion: _"the ball starts in general between 61% and 83% toward the face angle, with higher
numbers when the dynamic loft is lower."_

**Note the filtering rationale — it is itself a finding.** Strikes were restricted to within
0.25″ of centre _"in order to minimize changes in initial angle caused by the twisting of the
club head during impact."_ Off-centre impacts twist the head enough _during contact_ to alter
launch direction measurably.

### Older data points (recovered via Wood et al.'s literature review)

| Source                                           | Result                                                        |
| ------------------------------------------------ | ------------------------------------------------------------- |
| Cochran & Stobbs (1968)                          | −20° path, 0° face, ≈−7° ball direction → **65% toward face** |
| Sweeney et al., _Sports Biomech._ 12:247 (2003)  | 16° face-to-path change → 10° ball change → **62%**           |
| McCloy, Wallace & Otto, _Eng. of Sport 6_ (2006) | vertical launch **68%** toward dynamic loft                   |

⚠️ **Sourcing note:** TrackMan's launch-ratio values are cited in peer review **not** to the
newsletters but to **P. Dewhurst, _The Science of the Perfect Swing_, OUP, 2015.**

---

## 4. The ratio is ONE loft-dependent curve, not two separate "rules"

Wood et al. Figures 3c/3d show the ratio declining monotonically with obliqueness
(**spin loft = dynamic loft − attack angle** — confirmed by their own axis label), and they flag
it as **non-linear**.

Tutelman's fit `DAx = A(0.96 − 0.0071Φ)` reproduces the folklore exactly:
Φ = 15° → **85.3%**; Φ = 30° → **74.7%**.

> **The "85/15 driver" and "75/25 wedge" rules are one curve evaluated at two spin lofts.**
> They are not two separate laws. Any textbook treatment should say this explicitly.

---

## 5. Spin axis geometry — the tan/tan relation

From [Tutelman's derivation](https://www.tutelman.com/golf/ballflight/3dlaunch.php)
(A = horizontal face-to-path, L = spin loft):

- Obliqueness: $\cos\Phi = \cos A \cdot \cos L$
- Total spin: $S = 160\,V_{\text{club}}\sin\Phi$
- **Spin axis tilt** $= \arctan[\tan(A)/\tan(L)]$
- Launch: $DA_x = A(0.96 - 0.0071\Phi)$, $DA_y = L(0.96 - 0.0071\Phi)$

**Independent confirmation of the tan/tan form.** TrackMan #5 states spin axis tilts ≈**2×**
face-to-path for a 6-iron and ≈**4×** for a driver. Testing the formula for small A, the
multiplier is $1/\tan(\text{spin loft})$:

- Driver spin loft ≈14° → $1/\tan 14° =$ **4.01** ✅
- 6-iron spin loft ≈26.5° → $1/\tan 26.5° =$ **2.01** ✅

Exact match. **Strong evidence TrackMan's published rules of thumb are generated by precisely
this relation.**

### Curvature per degree of axis tilt — two sources agree

- Tuxen (TrackMan, 2013): 10° spin axis ≈ **7% sideways** ≈ 14 yd over 200 yd
- [TrackMan, _What is Spin Axis?_](https://www.trackman.com/blog/golf/spin-axis): at 200 yd,
  ±2° ≈ 3 yd, ±10° ≈ 15 yd; at 150 yd, ±2° ≈ 2.2 yd, ±10° ≈ 11 yd
- ⇒ ≈**0.7% side-curve per degree**

**Curvature is non-linear in distance** ([Tutelman](https://www.tutelman.com/golf/ballflight/slice.php)):
Y/X = 0.014(distance − 86 yd) → 1.6 at 200 yd, **3.0 at 300 yd**.

### Gear effect tilts the axis independently of the D-plane

Which is exactly why launch monitors separate _measured_ Spin Axis from _computed_ D-Plane Tilt.
Horizontal gear-effect spin $s = 58{,}830\,V_b C x / I_h$ (C = CG depth behind face, x =
horizontal miss); modern driver approximation $s \approx 16.4 V_b x$; vertical
$s \approx 25 V_b y$, i.e. **1.5–2× horizontal because $I_v \approx 0.5$–$0.66\,I_h$**
([Tutelman](https://www.tutelman.com/golf/ballflight/gearEffect.php)). TrackMan #5 quantifies:
6-iron struck **1 dimple (0.14″)** toward the toe → spin axis −2° → ~2.5 yd offline at 170 yd.

---

## 6. What disputes the 85/15 figure

1. **The robot number is the lowest of all** — 63% for a 7-iron vs 69% from the same lab's human
   data. Attributed to the robot's wrist rotation adding ~1° dynamic loft per 2° of face opening
   (~4° across the range) — i.e. the ratio fell _because obliqueness rose_, which is the paper's
   own thesis.

2. **PING vs TrackMan on mechanism — a genuine peer-reviewed dispute.** TrackMan/Dewhurst
   attribute the driver's higher ratio to a smoother titanium face producing less friction.
   Henrikson et al. 2020 **reject this**: _"The results of the current work will suggest that this
   behavior is governed by the compliant behavior of the reaction forces at impact and would be
   present even if the faces of a driver and high lofted iron were equally as 'smooth'."_ Their
   Fig. 6 shows the ratio decreasing with loft **even at constant μ**. Counterintuitively, below
   ~20° incidence _lower_ μ gives a launch direction _closer to the path_ (gross slip before
   stick) — the opposite of the friction hypothesis.

3. **Ball construction matters:** μ = **0.40 urethane** vs **0.35 surlyn** (Henrikson et al. 2020,
   measured by sled test).

4. **Measurement validity caveat** for anyone re-deriving these ratios: small denominators
   explode the ratio, which is why Wood et al. filtered at ≥1.5° face-to-path. They report the
   ratio changed by ≤3% across 1.5°/3°/4.5° thresholds. See also Leach et al., _Measurement_
   **112**:125–136 (2017), [doi:10.1016/j.measurement.2017.08.009](https://doi.org/10.1016/j.measurement.2017.08.009).

### Henrikson, Wood, Broadie & Nuttall, _Proceedings_ 2020, 49, 27 (13th ISEA)

[doi:10.3390/proceedings2020049027](https://doi.org/10.3390/proceedings2020049027) — the
friction/tangential-compliance paper. Model: modified Hertzian contact with tangential compliance
under Coulomb friction (Maw, Barber & Fawcett 1976/1981). Validated by firing a urethane ball at
a grooved/blasted steel plate at 106 mph, plate angles 3–33°, Phantom @9500 fps, **MAE < 1°**.

Its Table 1 compares **TrackMan against PING in the vertical plane**:
Driver **87 vs 83 ± 8**; 7-iron **75 vs 81 ± 5**; pitching wedge **70 vs 72 ± 6**.

---

## 7. Cochran & Stobbs (1968)

_The Search for the Perfect Swing_, Golf Society of Great Britain scientific study. Heinemann (UK)
/ J. B. Lippincott, Philadelphia (US), 1968; ISBN 0434140007. Reprints: The Booklegger 1986,
ISBN 0936421002 (xiii + 242 pp.), [archive.org](https://archive.org/details/searchforperfect0000coch);
Triumph Books ISBN 1572431091; 2005 ISBN 1572437294.

**Verified content:** the −20° path / 0° face / −7° launch example = **65% toward the face** (via
Wood et al. 2018, peer-reviewed).

⚠️ The book's text could not be obtained (archive.org copy lending-restricted, OCR errors). Its
specific treatment of **spin axis, gear effect, and friction is unverified** — **do not attribute
gear effect to Cochran & Stobbs without checking a physical copy.** The commonly cited "Triumph
Books 1999" date is also unverified.

---

## 8. Claims that could NOT be verified

1. **Jorgensen's actual text** — book not digitally accessible.
2. **Cochran & Stobbs' text** on spin axis, gear effect, friction.
3. **Any official PGA of America revision date** for its ball flight laws or curriculum. No
   primary document found. The Wood et al. sentence about the PGA _test_ is the strongest substitute.
4. **"Wrong for 100 years."** ❌ No source. The defensible institutional window is roughly
   **1972–2009 (~35–40 years)**, and it was **never universal** — Homer Kelley's _The Golfing
   Machine_ and Wiren's own manual both stated face dominance.
5. **Origin of "ball starts on the path."** Best candidate is **John Jacobs, _Practical Golf_,
   pp. 20–21** — but this is a forum attribution with no scan or quotation. **Highest-value
   follow-up**: a copy of Jacobs would name the source of the error.
6. Specific _Golf Digest_ / _Golf Magazine_ articles announcing the correction.
7. Roles of Andrew Rice and James Leitz in the correction (Rice's located writing is May 2013,
   well after). Brian Manzella's involvement documented from Feb 2009.
8. Faldo / Butch Harmon as teachers of the old laws — secondary allegation, uncited.
9. **TrackMan's own current statement of the laws** — trackman.com/blog/golf/ball-flight-laws
   **404s**; the 2009 newsletters survive only as third-party-hosted PDFs.

**Method note:** MDPI, ResearchGate and TrackMan's support site all return 403 to automated
fetches; both PING papers were retrieved via `mdpi-res.com` and Semantic Scholar and parsed
locally.
