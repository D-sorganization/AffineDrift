title: "On the Limits of Strokes-Gained Inference for Individual Golfers"
author: " "
format:
html:
toc: true
pdf: default
Abstract

Strokes gained has transformed golf analytics by decomposing scores into contributions from different parts of the game relative to a benchmark player. However, the same feature that makes strokes gained powerful—the use of a common population baseline—also limits its interpretability when we start talking about individual performance changes and practice priorities.

This article shows, using a formal statistical and mathematical framework, why “if I improve my strokes gained putting by 0.5 per round, I’ll score 0.5 shots better per round” is generally false. Strokes gained is defined with respect to an average player’s expected performance surface, not the individual golfer’s. When a player’s skill profile differs from the benchmark (e.g., unusually poor from short range, unusually strong with wedges), the mapping from a mechanical or tactical change (like leaving putts closer) to actual scoring impact can diverge substantially from what the strokes-gained tables suggest.

We formalize this using conditional expectations, derivatives of expected strokes with respect to state variables (distance, lie, etc.), and the distinction between population-level and individual-level response surfaces. A simple putting example shows that a poor short putter can gain more actual strokes than a good short putter from the same improvement in first-putt proximity—even though the standard strokes-gained metric values the two changes identically. The same logic extends to driving, approach shots, and the short game.

The upshot: strokes gained is excellent as a descriptive and comparative tool, but it is easy to misappropriate it as an individual causal model. Coaches and players who want to use strokes gained to guide training should be explicit about this limitation and, where possible, move toward player-specific or hierarchical models.

1. Introduction

Strokes gained is often treated as the gospel of modern golf analytics: clean, additive, and expressed in the same currency as the scorecard—strokes. But once you start using it to answer questions like

“If I improve my strokes gained putting by 0.3, how many shots will I actually save?”

you’re quietly stepping from description into causal inference, and that’s where things get slippery.

The central point of this article is simple:

Strokes gained is defined with respect to the expected performance of a benchmark population, not with respect to the conditional expectations of any specific golfer. Optimizing a player’s game by treating the benchmark function as if it were the player’s own can systematically misstate the value of changes in technique, training, or strategy.

We’ll formalize the strokes-gained machinery, then show—mathematically and with golf-specific examples—why:

Improving a player’s strokes gained putting does not guarantee a one-for-one improvement in their scoring average.

The same change in shot outcome (e.g., leaving putts 0.5 m closer) can have different scoring impacts for different players, even though strokes gained assigns the same value.

This is a textbook case of misapplying population-level regression functions to individual cases (ecological fallacy / misuse of average treatment effects).

We then extend the reasoning beyond putting to driving, approach play, and around-the-green play, and close with practical implications for science-based coaching.

2. The strokes-gained framework in mathematical form
2.1 The benchmark value function

Following Broadie’s original formulation, let a state on the golf course be described by variables such as:

distance to the hole, 
d
d,

lie / surface / condition, 
c
c (e.g. tee, fairway, rough, sand, green, recovery). 
Columbia University

For a reference population of golfers (e.g., PGA Tour pros measured with ShotLink), define the benchmark value function:

Jref(d,c)  =  E[H ∣ D=d,  C=c],
J
ref
	​

(d,c)=E[H
​

D=d,C=c],

where 
H
H is the random number of strokes required to hole out from state 
(d,c)
(d,c) for a randomly chosen player from the reference population. This function is estimated empirically using millions of shots and smoothed using statistical models such as splines or parametric curve families. 
Columbia University
+1

Intuitively, 
Jref(d,c)
J
ref
	​

(d,c) is “how many strokes an average player of this population needs to finish from here.”

2.2 Per-shot strokes gained

Consider a single shot that starts from state 
(di,ci)
(d
i
	​

,c
i
	​

) and finishes at state 
(di+1,ci+1)
(d
i+1
	​

,c
i+1
	​

), not yet holed. The strokes gained for that shot is defined as

gi  =  Jref(di,ci)−Jref(di+1,ci+1)−1.
g
i
	​

