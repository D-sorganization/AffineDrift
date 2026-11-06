---
title: "The Alpha War: plan and outline (UNPUBLISHED DRAFT)"
draft: true
listing: false
status: do-not-publish
---

# The Alpha War — thesis-level review: plan

**Status:** first-pass drafting. Not for publication until complete, verified, panel-reviewed and signed off by Dieter. Lives under `research/alpha-war/`, which is outside the Quarto render list.

**Question.** Near impact, do the golfer's hands apply positive or negative "alpha" torque (the in-plane couple about the grip that acts to open or close the wrist-hinge angle) to the club? Camp A: Nesbit, Manzella, Jacobs 3D. Camp B: Kwon, MacKenzie, Tutelman.

**Tone.** Neutral, educational, readable by a layperson, full mathematics in boxed derivations and appendices.

## Execution
| Stage | Model (Antigravity on OGLaptop) | Output |
|---|---|---|
| 1. Corpus extraction | Gemini 3.8 Flash | `work/01_corpus_digest.md` |
| 2. Reference gathering + claim matrix | Gemini 3.8 Flash | `work/02_references.md`, `work/03_claims.md` |
| 3. Full synthesis, first pass | Gemini 4 Argon (High) | `draft/alpha-war-v0.md` |
| 4. Calculations | UpstreamDrift tools (inverse dynamics, double-pendulum / grip couple decomposition) | `calcs/` |
| 5. Panel review (4-seat) | after v0 is complete | `critiques/` |

Raw Facebook data stays local (git-excluded `corpus/`); only paraphrase and short attributed quotes enter the draft.

## Outline
1. Problem statement: what "alpha torque" means and why it matters
2. Definitions and coordinate frames (club, grip, functional swing plane; alpha/beta/gamma axes; sign conventions)
3. Kinematics and kinetics: Newton–Euler for the club as a rigid body, grip force and couple, centripetal/"pull" contributions, energy and power flow
4. Camp A's argument and evidence (Nesbit 2005/2009 data, Manzella, Jacobs 3D)
5. Camp B's argument and evidence (Kwon, MacKenzie models, Tutelman)
6. Measurement issues: grip-point choice, filtering near impact, frame definitions, inverse-dynamics error propagation
7. Simulation results via UpstreamDrift (sensitivity of sign to grip point, filter cutoff, model)
8. Synthesis and resolution: what is settled, what is definitional, what remains open and how to test it
9. Glossary
10. References, categorized: (a) primary research, (b) instruction/coaching sources, (c) Facebook discussion corpus, (d) code and calculations
