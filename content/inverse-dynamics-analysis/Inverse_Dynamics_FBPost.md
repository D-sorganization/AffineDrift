# Reading Inverse-Dynamics Forces and Moments

Revised September 8, 2026. These two explanatory posts supersede the earlier
interpretations. The original handwritten sheets remain as a record of the
questions that motivated the analysis; the distinctions below govern their use.

## Post 1: A Reported Moment Is Not a Unique Hand Strategy

A torque curve can be mechanically correct without telling us exactly which
fingers pressed, which hand supplied the load or what the golfer intended.
That is the question behind this thought experiment: suppose a force acts at
one point on the grip, away from the point used to report inverse dynamics.

Use a rigid club and one fixed right-handed frame. A force $\mathbf F$ at $A$
can be represented at $P$ by the same force plus the moment

$$
\mathbf M_P=(\mathbf r_A-\mathbf r_P)\times\mathbf F.
$$

For example, put $P$ at the origin, $A=(0.5,0,0)$ m and
$\mathbf F=(0,4,0)$ N. The report at $P$ is a 4 N upward force and a
2 N m counterclockwise moment. Both components are needed for equivalence.
A pure couple alone has zero resultant force and would not give the same
center-of-mass acceleration.

The offset force has a real moment. It can change rotation even though no
separate pair of opposing contact forces was applied. Conversely, a hand can
produce a real contact couple through distributed forces. The useful conclusion
is that a reported moment does not identify a unique contact pattern, voluntary
command or sensation. It does not mean the rotational loading is imaginary.

The original two-hand calculation is also worth preserving. Keep the reporting
midpoint fixed, take $x$ toward the head, $y$ upward and positive $z$ out of the
page. Apply a downward 10 lbf left-hand force and an upward 15 lbf right-hand
force. In the first case their positions relative to the midpoint are -2 and
+1 inches; in the second they are -1 and +2 inches. The resultant is 5 lbf
upward in both cases, but the moments are

$$
M_P^{(1)}=(-2)(-10)+(1)(15)=35\ \mathrm{lbf\,in},
$$

$$
M_P^{(2)}=(-1)(-10)+(2)(15)=40\ \mathrm{lbf\,in}.
$$

These are 3.9545 and 4.5194 N m: a 14.3% increase relative to the first case.
The handwritten sheet uses clockwise-positive signs, hence its -35 and -40.
The earlier description of about 15% was a rounded illustrative comparison,
not a measured effect across golfers. Moving the forces changes the wrench
at the fixed midpoint. It does not demonstrate identical inverse-dynamics
outputs or merely a change of reporting convention.

## Post 2: Separate Three Different Experiments

First, change the **reporting point** while holding the actual wrench fixed.
The transformation is exact:

$$
\mathbf M_Q=\mathbf M_P+(\mathbf r_P-\mathbf r_Q)\times\mathbf F.
$$

For $\mathbf F=(0,40,0)$ N and $M_{P,z}=2$ N m, points at
$x=-0.10,0,+0.10$ m report 6, 2 and -2 N m. All three describe one loading.
The sign change does not identify where force was applied, establish an error
bar, or reverse the physical action. In three dimensions, a wrench with
$\mathbf F\cdot\mathbf M\ne0$ cannot be represented by one force with no
residual couple at any point. A presumed pressure center does not solve every
hand-wrench problem.

Second, change the **physical contact pattern** while preserving the complete
net wrench. At two distinct force-only contacts, add equal and opposite forces
along the line joining them. Their force and moment sums vanish, so rigid club
motion cannot distinguish those additions. Opposite transverse forces generally
form a couple and are visible. Friction, compression and anatomical constraints
limit which mathematical allocations are feasible. With distributed contacts,
local couples and more contact points, use the corresponding grasp map rather
than assuming the same number of degrees of ambiguity.

Third, change the **physical contact pattern without preserving the wrench**.
The two-hand numerical example in Post 1 does this: the same force magnitudes
at shifted locations produce different moments. That can affect the motion.
It answers a different question from either of the first two experiments.

The earlier proposal to reduce all tractions to two forces, subtract the smaller
magnitude and put the resultant at the larger force's location works only for
suitable special force geometries. It is not a general vector decomposition of
two arbitrary hand wrenches. Each hand may have a residual contact couple, and
net club motion does not select a unique allocation or a preferred physical
reporting point. A chosen optimization criterion is an assumption to test.

For the alpha-torque discussion, state the point, axis, basis and hand-on-club
versus club-on-hand convention before interpreting a sign. Wrench power combines
force and moment terms; a single moment sign does not establish total energy
transfer, muscular braking or a coaching instruction. Standard inverse dynamics
already includes the declared gravity and inertial coupling. Its net joint load
must not have a second “drift torque” subtracted as if it were unaccounted for.

The next useful measurements are those that address the missing layer:
instrumented grip loads, calibrated contact pressures and shear, full-body motion,
external ground loads, and physiological evidence for claims about muscle action
or perceived effort. These sources constrain different parts of the same chain.

## Source and Original-Sheet Notes

The wrench convention follows the
[Modern Robotics Wrench Supplement](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/).
See the [long technical manuscript](Drafts/inverse-dynamics-claude-current/inverse_dynamics_final.pdf)
for balances, contact maps, power and aerodynamic examples.

The eight sheets in `midpoint-location-effects/` are retained unchanged.
`IMG_8157.JPG` mixes reporting-point notation with moments about a common center
of mass; its scalar distance-ratio formula requires signed collinear lever arms.
The moment range for fixed force and reporting interval does not independently
grow with distance to the center of mass. `IMG_8158.JPG` contains the restricted
two-force decomposition discussed above. `IMG_8159.JPG` and `IMG_8160.JPG`
explore possible reference changes, which do not identify the actual hand load.
`IMG_8161.JPG` through `IMG_8163.JPG` illustrate the valid offset-force idea;
“a couple does not exist” must not be read as absence of a real force moment.
`IMG_8164.JPG` contains the two distinct physical load patterns calculated here.