=J
ref
	​

(d
i
	​

,c
i
	​

)−J
ref
	​

(d
i+1
	​

,c
i+1
	​

)−1.

If the shot finishes in the hole, then 
Jref(di+1,ci+1)=0
J
ref
	​

(d
i+1
	​

,c
i+1
	​

)=0. 
Columbia University
+1

The interpretation:

Jref(di,ci)
J
ref
	​

(d
i
	​

,c
i
	​

): how many strokes the benchmark player needs from where you started.

Jref(di+1,ci+1)
J
ref
	​

(d
i+1
	​

,c
i+1
	​

): how many strokes the benchmark player needs from where your ball ended up.

The difference minus the one stroke you actually played is how many strokes you gained (positive) or lost (negative) relative to the benchmark.

Strokes gained over any collection of shots (e.g., a hole, a round, a season, a category such as “putting”) is just the sum of the individual 
gi
g
i
	​

. The telescoping sum identity shows that for a hole:

∑i=1ngi=Jref(d1,c1)−n,
i=1
∑
n
	​

g
i
	​

=J
ref
	​

(d
1
	​

,c
1
	​

)−n,

where 
n
n is the actual number of strokes taken on the hole and 
(d1,c1)
(d
1
	​

,c
1
	​

) is the initial state (typically the tee). 
Columbia University

Thus, total strokes gained on a hole equals “benchmark strokes from the tee” minus “actual strokes,” exactly matching the intuitive description.

2.3 A dynamic programming perspective (briefly)

More formally, the benchmark function satisfies a Bellman equation:

Jref(d,c)=min⁡μE ⁣[Jref(D′,C′)+1 | (D,C)=(d,c),μ],
J
ref
	​

(d,c)=
μ
min
	​

E[J
ref
	​

(D
′
,C
′
)+1∣(D,C)=(d,c),μ],

where 
μ
μ denotes the shot strategy (club, target, etc.) and 
(D′,C′)
(D
′
,C
′
) is the random next state. 
Columbia University

Under this view, the strokes-gained value of a realized shot outcome is the difference between what the dynamic program expected and what actually happened, again measured in strokes. That’s elegant—and, for population-level analysis, very effective. The trouble starts when we implicitly assume that 
Jref
J
ref
	​

 is also the correct value function for each individual golfer.

3. Strokes gained as a population conditional expectation

The critical statistical fact is that 
Jref(d,c)
J
ref
	​

(d,c) is a population conditional expectation:

Jref(d,c)=Epop[H∣D=d,C=c],
J
ref
	​

(d,c)=E
pop
	​

[H∣D=d,C=c],

where the expectation is taken over all shots in the reference population that begin from state 
(d,c)
(d,c). 
Golfshot

Now consider a particular golfer 
i
i. They also have their own (unknown) value function:

Ji(d,c)=E[Hi∣Di=d,Ci=c],
J
i
	​

(d,c)=E[H
i
	​

∣D
i
	​

=d,C
i
	​

=c],

the expected number of strokes for that golfer to hole out from state 
(d,c)
(d,c). In general,

Ji(d,c)  ≠  Jref(d,c).
J
i
	​

(d,c)

=J
ref
	​

(d,c).

This inequality is the entire issue in one line.

Strokes gained uses 
Jref
J
ref
	​

 to score shots.

The player’s actual scoring future is governed by 
Ji
J
i
	​

.

If we use 
Jref
J
ref
	​

 not just for descriptive scoring but as a model of how changes in the state (e.g., closer approaches, better leaves) translate to changes in this golfer’s scoring average, we are implicitly assuming that

Ji(d,c)≈Jref(d,c)for all relevant (d,c),
J
i
	​

(d,c)≈J
ref
	​

(d,c)for all relevant (d,c),

and that the way 
Ji
J
i
	​

 changes with 
d
d, 
c
c, etc. is also similar to the reference player. For elite professionals this might be “not crazy” in aggregate; for ordinary golfers the assumption is often badly wrong.

What follows is a more precise description of how that mismatch creates problems when interpreting strokes-gained improvements for individuals.

