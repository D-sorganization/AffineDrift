# Golf Ball Aerodynamics — Model Structures and Gap Register

Compiled 2026-08-03. **Provenance warning:** the research agent for this topic emitted
before its retrieval threads reported. Only the computed material below is verified in
session. Coefficient values for all three canonical models were **not retrieved**, and are
recorded here as gaps rather than filled with plausible-looking numbers. A fabricated
coefficient in a reference document propagates indefinitely.

---

## 1. Reynolds-number anchor `[COMPUTED — verified]`

Ball diameter 42.67 mm, Re = Vd/ν.

| V (m/s) | V (mph) | Re @ 0 °C (ν=1.33e-5) | Re @ 15 °C (ν=1.47e-5) | Re @ 30 °C (ν=1.60e-5) |
| ------- | ------- | --------------------- | ---------------------- | ---------------------- |
| 30      | 67      | 96,200                | 87,100                 | 80,000                 |
| 45      | 101     | 144,400               | 130,600                | 120,000                |
| 60      | 134     | 192,500               | 174,200                | 160,000                |
| 70      | 157     | 224,600               | 203,200                | 186,700                |
| 90      | 201     | 288,700               | 261,200                | 240,000                |

**The framing fact:** a golf ball spends its entire flight in **Re ≈ 0.7–2.6 × 10⁵**, which
sits _above_ the dimpled-ball drag crisis and _below_ the smooth-sphere crisis. The ball is
always supercritical. Every model discussed is a fit over this window and is being
extrapolated outside it.

Note the temperature spread: at fixed ball speed, 0 °C versus 30 °C moves Re by ~20%, so any
Re-dependent model predicts a genuine temperature effect on Cd _independent of_ air density.
Most popular simulators ignore this.

**Spin ratio** S = ωR/V `[COMPUTED]`: driver at 3000 rpm and 70 m/s → **S ≈ 0.096**; wedge at
10,000 rpm and 30 m/s → **S ≈ 0.74**. Useful domain **S ∈ [0.05, 0.8]**, driver flight
concentrated at S ≈ 0.1–0.25, rising through flight as V decays faster than ω.

**Ball constants** `[COMPUTED]`: A = π(0.021335)² = **1.430×10⁻³ m²**; uniform-sphere
I = (2/5)mR² = **8.36×10⁻⁶ kg·m²** (real multi-layer balls differ, construction-dependent).

---

## 2. The three canonical models — structures, not coefficients

| Model                                                               | Basis                                                                              | Form                                                                             | Coefficients                                                                              |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Bearman & Harvey (1976)**, _Aeronautical Quarterly_ 27(2) 112–122 | Imperial College wind tunnel, scaled-up spinning model, round vs hexagonal dimples | Cd, Cl as functions of **both** Re and spin ratio                                | **NOT RETRIEVED**                                                                         |
| **Smits & Smith (1994)**, _Science and Golf II_ pp. 340–347         | Princeton spinning-ball tunnel                                                     | Closed-form in spin ratio W with a Re correction; low-order polynomial/power-law | **NOT RETRIEVED**                                                                         |
| **Quintavalla (2002)**, _Science and Golf IV_ pp. 341–348           | USGA Indoor Test Range, full-trajectory optical tracking, **inverse fit**          | Six-term expansion in Re and S                                                   | **NOT RETRIEVED — may be genuinely unpublished**, since the ITR underpins ODS conformance |

Qualitative findings that are secure:

- Cl increases monotonically with S, steeply at low S then flattening.
- **Cd also increases with S** — backspin costs drag as well as buying lift, which is why an
  optimum spin exists rather than "more spin = more carry."
- Hexagonal dimples produced lower drag than round in B&H.
- Increasing spin shifts the drag crisis to lower Re.

---

## 3. Why trajectory-derived coefficients differ from wind-tunnel ones

This is mechanism reasoning, not retrieved fact, but the mechanisms are well established:

1. **Support interference.** A tunnel ball must be held and spun by hardware sitting in the
   near wake — exactly the region setting pressure drag. Free flight has none.
2. **Tunnel turbulence intensity** promotes transition and **shifts Re_crit**, so two
   facilities need not report the same critical Reynolds number for the same ball.
3. **Fixed vs decaying spin.** A tunnel holds ω constant and samples the (Re, S) plane on a
   grid; a real trajectory traces a _curve_ through it, with S sweeping upward. Inverse fits
   are weighted toward where real balls actually go — arguably a feature for a conformance test.
4. **Dimple-pattern orientation.** A ball is not aerodynamically axisymmetric; free flight
   averages over orientations, a tunnel may not. This is the physical basis for the
   spherical-symmetry rule and the Polara ruling.
5. **Scale effects** — B&H used an oversized model to reach flight Re, matching Re but not
   every ratio of dimple depth to boundary-layer thickness.
6. **What you are actually fitting.** Inverse-fitted coefficients absorb _every_ modelling
   error in the integrator — spin-decay law, air properties, launch measurement. **Ported into
   a different integrator with a different spin-decay law they are no longer guaranteed
   correct.** This is the most important practical caveat and it is rarely stated.

---

## 4. Spin decay

