# Ignored Issues Log

**Date:** 2026-01-20

## Out of Scope
*   **Bus Factor / Documentation**: Issues related to project management and documentation (e.g., "Bus Factor = 1") were not addressed by the Code Quality Fixer agent.
*   **Interactive Visualizations**: Deployment of visualization features is a feature request, not a code quality fix.

## Suppressed Warnings
*   **`tools/wrist_universal_joint/Grip_Angle_Torque_Transmission_Streamlit.py`**: `@st.cache_resource` is untyped in the current Streamlit stubs, requiring `# type: ignore[misc]`.
*   **`articles/Tangent Hyperplane Articles/archive/generate_pdfs.py`**: `markdown` library lacks type stubs, requiring `# type: ignore[import-untyped]`.