4. Gradients of expected strokes and heterogeneous skill profiles
4.1 Local value of a small improvement

Let 
x
x be a continuous state variable, for example, distance to the hole along the green surface. For simplicity, suppose the lie is fixed (putts on the green), so we write

Jref(x)andJi(x)
J
ref
	​

(x)andJ
i
	​

(x)

for the benchmark and individual value functions, respectively.

If a training intervention or strategy change causes the player to leave their first putt, on average, 
Δx<0
Δx<0 metres closer to the hole, then (for small 
Δx
Δx) the change in the benchmark expectation is approximately

ΔJref≈∂Jref∂x(x) Δx,
ΔJ
ref
	​

≈
∂x
∂J
ref
	​

	​

(x)Δx,

while the change in the player’s actual expectation is

ΔJi≈∂Ji∂x(x) Δx.
ΔJ
i
	​

≈
∂x
∂J
i
	​

	​

(x)Δx.

The strokes-gained logic implicitly uses 
ΔJref
ΔJ
ref
	​

 as a surrogate for 
ΔJi
ΔJ
i
	​

. This is only valid if the gradient (slope) of the player’s value function matches the gradient of the benchmark:

∂Ji∂x(x)≈∂Jref∂x(x).
∂x
∂J
i
	​

	​

(x)≈
∂x
∂J
ref
	​

	​

(x).

There is no reason for this to hold in general.

If a golfer is worse than average at short putts, then their chance of holing out deteriorates more rapidly with distance than the reference population’s probability. Their 
Ji(x)
J
i
	​

(x) is steeper than 
Jref(x)
J
ref
	​

(x) for short putts, so 
∣∂Ji/∂x∣
∣∂J
i
	​

/∂x∣ is larger.

Conversely, if a golfer is better than average from short range, their value function is flatter there.

This immediately implies that the same improvement in leave distance (
Δx
Δx) will produce different changes in expected score for different players, even though strokes-gained calculations give them the same credit.

4.2 The key conceptual error

When we say:

“Improving average leave distances from 2.5 m to 2.0 m is worth ~0.05 strokes per putt because that’s what the strokes-gained table says,”

we’re really saying:

ΔJref≈0.05 strokes per putt,
ΔJ
ref
	​

≈0.05 strokes per putt,

and then smuggling in an extra assumption that

ΔJi≈ΔJref.
ΔJ
i
	​

≈ΔJ
ref
	​

.

That step is what is not justified without additional modeling of the individual. It is a classic case of using a population regression function as if it were an individual response curve.

5. A concrete putting example

Let’s make this more explicit with a toy model that still captures the real issue.

5.1 Simple two-putt model

Suppose from some short-putt distance 
x
x (say 1–3 metres), the reference population has one-putt probability 
pref(x)
p
ref
	​

(x), so that:

Probability of holing in one: 
pref(x)
p
ref
	​

(x).

Probability of holing in two: 
1−pref(x)
1−p
ref
	​

(x) (we ignore three-putts at this distance for simplicity).

The benchmark expected strokes from this state is then

Jref(x)=1⋅pref(x)+2⋅(1−pref(x))=2−pref(x).
J
ref
	​

(x)=1⋅p
ref
	​

(x)+2⋅(1−p
ref
	​

(x))=2−p
ref
	​

(x).

Differentiating:

∂Jref∂x(x)=−∂pref∂x(x).
∂x
∂J
ref
	​

	​

(x)=−
∂x
∂p
ref
	​

	​

(x).

So the local value (per metre) of getting closer is controlled by how fast make probability increases as you move in.

Now consider two golfers, both facing putts from distance 
x
x:

Golfer A: “good short putter,” with one-putt probability 
pA(x)
p
A
	​

(x).

Golfer B: “poor short putter,” with one-putt probability 
pB(x)
p
B
	​

(x).

Their individual value functions are

JA(x)=2−pA(x),JB(x)=2−pB(x),
J
A
	​

(x)=2−p
A
	​

(x),J
B
	​

