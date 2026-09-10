# Contact-Force Regularity Review

The acoustic article now distinguishes a finite force jump from an impulse,
derives its Fourier contribution, and explains why equal impulse or restitution
does not determine modal excitation. The original grip, prestress, structural
radiation and blinded-perception sections remain intact. Shared content stays
in the existing Quarto include; two references are added to its canonical
bibliography. No solver, provider pin, protected monograph or research dataset
is changed.

The derivation uses a compactly supported piecewise-smooth force and its
distributional derivative. Integrability of the regular derivative is explicit;
oscillatory cancellation forbids a monotone amplitude or pointwise lower-bound
claim. Continuous force with suitable derivative regularity has the stronger
bound stated in the text. The units of the transformed force and jump term are
N s. The distinction applies to a prescribed mathematical force history before
any structural or acoustic transfer is assumed.

Simbody 3.7 documentation was read directly for the sphere/sphere-plane
Hunt–Crossley equation, storage and low-speed restitution convention. The
Carvalho/Martins2019 institutional abstract and bibliographic metadata were
read for the externally forced adhesion limitation and proposed extensions;
the full article was not retrieved. The publication explicitly retains that
access limit. No exact restitution mapping is adopted from the abstract.
The source-identified Tools279926e95 reference and regularity note are linked;
its first-contact oracle is synthetic and its hosted entry240 timeout remains
unresolved. Numerical convergence is distinct from physical/acoustic validation.

## Validation and Limits

- Python3.12.10 full configured `pytest --cov` passes5229 tests, with29 skips,
  132 deselections and59 warnings in219.88s. Coverage79.29494% exceeds the
  unchanged75% floor. Skips cover absent Streamlit, obsolete helpers,
  unavailable run_async and unrendered legacy wrist examples; no new skip or
  deadline change is introduced.
- All five existing heavy-hit checks pass in0.37s. The separate content-lint
  lane passes131, skips4 and deselects5255 in6.64s.
- Bibliography quality passes169 catalog entries; cross-file audit reports651
  keys,91 shared definitions and zero disagreements. The new BibTeX citations
  resolve in the actual article render. Title case passes636 sources; cross-
  reference audit finds1161 targets and resolves all12 audited book references.
- Quarto1.8.26 renders the affected article successfully with no reported
  warning/error. Browser accessibility-tree inspection of the actual localhost
  route exposes the new section, display equation and both citation links.
  No screenshot, mobile-layout or exhaustive accessibility claim is made.
- Exact source/JUnit/coverage/render identities are in
  FORCE_REGULARITY_RESULTS.json. The rendered HTML and log are retained in TEMP.
  Only generated untracked/ignored files from this newly created worktree's
  docs/.quarto paths were removed after inspection; the known render-modified
  stylesheet was restored to its clean baseline. Existing worktrees were not
  cleaned. Cleanup retained a path/byte manifest.
- Initial bibliography invocation as a script lacked the repository import
  path; the module form passes. Initial read-only checks used systemPython3.13
  before the explicit3.12 runtime was selected; all stated Python qualification
  above was rerun with3.12. No environment or test gate was relaxed.
- Full/content tests rewrote six generated evidence-summary/registry files
  (dates, formatting and a platform-sensitive artifact hash). Their diff is
  retained in TEMP; each was restored from this worktree baseline, rather than
  publishing unrelated generated evidence. No protected source data changed.
- No agent-context catalog was present; focused source and test reads supplied
  the inventory. No protected evidence path was edited. Full-site/protected CI
  and review remain publication requirements.

Continue under Affine4255/4253, Tools5073/5074/5068 and UpstreamDrift9700.
The remaining numerical work includes event-resolved force/work accuracy and
runtime qualification; physical force/FRF, calibrated radiation and blinded
perception remain distinct acceptance requirements.
