# Bibliographic Analysis: Precision vs. Gross Control (The "Locked-In" Fallacy)

## A) Concept Map

- **Control Hierarchy**
  - **Gross Trajectory Control**: The ability to fundamentally reshape the path (e.g., stop, reverse, change plane). Requires large forces ($F \approx ma$) relative to momentum.
  - **Fine Outcome Control (Micro-Correction)**: The ability to adjust terminal parameters (face angle, impact location) by small margins. Requires precision, not large force.
  - **Drift-Control Ratio (DCR)**: A metric quantifying the dominance of passive dynamics over active control authority.

- **Motor Control Theory**
  - **Uncontrolled Manifold (UCM)**: The hypothesis that the nervous system allows variability in dimensions that don't affect the task (Todorov/Latash).
  - **Minimum Intervention Principle**: Control is applied only to task-relevant deviations to minimize effort and noise.
  - **Signal-Dependent Noise**: The observation that motor noise scales with control signal magnitude ($u$), creating a trade-off where "trying harder" reduces precision.
  - **Impedance Control**: Modulating stiffness/damping rather than force to stabilize trajectories against perturbations.

- **Mechanics of Variability**
  - **Reachability Sets**: The set of future states attainable from current state $x$ given input limits $u \in U$.
  - **Ballistic Motion**: Movements where trajectory is largely determined by initial conditions, with limited mid-flight correction.

## B) Bibliography (YAML)