(x)=2−p
B
	​

(x),

with local slopes

∂JA∂x(x)=−pA′(x),∂JB∂x(x)=−pB′(x).
∂x
∂J
A
	​

	​

(x)=−p
A
′
	​

(x),
∂x
∂J
B
	​

	​

(x)=−p
B
′
	​

(x).

For a good putter A, 
pA(x)
p
A
	​

(x) is already high near the hole and typically changes more slowly with distance; 
pA′(x)
p
A
′
	​

(x) (in magnitude) is moderate. For a poor short putter B, 
pB(x)
p
B
	​

(x) is lower and often changes more sharply with distance; 
∣pB′(x)∣
∣p
B
′
	​

(x)∣ is larger.

Now suppose improved approach play reduces their typical leave distance from 
x
x to 
x+Δx
x+Δx with 
Δx<0
Δx<0 (closer to the hole) by the same amount for both golfers. Then, for small 
Δx
Δx,

ΔJA≈−pA′(x)Δx,ΔJB≈−pB′(x)Δx.
ΔJ
A
	​

≈−p
A
′
	​

(x)Δx,ΔJ
B
	​

≈−p
B
′
	​

(x)Δx.

If 
∣pB′(x)∣>∣pA′(x)∣
∣p
B
′
	​

(x)∣>∣p
A
′
	​

(x)∣, the poor short putter B gets a larger reduction in expected strokes per putt from the same distance improvement. In plain language:

A player who is bad from short range gains more (in real scoring terms) from leaving the ball closer than a good short putter does, even though the strokes-gained benchmark assigns the same value to the change in leave distance.

However, the strokes-gained credit for the approach that yielded the closer putt is based on

ΔJref≈−pref′(x) Δx,
ΔJ
ref
	​

≈−p
ref
′
	​

(x)Δx,

which is common to both players. So:

For the poor short putter, strokes gained understates the actual score benefit of leaving the ball closer.

For the strong short putter, strokes gained overstates the benefit.

Strokes-gained putting numbers will still tell you who putted better relative to the benchmark, but they are not a direct estimator of how many strokes you will actually save by improving either your approach proximity or your short-putt skill.

5.2 When “gaining 0.3 strokes putting” is misinterpreted

When analysts say “Player X improved their strokes-gained putting by 0.3 per round this season,” they are reporting:

Δ(average gi on putts),
Δ(average g
i
	​

 on putts),

which is a change in relative performance versus the benchmark. This can be driven by many things:

better holing from specific distances,

better lag putting that changes the distribution of second-putt distances,

different course sets, green speeds, or environmental conditions.

The key: this 0.3 is a change in the sum of 
Jref(xstart)−Jref(xend)−1
J
ref
	​

(x
start
	​

)−J
ref
	​

(x
end
	​

)−1 over all putts—not a direct estimate of the causal impact of a particular mechanical improvement on the player’s own 
Ji
J
i
	​

.

Without a model for how 
Ji
J
i
	​

 changed, inferring “0.3 strokes gained putting → 0.3 strokes better scoring because of putting mechanics” is a leap.

6. Extension to other parts of the game

Exactly the same logic applies off the green.

6.1 Driving distance and the “how much is 10 yards worth?” question

Analyses that estimate the value of +10 yards of driving typically work by evaluating how much the benchmark function 
Jref
J
ref
	​

 decreases when moving the starting point of the second shot 10 yards closer, conditional on lie type. 
Data Golf

Formally, if fairway distance to the hole is 
d
d, the estimated benefit of 10 extra yards is

ΔJref(d)≈Jref(d,fairway)−Jref(d−10,fairway).
ΔJ
ref
	​

(d)≈J
ref
	​

(d,fairway)−J
ref
	​

(d−10,fairway).

To interpret this as “Golfer A gains X strokes per round from being 10 yards longer than Golfer B,” you must assume:

A and B are equally skilled at approach play and putting, so that their individual value functions 
JA
J
A
	​

 and 
JB
J
B
	​

 match 
Jref
J
ref
	​

 at those distances.

