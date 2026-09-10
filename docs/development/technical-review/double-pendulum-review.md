# Double-Pendulum Derivation and Golf Interpretation Review

Issue #4353 belongs to technical-review epic #4009, corpus #4021 and Physics
of Golf #4054. This is a complete paired review of Chapter 3, including its
derivation, numerical example, anatomical interpretation, figure and six
exercises. Original print source was approximately 5,536 words; the web source
was approximately 4,092 words. Both were read completely before correction.
The corpus beyond this chapter remains unfinished.

## Purpose and Model Boundary

The constructive question is how geometry, inertia, gravity and applied moments
produce distal motion, how power crosses physical body boundaries, and how that
motion maps into a specified task. The chapter now supplies a reproducible first
model in a hierarchy, with the same manufactured parameters as the corrected
affine and constraint chapters. Its exact equations do not validate a fixed
pivot, planar motion or rigid bodies as sufficient descriptions of a golf swing.
Moving hand paths, bilateral grasp, shaft deformation, face orientation and
collision require additional states, constraints or measurements.

## Findings and Corrections

1. The original model switched between upper-arm/forearm-plus-club anatomy and
   an arm/club interpretation, confusing elbow and wrist roles. It claimed
   negligible wrist effects and largely stabilizing hips without appropriate
   evidence. The revised model consistently calls the bodies links 1 and 2 and
   their connection hinge H. Generalized applied moments are not identified with
   individual muscles, neural commands or measured anatomical joints.
2. COM and hinge inertias were conflated, creating parallel-axis double counting
   and inconsistent print/web numerical results. Derivation starts from each
   COM velocity plus centroidal rotation, defines hinge inertias separately and
   retains the general rigid-body terms before choosing numerical parameters.
3. Both expanded Euler–Lagrange equations placed physical gravity on the right
   with the wrong sign, despite the later gradient vector having the correct
   convention. Both equations now agree with the potential gradient and total
   energy derivative. A zero first angle does not eliminate distal gravity.
4. The print Coriolis matrix included a squared rate in C21, generating a cubic
   rate when multiplied by velocity. The corrected Christoffel factorization
   produces the quadratic bias vector and the skew identity. Other valid C
   factorizations are possible; individual entries are not unique force channels.
5. M11 was interpreted as the denominator of a free distal joint's proximal
   acceleration. The revised text derives the Schur effective inertia and
   distinguishes prescribed motion, free motion and explicitly imposed locks.
6. Claims that all backswing energy becomes club motion, that stationary action
   necessarily minimizes a quantity, and that an unsupported 30–50 N m shoulder
   budget establishes efficiency were removed. Energy, input power, acceleration
   and metabolic effort now have distinct definitions and evidence requirements.
7. Algebraic interaction terms were treated as physical hinge torque/energy
   transfer and used to prescribe amateur or elite movement. The correction
   identifies actual force and moment power at physical interfaces, and explains
   why forward and inverse dynamics ask different questions.
8. Nonlinearity was equated with inevitable chaos and a 0.01 s timing change with
   an automatic sweet-spot miss. The replacement distinguishes regular local
   oscillations, regime-specific chaos and finite-duration task sensitivity,
   including feedback, input history, scales and event-time changes.
9. Endpoint acceleration omitted curvature, a scalar task request was treated
   as determining two joint accelerations, and acceleration in g was called a
   force. The full Jacobian and normal terms, an explicit solution family and
   the contact-model boundary correct these claims.
10. The old geometry sketch did not consistently depict its angle conventions
    and was missing from the web edition. The shared computed SVG/PDF uses true
    angle arcs and separate COM/endpoint markers. An unattributed epigraph was
    removed. Historical section, equation and citation destinations are preserved.

## Independent Derivation and Numerical Evidence

Angles q=(theta1,theta2) use downward vertical and a relative distal angle.
Absolute body angles are alpha=Aq with A=[[1,0],[1,1]]. Virtual work gives
Q_alpha=A^(-T) tau=(tau1-tau2,tau2); inertia transforms as
M_alpha=A^(-T) M_q A^(-1). These transformations preserve kinetic energy and
actuator power, including the equal-and-opposite hinge moment on the bodies.

