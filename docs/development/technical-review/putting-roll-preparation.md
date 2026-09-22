# Putting Review Preparation — #4422

## Scope and Status

Complete existing 4774-word article read, including overview, equations,
worked tables and references. Six issue groups recorded in #4422, native child
of #4059. This checkpoint preserves research and tests, not article completion.
Twelve independent checks pass. Initial two expected-value typos were corrected
from independently evaluated geometry; they were not production failures.

## Derivations to Carry Forward

- Let alpha = I/(m R^2). Straight level skid with initial slip s0 = v0-R omega0
  reaches rolling after alpha |s0|/((1+alpha) mu g), at speed
  (v0+alpha R omega0)/(1+alpha). Integrate signed friction for displacement;
  heat = m alpha s0^2/(2(1+alpha)). Overspin produces forward friction.
- Rolling couple tau = m(1+alpha)R a0 cos(beta) makes level a0 the measured
  deceleration. Newton and Euler together give downhill acceleration
  g sin(beta)/(1+alpha)-a0 cos(beta). Critical grade is (1+alpha)a0/g.
  This is a moving-ball threshold, not an independently validated rest law.
- Cross-slope first-order lateral velocity obeys w' + a w/(v0-at) = s,
  s = g sin(beta)/(1+alpha). With u=v0-at, w=(s/a)u log(v0/u),
  z=(s/a^2)[(v0^2-u^2)/4-u^2 log(v0/u)/2]. Use away from zero speed.
- Official 145-degree V groove gives rc/R=sin(72.5 degrees)=0.95371695.
  Ideal 30-inch, 20-degree ramp predicts 1.884547 m/s, not an exact 1.83.
  Nominal 1.83 m/s flat-rolling calibration must be an assumption. A single
  rollout constrains an integral of v/a(v), not the whole resistance law.
- Finite ball free-fall centre criterion uses D-R, giving 1.313307 m/s.
  Full D gives an incorrect geometry. Lip capture is a separate mechanism;
  Penner's historical approximate fit uses 1.63[1-(b/Rh)^2] m/s.
  Neither is a universal real-hole capture bound.
- Full slip uses vector spin and s=v-R omega cross n. Scalar spin cannot
  represent arbitrary 2D slip. Define event handling and limits at zero speed.

## Sources and Access Boundaries

Primary paper: A. Raymond Penner, The Physics of Putting, Canadian Journal of
Physics 80(2), 83–96 (2002), DOI 10.1139/p01-137. Downloaded 14-page author
manuscript mirror https://www.waddengolfacademy.com/putting/Penner_The%20Physics%20of%20Putting.pdf.
Read relevant Sections 1–3 and conclusion/references; Section 4 not fully read.
Direct author site TLS failed; verification was not disabled. Mirror PDF/text
are local research files and are not redistributed. Holmes originals were not
read: attribute their capture results only as discussed by Penner. Penner's
zero-resistance prose conflicts with its own rolling balances; independently
retain the rotational-inertia factor rather than copying that prose.

USGA official article 'To Post or Not To Post' supplies 145-degree geometry.
USGA 'The Impact of Technique and Tools on Green Speed Measurements' supplies
operator/release repeatability caveats. Official Stimpmeter booklet indexed
excerpts supply approximate notch/release geometry and measurement procedure;
full booklet download returned 403, so do not claim full-manual inspection.
Equipment and hole dimensions must cite official rule pages. Alpha=0.4 and
mu=0.4 remain model choices, not universal measured ball/turf properties.

## Next Steps

Rewrite canonical QMD; reopen audit status during correction. Reuse existing
force-measurement.css without modifying that frozen evidence path. Recalculate
tables; test complete equations and finite-speed break. Render production
route; inspect desktop/mobile, light/dark, expanded overview and all equations.
Save review/render records, commit complete scientific checkpoint, bind audit
findings to its committed LF bytes, then restore zero-deferred census.

Separately finish publication evidence for #4419 and protected merge/live
verification for #4421 before putting delivery. Never create draft PRs.
