# Golf Ball Spin Decay — Published Rates, Models, and a Model/Measurement Conflict

Compiled 2026-08-03. Unusually well-sourced; includes a caught unit error in the source and
a genuine unresolved conflict between models and radar measurement.

---

## The key accessible source

**A. M. Nathan, "The Effect of Spin-Down on the Flight of a Baseball" (2008)** —
https://baseball.physics.illinois.edu/spindown.pdf

Despite the title, §II is entirely about golf balls and reproduces **both** Smits & Smith and
Tavares numerically. It is the only fetchable document found stating both primary results,
and it reproduces Smits & Smith's Fig. 1. Ball properties used: M = 0.04593 kg,
R = 0.02134 m, I = 0.4MR².

---

## 1. The models

### Smits & Smith (Science and Golf II, 1994, pp. 340–347)

Wind tunnel. Found **ω̇R²/v² approximately linear in S and independent of Re** over
Re = (1.0–2.5)×10⁵. Nathan's Eq. 5:

$$\frac{d\omega}{dt} = -2.0\times10^{-5}\,\frac{v^2}{R^2}\,S \;=\; -2.0\times10^{-5}\,\frac{v\,\omega}{R}$$

Equivalent β = 0.0096.

> ⚠️ **Unit error in the source, caught by arithmetic.** Nathan's Eq. 5 text says "with v in
> mph," but footnote 5 says "The numerical factor is 2.0×10⁻⁵ if v is in m/s," and the printed
> coefficient is 2.0×10⁻⁵ in both places. Checking against his own stated τ = 23.8 s at
> 100 mph: R/(2.0×10⁻⁵ × 44.7 m/s) = 23.9 s. **v must be in m/s.** Implementing from the
> equation text with mph gives a 2.24× error.

### Tavares, Shannon & Melvin (Titleist), Science and Golf III

Full citation: G. Tavares, K. Shannon, T. Melvin, "Golf ball spin decay model based on radar
measurements," _Science and Golf III_, Proc. 1998 World Scientific Congress on Golf, eds.
Farrally & Cochran, **Human Kinetics, Champaign IL, 1999, pp. 464–472** (congress 1998,
volume published 1999).

Method: novel radar gun measuring time-dependent spin in real flight.
Result **C_M ≈ 0.012·S**, i.e. dω/dt = −2.5×10⁻⁵ v²S/R² (v in m/s). **25% larger than Smits.**

### The correct nondimensionalisation

$$I\,\frac{d\omega}{dt} = -R\,\rho\,A\,C_M\,v^2, \qquad A = \pi R^2,\quad I = 0.4MR^2$$

Reference quantity is ρAv²R — **note there is no factor of ½**, unlike the C_D/C_L convention.
This is a common source of factor-of-two errors.

> ⚠️ **C_M is NOT a constant.** It is linear in S: C_M ≈ βS with β = 0.0096 (Smits) or
> 0.012 (Tavares). The often-quoted "0.005–0.01" matches **β**, not C_M. At driver conditions
> (S ≈ 0.10–0.15) the actual **C_M ≈ 0.0010–0.0018**.

### Time constants

τ = (M/R²)·α/(πρβv), so **τ ∝ 1/v** — the literature does _not_ use a constant τ.

| v (m/s)            | τ Smits | τ Tavares | %/s Smits | %/s Tavares |
| ------------------ | ------- | --------- | --------- | ----------- |
| 70 (driver launch) | 15.6 s  | 12.5 s    | 6.4       | 8.0         |
| 60                 | 18.2 s  | 14.6 s    | 5.5       | 6.9         |
| 50                 | 21.8 s  | 17.5 s    | 4.6       | 5.7         |
| 44.7 (100 mph)     | 24.4 s  | 19.5 s    | 4.1       | 5.1         |
| 30 (late flight)   | 36.4 s  | 29.1 s    | 2.7       | 3.4         |

Closed forms: τ_Smits ≈ 1092/v s, τ_Tavares ≈ 874/v s (v in m/s). Range across a driver
trajectory: **roughly 12–37 s**.

---

## 2. The USGA adopted Smits exactly

**US Patent 6,186,002 B1**, "Method for determining coefficients of lift and drag of a golf
ball," Lieberman, Smith, **Quintavalla**, Thomas & Winfield (USGA), granted 13 Feb 2001 —
https://patents.google.com/patent/US6186002B1/en

ITR trajectory model uses ω̇ = −SRD·ω|V|/r with **SRD = 2×10⁻⁵** — algebraically identical to
Smits & Smith. (⚠️ The patent text carries both "SRD = a constant equal to −0.00002" _and_ a
leading minus, which would double-negate to spin-up — almost certainly a sign-convention slip;
the magnitude is unambiguous.)

Key ITR caveat, quoted: **"The angular velocity does not significantly change down the 70 foot
ITR."** So the USGA extracts C_L and C_D at effectively constant spin and applies decay only
in the downstream full-trajectory integration.

Quintavalla's _Science and Golf IV_ (2002) paper is a **lift/drag** model; no evidence it
contributes a spin-decay model of its own. ⚠️ Primary text not accessed.

---

## 3. ⚠️ THE IMPORTANT CONFLICT: models overpredict measured decay by 2–3×

