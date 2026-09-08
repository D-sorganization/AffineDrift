# Air Resistance and Inferred Hand Loading

Revised September 8, 2026. Aerodynamics can change the hand wrench inferred from
club motion. The correction depends on the direction and application of the
external load, the reference point and the accuracy of the aerodynamic model.
The original numerical example is a useful sensitivity exercise when those
assumptions are made explicit.

## What the Evidence Establishes

[Henrikson, Wood and Hart's driver study](https://doi.org/10.1016/j.proeng.2014.06.123)
compared two matched driver heads. At the near-impact wind-tunnel condition of
96 mph and the paper's 90-degree head orientation, the plotted drag is about
9 versus 6.6 N, with a reported 2.3 N difference. Lift also changed. The player
comparison involved forty golfers and reported about a 1 mph mean speed increase;
the roughly four-yard carry gain was modeled. These results concern those driver
configurations. They do not calibrate a seven-iron's drag or its aerodynamic
application point. The [complete public author manuscript](https://pgamagazine.com/wp-content/media/2014/07/PING_Turbulator_Science.pdf)
provides the test conditions and figures.

The retained video stills, `air-resistance-effects/IMG_8168.JPG` and
`IMG_8169.JPG`, show a 7.5 lbf user-frame force component, -18.4 N m user-frame
alpha torque and 97.0 mph club speed. The handwritten note instead says 95 mph.
The stills do not establish the full coordinate transformation, club geometry,
aerodynamic loading or the validity of treating the club as a rigid seven-iron.
Those remain assumptions in the reconstruction below.

## A Signed Reconstruction of the Original Sketch

Assume a 37-inch club, a grip reporting point $P$ 3.5 inches from the butt,
a center of mass $C$ 10 inches from the head end and aerodynamic application
point $D$ one inch from that end. Take a local right-handed frame with $x$
toward the head, $y$ transverse and $z=x\times y$. Draw $x$ rightward and $y$
upward. Put $P$ at zero, so

$$
x_C=23.5\ \mathrm{in}=0.5969\ \mathrm m,\qquad
x_D=32.5\ \mathrm{in}=0.8255\ \mathrm m.
$$

Choose the sketch's hand force along $-y$. The no-aerodynamics inference is
$F_{h,y}^0=-7.5$ lbf and $M_{h,P,z}^0=-18.4$ N m. These are explicitly defined
local components, not an undocumented relabeling of the video's beta and alpha
axes. Use 1 lbf = 4.4482216152605 N and assume zero intrinsic aerodynamic couple.

Keeping motion fixed, the corrected hand wrench satisfies

$$
F_{h,y}=F_{h,y}^0-F_{a,y},\qquad
M_{h,P,z}=M_{h,P,z}^0-x_DF_{a,y}.
$$

| Quantity | Air Force Along $-y$: Original Sketch | Air Force Along $+y$ |
|---|---:|---:|
| Assumed $F_{a,y}$ (lbf) | -2.0 | +2.0 |
| Corrected $F_{h,y}$ (lbf) | -5.5 | -9.5 |
| Aerodynamic moment about $P$ (N m) | -7.3440 | +7.3440 |
| Corrected hand moment about $P$ (N m) | -11.0560 | -25.7440 |

For the original direction, the transverse force magnitude falls to 5.5 lbf
and the negative moment magnitude decreases by 39.9%. The original sketch is
mechanically consistent under this geometry and sign convention. Reversing the
aerodynamic projection increases both magnitudes. Drag opposes relative airflow;
its coordinate sign must follow the actual airflow and orientation, not whichever
correction is favorable to an argument.

The same result follows by first taking moments about $C$, subtracting the
aerodynamic moment there, and transporting the corrected hand wrench back to $P$.
The aerodynamic lever arm about $C$ is 9 inches, whereas that about $P$ is 32.5
inches. Mixing those origins or counting both corrections twice gives the wrong
answer. Translating the reporting point also changes a quoted percentage, which
can become unstable near a zero baseline moment.

## What the Example Means for the Swing

The two-pound force and its location are chosen inputs, not measured seven-iron
parameters. Different geometry, orientation, wind, distributed shaft loading,
lift or an intrinsic aerodynamic couple can change the result. Equipment design
can influence aerodynamics, as the driver study itself demonstrates.

The example justifies checking an omitted aerodynamic wrench when a conclusion
depends on a small residual moment. It does not establish a universal 40% error,
a corresponding percentage change in muscle effort, or what either hand feels.
Dividing a pure couple by a chosen perpendicular separation gives the force in
an ideal opposing-force pair; it does not recover the actual two-hand allocation
when a net force, distributed contacts and local contact couples are also present.

All four original images in `air-resistance-effects/` remain unchanged as
source records. `IMG_8166.JPG` supplies the hypothetical geometry and calculation;
`IMG_8167.JPG` illustrates a selected force-pair representation, not measured hand
forces or a general physiological lower bound. Read them with the explicit
assumptions above. The [long manuscript](Drafts/inverse-dynamics-claude-current/inverse_dynamics_final.pdf)
connects these external-load errors to wrench translation, contact ambiguity,
constrained dynamics and power.