Manufactured parameters are m1=2.5 kg, m2=0.4 kg, L1=0.35 m, L2=1 m,
r1=0.175 m, r2=0.5 m, I1_COM=0.025 kg m², I2_COM=0.03 kg m² and
g=9.81 m/s². Hinge inertias are 0.1015625 and 0.13 kg m². L2 locates the
endpoint; r2 locates the COM. The older expanded notation L_i,cm equals r_i.

Writing b=m2 L1 r2, the bias is
c=b sin(q2) (-2 v1 v2-v2², v1²). The selected C is
b sin(q2)[[-v2,-v1-v2],[v1,0]]. Independent finite differences verify
Mdot-2C is skew and grad(V)=g_vector, while COM-based energy verifies M.
Consequently Edot=tau·v for the declared fixed-pivot, lossless system.

At q=(0,-5 degrees), v=(10,9) rad/s:

- M=[[0.420029757733,0.199733628866],[0.199733628866,0.13]] kg m².
- c=(1.592335420000,-0.610090199234) N m and
  g_vector=(-0.170999567271,-0.170999567271) N m. Physical gravity is -g_vector.
- Zero applied moments give acceleration=(-23.166250084839,41.601299716741)
  rad/s²; input (5,0) N m gives (21.020338033059,-26.287527914132) rad/s².
  Input changes both accelerations and reverses distal relative acceleration.
- Input power is 50 W. Kinetic energy is 44.242514484620 J.
  Schur effective inertia is 0.113156507732 kg m², not M11=0.420029757733.
- Endpoint velocity is (22.427699263743,-1.655959112206) m/s. Zero-input
  endpoint acceleration is (41.719934304571,393.019565567862) m/s².
  Acceleration magnitude is not speed derivative; the latter projects onto
  the nonzero velocity direction.

With e(a)=(sin(a),-cos(a)) and t(a)=(cos(a),sin(a)), endpoint position is
p=L1 e(q1)+L2 e(q1+q2). Its Jacobian columns are
L1 t(q1)+L2 t(q1+q2) and L2 t(q1+q2). Acceleration includes
-L1 v1² e(q1)-L2(v1+v2)² e(q1+q2), independently checked by differentiating
position along a quadratic joint trajectory. det(J)=L1 L2 sin(q2). Aligned
links lose task rank while the mass matrix remains positive definite.

All six exercises contain worked answers:

- Separate uniform rod, 1.5 kg and 1 m: I_COM=0.125 and K_end=0.5 kg m².
- Gravity work from (150,-70 degrees) to (0,0) is 12.192849344842 J, a
  total-system contribution rather than necessarily distal kinetic energy.
- Aligned rigid rotation at 10.47 rad/s gives inward endpoint acceleration
  147.988215 m/s², or 15.085444954 g; nonzero relative rate needs the full model.
- At (0,0), horizontal acceleration 50 m/s² requires 1.35 a1+a2=50.
  Examples (0,50), (20,23), (37.037037037,0) rad/s² share that task value.
  At v=(10,9), each has upward normal acceleration 396 m/s².
- Physical gravity moments at (150,-70 degrees) are
  (-4.764830311410,-1.932192811410) N m; acceleration still requires the
  full inverse mass matrix and the other loads.
- The downward linearization has positive small-oscillation angular frequencies
  3.644068204748 and 7.552873204213 rad/s. It is a local oscillatory model,
  not a proof of global regularity or a diagnosis of human-swing chaos.

The numerical reproducer reuses the audited affine dynamics operator, while
independent COM, gradient, kinematic and virtual-work tests avoid merely
comparing duplicate formulas. The JSON records inputs and computed outputs.

## Primary Evidence and Reading Limits

- [Tedrake, Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html):
  read the relevant double-pendulum derivation, manipulator form and C
  nonuniqueness/Christoffel energy discussion. That point-mass example has
  different mass placement; this chapter's COM derivation is independent.