A and B have similarly shaped dispersion patterns (fairway vs rough, hazards, etc.), or you explicitly account for different lie distributions. 
Data Golf

If Golfer A is substantially better from long irons than the reference player, and Golfer B is worse, the actual marginal value of moving both of them 10 yards closer is not the same as the benchmark calculation. The reference curve is computing something like an average treatment effect (ATE) of distance across the population; the coach really cares about a conditional individual treatment effect (CITE) for the specific golfer.

6.2 Approach play and wedge distance optimization

“Optimal wedge distance” discussions often use baseline curves of 
Jref(d,fairway)
J
ref
	​

(d,fairway) versus 
d
d to argue about whether a player should lay up to, say, 90 yards versus 50 yards.

Again, the decision is being evaluated with the population expectation surface. But individuals vary enormously in:

spin control,

trajectory consistency,

performance from partial wedges vs fuller swings.

If a particular player is unusually strong at 50-yard shots and unusually weak at 90-yard shots, their individual 
Ji(d,fairway)
J
i
	​

(d,fairway) is shaped differently:

Ji(50,fairway)−Ji(90,fairway)  ≠  Jref(50,fairway)−Jref(90,fairway).
J
i
	​

(50,fairway)−J
i
	​

(90,fairway)

=J
ref
	​

(50,fairway)−J
ref
	​

(90,fairway).

Using the reference surface to prescribe “optimal” lay-up distances can therefore systematically misguide a player whose skill profile is atypical.

6.3 Around-the-green play

Around the green, the same phenomenon appears in:

choice of shot type (chip vs pitch vs putter from fringe),

aggressiveness vs conservativeness,

target selection relative to hazards.

The strokes-gained decomposition will correctly attribute relative performance to different shot types on average, but the marginal value of improving, say, bunker play depends on how that interacts with the player’s proximal putting skill and their existing dispersion pattern out of sand. The benchmark function blends all that over the population.

7. Statistical perspective: ecological fallacy and heterogeneity

The core statistical issue is that strokes gained relies on a single regression surface 
Jref(d,c)
J
ref
	​

(d,c) estimated from a pooled population. In causal-inference language:

Jref
J
ref
	​

 approximates the average potential outcome surface across players.

Player-specific surfaces 
Ji
J
i
	​

 are random draws from a (usually unmodeled) distribution of skill profiles.

Using 
Jref
J
ref
	​

 to make forward-looking statements about interventions on a specific individual implicitly assumes away heterogeneity of treatment effects.

This is analogous to:

Taking a regression of medical outcomes on dosage for a population, then assuming the same dose-response curve holds for every patient.

Using an “expected points added” (EPA) model in American football as if the marginal value of a play call were the same for all teams, regardless of their personnel and scheme. 
lonnylikes.com

From a statistical standpoint, we can view the standard strokes-gained system as estimating:

Jref(d,c)=Ei[Ji(d,c)],
J
ref
	​

(d,c)=E
i
	​

[J
i
	​

(d,c)],

where the expectation is taken over players 
i
i in the reference population. The gradients, second derivatives, and other local properties of 
Jref
J
ref
	​

 are then averages of the corresponding properties of the individual surfaces.

But the coaching question “If this player improves factor X, what happens to their scoring?” is about 
Ji
J
i
	​

, not about 
Ei[Ji]
E
i
	​

[J
i
	​

].

This is precisely where ecological fallacy comes in: inferring individual-level behavior or treatment effects from group-level averages.

7.1 What a more rigorous model would look like

A statistically coherent approach to individualized strokes-gained analysis would model:

Ji(d,c)=Jref(d,c)+δi(d,c),
J
i
	​

(d,c)=J
ref
	​

(d,c)+δ
i
	​

(d,c),

where 
δi(d,c)
δ
i
	​

(d,c) is a player-specific deviation surface. A hierarchical (multilevel) model could:

shrink 
δi
δ
i
	​

 toward zero where data for player 
i
i are sparse,

allow for structured variation, e.g., players differ mainly along a small number of latent dimensions (long game, wedge play, short putts, etc.),