**Radar-measured data** (Acushnet/Titleist, US 8,016,695 and US 8,529,373, TrackMan-measured —
https://patents.google.com/patent/US8529373B2/en). Table 6B:

| Ball                   | Club   | 1 s  | 3 s   | 5 s   |
| ---------------------- | ------ | ---- | ----- | ----- |
| Pro V1x (prior art)    | Driver | 3.1% | 8.8%  | 12.8% |
|                        | 5 iron | 3.4% | 9.7%  | 15.5% |
|                        | 8 iron | 3.6% | 9.0%  | 13.3% |
| Invention (high decay) | Driver | 6.2% | 15.8% | 21.3% |
|                        | 5 iron | 4.8% | 12.0% | 16.6% |

Implied τ: Pro V1x driver **τ ≈ 32–37 s** (~3%/s). But Smits predicts τ ≈ 16 s and Tavares
τ ≈ 12 s at 70 m/s launch — i.e. **6–8%/s**.

**The models overpredict measured driver spin decay by roughly 2–3×.**

Compounding it: the models say decay rate ∝ v, so %/s should fall sharply as the ball slows —
yet measured Pro V1x driver rate is nearly constant (3.1%/s in second 1 versus ~2.7%/s averaged
over 5 s). US 8,016,695 states directly: _"spin rate will decline more rapidly in the first
second of flight, but after about two seconds, the spin rate and spin decay rate over the
remainder of the flight becomes substantially equal."_

**No source found that reconciles these. Do not treat 4%/s and C_M = 0.012S as
interchangeable.**

⚠️ The 8-iron 3 s value (8.7%) is lower than the 5-iron (12.0%) and breaks monotonicity with
the 1 s column — possibly an OCR/transcription artifact; read via Google Patents OCR of a
scanned page.

---

## 4. The "4% per second" radar figure — chain of custody

Appears in peer-reviewed literature at: **Lyu, Kensrud, Smith & Tosaya (WSU Sports Science
Lab), "Aerodynamics of Golf Balls in Still Air," _Proceedings_ 2018, 2(6), 238** —
https://www.mdpi.com/2504-3900/2/6/238

> "All balls were given identical release conditions of 71.5 m/s; 6° launch angle; and
> 3000 rpm backspin with **4% per second spin decay [21]**."

Their **reference [21] = "Trackman Newsletter #7, p. 7"**, whose URL is **dead**. So 4%/s is
properly attributable but **not independently verified at source**.

---

## 5. Dependence on speed, spin, construction

- **Speed and spin:** ω̇ ∝ v·ω (≡ v²S) in every model. Smits found the nondimensional group
  **independent of Reynolds number** at fixed S over Re = 1.0–2.5×10⁵.
- **Moment of inertia:** τ scales as M/R² at fixed α, β. Golf 101.2 kg/m² vs baseball
  109.4 kg/m² → baseball τ 8% longer. Redistributing mass outward (raising α) raises τ
  proportionally. **The cleanest published construction-dependence result.**
- **Dimple pattern:** Acushnet's patents are built on the premise that dimple geometry tunes
  decay (they nearly double it), so the effect is real and large — but they disclose the
  _outcome_, not a coefficient. ⚠️ No published β as a function of dimple geometry found.
- ⚠️ **Cover material (urethane vs ionomer) — NO SOURCE FOUND.** Everything returned concerns
  spin _generation at impact_, a completely different phenomenon. Do not assume a decay effect
  exists.
- General sports-ball context: Sheffield Hallam, "The Spin Decay of Sports Balls in Flight"
  (https://shura.shu.ac.uk/2132/) reports a strong linear relationship between spin decay and
  the product of initial spin and speed — consistent with ω̇ ∝ vω. ⚠️ **Tested tennis balls and
  footballs, no golf balls.**

---

## 6. Does spin decay matter to carry?

- **Nathan (2008) §III**: for baseballs, trajectories with the golf-derived k = 0.02 versus
  k = 0 (no spin-down) are _"barely distinguishable"_ — _"spin decay plays only a minor role."_
  Note: a baseball result using golf-derived coefficients, not a golf carry study.
- **Acushnet US 8,016,695 Table 6A**: roughly **doubling** spin decay (3.1% → 6.2% at 1 s,
  driver) changes carry by **+1 to +3 yards**. Direction: **more decay → slightly more carry**,
  because reduced late-flight spin cuts lift-induced drag and ballooning. That is ~0.4–1% of a
  270 yd drive.

**Read:** spin decay is **second-order** for carry — far smaller than the 18 m spread Lyu et al.
found across ball models from C_L/C_D differences alone — but not negligible at tour or
regulatory precision, and large enough that Acushnet patented tuning it.

---

## 7. Not verified

1. Smits & Smith 1994 and Tavares 1998 primary texts — not online; all numbers via Nathan (2008).
2. TrackMan Newsletter #7 — dead link.
3. Quintavalla _Science and Golf IV_ (2002) — inaccessible; no spin-decay content confirmed either way.
4. Tavares' MOI/dimple-depth findings — secondhand snippets only.
5. Cover material effect on decay — no source found.
6. "A review of dynamic models and measurements in golf" (doi:10.1007/s12283-022-00387-0) — paywalled; likely the best modern synthesis.
