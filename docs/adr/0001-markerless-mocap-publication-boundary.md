# 0001. Markerless Mocap Publication and Licensing Boundary

## Status

Accepted for AffineDrift issue #3954 under parent epic #3952.

## Context

The markerless motion-capture program spans repositories with different authority,
licenses, data exposure, and validation duties. Runtime capture and reconstruction
belong outside AffineDrift. A public textbook cannot silently acquire private shop
recordings, reproduce another repository's computational contracts, follow a moving
branch, or turn a model scenario into an observed human result.

AffineDrift already publishes immutable upstream projections. Markerless mocap uses
the same fail-closed pattern, with additional human-subject, privacy, security, and
license gates.

## Decision

AffineDrift never owns capture, synchronization, calibration, or reconstruction runtime.
The responsibility boundary is:

| Authority | Repository | AffineDrift Relationship |
| --- | --- | --- |
| Camera, frame, time, skeleton, and interchange contracts | Tools | Consume a protected, versioned public release; do not copy the implementation. |
| Session orchestration, calibration execution, inference, reconstruction, validation, and runtime UI | UpstreamDrift | Consume only a protected, qualified evidence release. |
| Public pedagogy, sanitized visualization, compatibility reporting, and immutable evidence projection | AffineDrift | Own the presentation and projection verifier, not the computational result. |

Every public projection must conform to
`affinedrift/mocap-publication-projection/v1`, defined by
`schemas/markerless_mocap_publication_projection_v1.schema.json` and enforced by
`scripts/verify_markerless_mocap_projection.py`. The verifier requires:

- an exact 40-character source commit and matching revision-pinned source links;
- SHA-256 and byte-size locks for every projected artifact;
- approved security and privacy reviews, sanitized-artifact-only retention, and
  public-release consent for live-lab evidence;
- explicit `observed`, `derived`, `model_scenario`, or `unavailable` claim classes;
- qualification by the declared protected Tools or UpstreamDrift authority;
- an MIT AffineDrift publication and an allowlisted SPDX license for every
  embedded or linked distribution component.

The public projection must contain no raw video, PII, secrets, or AGPL-licensed components.
AffineDrift does not import, vendor, bundle, redistribute, or runtime-link AGPL
implementations, model weights, or assets. A bibliographic citation to external
research is not a software or artifact dependency.

Synthetic evidence may be published only as a qualified `model_scenario`; it must
not be relabeled as observed or derived human evidence. Live-lab evidence requires
approved public-release consent and may contain only sanitized derived or aggregate
artifacts. Unknown, unsupported, unapproved, or missing authority remains
`unavailable` and must not cite a result artifact.

## Contract Invariants

1. AffineDrift remains standalone and performs no cross-repository Python import.
2. Moving links such as `/blob/main/` and `/tree/main/` fail verification.
3. Artifact paths are normalized, relative, and free of video, key, environment,
   and certificate file types.
4. Claim-to-artifact references resolve within the same verified manifest.
5. A changed, missing, or differently sized artifact fails closed.
6. Schema additions require a new schema identifier; version 1 semantics do not
   change in place.

## Consequences

Readers can trace a public result to one immutable computational release without
granting AffineDrift runtime or scientific authority. Public C3D compatibility
examples are permitted only as `sanitized_c3d` artifacts after the same approvals;
raw capture remains outside this repository.

The verifier proves manifest conformance, revision identity, and artifact integrity.
It does not prove that a human review was performed correctly, discover undeclared
PII inside an already approved opaque binary, establish camera accuracy, or qualify
a physical lab. Those gates remain external evidence and human-review obligations.

## Drift Detection

`tests/test_markerless_mocap_projection_contract.py` exercises accepted projections
and rejects mutable revisions, raw/private/secret material, incompatible licenses,
unqualified claims, invalid synthetic or live-lab classification, and artifact drift.
The focused gate is:

```text
python3 -m pytest tests/test_markerless_mocap_projection_contract.py -q
```