```yaml
- id: todorov2004optimality
  title: "Optimality principles in sensorimotor control"
  authors:
    - "Emanuel Todorov"
  year: 2004
  venue: "Nature Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Optimality+principles+in+sensorimotor+control+Todorov"
  clusters: ["motor control", "neuroscience"]
  concepts: ["minimum intervention", "uncontrolled manifold", "optimal feedback control"]
  related_ids: ["harris1998signal", "latash2008synergy"]
  references_out_ids: ["scott2004optimal", "loeb2012optimal"]

- id: harris1998signal
  title: "Signal-dependent noise determines motor planning"
  authors:
    - "Christopher M. Harris"
    - "Daniel M. Wolpert"
  year: 1998
  venue: "Nature"
  scholar_link: "https://scholar.google.com/scholar?q=Signal-dependent+noise+determines+motor+planning+Harris"
  clusters: ["motor control", "neuroscience"]
  concepts: ["signal-dependent noise", "trajectory planning", "fitts law"]
  related_ids: ["todorov2004optimality"]
  references_out_ids: ["fitts1954information"]

- id: latash2008synergy
  title: "Synergy"
  authors:
    - "Mark L. Latash"
  year: 2008
  venue: "Oxford University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Synergy+Latash"
  clusters: ["motor control", "biomechanics"]
  concepts: ["principle of abundance", "motor synergies", "variability"]
  related_ids: ["bernstein1967coordination"]
  references_out_ids: ["bernstein1967coordination", "scholz1999uncontrolled"]

- id: langdown2013address
  title: "Address Position Variability in Golfers of Differing Skill Level"
  authors:
    - "Ben Langdown"
    - "Matthew Bridge"
    - "Francois-Xavier Li"
  year: 2013
  venue: "International Journal of Golf Science"
  scholar_link: "https://scholar.google.com/scholar?q=Address+Position+Variability+in+Golfers+Langdown"
  clusters: ["golf biomechanics", "variability"]
  concepts: ["kinematic variability", "setup consistency", "skill acquisition"]
  related_ids: ["bradshaw2009variability"]
  references_out_ids: ["bradshaw2009variability"]

- id: bradshaw2009variability
  title: "Variability of the golf swing"
  authors:
    - "Elizabeth J. Bradshaw"
    - "et al."
  year: 2009
  venue: "Journal of Sports Sciences"
  scholar_link: "https://scholar.google.com/scholar?q=Variability+of+the+golf+swing+Bradshaw"
  clusters: ["golf biomechanics", "variability"]
  concepts: ["inter-trial variability", "kinematics", "consistency"]
  related_ids: ["langdown2013address"]
  references_out_ids: []

- id: hogan1985impedance
  title: "Impedance control: An approach to manipulation: Part I—Theory"
  authors:
    - "Neville Hogan"
  year: 1985
  venue: "Journal of Dynamic Systems, Measurement, and Control"
  scholar_link: "https://scholar.google.com/scholar?q=Impedance+control+An+approach+to+manipulation+Hogan"
  clusters: ["robotics", "motor control"]
  concepts: ["mechanical impedance", "stiffness control", "interaction"]
  related_ids: ["burdet2001central"]
  references_out_ids: ["burdet2001central"]

- id: burdet2001central
  title: "The central nervous system stabilizes unstable dynamics by learning optimal impedance"
  authors:
    - "Etienne Burdet"
    - "R. Osu"
    - "D. W. Franklin"
    - "T. E. Milner"
    - "M. Kawato"
  year: 2001
  venue: "Nature"
  scholar_link: "https://scholar.google.com/scholar?q=The+central+nervous+system+stabilizes+unstable+dynamics+Burdet"
  clusters: ["motor control", "neuroscience"]
  concepts: ["impedance learning", "stability", "stiffness modulation"]
  related_ids: ["hogan1985impedance"]
  references_out_ids: ["franklin2008cns"]

- id: bernstein1967coordination
  title: "The Co-ordination and Regulation of Movements"
  authors:
    - "Nikolai A. Bernstein"
  year: 1967
  venue: "Pergamon Press"
  scholar_link: "https://scholar.google.com/scholar?q=The+Co-ordination+and+Regulation+of+Movements+Bernstein"
  clusters: ["motor control", "foundational"]
  concepts: ["degrees of freedom problem", "repetition without repetition", "coordination"]
  related_ids: ["latash2008synergy"]
  references_out_ids: ["latash2008synergy"]

- id: flash1985coordination
  title: "The coordination of arm movements: an experimentally confirmed mathematical model"
  authors:
    - "Tamar Flash"
    - "Neville Hogan"
  year: 1985
  venue: "Journal of Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=The+coordination+of+arm+movements+Flash+Hogan"
  clusters: ["motor control", "trajectory planning"]
  concepts: ["minimum jerk", "smoothness", "invariant features"]
  related_ids: ["harris1998signal"]
  references_out_ids: ["shadmehr1994adaptive"]

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors:
    - "Sasho J. MacKenzie"
    - "Eric J. Sprigings"
  year: 2009
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=A+three-dimensional+forward+dynamics+model+of+the+golf+swing+MacKenzie"
  clusters: ["golf biomechanics", "simulation"]
  concepts: ["forward dynamics", "impact parameters", "sensitivity"]
  related_ids: ["nesbit2005three"]
  references_out_ids: ["nesbit2005three"]

- id: fitts1954information
  title: "The information capacity of the human motor system in controlling the amplitude of movement"
  authors:
    - "Paul M. Fitts"
  year: 1954
  venue: "Journal of Experimental Psychology"
  scholar_link: "https://scholar.google.com/scholar?q=The+information+capacity+of+the+human+motor+system+Fitts"
  clusters: ["motor control", "psychology"]
  concepts: ["fitts law", "speed-accuracy trade-off", "information theory"]
  related_ids: ["harris1998signal"]
  references_out_ids: []

- id: scott2004optimal
  title: "Optimal feedback control and the neural basis of volitional movement"
  authors:
    - "Stephen H. Scott"
  year: 2004
  venue: "Nature Reviews Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Optimal+feedback+control+and+the+neural+basis+Scott"
  clusters: ["motor control", "neuroscience"]
  concepts: ["optimal feedback control", "primary motor cortex", "reflex gains"]
  related_ids: ["todorov2004optimality"]
  references_out_ids: []

- id: wolpert1996forward
  title: "Forward models for physiological motor control"
  authors:
    - "Daniel M. Wolpert"
    - "R. Christopher Miall"
  year: 1996
  venue: "Neural Networks"
  scholar_link: "https://scholar.google.com/scholar?q=Forward+models+for+physiological+motor+control+Wolpert"
  clusters: ["motor control", "computational neuroscience"]
  concepts: ["forward models", "internal models", "prediction"]
  related_ids: ["kawato1999internal"]
  references_out_ids: ["kawato1999internal"]

- id: shadmehr1994adaptive
  title: "Adaptive representation of dynamics during learning of a motor task"
  authors:
    - "Reza Shadmehr"
    - "Sandro A. Mussa-Ivaldi"
  year: 1994
  venue: "Journal of Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Adaptive+representation+of+dynamics+during+learning+Shadmehr"
  clusters: ["motor learning", "neuroscience"]
  concepts: ["force fields", "internal models", "adaptation"]
  related_ids: ["burdet2001central"]
  references_out_ids: []

- id: kawato1999internal
  title: "Internal models for motor control and trajectory planning"
  authors:
    - "Mitsuo Kawato"
  year: 1999
  venue: "Current Opinion in Neurobiology"
  scholar_link: "https://scholar.google.com/scholar?q=Internal+models+for+motor+control+Kawato"
  clusters: ["motor control", "neuroscience"]
  concepts: ["inverse models", "cerebellum", "motor learning"]
  related_ids: ["wolpert1996forward"]
  references_out_ids: []

- id: franklin2008cns
  title: "CNS learns stable, accurate, and efficient movements using a simple algorithm"
  authors:
    - "David W. Franklin"
    - "et al."
  year: 2008
  venue: "Journal of Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=CNS+learns+stable+accurate+and+efficient+movements+Franklin"
  clusters: ["motor learning", "impedance control"]
  concepts: ["stability", "energy efficiency", "learning algorithms"]
  related_ids: ["burdet2001central"]
  references_out_ids: []

- id: opensim_lib
  title: "OpenSim: open-source software to create and analyze dynamic simulations of movement"
  authors:
    - "Scott L. Delp"
    - "et al."
  year: 2007
  venue: "IEEE Transactions on Biomedical Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=OpenSim+Delp"
  clusters: ["software", "biomechanics"]
  concepts: ["musculoskeletal modeling", "simulation", "inverse kinematics"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: []

- id: simscape_lib
  title: "Simscape Multibody"
  authors:
    - "MathWorks"
  year: 2024
  venue: "Software"
  scholar_link: "https://scholar.google.com/scholar?q=Simscape+Multibody"
  clusters: ["software", "simulation"]
  concepts: ["multibody simulation", "block diagram", "physical modeling"]
  related_ids: []
  references_out_ids: []

- id: loeb2012optimal
  title: "Optimal control of biological movement"
  authors:
    - "Gerald E. Loeb"
  year: 2012
  venue: "Comprehensive Physiology"
  scholar_link: "https://scholar.google.com/scholar?q=Optimal+control+of+biological+movement+Loeb"
  clusters: ["motor control", "physiology"]
  concepts: ["optimal control", "muscle mechanics", "redundancy"]
  related_ids: ["todorov2004optimality"]
  references_out_ids: []

- id: nesbit2005three
  title: "A three dimensional kinematic and kinetic study of the golf swing"
  authors:
    - "Steven M. Nesbit"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=A+three+dimensional+kinematic+and+kinetic+study+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "inverse dynamics"]
  concepts: ["joint torques", "work and power", "full-body model"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: ["mackenzie2009three"]
```

