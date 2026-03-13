What it conveys:

- **Top panel**: visual proof of “drift explodes, control fades” as we approach impact.
- **Bottom panel**: DCR goes from < 1 (control-dominated) to ≫ 10 (drift-dominated) → nice visual hook for your “collapse of control authority” sections.

---

## 2. Control Cone Visualization (Relativity Analogy)

Now for the fun one: a **control cone** diagram, inspired by light cones.

We’ll plot:

- Horizontal axis: time (normalized swing phase)
- Vertical axis: “reachable deviation” from the nominal trajectory (abstracted as ±max deviation)
- The cone narrows as time → impact, representing the reachable set shrinking as DCR explodes.

You can drop this **as-is** into your Quarto paper as another figure:

```{python}
import numpy as np
import matplotlib.pyplot as plt

# Time axis: start of backswing (0) to impact (1)
t = np.linspace(0, 1, 500)

# Define "cone half-width" as a simple decreasing function of time
# Wide early (large reachable set), narrow near impact
# Using a gaussian decay to ensure it shrinks towards impact
max_dev = 0.4 * np.exp(-3 * t**2)  # Wide at t=0, narrow at t=1

upper = max_dev
lower = -max_dev

plt.figure(figsize=(10, 5))

# Fill the cone region
plt.fill_between(t, lower, upper, alpha=0.3)

# Nominal trajectory (zero deviation line)
plt.plot(t, np.zeros_like(t), linestyle="--", linewidth=2)

plt.title("Control Cone: Shrinking Reachable Set as the Swing Approaches Impact")
plt.xlabel("Normalized Swing Phase (0 = Start, 1 = Impact)")
plt.ylabel("Reachable State Deviation (Abstract Units)")
plt.grid(True)

# Annotate phases
plt.text(0.05, 0.25, "Backswing:\nWide Control Cone", fontsize=10)
plt.text(0.45, 0.18, "Transition:\nCone Tilting/Narrowing", fontsize=10)
plt.text(0.8, 0.05, "Late Downswing:\nCone Collapse", fontsize=10)

plt.tight_layout()
plt.show()
```