- [Nesbit (2005)](https://www.jssm.org/volume04/iss4/cap/jssm-04-499.pdf):
  read introduction/methods, relevant results/discussion on hand paths, wrist
  motion, grip versus head velocity and grip torque, and selected conclusion
  passages. The complete 21-page paper was not read. Its measured-motion-driven
  spatial model uses a flexible club and does not calibrate our manufactured
  parameters, establish negligible wrist effects or identify an optimal policy.
  The old Gatt knee-biomechanics citation did not support a shoulder-torque
  budget; its historical web anchor now lands at the corrected evidence boundary.
- [Shinbrot et al. (1992)](https://doi.org/10.1119/1.16860): read printed pages
  491–492, including abstract, introduction and demonstration, from a facsimile
  of the primary paper. The remaining article pages were not fully read.
  The cited finding concerns experimental/simulated mechanical-pendulum chaos
  under specified conditions, not a controlled human swing. The author's hosted
  PDF timed out; the facsimile preserved the original article and metadata.
- Official DFKI double-pendulum dynamics documentation was read as another
  convention comparison. Its hinge-inertia/motor conventions differ and are
  not used as a numerical oracle or golfer evidence.

## Validation and Failures Corrected

- TDD began with 12 errors for the missing reproducer and two failures against
  the old source. Final 14 numerical/source tests pass; combined with figure
  parity, 37 pass. Ruff, Black100 and focused code-quality pass.
- Root pytest with configured coverage: 5,243 passed, 29 skipped,
  132 deselected, 59 warnings; 79.29% coverage. Content-lint: 131 passed and
  four skipped. All 34 static CI contracts, title audit of 636 sources,
  configured mypy over 91 files, citation and site-link checks pass.
- Full 542-page PDF rebuilt. All 14 chapter pages 53–66 were read. The final
  title/prose/hinge-subscript revision changed only pages 53/54/56/57 by full-book
  extracted-text comparison; all four were rerendered and reread. New Shinbrot
  entry on physical page 533 was read. The chapter has no final layout or
  undefined-reference warnings. Other chapters retain existing layout warnings.
- All 26 full web captures were read through examples, six answers and references.
  Full reading caught literal outer math delimiters missed by the first layout
  pass: blank lines left by equation-label extraction broke aligned displays.
  Removing those blank lines restored 44 displays and 179 total expressions.
  A second reading caught the Related Articles heading joined to the preceding
  paragraph; its missing blank line was corrected and the delimiter check expanded.
  The final run produced 27 captures; changed ending captures were reread,
  and all 14 final canonical records were individually inspected and passed.
- Exhaustive browser checks cover 14 viewport/theme combinations, 270 detailed
  regions and 134 keyboard-scroll checks, with all 30 historical destinations
  retained, no duplicate IDs, broken local fragments or unloaded figures. The
  canonical gate individually verifies every one of the 14 actual-route records.
  Both themes retain only the shared moderate landmark-unique axe finding;
  no serious/critical findings. Console noise remains and is not reported as zero.
- Figure parity retains 38 print figures: nine TikZ and 29 includegraphics;
  30 web figures leave eight remaining missing-parity figures elsewhere.
  Scratch captures, conversion scripts and generated trust-file churn are not
  canonical deliverables and are excluded from staging.

## Delivery Boundary

Implementation and complete paired reading are locally complete. Protected PR,
merge and revision-matched live verification remain. Preserve peer-owned
#4253/#4255/Chapter 29, immutable proximal-distal publications and scientific
authority pins. Next review should prioritize Chapter 4 because it directly
reuses this chapter's old numerical assumptions; the corpus queue also retains
longer articles and the five read-but-uncorrected critiques under #4340.

## Protected Delivery Checkpoint

Implementation 96ae7eb69c9622b176aabf8507c4fa293a296298 preserves validated tree 272e173c046e86a64893219a43d726c0e2c26b15 after replay onto constraint squash b5362af0005c8ae1ad00e81390e9151991157155. Parent/squash trees matched. Normal commit/push hooks passed. Ready PR #4354 closes #4353; protected checks, merge and exact live publication remain. Final heading-only web revision was reread; all final actual-route records passed.

## Protected Merge

All required checks passed. PR #4354 squash-merged as e9ad402e50f111589252292178e5f45ac58b427c; final head fe8ee652 and squash share tree d8932835286b0ed9ed2e31bc4066073d6b9fbd94. Exact deployment 34473831404 is in progress; revision-matched live verification remains.

## Verified Publication at Handoff

Exact deployment34473831404 was cancelled before publication when superseded. Successful later deployment34477888759 at0c753400190cf330533bffc12e9b035162f37749 includes the chapter: GitHub comparison proves e9ad402e ancestry and both Chapter3 canonical sources unchanged. All956 records/239 routes of artifact10153444359 individually passed, including all four Chapter3 records. This is verified descendant publication, not success of the cancelled exact run.