estimate player-specific gradients 
∂Ji/∂d
∂J
i
	​

/∂d that better reflect their own response to distance.

With such a model, we could talk meaningfully about the causal effect of, say, improving proximity from 15–25 feet on this player’s expected scoring, instead of relying on 
Jref
J
ref
	​

 as a proxy.

8. Practical implications for coaching and analysis

Given these limitations, how should science-based coaches and analysts use strokes gained responsibly?

8.1 Use strokes gained for what it is excellent at

Strokes gained is outstanding for:

Performance decomposition: breaking down scoring into off-the-tee, approach, around-the-green, and putting contributions relative to a reference field. 
GolfWRX
+1

Comparisons within a peer group: ranking players against each other within the same dataset and course conditions.

Tracking relative changes over time: seeing whether a player’s performance in a given facet is improving or declining relative to the same benchmark.

For these uses, the fact that 
Jref
J
ref
	​

 is population-based is a feature, not a bug.

8.2 Be explicit when making causal statements

Any time a statement starts to sound like:

“If you improve X by Y, you’ll gain Z strokes,” or

“This practice intervention is worth Q strokes per round,”

you are no longer in purely descriptive territory. At that point:

Recognize that strokes-gained tables are giving you 
ΔJref
ΔJ
ref
	​

, not 
ΔJi
ΔJ
i
	​

.

Ask how plausible it is that the player’s skill profile matches the benchmark assumptions underlying that table.

Where feasible, estimate player-specific baselines from the player’s own shot-level data (even if noisy), possibly with hierarchical shrinkage.

8.3 Pay attention to interaction effects

Because all parts of the game interact through the state transitions, the value of improving any aspect (e.g., proximity on approaches) is conditional on others (e.g., putting performance from the resulting distances).

A lag-putting improvement that changes the distribution of second-putt distances will be worth more for a player who is weak from 4–6 feet than for one who is elite from that range.

A driving-distance gain is worth more to a player who is above average with mid-irons than to one who gains little from slightly shorter approaches.

The reference 
Jref
J
ref
	​

 integrates over these interactions on average; it does not know the player’s individual strengths and weaknesses.

9. Conclusion

Strokes gained is, mathematically, a value function for an average player in a specified reference population. It assigns a score to each shot by comparing the realized state transition to what that average player would experience. For comparing players and decomposing performance, this is extremely powerful.

However, when that same machinery is used to infer the individual causal impact of changes in technique, practice, or strategy, an important assumption is often left unstated: that the individual golfer’s conditional expectation surface 
Ji
J
i
	​

 looks enough like the benchmark 
Jref
J
ref
	​

 that the gradients and local changes calculated from 
Jref
J
ref
	​

 are good proxies for those of 
Ji
J
i
	​

.

In reality:

Golfers differ systematically in their skill profiles across distances and shot types.

The same physical or strategic change can have different scoring impacts for different players, even when strokes gained assigns identical value to the resulting shot patterns.

Interpreting changes in strokes gained as direct, player-specific causal effects is a misappropriation of a population-level model to an individual case.

For a science-based golf community, the way forward is not to discard strokes gained but to contextualize it:

Keep using it as a descriptive and comparative tool.

Treat causal claims about individual players as requiring additional modeling—ideally player-specific or hierarchical models of expected strokes to hole out.

Acknowledge the difference between “average effect according to the benchmark” and “effect for this player with this particular skill profile.”

Or, less formally: the “average player” that strokes gained is based on is a useful fictitious character—but nobody on your lesson tee is actually that golfer.

References (informal)

Broadie, M. (2011). Assessing Golfer Performance on the PGA TOUR. Working paper, Columbia University. 
Columbia University

Broadie, M. (2014). Every Shot Counts. Gotham Books.

DataGolf. “How much is 10 yards worth?” (accessed 2025). 
Data Golf

Various explanatory articles on strokes gained calculation and usage (ShotLink-based benchmark functions, category decomposition, and practical examples). 
GolfWRX
+2