# Launch Monitor Technology Review

A comprehensive LaTeX technology review of how commercial golf launch monitors
work — radar physics, camera photogrammetry, patent landscape, and the
club/ball parameter calculations — a vendor-neutral technical reference.

> **This document lives here now.** It was previously maintained in
> `openflight_development/tech-review/`. All the golf articles are kept in
> AffineDrift so they share one CI and release path; `openflight_development`
> reaches it through a submodule, the same way the fleet's other repositories
> vendor shared content. It is built by the shared `compile-textbooks` workflow
> alongside the other LaTeX documents here.
>
> Its companion, **[Screw Theory Applied to Launch
> Monitors](research/screw-theory-research-outline.md)**, moved at the same
> time. That outline seeds future sections of this document and depends on
> Appendix E, so the two are kept together.

> **Contributing?** Read **[CONVENTIONS.md](CONVENTIONS.md)** first — it covers file
> layout, labels, citation keys, prose style, and the build. This document is
> designed to grow toward a textbook-scale reference edited by many hands.

- **[main.pdf](main.pdf)** — the compiled report
- `main.tex` + `sections/` — LaTeX source (11 chapters + 5 appendices), one file per chapter
- `references.bib` — the bibliography database (grouped by source category)
- `build.ps1` — local build; CI builds every PR via `.github/workflows/compile-textbooks.yml`
- `research/` — the four raw research dossiers the report was synthesized from
  (radar systems, camera systems, patents, physics/algorithms), with source
  URLs for every claim
- `build.ps1` — compile script (MiKTeX pdflatex, 3 passes)

## Report contents

1. Introduction — sensing families, market convergence
2. Parameter definitions — TrackMan conventions, the measured/derived/estimated hierarchy
3. Impact physics — D-plane, face/path weighting, smash factor, spin generation, gear effect
4. Doppler radar systems — CW/FMCW, phase interferometry, harmonic-sideband spin, spin-axis inversion, OERT
5. Photometric systems — stereo photogrammetry, dimple-registration spin, fiducial club tracking, PiTrac
6. Commercial survey — architecture table for every major device
7. Patent landscape — TrackMan/Tuxen, Foresight/Wintriss, FlightScope/EDH, Acushnet, with freedom-to-operate map
8. Ball flight models — Smits–Smith / Quintavalla aerodynamics, EKF trajectory estimation
9. Accuracy — Leach 2017 and the validation literature
10. Design guidance for implementers — capability tiers (radar hardening → optical spin/impact module → fusion → measured club delivery)
11. Governed analytics and validation program — qualified-corpus limits, canonical statistics, Release A analytics, and the preregistered paired-device gate for Release B

Appendix A — Annotated reference library: sources organized by evidential role, with historical vendor specifications, study conditions, patent-disclosure limits, and distinctions between accuracy, dispersion, and data availability

Appendix C — Sensor hardware and integration reference: OPS243-A specs/API/rolling buffer + the AN-029 vendor golf recipe (a vendor-published golf configuration), K-LD7 datasheet + UART protocol, IWR6843 FMCW specifics, Pi Global Shutter XTR triggering, the full GSPro Open Connect schema, USGA equipment constants, and CFAR selection guidance

Appendix D — Patent portfolio compendium: every identified US patent for TrackMan (all 45 on their legal page + 7 more), Topgolf Sweden/Toptracer, FlightScope/EDH, Full Swing (US11311789 grant), Garmin, Rapsodo, Foresight/Wintriss, Creatz/Uneekor, Golfzon, Acushnet (back to the ancestral 1977 US4136387), plus prior art (Sports Sensors, Weibel, Stalker) — each number hotlinked to Google Patents, with two attribution corrections (US10596416 family = Toptracer, not TrackMan)

Appendix E — Radar Clubhead Kinematics: Motion and Observability — consistent point/body/spatial velocity conventions; the exact single-origin Doppler rank limit; conditional uncertainty and temporal observability; coupled TDM waveform budgets; and a proposed estimation and validation sequence. Speed, path, face closure, swing plane, and low point require distinct reference, geometry, timing, and evidence conditions. This appendix is a bounded technical review; the remaining chapters and historical research outline are not newly qualified.

Appendix B — Detailed implementation guidance: OPS243-A DSP parameters (Doppler scaling, window/chirp trade-offs, comb spin estimation), K-LD7 interferometry + EKF/RTS smoother design, alignment calibration procedures, D-plane inversion with priors and gear-effect bounds, Phase-2 optical module design parameters (strobe timing, dimple registration), and the MLM2PRO validation protocol
