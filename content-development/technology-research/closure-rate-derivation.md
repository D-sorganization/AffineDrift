# Closure Rate: Derivation of its Effect on Measured Delivery Parameters

Working notes for the impact-mechanics article. Everything here is derived from
rigid-body kinematics; the numeric inputs are flagged where they need literature
verification.

---

## 1. The governing relation

For two points on a rigid clubhead,

$$\mathbf{v}_P = \mathbf{v}_O + \boldsymbol{\omega}\times\mathbf{r}, \qquad \mathbf{r} = \mathbf{p}_P - \mathbf{p}_O$$

Every reference-point effect follows from this one equation. Closure rate enters as a
component of $\boldsymbol{\omega}$.

## 2. The elegant form: it is a ratio of two lengths

Take $\mathbf{r}$ of magnitude $d$ (the CG-to-face-centre separation, 25–50 mm on a
driver) and $\boldsymbol{\omega}$ of magnitude $\omega$ perpendicular to it. The
velocity difference is $\omega d$, so the **angular** difference in path direction is

$$\Delta\theta \approx \frac{\omega d}{v}$$

But $v/\omega$ is precisely the distance from the **instantaneous screw axis**,
$R_{\text{ISA}}$. Therefore

$$\boxed{\ \Delta\theta \approx \frac{d}{R_{\text{ISA}}}\ }$$

**The path difference between two reference points is the ratio of their separation to
the distance from the instantaneous screw axis.** This is the cleanest statement of the
whole reference-point problem, and it says the offset is governed by _where the club is
instantaneously rotating about_, not by speed as such.

### Consistency check against the vendor figure

TrackMan reports ~3° between CG path and face-centre path for a driver. With
$d = 40$ mm:

$$R_{\text{ISA}} = \frac{d}{\Delta\theta} = \frac{0.040}{0.052} \approx 0.77\ \text{m}$$

For comparison, pure rotation about the hands (hub) would give $R \approx 1.6$ m and
only $\Delta\theta \approx 1.4°$. So the ISA sits roughly **half the hub distance** from
the clubhead — the closure rotation pulls it in. That is a sensible number and it means
**closure contributes roughly as much as the arc does.**

## 3. Does the effect scale with swing speed?

$\Delta\theta = \omega d / v$. If closure rate scales proportionally with clubhead speed
— faster swings closing proportionally faster — then $\omega = kv$ and

$$\Delta\theta = k d$$

**independent of swing speed.** The offset is set by technique geometry ($R_{\text{ISA}}$),
not by speed.

This is the correct answer to "does a faster swing amplify the effect?": **not by itself.**
A player who swings faster _in the same geometric pattern_ has the same offset. A player
whose face rotation is fast _relative to_ their clubhead speed — a short, handsy release
that brings the ISA close to the head — has a larger offset at any speed.

The dimensionally correct predictor is therefore $\omega/v$ (units of 1/length), not
$\omega$.

## 4. Magnitudes

$\Delta\theta = \omega d / v$, with $d = 0.04$ m, $v = 50$ m/s (112 mph driver):

| Closure rate $\omega$ | $\omega$ (rad/s) | $\Delta\theta$ (path offset) | Implied $R_{\text{ISA}}$ |
| --------------------- | ---------------- | ---------------------------- | ------------------------ |
| 500 °/s               | 8.7              | 0.40°                        | 5.7 m                    |
| 1000 °/s              | 17.5             | 0.80°                        | 2.9 m                    |
| 2000 °/s              | 34.9             | 1.60°                        | 1.4 m                    |
| 3000 °/s              | 52.4             | 2.40°                        | 0.95 m                   |
| 4000 °/s              | 69.8             | 3.20°                        | 0.72 m                   |

⚠️ **Typical closure-rate values need literature verification.** Back-solving from
TrackMan's 3° total (arc ~1.4° + closure ~1.6°) suggests an effective closure component
around **2000 °/s** near impact for a driver. Treat as an estimate until sourced.

For irons, $d$ is much smaller (CG closer to the face), so the offset falls roughly in
proportion — consistent with TrackMan's statement that non-drivers are "less sensitive to
the point on the club face that is being used."

## 5. Attack angle is affected too