## C) Reading Paths

### Path 1: Fast Ramp (The Core Argument)

_Target: Understand why "Locked-In" doesn't mean "Helpless"._

1.  **Todorov (2004)** - _Optimality principles_ (`todorov2004optimality`). The key paper explaining why we shouldn't control everything, only what matters.
2.  **Bernstein (1967)** - _Co-ordination..._ (`bernstein1967coordination`). The concept of "Repetition without Repetition"—achieving the same outcome with different movements.
3.  **MacKenzie & Sprigings (2009)** - _Forward dynamics model_ (`mackenzie2009three`). Shows that small changes in input lead to meaningful changes in impact.
4.  **Harris & Wolpert (1998)** - _Signal-dependent noise_ (`harris1998signal`). Explains the cost of control: more force = more noise.
5.  **Fitts (1954)** - _Information capacity..._ (`fitts1954information`). The classic trade-off between speed (force) and precision.

### Path 2: Deep Technical (Motor Control Theory)

_Target: The mathematical basis for variability and control._

1.  **Latash (2008)** - _Synergy_ (`latash2008synergy`). Thorough exploration of the Uncontrolled Manifold (UCM) hypothesis.
2.  **Burdet et al. (2001)** - _CNS stabilizes unstable dynamics..._ (`burdet2001central`). How humans use impedance (stiffness) to handle instability.
3.  **Scott (2004)** - _Optimal feedback control..._ (`scott2004optimal`). The neural implementation of Todorov's theory.
4.  **Wolpert & Miall (1996)** - _Forward models..._ (`wolpert1996forward`). How the brain predicts consequences of action.
5.  **Shadmehr & Mussa-Ivaldi (1994)** - _Adaptive representation..._ (`shadmehr1994adaptive`). Learning dynamics fields.
6.  **Kawato (1999)** - _Internal models..._ (`kawato1999internal`). Computational neuroscience of trajectory planning.
7.  **Flash & Hogan (1985)** - _Coordination of arm movements_ (`flash1985coordination`). The Minimum Jerk hypothesis.
8.  **Hogan (1985)** - _Impedance control_ (`hogan1985impedance`). Theory of managing interaction forces.

### Path 3: Implementation (Simulation & Data)

_Target: Verifying the claims numerically._

1.  **Langdown et al. (2013)** - _Address Position Variability_ (`langdown2013address`). Empirical data on how much golfers actually vary.
2.  **Bradshaw et al. (2009)** - _Variability of the golf swing_ (`bradshaw2009variability`). More data on swing consistency.
3.  **MacKenzie (Code/Model)** - (`mackenzie2009three`). Reference for forward dynamics implementation.
4.  **OpenSim (Delp et al.)** - (`opensim_lib`). Open-source musculoskeletal modeling software to test these theories.
5.  **Simscape Multibody** - (`simscape_lib`). Tool for building rigid/flexible multibody simulations (like AffineDrift).
