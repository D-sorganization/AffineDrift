# Induced-Acceleration Review Preparation — #4425

## Scope and Findings

Both ch30b_induced_acceleration.tex and its Quarto companion read completely,
including exercises. The shared attribution include was read; preserve it
unchanged unless necessary, because it is reused in other qualified pages.
The previous targeted fix4050 left large print/web divergence. Print still
asserts late-golf drift dominance, shoulder rates5000–7000deg/s, muscle-removal
interventions, full framework equivalence and a biarticular pectoralis-major
exercise. Web already qualifies/removes most of these. Both still say first
golf application, every-joint coupling, and a bare inverse despite constraints.

## Mathematical Plan

Use M qdd = Q + A^T lambda, A qdd=b. With W=A M^-1 A^T,
P=M^-1-M^-1 A^T W^-1 A M^-1 and ac=M^-1 A^T W^-1 b,
qdd=P Q+ac. All source increments are P Qk; count ac once. Alternatively
subtract a feasible complete reference acceleration from each force perturbation.
State independent rows and positive-definite mass requirements and active-mode
feasibility. Point output p(q) has pdd=J qdd+Jdot qdot; count its transport
term once as well. Existing superposition tests independently exercise these
formulas against KKT, including circular-guide curvature and task differences.

Use a uniform-unit-rod2R toy in relative joint angles: M11=5/3+cos(q2),
M12=1/3+cos(q2)/2, M22=1/3. At q2=arccos(-2/3), cross acceleration vanishes
although links remain connected. At q2=0, equal-torque cross gains are reciprocal,
while |A21/A11|=2.5 and |A12/A22|=0.3125. Their ratio8 reflects normalization,
not nonreciprocal mobility. For multiple passive coordinates use a block solve;
-Mkk^-1 Mkj only works in the appropriate two-coordinate case. Mixed coordinate
units/rescaling alter ratios. Derive independently unless Challis full text is
obtained; the abstract alone does not establish his exact equation convention.

Consistent coordinate changes preserve fixed physical output increments:
q=Tz, Qz=T^TQ, Mz=T^TMT, Jz=JT. Component changes do not imply that physical
responses change. For nonlinear q=phi(z), include acceleration transport.
The free particle q=z^2 has zdd=-zdot^2/z despite qdd=0: velocity terms can
change with coordinates without new physics. A rotating point has nonzero
centripetal acceleration even when joint angular acceleration is zero.

Integrating a ledger along the observed trajectory is valid bookkeeping, but
not a removed-force simulation. Toy xdot=x^2+u, x(0)=0, u=1 gives x=tan(t):
input integral t plus state integral tan(t)-t closes. Removing u gives x=0,
so the finite intervention effect tan(t) differs from the input integral t.
Also u=1 and u=2+6t^2-6t reach the same (position,velocity)=(0.5,1) at t=1
for a double integrator. State does not uniquely identify input history.

Energy requires velocities and power/flux: acceleration terms alone do not
supply segment energy transport or individual muscle-force identification.
Keep empirical evidence and model-conditioning concise, not repeated slogans.
Provide fully specified worked exercises in both editions.

## Source Access So Far

- Hirashima2008: DOI10.1016/j.jbiomech.2008.06.014; full10-page PDF downloaded
  from StFX university course archive to iaa-hirashima-2008.pdf/.txt. Read abstract,
  introduction, methods2.1–2.6 and beginning of Results3.1. Remaining results,
  discussion and appendix still need reading. Model13DOF, four segments including
  hand+ball; six players; three fast throws each; inverse dynamics estimates
  net generalized forces. Resampling at2000Hz does not create new measurement
  bandwidth from200Hz markers. Do not turn net torque into measured muscle force.
- Challis2011 abstract and metadata read on PubMed21723558 and PennState author
  record. DOI10.1016/j.jbiomech.2011.06.013. Reported over12-fold quiet-standing
  index ratio is abstract-supported; exact full-text index remains unverified.
- Takagi/Murata/Yokozawa/Shiraki, Dynamics of Pelvis Rotation About Its
  Longitudinal Axis During the Golf Swing, Sports Biomechanics20(5),583–602,
  2021 (online2019), DOI10.1080/14763141.2019.1585472, PubMed31038009.
  Abstract read:31 skilled golfers and model-partitioned pelvis acceleration.
  This is prior golf dynamics attribution, contradicting an unqualified novelty
  claim; full methods have not been inspected and are not certified here.
- ZajacGordon1989 PubMed2676547 has no abstract but confirms volume17, not the
  current BibTeX16. Full review not obtained. Other cited papers still need
  primary records before preserving detailed numerical/anatomical claims.
- Koike et al2019, DOI10.1016/j.jbiomech.2019.01.032, is a swinging/kicking
  study; do not mislabel it as a MacKenzie golf paper based on its title.

## Validation and Delivery

Eight new checks in tests/test_induced_acceleration_chapter_rigor.py pass;
19 with tests/test_superposition_article_rigor.py. Black100/Ruff pass. No
chapter changes or final acceptance yet. Need reopen the chapter route, update
its review report, validate source parity and a small chapter PDF with all pages
inspected, plus final root website render and bound evidence. Disk headroom is
low; avoid full-book rebuilds and preserve all tracked/frozen evidence.

Predecessor regular putting PR4424 at d3bc7d76 awaits CI. Force4421 merged as
9ef76c6e with tree equality to4047d917; deploy35787101015 remains pending.
Superposition publication record is already saved and all960 live cases passed.