Standard form ω(t) = ω₀ exp(−t/τ). **Published τ not retrieved.** Internal consistency check:
~6–7 s hang time with spin falling roughly a quarter to a third implies **τ of order 20–30 s**
`[inferred, not sourced]`. A commonly quoted radar figure of ~4%/s corresponds to
τ ≈ 24.5 s `[COMPUTED]` — consistent, but the percentage itself needs a primary source.

The moment-coefficient formulation is more physical (decay depends on flight state rather than
a fixed clock) but **the two are not equivalent**: constant τ implies decay independent of
airspeed, C_M implies faster decay at higher speed. They diverge most for unusual speed/spin
combinations — exactly the shots one cares about. Nondimensionalisation varies between authors
and is a common source of factor-of-two errors.

**Priority retrieval:** Tavares, Shannon & Melvin, "Golf ball spin decay model based on radar
measurements," _Science and Golf III_, 1998.

---

## 5. Equations of motion and atmosphere `[standard]`

$$m\,d\mathbf{V}/dt = -\tfrac12 \rho A C_D |\mathbf{V}|\mathbf{V} + \tfrac12 \rho A C_L |\mathbf{V}|^2 \hat{\mathbf{n}} + m\mathbf{g}, \qquad \hat{\mathbf{n}} = \frac{\boldsymbol\omega\times\mathbf{V}}{|\boldsymbol\omega\times\mathbf{V}|}$$

**Two convention traps:** some authors write the Magnus term with an _unnormalised_
(ω × V), folding |ω||V|sinθ into the coefficient — mixing conventions gives badly wrong
answers. And spin axis tilt makes n̂ horizontal-component-bearing, which is what launch
monitors repackage as "spin axis."

Moist air: ρ = p_d/(R_d T) + p_v/(R_v T), R_d = 287.058, R_v = 461.495 J/(kg·K).

- **Humidity**: humid air is _less_ dense (M*H₂O 18 < M_air 29), so humidity slightly
  \_increases* carry — the opposite of the "heavy humid air" folk belief. Effect is small.
- **Temperature — three mechanisms routinely conflated**: (i) air density, cold = denser =
  more drag; (ii) ball COR, cold ball is stiffer with lower COR; (iii) ν(T) shifting Re by
  ~20% across 0–30 °C. Independent and additive.
- **Wind** enters through relative velocity in _both_ force terms, so **a headwind costs more
  than an equal tailwind gains** — quadratic in relative speed, and a headwind also raises
  spin ratio, lifting both Cl and Cd.

Numerics: RK4 at ~1 ms is ample; **spin must be integrated as a coupled state**, not applied
as a post-hoc correction, since both Cl and Cd depend on S(t).

---

## 6. Dimples and the drag crisis

- Smooth sphere: subcritical Cd ≈ 0.5, crisis at Re ≈ 3–4×10⁵, post-critical Cd ≈ 0.07–0.1
  (Achenbach 1972, 1974).
- Dimpled ball: crisis pulled down to Re ≈ 5–7×10⁴, minimum Cd ≈ 0.22–0.25, then Cd **rises
  slowly with Re** above the crisis — which is why a golf ball's Cd is _higher_ at driver
  speeds than at its minimum.
- Mechanism: dimples trip the boundary layer turbulent → delayed separation → narrower wake →
  lower pressure drag, and substantially increased Magnus lift versus a smooth sphere.
  Canonical: Choi, Jeon & Choi, _Phys. Fluids_ 18, 041702 (2006), DOI 10.1063/1.2191848.
- Modern computational counterpart: Smith, Beratlis, Balaras, Squires & Tsunoda, _Int. J. Heat
  and Fluid Flow_ 31, 262–273 (2010) — DNS/LES over real dimpled geometry.

---

## 7. Gap register — priority order

| #   | Gap                                     | Best target                                                                  | Status                                               |
| --- | --------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------- |
| 1   | Smits & Smith coefficients              | Penner 2003 _Rep. Prog. Phys._ 66:131, DOI 10.1088/0034-4885/66/2/202        | **Paywalled — IOP fetch returned abstract only**     |
| 2   | Bearman & Harvey tabulated Cd/Cl        | Cambridge Core; Mehta 1985 _Annu. Rev. Fluid Mech._ 17:151 reproduces curves | Not retrieved                                        |
| 3   | Quintavalla six-term coefficients       | _Science and Golf IV_; USGA R&TC notes                                       | May be genuinely unpublished                         |
| 4   | Lyu/Kensrud/Smith values                | ISEA proceedings in MDPI _Proceedings_ (open access)                         | Easiest open-access win                              |
| 5   | Spin-decay τ, sourced                   | Tavares/Shannon/Melvin, _Science and Golf III_ 1998                          | Not retrieved                                        |
| 6   | dCarry/dCd, dCarry/dCl                  | Any sensitivity analysis, or compute directly                                | Converts coefficient disagreement into yards         |
| 7   | Published head-to-head model comparison | Theses; _Sports Engineering_; Nathan's baseball methodology as template      | **May not exist — that absence is itself a finding** |

**Editorial note for the article:** any model-vs-model comparison must control for
**integrator and spin-decay mismatch** (§3.6), or apparent aerodynamic disagreement will
largely be integrator mismatch. That confound appears under-addressed in the literature.
