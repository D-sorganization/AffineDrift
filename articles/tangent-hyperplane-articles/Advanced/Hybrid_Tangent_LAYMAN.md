# In Layman's Terms: Hybrid Tangent Spaces

**Target Audience:** Non-technical readers, practitioners, students
**Source:** Hybrid_Tangent_Spaces.qmd
**Date:** January 18, 2026

---

## The Big Idea in One Sentence

**"Most real-world systems don't just flow smoothly—they jump, collide, and switch modes suddenly—but we can still understand them using the same tangent space framework, with a few special tools for handling the jumps."**

---

## The Problem with Smoothness

Remember the main tangent space idea? Systems are secretly linear at each instant, like a winding road that's flat if you zoom in close enough.

**But that story had a hidden assumption:** The road is smooth. No potholes, no sudden cliffs, no jumps.

### When Smoothness Breaks Down

Real systems aren't always smooth. Consider:

1. **A basketball hitting the floor**: The ball falls smoothly, then BOOM—the velocity instantly reverses. That's not smooth. There's no "zooming in" that makes the impact gradual.

2. **Walking**: Your foot swings smoothly through the air (smooth motion), then strikes the ground (sudden stop), then your other foot lifts off (sudden mode switch). Two different types of physics: "foot in air" vs. "foot on ground."

3. **A light switch**: It's either ON or OFF. There's no smooth transition—you flip it and the state jumps instantly.

4. **A bouncing ball losing energy**: It bounces, hits the ground, bounces lower, hits again. Each impact is a discontinuity—the velocity direction flips instantaneously.

**The question:** Can we still use our tangent space framework when systems jump around like this?

**The answer:** Yes! We just need to extend it with the concept of **hybrid systems**—systems that mix smooth flow with sudden jumps.

---

## What Are Hybrid Systems?

Think of a hybrid system as having two types of behavior:

### 1. **Smooth Flow (Within Modes)**

Between jumps, the system behaves normally—it's smooth and our usual tangent space ideas apply.

**Example:** While a basketball is flying through the air, gravity pulls it down smoothly. The trajectory is a nice parabola.

### 2. **Sudden Jumps (At Guards)**

At special moments, the system hits a "boundary" (called a **guard surface**) and something discontinuous happens:

- The state might jump to a new value
- The mode of operation might switch
- Forces might appear or disappear

**Example:** When the ball touches the floor (guard surface), the velocity instantly reverses and gets multiplied by 0.8 (if the ball is somewhat bouncy). That's a jump.

### The Analogy: Driving with Gear Shifts

Imagine driving a manual transmission car:

- **Smooth flow:** While you're in 2nd gear, pressing the gas smoothly increases speed
- **Guard crossing:** RPMs hit 4000 (the guard)
- **Mode switch:** You shift to 3rd gear (new mode)
- **Jump in dynamics:** Suddenly the relationship between gas pedal and acceleration changes (different gear ratio)

You go from "2nd gear physics" to "3rd gear physics" instantly at the shift point.

**Hybrid systems formalize this:** Different "gears" (modes) with smooth behavior in each gear, and sudden transitions (jumps) when you shift.

---

## Why This Matters

Most interesting systems are hybrid:

- **Walking robots:** Stance phase (foot on ground) vs. swing phase (foot in air)
- **Manufacturing:** Cutting metal (tool touching workpiece) vs. moving to next position (no contact)
- **Climate control:** Heater ON vs. heater OFF
- **Golf swing:** Club approaching ball (smooth) → impact (sudden) → follow-through (smooth)
- **Space docking:** Approach (smooth) → contact (impact) → latched (new mode)

If we ignored the jumps and pretended everything was smooth, our predictions would be wildly wrong. We need tools that respect the discontinuities.

---

## Key Concept 1: Modes and Guards

### Modes

A **mode** is a "regime" where the system behaves according to one set of rules.

**Example: A Simple Hopping Robot**

- **Mode 1 (Flight):** Robot in the air. Gravity pulls it down. No ground contact forces.
- **Mode 2 (Contact):** Foot on ground. Spring in the leg compresses. Ground pushes back.

Each mode has its own physics, its own equations. In flight, you can't push off the ground. In contact, gravity isn't the only force—the spring matters too.