The same $\boldsymbol{\omega}\times\mathbf{r}$ acts vertically. Decomposing with a swing
plane inclined $\beta \approx 55°$ from horizontal and a shaft inclined ~58°:

- **Arc contribution:** face centre sits ahead of the CG on an arc turning upward through
  the bottom → velocity tilted **up** by $\omega_{\text{arc}} d \sin\beta / v \approx 1.2°$
- **Closure contribution:** rotation about a shaft axis leaning toward the golfer gives a
  small **downward** component, $\approx -0.4°$

**Net: face-centre attack angle ≈ 0.7–0.8° shallower (less negative) than CG attack
angle** for a driver. Smaller for irons.

## 6. Face rotation _during_ contact

Contact lasts ~0.4–0.5 ms. The face keeps closing during it:

$$\Delta\text{face} = \omega \cdot \Delta t$$

| Closure rate | Face rotation during 0.45 ms contact |
| ------------ | ------------------------------------ |
| 1000 °/s     | 0.45°                                |
| 2000 °/s     | 0.90°                                |
| 3000 °/s     | 1.35°                                |
| 4000 °/s     | 1.80°                                |

So a high-closure player's face closes by **~1–2° during the collision itself**. Note this
biases toward a _draw_, opposing the reference-point effect of §4.

**This is largely handled by convention:** TrackMan defines face angle at _maximum
compression_ — mid-contact rather than first contact — which is approximately the
time-average. Systems that report face angle at first contact would carry a systematic
open bias for high-closure players.

## 7. The dominant practical effect: timing sensitivity

$$\frac{d(\text{face angle})}{dt} = \omega$$

| Closure rate | Face-angle error per 1 ms of timing error | Per 5 ms |
| ------------ | ----------------------------------------- | -------- |
| 1000 °/s     | 1.0°                                      | 5°       |
| 2000 °/s     | 2.0°                                      | 10°      |
| 3000 °/s     | 3.0°                                      | 15°      |
| 4000 °/s     | 4.0°                                      | 20°      |

Since face angle carries ~85% of launch direction on a driver, and 1° of face-to-path
tilts the spin axis ~4° on a driver, **this is by far the largest consequence of closure
rate.** A high-closure release is a high-gain system: it can square the face, but it
converts small timing errors into large directional errors.

**This, not any systematic bias, is the main reason closure rate matters to a player.**

## 8. Does high closure rate make a player hit a cut?

Three separate mechanisms, and they do not all point the same way:

| Mechanism                                                                        | Direction              | Rough size             | Notes                                              |
| -------------------------------------------------------------------------------- | ---------------------- | ---------------------- | -------------------------------------------------- |
| Reference-point offset (§2–4): true face-centre path is left of reported CG path | **Fade**               | 0.4–3° of face-to-path | Only if the player is held to a _measured_ CG path |
| Face rotation during contact (§6)                                                | **Draw**               | ~0.5–2°                | Mostly absorbed by max-compression convention      |
| Timing sensitivity (§7)                                                          | **Neither — variance** | ±5–20° face            | Dominant effect                                    |

**Conclusion.** It is _not_ fair to say a high-closure player is systematically a cutter in
free play — players calibrate to ball flight, and the draw-side mechanism partly cancels the
fade-side one. But it **is** fair to say that a high-closure player who is coached to a
_number_ — "get your path to zero" on a CG-referenced radar unit — is being trained toward a
delivery whose true contact-point path is further left, and so is being biased toward a cut
by the measurement convention rather than by their swing.

The honest headline is that closure rate is primarily a **dispersion** variable, not a
**bias** variable.

## 9. Interaction with gear effect

Closure rate and gear effect are separate mechanisms (gear effect depends on impact offset
and head MOI, not on $\omega$), but they compound in one respect: a high-closure player who
is also inconsistent in strike location gets face-angle variance _and_ gear-effect
spin-axis variance from the same mistimed release, since a late or early release tends to
move the strike toward heel or toe respectively.

## 10. What to verify in the literature

1. Typical closure rates (°/s) for driver and iron, tour vs amateur — **the key missing number**
2. Whether closure rate scales with clubhead speed (tests the §3 speed-invariance prediction)
3. Measured face-angle standard deviation at impact and whether it correlates with closure rate
4. Contact duration primary source
5. Whether any vendor reports face angle at first contact rather than max compression
