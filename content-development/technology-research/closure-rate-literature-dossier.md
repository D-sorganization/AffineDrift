# Clubface Closure Rate — Literature Dossier

Compiled 2026-08-03. Contains the central finding for the whole topic (four incompatible
reference frames) and a result that **contradicts the coaching consensus** — and contradicts
the naive prediction from timing-sensitivity arithmetic.

---

## 0. THE central finding: four incompatible reference frames

Published "closure rate" numbers span ~200 °/s to ~3,900 °/s. This is **not** measurement
disagreement — it is **four different quantities sharing one name.** Any treatment that does
not state the frame produces nonsense.

| Quantity                                                | Axis / reference                    | Typical tour magnitude          |
| ------------------------------------------------------- | ----------------------------------- | ------------------------------- |
| **Handle/shaft twist velocity (HTV)**                   | About the shaft's long axis         | **~650–2,430 °/s** (mean 1,307) |
| **Clubhead closing velocity (CCV)** = "rate of closure" | Face vs **target line** (global)    | **~1,800–3,600 °/s**            |
| **Face-to-path closure rate** (GEARS)                   | Face vs **instantaneous club path** | **~360–620 °/s**                |
| **Speed-normalised RoC**                                | °/foot of clubhead travel           | **13–25 °/ft**                  |

**The reconciling equation**, from Cheetham's dissertation (p. 12–13), attributed to E. Henrikson (PING):

$$\text{CCV} = \text{HTV}\sin(\text{lie}) + \text{SPV}\cos(\text{lie})$$

PING measured the **HTV:CCV ratio at impact = 0.62** across 150 players, so CCV ≈ 1.61 × HTV.
Applying that to Cheetham's tour mean HTV of 1,307 °/s gives **CCV ≈ 2,100 °/s**, and his range
652–2,432 °/s maps to **~1,050–3,920 °/s** — landing almost exactly on MacKenzie's published
1,800–3,600 °/s band. **The two "contradictory" figures are the same population measured about
different axes.**