### Guards

A **guard** is the boundary that triggers a switch from one mode to another.

**Example:**

- **Guard 1:** "Foot touches ground" (flight → contact)
- **Guard 2:** "Spring force becomes zero" (contact → flight, i.e., takeoff)

When you hit a guard, three things happen:

1. Check that you've crossed the boundary (e.g., foot height = 0)
2. Apply the **reset map** (more on this in a moment)
3. Switch to the new mode

### Visual Metaphor

Imagine a pinball machine:

- **Modes:** Different regions of the table (upper area, lower area, bonus chamber)
- **Guards:** The flippers and bumpers (boundaries between regions)
- **Flow:** Ball rolls smoothly within each region
- **Jumps:** When the ball hits a flipper, its velocity suddenly changes direction

The ball doesn't teleport across the table—it flows smoothly until it hits a boundary, then jumps.

---

## Key Concept 2: Reset Maps (What Happens When You Jump)

When you cross a guard, the state of the system might jump. The **reset map** is the rule for how.

### Example 1: Bouncing Ball

**Before impact (state $x^-$):**

- Height: 0 meters (just touching ground)
- Velocity: -5 m/s (moving down)

**Guard crossed:** Ball touches ground

**Reset map:**

- New height: Still 0 meters (no change in position)
- New velocity: $-0.8 \times (-5) = +4$ m/s (moving up, but slower due to energy loss)

The **0.8** is called the **coefficient of restitution** ($e$). It measures bounciness:

- $e = 1$: Perfectly elastic (no energy lost, bounces to the same height)
- $e = 0$: Perfectly inelastic (sticks to the ground, no bounce)
- $e = 0.8$: Typical rubber ball (bounces to 64% of original height, since height $\propto v^2$)

**What jumped:** The velocity flipped sign and got smaller. Position stayed continuous (the ball was at the ground before and after).

### Example 2: Walking Robot Heel Strike

**Before heel strike:**

- Leg swinging forward at 2 m/s

**Guard crossed:** Foot contacts ground

**Reset map:**

