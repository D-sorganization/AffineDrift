# Ignored Issues Register

This document tracks linting and static analysis issues that have been explicitly ignored or suppressed, along with the justification.

## Python (MyPy)

### `tools/wrist_universal_joint/Grip_Angle_Torque_Transmission_Streamlit.py`
- **Rule:** `misc` (Untyped decorator)
- **Target:** `@st.cache_resource` decorators
- **Justification:** Streamlit's caching decorators are not fully typed in the current version or stubs are missing. Annotating with `ignore[misc]` is the recommended workaround to allow strict checking on the rest of the file.

### `articles/Tangent Hyperplane Articles/archive/generate_pdfs.py`
- **Rule:** `import-untyped`
- **Target:** `import markdown`
- **Justification:** The `markdown` library does not ship with type stubs by default. Since this is an archival utility script, installing `types-Markdown` globally is not prioritized.

## General
- **Rule:** `missing-imports` (MyPy)
- **Target:** Global
- **Justification:** The CI command `mypy . --ignore-missing-imports` is used to prevent failures due to missing third-party stubs for non-critical dependencies.