⚠️ The "tour pros average 200–300 °/s" claim ([Rotary Swing](https://rotaryswing.com/golf-instruction/club-face-rotation-golf)) is **not credible as stated** — most likely a garbled retelling of path-relative GEARS values. Do not cite.

---

## 1. Vendor definitions

- **Foresight GCQuad** — "The rotation of the club head heel to toe measured about the shaft in degrees per second or rpm" ([What We Measure](https://www.foresightsports.com/pages/what-we-measure)). **Axis = shaft long axis** → closer to HTV than global RoC. **No benchmark table published.**
- **GEARS** — "the rate of change of the angle measurement (in degrees/second) of the club's face **relative to the club's path**" ([GEARS metrics](https://www.gearssports.com/articles/gears-golf-club-ball-metrics/)). **Path-relative** — which is why GEARS numbers are an order of magnitude lower.
- **AMM3D (Cheetham)** — Polhemus Liberty EM, 6-DOF, **240 Hz**, static accuracy 0.03 in / 0.15° RMS. HTV = "the component of the local angular velocity vector of the handle around its long axis." TPI 3D calls it "handle axial velocity"; Nesbit (2005) calls it "gamma velocity."
- **TrackMan** — does **not** publish a closure-rate metric.
- **Sportsbox** — no closure metric found ⚠️ (absent, not confirmed-absent).

---

## 2. Numeric values

### Cheetham (2014), ASU dissertation — the best dataset in existence

[PDF](https://www.philcheetham.com/media/Phillip-Cheetham-Doctoral-Dissertation-2014.pdf). 94 PGA/European Tour professionals (70 with PGA Tour driving-accuracy stats), AMM3D at TPI, 240 Hz, driver. Clubhead speed **48.4 ± 2.5 m/s (108.3 mph)**; driving accuracy **62.8 ± 6.4 %**.

**Handle twist velocity (°/s):**

| Group         | Mean      | SD  | High  | Low   |
| ------------- | --------- | --- | ----- | ----- |
| Total (n=94)  | **1,307** | 304 | 2,432 | 652   |
| Hi-HTV (n=32) | **1,631** | 205 | 2,432 | 1,408 |
| Lo-HTV (n=32) | **996**   | 150 | 1,173 | 652   |

**Wrist/forearm kinematics (°/s):**

| Variable                         | Hi-HTV          | Lo-HTV          | p        | d        |
| -------------------------------- | --------------- | --------------- | -------- | -------- |
| Lead forearm supination (impact) | **1,811 ± 286** | **1,295 ± 256** | **.000** | **1.90** |
| Lead wrist extension (impact)    | 433 ± 195       | 446 ± 228       | .813     | 0.06     |
| Lead wrist ulnar deviation (max) | 922 ± 126       | 859 ± 180       | .109     | 0.40     |
| Trail elbow extension (max)      | 931 ± 190       | 851 ± 156       | .070     | 0.46     |

**Supination is the ONLY significant discriminator** — group mean 1,569 ± 338 °/s, r = .68 with HTV, range 851–2,299 °/s. 92 of 94 players had the lead wrist **extending** at impact despite a mean 2° of flexion.

**Body posture at impact:** thorax open 27 ± 9° (r = −.40); thorax side bend 31 ± 5° (r = −.50); pelvis open 41 ± 9° (r = −.36). **Lower-HTV players are more open and more side-bent — they substitute body rotation for forearm roll.**

**Time course:** Cheetham identifies a **"twist release point"** — at the swing-plane release point HTV is actually **negative (opening)**, driven by slight pronation, then crosses zero and rises steeply into impact. **RoC is not monotonic; it peaks at or just before impact.**

### PING / Fujikura ENSO

150 players × 5 swings, mean handicap 12 (tour → 30+), 15% female, ages 18–70. **HTV range ~500–3,000 °/s** — far more diverse population, nearly the same range.

### MacKenzie, global frame ([Golf.com](https://golf.com/instruction/what-is-rate-of-closure-golf-swing-sasho-mackenzie/))

- **RoC typical range 1,800–3,600 °/s**, explicitly "for any group of golfers, **regardless of level**."
- **~70–100° of face closing remains with only 0.04 s to go** — including for tour players.
- **Swing-plane contribution alone**, 90 mph driver: plane 30° from vertical → **~800 °/s**; 45° → **~1,200 °/s**. Tour driver planes run 40–45°. **Roughly a third of total RoC comes from plane inclination with zero forearm roll.**
- **Speed-normalised in °/ft** to remove the speed confound. Worked example (Jon Sinclair, 6-iron): **25 °/ft at 86 mph** vs **13 °/ft at 88 mph** — ~2× RoC change, both carrying 180+ yds relatively straight.

> **NOTE for the article:** MacKenzie's °/ft is exactly ω/v — independently confirming that the dimensionally correct predictor is ω/v (units 1/length), i.e. 1/R_ISA, not ω alone.

⚠️ **Driver vs iron split: NO source publishes one.** Mechanically the lie term in CCV = HTV·sin(lie) + SPV·cos(lie) predicts irons (more upright) convert _more_ HTV into face closure, but no measured confirmation. Open gap.

---

## 3. ⚠️ THE HEADLINE: closure rate does NOT predict accuracy at tour level

**The theory** (Cochran & Stobbs 1968): faster face rotation → harder to time → worse accuracy.

**The measured result** — Cheetham tested exactly this on 70 PGA Tour players:

- HTV vs driving accuracy **r = −.14 (r² = .02, "weak")**; HTV vs clubhead speed r = .14.
- Hi-HTV vs Lo-HTV driving accuracy: **62.9 % vs 63.9 %, NOT significant**, d = 0.26.
- Hi-HTV vs Lo-HTV clubhead speed: 48.9 vs 48.0 m/s, not significant, d = 0.42.

His conclusion: _"These results are contrary to popular belief among many instructors."_

**MacKenzie concurs independently:** _"there is currently no evidence to suggest that players with lower RoC hit more fairways or hit their approaches closer to the hole."_

**Why the theory is seductive (the arithmetic is sound):** face angle accounts for ~**82% of variance in launch direction** with a driver. Robot testing at 95 mph: **1° open = ~10 yards offline; 2° = ~20 yards** ([Golf.com RoboTest](https://golf.com/gear/drivers/open-closed-club-face-driver-robotest/)). At 2,100 °/s, **1° of face = 0.48 ms of timing.**

**Verdict:** state the mechanism, then state clearly it is **empirically unsupported at tour level** — presumably because players self-organise their timing precision around their own RoC. What _is_ supported (Betzler) is that better players are less variable in face angle, which is a statement about outcome variability, not about closure rate.

**Betzler, Monk, Wallace & Otto (2012)**, _J Sports Sci_ 30(5):439–448, **285 participants** — low-handicap golfers showed significantly lower shot-to-shot variability in face angle, club path, attack angle, impact location, clubhead speed and efficiency. [PubMed 22272690](https://pubmed.ncbi.nlm.nih.gov/22272690/). ⚠️ Exact SDs by handicap band paywalled.

---

## 4. Peer-reviewed literature

- **Cheetham, P. (2014).** _The Relationship of Club Handle Twist Velocity to Selected Biomechanical Characteristics of the Golf Drive._ PhD dissertation, Arizona State University.
- **Nakashima/Kwon et al. (2017).** "Relationships between clubshaft motions and clubface orientation during the golf swing." 8 skilled golfers. Sensitivity: swing-plane horizontal angle affects clubface horizontal angle **100%**; clubshaft angle in plane **74%/68%**; **clubshaft rolling angle 67%/75%**. Conclusion: plane orientation alone is insufficient — rolling angle must be measured. [PubMed 28554300](https://pubmed.ncbi.nlm.nih.gov/28554300/)
- **MacKenzie & Sprigings (2009).** "Understanding the role of shaft stiffness in the golf swing." 3D forward dynamics, 9 optimised models. **Dynamic close at impact 4.01° (slow/stiff) to 5.17° (fast/flexible)**; dynamic loft 4.42–6.27°. Critically these arise **purely from clubhead droop**, "without any ability of the shaft to twist about its longitudinal axis." **Shaft torsional twist measured at only 0.6° and deemed negligible.** Shaft stiffness had **no meaningful effect on clubhead speed** (max 0.08 m/s). [PDF](http://www.waddengolfacademy.com/biomechanics/MacKenzie%202009%20Understanding%20the%20role%20of%20shaft%20stiffness%20in%20the%20golf%20swing.pdf)
- **Keogh & Hume (2012):** face angle at impact is the single biggest factor in driving accuracy.
- **Nesbit (2005):** "gamma velocity" generates ~1.5 m/s extra clubhead-mass-centre velocity for a scratch golfer; Cheetham measured only 0.9 m/s Lo→Hi, non-significant.

---

## 5. The two-technique taxonomy — both valid

|                         | High HTV / High RoC                       | Low HTV / Low RoC                               |
| ----------------------- | ----------------------------------------- | ----------------------------------------------- |
| Cochran & Stobbs (1968) | **"Rollers"**                             | **"Pushers"**                                   |
| Suttie (2011)           | **Open-Face** method                      | **Closed-Face** method                          |
| Cheetham measured       | Supination 1,811 °/s; less open/side-bent | Supination 1,295 °/s; more open, more side-bent |

Suttie: the **Closed-Face/low-HTV** method requires limiting forearm roll in the backswing, demands **more body action and better physical condition**, is "easier to time," and risks a **severe hook if the hands get too active**. The **Open-Face/high-HTV** method uses more arm roll, needs less flexibility and less body turn. Cochran & Stobbs likewise held Pushers must be stronger.

**Tyler Ferrell** — mechanistic predictors of RoC in order: (1) **when the club passes the chest** (earlier → faster); (2) **arc width** (narrower → faster); (3) total supination. Important warning: **visual appearance is anti-correlated with measurement** — a "more rotated-looking" swing often has _slower_ closure at impact because the body kept turning. **Eyeballing roller-vs-holder from the follow-through is unreliable.**

**Draw/fade mapping — NOT supported.** No credible source maps high RoC → draw or low RoC → fade. The consistent _claim_ is a two-way miss and unpredictable curvature rather than directional bias — but per §3 that claim is itself untested.

⚠️ **Grip strength → required RoC: no source quantifies this in °/s.** Mechanism is theoretically weak anyway — grip shifts the face's _starting offset_, changing required total rotation, not necessarily rate.

⚠️ **Shaft-torque conflict:** GEARS reports shaft twist **~2° (low torque) to 6–7° (high torque)** and says twist "helps the player square the clubface when closure rate is lower" — **directly contradicting MacKenzie & Sprigings' modelled 0.6° and their negligibility conclusion.** GEARS measures the whole club optically under load; MacKenzie modelled shaft torsion in isolation. May not be the same quantity. Flag the conflict.

---

## 6. Rotation during contact

**Contact time ~450–500 µs** ([USGA](https://www.usga.org/content/usga/home-page/articles/2025/05/what-happens-collision-between-club-ball.html)); average force >2,000 lb; ball compresses ~¼ of its diameter.

**Face rotation during contact:** citing Fredrik Tuxen (TrackMan), **~0.8° of total face closure during the impact interval**, with a straight ball requiring ~0.4° closed face at mid-impact against ~0.7° in-to-out path ([forum thread](https://forum.brianmanzellagolf.com/threads/hinge-action-rate-of-closure-and-what-you-should-do-with-the-clubface-p9-pic.17179/)). ⚠️ Forum-sourced, attributed-to-Tuxen, not peer-reviewed.

> **Independent check:** 2,100 °/s × 0.00045 s = **0.95°** — consistent with the 0.8° figure.

Manzella argues **less closure during impact produces _more_ hook spin** (gear-effect argument), inverting The Golfing Machine's hinge-action teaching. ⚠️ Not peer-reviewed. **Do not conflate this intra-impact quantity with pre-impact RoC** — they differ by ~3 orders of magnitude in duration.

⚠️ **Toe-up to toe-up** exists purely as a coaching drill, never a quantified checkpoint. Geometrically implies ~180° of face rotation between shaft-parallel positions, but **no source states or measures it.**

---

## 7. Method note — a fabrication caught

A WebFetch summary of Cheetham's dissertation **returned fabricated numbers** — "n = 24," "closure rate 4.2 °/s," "HTV vs accuracy r = 0.52, p = .015" — inverting the study's actual null result. The PDF had failed to decode and the summariser invented plausible-looking values. Real text was extracted with `pdftotext`; every Cheetham figure above is from the primary document. **Anything sourced to that dissertation via a fetch-summary elsewhere should be distrusted.**

**Open gaps:** driver-vs-iron split (no source); Betzler face-angle SDs by handicap (paywalled); MacKenzie 2018 torque numerics (expired cert/paywall); grip-strength quantification (does not exist); Sportsbox metric (unconfirmed).