- Foot velocity → 0 m/s (can't sink into the ground)
- Other joint velocities change due to conservation of angular momentum

**What jumped:** The whole velocity vector changes suddenly. The robot's "stride pattern" depends crucially on getting this jump right.

### The Key Insight: Linear Maps on Jumps

Even though the trajectory itself jumps discontinuously, the **effect on small perturbations is linear**.

**What this means:**

- If you nudge the pre-impact velocity by 0.1 m/s, the post-impact velocity gets nudged by (some linear factor) × 0.1 m/s
- That linear factor is captured in a matrix called the **saltation matrix** (more on that next)

**Why this matters:** We can still use linear algebra to track how errors and perturbations propagate through jumps. The core tangent space framework survives!

---

## Key Concept 3: Saltation Matrices (The Secret Sauce)

The word **saltation** comes from Latin "saltare" (to jump). A saltation matrix tells you how perturbations jump across a guard.

### The Setup

You have:

- A nominal trajectory that crosses a guard at time $t_j$
- A slightly perturbed trajectory (maybe you started from a slightly different position)

**Question:** If the nominal trajectory hits the ground at exactly 1.5 seconds, and the perturbed one is slightly different before impact, what happens to the difference after impact?

**Answer:** The difference vector $\delta x$ (perturbation) gets multiplied by the saltation matrix $S_j$:

$$\delta x^+ = S_j \cdot \delta x^-$$

Where:

- $\delta x^-$ is the perturbation just before the jump
- $\delta x^+$ is the perturbation just after the jump
- $S_j$ is the saltation matrix for that particular guard crossing

### What Does $S_j$ Do?

It has two parts:

**Part 1: Direct effect of the reset map**

- If the ball velocity gets multiplied by -0.8, perturbations in velocity also get multiplied by -0.8
- This is captured by the **reset Jacobian** $P_j$

**Part 2: Timing correction**

- The perturbed trajectory might cross the guard at a slightly different time
- During that time difference, the system is still evolving (e.g., gravity is still pulling)
- This adds a correction term to $P_j$ to get the full saltation matrix $S_j$

### Analogy: Rotation of the Tangent Space

Imagine you're driving on a road that suddenly turns 90 degrees to the right (a sharp corner, like a guard surface).

**Before the turn:**

- Your velocity is "forward" (let's say north)
- Perturbations (small changes in speed or steering) are in the "roughly north" tangent space

**At the turn:**

- You rotate the steering wheel
- Your velocity is now "right" (east)
- The tangent space rotates with you—perturbations are now in the "roughly east" space

The saltation matrix is like that rotation: it tells you how the "perturbation space" (tangent space) transforms when you hit the discontinuity.

### Example: Bouncing Ball Saltation Matrix

For our ball with $e = 0.8$ and velocity $v^- = -5$ m/s just before impact:

$$S_j = \begin{bmatrix} -0.8 & 0 \\ \frac{-9.8 \times 1.8}{-5} & -0.8 \end{bmatrix} = \begin{bmatrix} -0.8 & 0 \\ 3.53 & -0.8 \end{bmatrix}$$

**What this tells us:**

- First row: A perturbation in velocity before impact creates a perturbation in height after impact (because timing of the bounce shifts)
- Second row: Velocity perturbations scale by -0.8, plus a bit of coupling from height perturbations

**Key property:** The eigenvalues are both -0.8, which is less than 1 in magnitude. This means **perturbations shrink** through the impact—bouncing stabilizes the ball's trajectory! Each bounce damps out errors.

---

## Key Concept 4: Extending the Tangent Space Framework

Now we can state the full hybrid version of the tangent space principle:

### Original Framework (Smooth Systems)

**"At every instant, a nonlinear system is exactly linear—perturbations evolve via the Jacobian matrix $A$."**

Mathematically:
$$\delta \dot{x} = A(t) \delta x$$

This is the variational equation. It's exact for infinitesimal perturbations.

### Hybrid Extension

**"At every instant within a mode, the system is exactly linear. At guard crossings, perturbations jump linearly via the saltation matrix $S_j$."**

Mathematically:

- **Within modes:** $\delta \dot{x} = A(t) \delta x$ (same as before)
- **At jumps:** $\delta x^+ = S_j \delta x^-$ (new rule)

Over a full trajectory with multiple jumps, perturbations evolve as:

$$\text{Perturbation at end} = (\text{Smooth flow}) \times S_3 \times (\text{Smooth flow}) \times S_2 \times (\text{Smooth flow}) \times S_1 \times (\text{Initial perturbation})$$

Each $S_j$ is a "connector" that threads through a jump. Between jumps, you use the usual smooth flow. The product of all these gives the total sensitivity.

### Why This Is Powerful

Even though the trajectory is discontinuous (it jumps), the **effect on perturbations** is still a linear map. This means:

1. You can compute sensitivities exactly (how does changing the initial speed affect the final position?)
2. You can optimize trajectories using gradient-based methods (DDP, iLQR)
3. You can design feedback controllers that stabilize through impacts

All the tools from smooth systems still apply—you just need to include the $S_j$ matrices at the jumps.

---

## When Smooth Assumptions Break: Examples

Let's revisit the examples from the beginning and see how the framework handles them.

### 1. Basketball Bouncing

**Smooth assumption breaks:** Velocity jumps discontinuously at each impact.

**Hybrid framework solution:**

- **Mode:** Flight (ball in air)
- **Guard:** Height = 0, moving downward
- **Reset:** Velocity reverses and scales by $e$
- **Saltation matrix:** Captures how perturbations transform through impact

**Result:** We can predict the height of the 10th bounce, optimize the initial throw to land in a basket after three bounces, or design a controller that catches the ball by timing the guard crossings.

### 2. Walking (Stance vs. Swing)

**Smooth assumption breaks:** Foot strike and toe-off are sudden events. The dynamics are totally different depending on whether the foot is on the ground.

**Hybrid framework solution:**

- **Mode 1:** Stance (foot on ground, single support)
- **Mode 2:** Swing (foot in air, no ground contact)
- **Guards:** Heel strike (enter stance), toe-off (enter swing)
- **Resets:** Velocity jump at heel strike due to inelastic collision; continuous transition at toe-off

**Result:** Humanoid robots use hybrid trajectory optimization to plan walking gaits. The optimizer knows that stance and swing have different physics, and it plans accordingly.

### 3. Light Switch

**Smooth assumption breaks:** The light is either ON or OFF, no in-between.

**Hybrid framework solution:**

- **Mode 1:** Light OFF
- **Mode 2:** Light ON
- **Guards:** User flips switch (discrete event)
- **Reset:** State jumps from OFF to ON

**Result:** This is a "purely discrete" hybrid system (no continuous dynamics within modes, unless you model the filament heating up). The framework handles it by treating each mode as having trivial continuous dynamics ($\dot{x} = 0$) and all the action happening at guards.

### 4. Bouncing Ball Losing Energy (Zeno Behavior)

**Smooth assumption breaks:** Infinitely many bounces in finite time (if $e < 1$, the ball bounces faster and faster until it "settles" in finite time).

**Hybrid framework solution:**

- Same as basketball, but now we track the sequence of bounces
- The time between bounces decreases geometrically: $T_1, T_2, T_3, \ldots$ with $T_n = e^n T_1$
- Total time: $T_{total} = T_1 (1 + e + e^2 + \ldots) = \frac{T_1}{1 - e}$ (finite!)

**Result:** The framework correctly predicts that the ball settles in finite time. Mathematically, the infinite sequence of jumps is well-defined because jumps have "measure zero" (they occupy no time, so integrals over the trajectory ignore them).

---

## Real-World Applications

### Application 1: Humanoid Robot Walking

**Challenge:** A walking robot has two feet. At any moment, one foot might be on the ground (stance) or in the air (swing). The contact forces appear and disappear suddenly.

**Hybrid model:**

- **Modes:** Single support left, single support right, double support (both feet down), flight (running)
- **Guards:** Heel strike (foot touches ground), toe-off (foot leaves ground)
- **Resets:** At heel strike, the foot velocity must go to zero. This causes a shock wave through the robot's joints, which is captured by the saltation matrix.

**Why it matters:**

- Traditional smooth optimization would "smooth out" the foot strike, predicting the foot sinks into the ground slightly. This is physically wrong and leads to bad gaits.
- Hybrid optimization respects the contact: the foot stops instantly, energy is lost, and the gait is stable.

**Result:** Companies like Boston Dynamics use hybrid models to plan robust walking gaits. The jumps are explicit, not approximated.

### Application 2: Golf Swing (Club-Ball Impact)

**Challenge:** A golf club head traveling at 50 m/s hits a 46-gram ball. The collision lasts about 0.5 milliseconds. During that time, forces are enormous (10,000 Newtons), and the ball goes from 0 to 70 m/s.

**Hybrid model:**

- **Phase 1 (Backswing):** Smooth dynamics, club rotates back
- **Phase 2 (Downswing):** Smooth dynamics, club accelerates toward ball
- **Phase 3 (Impact):** Discontinuous jump. Club and ball exchange momentum according to restitution coefficient $e \approx 0.78$
- **Phase 4 (Follow-through):** Smooth dynamics, club decelerates

**Saltation matrix at impact:**

- Ball velocity after impact: $v_{ball}^+ = 1.48 \times v_{club}^-$ (for typical club/ball mass ratio)
- The factor 1.48 comes from the impact equations (momentum + restitution)
- Perturbations in club speed map linearly to perturbations in ball speed via this factor

**Optimization insight:**
Using hybrid DDP (differential dynamic programming) to optimize the swing, the algorithm discovers:

- The club should decelerate _slightly_ just before impact (counter-intuitive!)
- This maximizes energy transfer and minimizes vibration losses

This would be missed by a smooth approximation that doesn't respect the discontinuity.

### Application 3: Spacecraft Docking

**Challenge:** A spacecraft approaches the International Space Station at 0.1 m/s. When the docking mechanism touches, there's a soft capture (impact with $e = 0.3$, highly dissipative to avoid bouncing away).

**Hybrid model:**

- **Mode 1 (Approach):** Smooth orbital dynamics, thrusters provide control
- **Guard:** Contact sensor detects docking port touch
- **Reset:** Velocity jumps according to the soft-capture mechanism (like a very squishy collision)
- **Mode 2 (Latched):** Spacecraft is now rigidly connected to ISS

**Why it matters:**

- If you modeled the docking mechanism as a stiff spring (smooth approximation), the simulation timesteps would need to be incredibly small (microseconds) to capture the stiffness accurately. This is computationally expensive.
- Hybrid model treats the capture as a discrete event with a known reset map. Simulation is fast and accurate.

**Result:** NASA's trajectory planners use hybrid models for rendezvous and docking, ensuring the approach is gentle and the capture is reliable.

### Application 4: Manufacturing (Drilling or Cutting)

**Challenge:** A drill bit cuts into metal. Two phases:

- **Air mode:** Drill spinning, approaching the workpiece (no cutting forces)
- **Contact mode:** Drill touching metal, huge cutting forces appear, chips form, heat is generated

The transition is sudden—cutting forces don't "gradually appear," they jump to a large value the instant contact is made.

**Hybrid model:**

- **Mode 1:** Air (smooth dynamics, just motor torque)
- **Guard:** Bit touches workpiece (sensed by position or force threshold)
- **Reset:** Cutting forces appear (no jump in position, but force/torque jumps)
- **Mode 2:** Cutting (different dynamics due to friction, chip formation)

**Why it matters:**

- Machining optimization needs to avoid chatter (vibration) and tool breakage
- The jump in forces at contact excites vibrations
- Hybrid models predict these and allow the optimizer to plan feed rates that avoid resonance

**Result:** Modern CNC controllers use hybrid models to plan tool paths that maximize material removal while staying within safe vibration limits.

---

## Saltation as "Rotation of the Tangent Space When You Hit a Wall"

Let's revisit the geometric interpretation of saltation with a concrete analogy.

### The Wall Analogy

Imagine you're pushing a cart across a flat floor. Suddenly, the cart hits a wall.

**Before impact:**

- Cart moving forward at 2 m/s
- Small perturbations (wiggling the handle) change the cart's velocity in any direction—forward, sideways, etc.
- The "tangent space" is 2D (you can perturb forward/backward and left/right)

**At impact (hitting the wall):**

- The cart's forward velocity suddenly goes to zero (inelastic collision)
- Sideways velocity is unaffected (the wall only stops forward motion)
- The tangent space "rotates": perturbations in the forward direction get killed, perturbations sideways remain

**After impact:**

- Cart is at rest against the wall
- Small perturbations can only move sideways (forward is blocked by the wall)
- The tangent space is now effectively 1D (only sideways motion allowed)

**The saltation matrix** captures this transformation:

$$S = \begin{bmatrix} 0 & 0 \\ 0 & 1 \end{bmatrix}$$

Meaning:

- Forward velocity perturbation → 0 (first row)
- Sideways velocity perturbation → unchanged (second row)

### Why "Rotation"?

The tangent space doesn't literally rotate in space, but its _effective directions_ change:

- Before: "forward" is a valid perturbation direction
- After: "forward" is forbidden (blocked by the wall)

In linear algebra terms, the saltation matrix is a projection operator that kills the normal component and preserves the tangential component.

### General Principle

At any impact or switch:

- The tangent space before the jump has certain directions
- The saltation matrix maps those directions to new directions after the jump
- Some directions might get scaled (damped or amplified)
- Some directions might get "rotated" (coupled to other directions)
- Some directions might get eliminated (if the reset map constrains the state)

This is why we call it "rotation of the tangent space"—it's a linear transformation that reorients how perturbations behave.

---

## Handling Complexity: Multiple Jumps

Real systems often have many jumps. A basketball might bounce 20 times. A walking robot might have 100 footsteps in a single gait cycle.

### Composing Saltation Matrices

If you have jumps at times $t_1, t_2, t_3, \ldots$, the total effect on perturbations is:

$$\text{Final perturbation} = \Phi_3 S_3 \Phi_2 S_2 \Phi_1 S_1 \times \text{Initial perturbation}$$

Where:

- $\Phi_1$ is smooth flow from start to jump 1
- $S_1$ is saltation at jump 1
- $\Phi_2$ is smooth flow from jump 1 to jump 2
- $S_2$ is saltation at jump 2
- And so on...

**Key insight:** This is still a linear map! Even though there are multiple jumps, the overall sensitivity (how does the end depend on the start?) is a matrix product.

### Example: Ball Bouncing 5 Times

Each bounce multiplies perturbations by the saltation matrix $S$. After 5 bounces:

$$\text{Perturbation} = S^5 \times \text{Initial perturbation}$$

If the eigenvalues of $S$ are less than 1 (dissipative impact), then $S^5$ is very small—perturbations die out quickly. The ball's trajectory is stable.

If the eigenvalues were greater than 1 (energy-adding impact, like a ball on a vibrating table), then $S^5$ would be large—perturbations grow, and the trajectory is unstable.

**This explains why:**

- A bouncing ball settles down (eigenvalues < 1)
- A ball on a shaking table can bounce chaotically (eigenvalues can be > 1)

---

## Trade-offs: Hybrid vs. Smooth Approximations

You might ask: "Why bother with all this hybrid machinery? Can't we just smooth things out?"

### Approach 1: Smooth Approximation (Modeling Impact as a Stiff Spring)

**Idea:** Instead of a discontinuous jump, replace the impact with a very stiff spring:

$$F_{contact}(x) = \begin{cases} 0 & \text{if } x > 0 \\ -k \cdot x & \text{if } x \leq 0 \end{cases}, \quad k \to \infty$$

With $k$ very large, this approximates a hard collision.

**Pros:**

- Smooth everywhere (standard calculus applies)
- No special event detection needed

**Cons:**

- **Numerical stiffness:** Requires tiny timesteps (proportional to $1/\sqrt{k}$). For $k = 10^6$, timesteps are microseconds—simulation is slow.
- **Parameter tuning:** What value of $k$ to use? Too small: not realistic. Too large: numerically unstable.
- **Obscures physics:** The "sharpness" of the impact (guard surface) has physical meaning. Smoothing it out hides that structure.

**Verdict:** Works for simple prototypes, but impractical for complex systems like humanoid robots.

### Approach 2: Hybrid Explicit (This Framework)

**Idea:** Treat jumps as discrete events with explicit guards and reset maps.

**Pros:**

- **Accurate:** Respects the physics exactly
- **Fast:** Timesteps can be large (no stiffness)
- **Interpretable:** Clear separation of modes and jumps
- **Optimizable:** Saltation matrices enable gradient-based optimization through jumps

**Cons:**

- **Requires event detection:** Need to find when guards are crossed (adds complexity)
- **Non-smooth:** Standard smooth calculus doesn't apply at jumps (need special handling)

**Verdict:** Best for systems where impacts/switches are the dominant features (robots, manufacturing, docking).

### Approach 3: Contact-Implicit Optimization

**Idea:** Treat contact forces as decision variables with complementarity constraints:

$$\text{Gap} \times \text{Force} = 0, \quad \text{Gap} \geq 0, \quad \text{Force} \geq 0$$

**Pros:**

- Automatically discovers contact timings (don't need to pre-specify when jumps occur)
- Handles multiple simultaneous contacts

**Cons:**

- Non-convex (many local minima)
- Requires good initialization
- Complementarity is tricky to enforce numerically

**Verdict:** Useful for exploration (finding new gaits), then refine with hybrid DDP for robustness.

### Recommendation

Use **hybrid explicit** when:

- Contact sequence is known (e.g., walking: left-right-left-right)
- Accuracy and speed matter
- You need guarantees (convergence, stability)

Use **contact-implicit** when:

- Contact sequence is unknown (e.g., exploring novel gaits)
- System has many potential contacts (e.g., multi-fingered hand grasping)

Use **smooth approximation** when:

- Prototyping quickly
- Impacts are "soft" (stiffness is moderate, not extreme)

---

## Common Questions

### Q1: "Is this just a fancy way of saying 'piecewise smooth'?"

**A:** Yes and no.

**Yes:** Hybrid systems are piecewise smooth (smooth within each mode, jumps at boundaries).

**No:** The framework provides much more than just that label:

- Rigorous tools for computing sensitivities through jumps (saltation matrices)
- Algorithms for optimization (hybrid DDP)
- Geometric interpretation (tangent space transformations)

Saying "piecewise smooth" is like saying a car is "a vehicle with wheels." True, but missing all the engineering details.

### Q2: "Do I need to know the jump times in advance?"

**A:** Not necessarily.

- **If you're simulating:** You detect jumps on the fly using event detection (root-finding when a guard function crosses zero).
- **If you're optimizing:** You can either:
  - Fix the mode sequence and optimize within it (hybrid DDP)
  - Treat jump times as decision variables (mixed-integer optimization)
  - Use contact-implicit methods (complementarity)

The framework supports all three.

### Q3: "What if my system has sliding contact (not just impacts)?"

**A:** Good question. Sliding is handled by **Filippov solutions**.

When a system "slides" along a boundary (like a block on a table with friction), the velocity is tangent to the boundary. Filippov's theory says the dynamics are a _convex combination_ of the vector fields on either side of the boundary.

**Example:** A block on a table:

- If $F_{push} < F_{friction}$: Block doesn't move (stuck)
- If $F_{push} > F_{friction}$: Block slides
- If $F_{push} = F_{friction}$ exactly: Block might be on the edge (sliding mode)

Filippov solutions handle this rigorously. The framework includes this via complementarity constraints.

### Q4: "Can I use this for systems with friction, saturation, or other non-smoothness?"

**A:** Yes, if you model them as hybrid systems:

- **Coulomb friction:** Two modes (sticking vs. sliding), guard at velocity = 0
- **Saturation (e.g., motor torque limits):** Two modes (below limit vs. at limit), guard at torque = max
- **Deadband (e.g., joystick with dead zone):** Multiple modes (dead zone vs. active), guards at threshold values

Any time you have "if-then" rules in your dynamics, you can model it as a hybrid system.

---

## The Bottom Line

**Smooth systems** are the ideal case: flowing nicely on a tangent space at every moment.

**Real systems** often jump, collide, switch modes, and violate smoothness.

**The hybrid framework** extends the tangent space idea to these systems by:

1. Allowing different modes with different physics
2. Explicitly handling guards (boundaries between modes)
3. Using saltation matrices to map perturbations across jumps
4. Composing smooth flow and discrete jumps into a unified picture

**The payoff:**

- We can still optimize trajectories (hybrid DDP)
- We can still design controllers (mode-aware feedback)
- We can still analyze stability (eigenvalues of saltation matrices)

**The cost:**

- More machinery (guards, resets, event detection)
- Non-smooth math (measure theory, complementarity)

But for systems like walking robots, bouncing balls, golf swings, and spacecraft docking, this cost is worth it. The hybrid framework captures the physics correctly, and correct physics leads to better designs.

---

## Connections to the Main Tangent Space Thesis

The main thesis said:
**"Nonlinear systems are secretly linear at every instant."**

This article adds a crucial caveat:
**"...as long as the system is smooth. When it jumps, the tangent space jumps too, but in a predictable linear way."**

**Unified view:**

- **Within modes:** The original tangent space framework applies unchanged
- **At jumps:** We augment the framework with saltation matrices
- **Overall:** Hybrid systems have a _piecewise linear tangent space structure_

This is a natural extension, not a contradiction. The core geometric insight (local linearity) survives, and we gain the ability to handle the most common forms of non-smoothness in engineering.

---

## For Further Exploration

- **Full technical article:** See [Hybrid_Tangent_Spaces.qmd](Hybrid_Tangent_Spaces.qmd) for the math
- **Main tangent space thesis:** See [Tangent_Hyperplanes_Unified_Thesis.qmd](../Tangent_Hyperplanes_Unified_Thesis.qmd) for the smooth case
- **Critical review:** See [CRITICAL_REVIEW.md](../CRITICAL_REVIEW.md) for limitations and edge cases

**Practical resources:**

- Hybrid system simulation: Look up "event-driven simulation" and "zero-crossing detection"
- Optimization: Search for "hybrid DDP," "contact-implicit optimization," and "complementarity constraints"
- Robotics applications: Boston Dynamics walking robots, MIT humanoid locomotion research

---

**Key takeaway:** Most real-world systems aren't perfectly smooth, but that's okay. By treating jumps explicitly (not as approximations), we can leverage the same tangent space framework that works so well for smooth systems, extended with a few new tools (guards, resets, saltation matrices). The result is a unified approach that handles everything from bouncing balls to walking robots to golf swings—all with the same underlying geometric principle: systems are locally linear, even when they jump.
