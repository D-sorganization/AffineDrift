# The Club–Ball Collision — Research Dossier

Compiled 2026-07-30. Verification key: ✅ primary text read · 🟡 metadata/abstract verified,
full text not obtained · ❌ **unverified — do not cite**.

---

## 1. Normal impact

### 1.1 The governing relation

$$\frac{v_{\text{ball}}}{v_{\text{club}}} = \frac{1+e}{1+m/M}$$

This is _identical_ to the normal-direction equation in Kensrud/Nathan/Smith's baseball
work: $v_{\text{ball},n} = [(1+e_y)/(1+r_y)]\,v_{\text{bat},n}$ with $r_y = m/M_{\text{eff}}$.
**The golf and baseball formalisms are the same equation.**

Ceiling `[COMPUTED]`: ball 45.93 g, head 200 g, $e = 0.83$ → $1.83/1.2297 = 1.488$. This is
the origin of the "smash factor ≈ 1.50" ceiling. ⚠️ Popular sources assert 1.50 but **no
primary derivation was located** — derive it, don't cite it.

### 1.2 COR limit — a real numerical conflict

- **0.822** — USGA's own 2025 article: _"The USGA's limit for COR for a golf club is 0.822,
  which hasn't changed since 1998"_
  ([usga.org](https://www.usga.org/content/usga/home-page/articles/2025/05/what-happens-collision-between-club-ball.html)).
- **0.830** — cited as "the USGA COR limit" by secondary sources.

Almost certainly **0.822 limit + 0.008 tolerance = 0.830 conformance threshold**, parallel to
the CT structure below — ⚠️ **but this reconciliation was NOT verified from a primary
document.** The USGA page 403s to direct fetch; text came via search index.

The USGA article also defines COR as _"ball speed after impact minus club speed after impact,
divided by club speed before impact"_ — that is **apparent COR (ACOR)**, not classical
relative-velocity COR. The two differ by the mass ratio. Worth flagging explicitly.

### 1.3 Characteristic Time — and the conflation to avoid

- Introduced 2004 to replace COR for policing spring-like effect in **drivers only**; COR
  remains the method for fairway woods, hybrids and irons.
- Pendulum test: a steel ball with internal sensors strikes the face; sensors time the contact.
- **Limit 239 µs, tolerance 18 µs, ≤ 257 µs conforms.**
- Procedure: USGA TPX3004. ⚠️ **PDF is Akamai-blocked (403); steel-ball mass, pendulum speed,
  and CT↔COR mapping remain unverified.**

> **The 239 µs CT is NOT the golf-ball contact time (~450–500 µs).** It is a small steel
> pendulum ball on the face, a proxy for face flexibility. Popular literature conflates these
> constantly and they are the same order of magnitude.

### 1.4 COR versus speed

**Arakawa 2009** (_Exp. Mech._ 49(4) 471–477, DOI 10.1007/s11340-008-9156-y), abstract
verbatim: _"As the inbound ball velocity increased, the maximum normal compression ratio
increased while the maximum tangential compression ratio, contact time and coefficient of
restitution decreased."_ Also: **Hertz theory predicted maximum normal force well.**

This monotonic decline is why ball-COR testing is speed-normalised — USGA-adjacent patent
text describes correcting _"as if the ball had an incoming speed of exactly 125.0 fps"_
(air-cannon range 50–180 ft/s; e.g. US6945880). ⚠️ Specific COR-vs-speed curves ❌ not verified.

### 1.5 COR versus loft `[ANALYSIS, not cited]`

Loft doesn't change material COR; it changes which velocity component COR acts on. Only
$v\cos\delta$ ($\delta$ = spin loft) drives normal compression, so a normal-only model
predicts smash factor falling as $\cos^2\delta$. **Known incomplete:** measured driver smash
(~1.48–1.50 at ~11° dynamic loft) _exceeds_ $1.488 \times 0.967 = 1.44$, because the
tangential impulse also contributes forward ball speed. ❌ No measured COR-vs-loft dataset found.

---

## 2. Contact duration and peak force

**Duration.** USGA (2025): _"Impact lasts for about 500 microseconds, or half a millisecond"_
(⚠️ search-index only, direct fetch 403).

**Roberts, Jones & Rothberg**, _Sports Engineering_ **4**, 191–203 (2001) — measured contact
time by making **the ball and clubface act as a switch closing an electrical circuit**, across
**5 clubhead types × 2 ball constructions**. ⚠️ **Method verified; the measured values could
NOT be extracted — Loughborough repo and Springer both 403.** This is the highest-value gap
in the dossier.

Contact time _decreases_ with impact speed (Arakawa 2009), so "0.45 ms" vs "0.50 ms" is not a
contradiction — driver at the short end, wedge/putt at the long end.

**Peak force.** USGA: _"upwards of 3,000 pounds of force"_ (≈13.3 kN). Consistency check
`[COMPUTED]`: $J = 0.0459 \times 67 = 3.08$ N·s over 0.45 ms → mean 6.8 kN; half-sine peak
$= (\pi/2)\times$ mean ≈ **10.7 kN ≈ 2,400 lbf**. Correct order, USGA slightly conservative-high.
A "4,000 lbf" figure circulates on low-quality sites — ❌ **discard.**

**FE calibration note:** golf-ball FE material constants are fitted against maximum load,
contact time, deformation history and rebound velocity _simultaneously_ — contact time is a
model-identification target, not merely an output.

---

## 3. Oblique impact theory

### 3.1 Maw–Barber–Fawcett

**MBF 1976** (_Wear_ 38, 101–114, DOI 10.1016/0043-1648(76)90201-5): Hertzian normal
components with the contact area comprising **coexisting stick and slip regions** under
constant Coulomb friction; the mixed boundary-value problem reduced by **dividing the contact
circle into concentric annuli**. Trajectory depends on two non-dimensional parameters.

Cross's summary ✅ (read verbatim from Cross 2002):

> "the approach is to divide the contact circle into small annuli, some of which grip the
> surface and some of which slip. Because the component of the normal reaction force acting on
> the outermost annulus is zero, this and several adjacent annuli usually slip … As time
> progresses, the annuli in slip spread radially inward, reducing the friction force to zero
> and then reversing it. Near the end of the bounce period the whole contact area slides
> backwards on the surface."

**MBF vs Brody ✅:** Brody assumed the ball begins **rolling** when $v_x = R\omega$, at which
point $F$ drops instantly to zero. **MBF assume the whole contact area _sticks_** at that
instant. MBF's friction decays smoothly and then **reverses sign**. Friction reversal is the
experimental signature distinguishing grip from roll.

**MBF 1981** (_J. Lubr. Technol._ 103, 74–80, DOI 10.1115/1.3251617), abstract verbatim:
_"The tangential compliance of the contact surface under the action of Coulomb friction is
shown to have a significant effect on the rebound angles, if the local angle of incidence does
not greatly exceed the angle of friction."_ Test disk sliced from a 4-inch ball bearing; good
agreement at μ = 0.115.

### 3.2 Stronge

_Impact Mechanics_ (CUP 2000/2018), Ch. 5 "Tangential Compliance in Planar Impact of Rough
Bodies," pp. 89–115, DOI 10.1017/9781139050227.007; and _IJIE_ **15**, 435–450 (1994),
DOI 10.1016/0734-743X(94)80027-7.

Stronge replaces MBF's annular distribution with a **lumped two-spring contact** (normal $k_n$,
tangential $k_t$). Three regimes: initially sticks / slides then sticks / slides throughout.
Tangential compliance _reduces_ the largest friction force relative to a rigid contact.

**Energetic COR** = square root of the fraction of compression-phase strain energy released
during restitution. It measures dissipation directly and is **guaranteed energy-consistent**,
unlike kinematic (Newton) or kinetic (Poisson) definitions, which can be non-conservative in
oblique/eccentric impacts. **This is the definition a rigorous treatment should adopt.**

### 3.3 Three contact regimes (tangential COR $e_x$)

1. **Gross slip** — slides throughout, $e_x < 0$
2. **Rolling** — sliding ceases mid-impact, $e_x = 0$
3. **Gripping** — grips and stretches tangentially, $e_x > 0$

---

## 4. Rod Cross's experiments — the load-bearing empirical section

_Everything in §4 read directly from Cross 2002 full text_ ✅
(_Am. J. Phys._ **70**(11) 1093–1102, DOI 10.1119/1.1507792,
[PDF](https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/GripSlip.pdf)).

**Method:** 340 g wood block on frictionless rollers; 19 mm × 0.3 mm ceramic piezo disk
measures horizontal friction force; two 51 mm piezo blocks form a normal force plate.
Calibrated absolutely by $\int F\,dt = \Delta(mv_x)$ and $\int N\,dt = \Delta(mv_y)$.

**Core result** ✅:

> "Measurements of the friction force on a bouncing ball demonstrate that **balls can slide on
> a surface or they can grip the surface but they do not roll.** As a result, balls can spin
> faster than allowed by the rolling condition $\omega_2 = v_{x2}/R$ and they can bounce with a
> horizontal coefficient of restitution greater than zero."

Friction force **reverses** during the bounce — once or twice for a tennis ball, **six times
for a basketball**. Confirms MBF qualitatively.

### Golf-ball-specific measured values ✅

| Quantity                                     | Value                                                                |
| -------------------------------------------- | -------------------------------------------------------------------- |
| Mass / radius / $\alpha$ ($I = \alpha mR^2$) | 45.5 g / 21.3 mm / **0.40**                                          |
| $\mu$, golf ball on polished granite         | **0.18**                                                             |
| Normal COR $e_y$                             | **0.90 ± 0.02**, _independent of incidence angle_ (low speed ~4 m/s) |
| Tangential COR $e_x$ when gripping           | **≈ 0.1**                                                            |
| Slides throughout for                        | $\theta_1 \lesssim 40°$ (Eq. 7 predicts 39.9°)                       |
| **Maximum spin occurs at**                   | **$\theta_1 \approx 40°$** — the slide→grip transition               |
| Superball comparison                         | $\mu \gtrsim 0.9$, $e_y = 0.97$, $e_x = 0.49$                        |

⚠️ Cross's $\theta_1$ is measured **from the surface plane**; the golf analogue is
(90° − spin loft) with the clubface as the surface.

### Spin equations ✅

Pure sliding throughout:
$$v_{x2} = v_{x1} + \mu(1+e_y)v_{y1}, \qquad \omega_2 = \omega_1 - \frac{(R\mu + D)(1+e_y)v_{y1}}{\alpha R^2}$$

$$e_x = -\frac{v_{x2} - R\omega_2 - V_2}{v_{x1} - R\omega_1}$$

Spin-parameter limits for a solid sphere ($\alpha = 0.4$):

- **Rolling:** $R\omega_2/v_1 = \tfrac57\cos\theta_1$
- **Garwin ideal ($e_x = e_y = 1$):** $\tfrac{10}{7}\cos\theta_1$ — **exactly twice rolling**
- **Sliding throughout:** $2.5\mu(1+e_y)\tan\theta_1$ → spin → 0 at glancing incidence

**Cross's verdict on golf specifically** ✅: _"Brody's model provides a better quantitative
description in the case of a golf ball, presumably because the storage and recovery of elastic
energy due to tangential compliance is less efficient for the golf ball, giving a value for
$e_x$ of only about 0.1 when the ball grips."_ MBF is qualitatively right; Brody is
numerically closer **for golf**. Say this plainly.

### The overlooked third spin mechanism — offset normal force ✅

$R\!\int\!F\,dt$ was consistently **30–40% less** than the measured change in angular momentum
(only 3% low for the superball). Resolution: the normal reaction acts a distance $D$ _behind_
the centre of mass, adding torque $ND \approx 0.3FR$. $D \approx R/10$ — 2–3 mm for tennis
balls and baseballs, **< 0.5 mm for golf balls**. Mechanically analogous to weight transfer
onto the front wheels under braking.

⚠️ **Minor for golf** given $D < 0.5$ mm — but it is a genuine third spin source alongside
friction and tangential compliance, and it is essentially never mentioned in golf literature.

### Cross & Dewhurst 2018 — the direct golf transfer

_Eur. J. Phys._ **39**(6) 065003, DOI 10.1088/1361-6404/aadda8. Abstract verbatim:

> "The impact of a golf club with a golf ball has previously been analysed by several authors,
> **assuming that the ball rolls across the club face**. In this paper it is shown that **the
> ball grips the club face, rather than rolling**, with the result that the **outgoing ball
> spin is generally larger than previously estimated**. Experimental results are presented for
> three different balls, showing that the ball spin can vary from one ball to the next,
> **depending on the tangential coefficient of restitution of the ball**."

⚠️ Full text not obtained; the three balls' $e_x$ values ❌ unverified. **Most on-point
citation for golf impact — obtain in full.**

### Kensrud/Nathan/Smith 2017 — the transferable formalism

_Am. J. Phys._ **85**(7) 503–509, DOI 10.1119/1.4982793,
[arXiv:1610.03464](https://arxiv.org/abs/1610.03464).

$$
v_{\text{ball},n} = \left[\tfrac{1+e_y}{1+r_y}\right]v_{\text{bat},n}, \qquad
v_{\text{ball},t} + r\omega = \left[\tfrac{1+e_x}{1+r_x}\right]v_{\text{bat},t}
$$

Measured tangential COR: **baseballs 0.405 ± 0.010; softballs 0.146 ± 0.009.** Grip yields
spin **up to 40% above the rolling prediction.** Stiffness ratio $\eta^2 = k_n/k_t$: baseball
4.75, softball 6.30. Data **rule out gross slip**; $\mu_k \ge 0.15$–0.20.

> **Ordering worth stating in a textbook:** golf $e_x \approx 0.1$ < softball 0.146 <
> baseball 0.405 < superball 0.49. **The golf ball is among the tangentially stiffest sports
> balls**, which is exactly why golf spin sits closer to the rolling limit than baseball spin.

---

## 5. Spin generation — three contributors, in order for golf

1. **Coulomb friction impulse**, $\Delta L = R\!\int\!F\,dt$ — dominant
2. **Tangential compliance / grip** — adds spin beyond the rolling limit; $e_x \approx 0.1$
   for golf, real but modest
3. **Offset normal force** ($ND$) — negligible for golf ($D < 0.5$ mm)

**"Super-spin":** the rolling limit is _not_ a ceiling. $R\omega_2/v_{xR} > 1$ means the ball
is sliding _backwards_ on the face at separation. Garwin's $e_x = 1$ ideal gives exactly 2×
rolling spin; no real ball reaches it.

### The friction-saturation "spin loft cliff"

Cross's Eq. (7) gives a critical incidence angle separating pure sliding from gripping —
**≈ 40° for a golf ball on granite, and peak spin occurs exactly there.** Below it spin falls
as $2.5\mu(1+e_y)\tan\theta_1$; above it the ball grips. **This is the spin-loft cliff with a
first-principles basis**, and the critical angle scales with $\mu$ — which is why the cliff
moves when the face is wet or grassy.

⚠️ The coaching claim that "maximum spin occurs at ~45–50° spin loft" is ❌ **not verified
against a primary source**, and being $\mu$-dependent it may not be a universal constant at all.

### Grooves, moisture, grass

**Peer-reviewed:** Monk, Davis, **Otto** & Strangwood, _Sports Engineering_ **8**(1) 3–11
(2005), DOI 10.1007/BF02844127. S. R. Otto is the R&A's Director of Research — closest thing
to a governing-body peer-reviewed source on face-surface effects. ⚠️ Findings ❌ unverified
(paywalled).

**2010 groove rule:** limits groove **volume** (all clubs but drivers and putters) and groove
**edge sharpness** (lofts ≥ 25°). New models manufactured after 1 Jan 2010; CoC at elite pro
level from 2010, elite amateur/other pro from 2014. Rationale: joint USGA/R&A 2007–08 research
found "the rough had become less of a challenge for expert players"; the rule restores the
fairway-vs-rough spin differential.
⚠️ **Numeric specs ❌ NOT verified** — the R&A URL is dead and the one PDF found is scanned
images with no extractable text.

**The physically correct framing:** grooves do not primarily "grip." They are **drainage
channels** evacuating water, grass and debris so dry rubber-on-metal friction can be
established. Moisture lowers $\mu$, which via Cross's Eq. (7) **lowers the critical angle**,
pushing normal-loft shots into the pure-sliding regime where spin scales as
$2.5\mu(1+e_y)\tan\theta_1$ — **spin falls roughly linearly in $\mu$.** That is the flier lie,
and it is a direct prediction of verified physics. (Supporting sources here are coaching-grade.)

---

## 6. FE and numerical models

**Tanaka 2006** (_IMechE Part L_ 220, 13–22, DOI 10.1243/14644207JMDA80), abstract verbatim:
FE model with **hyperelasticity and viscoelasticity** — **Mooney-Rivlin plus a three-element
viscoelastic model**; normal and oblique impacts against a rigid body.

**Tanaka 2013** (_IMechE Part P_ 227, 20–30, DOI 10.1177/1754337112442117): ball from solid
elements; club from CAD of a commercial driver, **head solid, shaft shell**, with elasticity;
studied impact point and club posture. "Closely matched the experimental results."

- **Caldwell & McPhee 2024**, "Three-dimensional golf clubhead-ball impact models for drivers
  and irons," _Sports Engineering_ **27**, DOI 10.1007/s12283-024-00456-6 — current state of
  the art for real-time 3-D impact models. 🟡
- **McPhee 2022**, "A review of dynamic models and measurements in golf," _Sports Engineering_
  **25**, DOI 10.1007/s12283-022-00387-0 — modern companion to Penner. ⚠️ Paywalled, not read.

---

## 7. Penner 2003 — the canonical review

A. R. Penner, "The physics of golf," _Rep. Prog. Phys._ **66**(2) 131–171 (2003),
DOI 10.1088/0034-4885/66/2/202.

⚠️ **Metadata and scope verified; full text NOT obtained.** IOP/ADS 403;
www.raypenner.com has an **expired TLS certificate**.

Verified scope: swing as a double pendulum; then, for impact, "reviews **measurements and
models of the impact of golf balls with barriers**," and examines "the effects that the
**curvature of a clubface** (bulge and roll) and the **moments of inertia of the clubhead**
have on the launch parameters and trajectory of an **off-centre impacted golf ball**."

**This is the entry point for two things this dossier could not otherwise source:** the
barrier-impact COR literature (COR-vs-speed, COR-vs-material) and **gear effect**. Penner's
companion paper "The physics of golf: The convex face of a driver" treats bulge-and-roll.
**§7 is a placeholder until the full text is obtained.**

---

## 8. Gap register — priority order

| #   | Item                                                                   | Blocker                             | Priority                   |
| --- | ---------------------------------------------------------------------- | ----------------------------------- | -------------------------- |
| 1   | Roberts/Jones/Rothberg 2001 measured contact times (5 heads × 2 balls) | repo + Springer 403                 | **Highest**                |
| 2   | USGA TPX3004 CT procedure                                              | Akamai 403                          | **Highest**                |
| 3   | COR 0.822 vs 0.830 reconciliation                                      | USGA page 403                       | High                       |
| 4   | Penner 2003 full text — barrier COR, gear effect                       | IOP 403; author site cert expired   | High                       |
| 5   | Cross & Dewhurst 2018 full text — golf $e_x$ for three balls           | IOP paywall                         | High                       |
| 6   | COR-vs-speed curve values                                              | trend verified, values not          | Medium                     |
| 7   | COR-vs-loft dataset                                                    | none found                          | Medium                     |
| 8   | Groove-rule numeric specs                                              | R&A URL dead; PDF is scanned images | Medium                     |
| 9   | Monk et al. 2005 findings                                              | Springer paywall                    | Medium                     |
| 10  | Gobush, _Science and Golf II_ 381–387                                  | metadata only                       | Medium                     |
| 11  | Primary derivation of the 1.50 smash ceiling                           | secondary assertions only           | Low (derivable)            |
| 12  | "45–50° spin loft maximises spin"                                      | coaching sources only               | Low — likely not universal |
| 13  | "4,000 lbf peak force"                                                 | one low-quality site                | **Discard**                |

Items 1–5 are paywall/WAF blocks, not dead ends — an institutional library session clears them.

---

## 9. The two most consequential corrections to conventional golf writing

1. **CT 239 µs ≠ ball contact time.** The former is a steel pendulum ball measuring face
   flexibility; the latter is ~450–500 µs. The literature conflates them constantly.
2. **The ball grips the face; it does not roll.** Cross 2002 ✅ and Cross & Dewhurst 2018 both
   state this, and it means every rolling-contact-based golf spin model **systematically
   under-predicts spin**. Golf's $e_x \approx 0.1$ is small next to baseball's 0.405, so the
   error is smaller in golf — but it is not zero and it is consistently signed.
