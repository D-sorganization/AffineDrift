# Embedding the Cardan and Torque Projection Demonstration

## Browser Version

The implemented browser entry is `src/tools/wrist_universal_joint/grip_angle_simulator.html`.
Serve it together with its adjacent JavaScript assets. It loads Plotly from an
external script URL, so offline operation requires an explicit local dependency
and cache strategy; the current page is not dependency-free.

For a page at the site root:

```html
<h2>Cardan and Torque Projection Demonstration</h2>
<p>
  Supported shafts and synthetic torque projections; not a calibrated wrist
  model.
</p>
<iframe
  src="src/tools/wrist_universal_joint/grip_angle_simulator.html"
  title="Cardan and Torque Projection Demonstration"
  width="100%"
  height="1000"
  loading="lazy"
>
</iframe>
```

Resolve the path relative to the embedding page and verify that the deployment
copies the HTML and adjacent assets. Resize and scroll the embed on small
screens; a fixed iframe height does not itself prove mobile usability.

## Optional Streamlit Version

The module uses package-relative imports. Create a local entry script at the
repository root containing:

```python
from src.tools.wrist_universal_joint.streamlit_app import main

main()
```

With the dependencies in this directory's `requirements.txt` installed, run
`python -m streamlit run app_entry.py`, replacing `app_entry.py` with the actual
entry filename. A hosted deployment must use that entry and supply the same
package layout and dependencies. Do not use the removed historical filename
`Grip_Angle_Torque_Transmission_Streamlit.py`.

If an instance is hosted, embed its actual URL with an accessible iframe title.
The placeholder URL in `embed_example.html` is not a deployed service. Hosting
plans, availability and pricing must be checked with the provider when deploying.

## Interpretation

The bend and phase controls belong to a supported Cardan assembly. The hand
sketch is historical, and the extra torque projection is a synthetic choice.
The scalar inertia response omits the moving-support and coupled spatial
dynamics needed for a golf model. Keep this qualification beside an embed.
See [the model README](README.md) for the complete scope and technical sources.
