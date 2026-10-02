# Chapter 7 Preparation — No Audit Credit

Prepared while Chapter 19 delivery and parent #4800 CI are pending. No new
issue, lease, canonical chapter edit, figure edit or completion credit exists.
The full 255-line lay chapter was read; its indexed approximate word count is
2,080, the largest remaining pending entry. Two supplied-text agy CLI
`gemini-3.8-flash-high` inventory/copy helpers completed and were read by the
lead. They did not decide technical truth or edit/publish. Their exact output is
retained in `pendulum-preparation-{inventory,copy}-flash.txt`.

## Lead Candidates for a Later Review

1. Declare absolute versus relative coordinates before naming input torques.
   For absolute arm/club angles a shoulder actuator and internal wrist actuator
   have generalized loads `(tau_s - tau_w, tau_w)`. With relative wrist angle,
   the loads are `(tau_s, tau_w)`. Virtual work and power must be invariant under
   the change of coordinates. A generalized mass-matrix diagonal is not simply
   that link's own physical inertia in every coordinate convention.
2. A zero off-diagonal entry at one configuration is not physical decoupling.
   In absolute angles the cross inertia can vanish at a right angle while its
   configuration derivative, and hence velocity-dependent interaction, remains.
   Deleting a matrix entry without the corresponding energy/bias model is not a
   valid mechanical limiting case. An appropriate manufactured check should
   compare equivalent coordinate formulations and conserve power/energy.
3. Both components of a hand-applied force have zero moment about that hand
   point. About the club COM, the tangential component can have a moment. An
   accelerating hand is not a fixed inertial pivot: the planar balance about it
   includes `m r_COM/hand × a_hand`, in addition to `I_hand alpha`. Contact power
   uses the actual hand-point velocity. The current wording about tangential
   force accelerating the club 'about the hand' needs a declared reference and
   moving-point balance, not a radial-force-is-workless rule.
4. Mass/length limits require a complete parameter and loading family. Sending
   mass to zero while retaining rotary inertia or a finite actuator couple need
   not remove all reactions. A massless/inertia-free dynamic coordinate can be
   singular; a bounded-state family is not the same as holding finite torque
   while inertia vanishes. Zero length need not eliminate retained rotary DOF.
   An already locked joint differs from an impulsive locking event and its
   energy loss. No universal zero-input-energy rule permits hidden damping or
   preloaded storage to be ignored.
5. Underactuation concerns available actuator rank, not whether a fully
   actuated system happens to receive a zero wrist command. Pointwise zeroing
   and a forward branch answer different questions; velocity deletion may
   remove damping as well as quadratic inertial terms if both are present.
6. Avoid describing absolute angular velocity about a translating hand as
   relative wrist angular velocity, or adding scalar speeds as if their
   directions were identical. A rigid-link benchmark has no shaft strain state;
   explain what 'stored' energy means before invoking higher-model elasticity.
7. Replace generic schedule results and 'invariants' with registered input,
   state, event, output and model qualification. A changed-model sign reversal
   is sensitivity, not automatically a bug; non-replication is not proof that
   added relevant physics could never change the conclusion. Check cited model
   studies directly before attributing optimal torque timing or human strategy.
8. Inspect the existing carry/reorient/handoff figure before deciding whether
   its graphic and caption imply a sequential transfer contradicted by prose.
   No figure pixels have been inspected in this preparation.

These are candidate corrections, not completed findings. Proposed arithmetic
and transformed dynamics have not yet been executed as tests in this packet.

## Reading Scope and Remaining Evidence

- Upstream `85cce4d3307bb7ad3953d9fc6e583e370803515c`: saved mechanics and
  interaction chapters from local Git. Read only the first 230 physical lines
  of the mechanics chapter in this preparation, including formalism, sequencing
  and double-pendulum literature discussion. The remainder and the interaction
  capture are unread here; do not credit them based on file creation.
- [MIT Acrobot equations](https://underactuated.mit.edu/acrobot.html): read the
  Acrobot definition and equations of motion (rendered lines 15–26). The source
  explicitly uses a relative elbow angle and pivot inertias, distinguishes
  Acrobot from shoulder-driven Pendubot, and gives the input map and coupled
  dynamics. No exercise execution, image inspection or whole-page review.
- Sharp 2009 DOI lookup returned an internal fetch error. Search snippets and
  third-party summaries do not establish full-paper reading. Locate an original
  copy before using detailed claims; Jorgensen and Putnam direct reading also
  remain pending for this chapter's final literature assessment.
- Helper repeated-phrase inventory is useful navigation. Retain pedagogically
  useful reinforcement and correct directives; a helper flag on 'must not'
  does not itself identify a technical defect. Reject treating every pronoun as
  an error or interpreting a failed benchmark automatically as a software bug.

Resume only after coordination/claim checks and in an owned issue worktree.
Keep Chapter 19's eight source helpers distinct from these two preparation jobs.
