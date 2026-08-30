# Immutable Programming Companion Consumer

## Purpose and Authority Boundary

`src.affine_control.programming_companion` acquires one UpstreamDrift companion
manifest without importing UpstreamDrift runtime code or reading a mutable
branch. UpstreamDrift remains the software-fact authority. AffineDrift stores
only exact downloaded bytes, their strict provider schema, and a deterministic
active lock.

This foundation does **not** authorize a production catalog. No active lock or
snapshot is checked into AffineDrift while UpstreamDrift issue #9174 and its
publication children remain open. Manufactured fixtures prove consumer behavior;
they are not provider evidence.

The pinned provider schema is
`schemas/upstreamdrift-companion-v1.schema.json`. Its adjacent provenance record
binds the source repository, protected source commit, source path, schema ID,
and SHA-256.

## Storage Contract

An initialized store contains:

```text
<store>/
|-- active-lock.json
`-- snapshots/
    |-- <commit>-<manifest-digest-prefix>/
    |   |-- manifest.json
    |   `-- schema.json
    `-- <prior immutable snapshots>/
```

The active lock is the only authority pointer. Snapshot directories are
content-addressed and never edited. A normal `install` refuses a different
active pin. `replace_pin` is the sole replacement path; it requires the exact
SHA-256 of the current canonical lock bytes and rechecks that precondition after
the candidate download. Prior snapshots remain available for review.

## Acquisition Contract

The consumer requires all of the following before a write:

- `https` on the exact `raw.githubusercontent.com` allowlisted host;
- the exact `D-sorganization/UpstreamDrift` repository path;
- an exact lowercase 40-hex commit in both URLs and the manifest source record;
- the two approved manifest and schema paths, with no credentials, port,
  query, fragment, percent encoding, backslash, mutable branch, or redirect;
- exact manifest and schema SHA-256 values and bounded streaming payloads;
- duplicate-key-free UTF-8 JSON, a valid Draft 2020-12 schema with the pinned
  schema ID, and a manifest that passes that schema;
- the exact provider repository plus safe repository-relative paths; and
- a canonical, internally consistent lock and regular, non-symlink snapshot
  files whose byte counts and digests still match on every provenance read.

Any failed acquisition leaves the active lock and active snapshot bytes
unchanged. A failed first install also removes any candidate snapshot that it
created. Network redirects are rejected rather than followed.

## API Use

Construct configuration explicitly; the package does not contain a mutable
default URL or production digest:

```python
from pathlib import Path

from src.affine_control.programming_companion import (
    CompanionConsumer,
    ConsumerPolicy,
    ImportRequest,
    RequestsTransport,
    SnapshotStore,
)

policy = ConsumerPolicy.upstreamdrift()
consumer = CompanionConsumer(
    policy,
    RequestsTransport(),
    SnapshotStore(Path("data/programming_companion")),
)
request = ImportRequest(
    source_commit="<exact 40-hex protected commit>",
    manifest_url="<exact-commit approved raw manifest URL>",
    manifest_sha256="<reviewed manifest SHA-256>",
    schema_url="<exact-commit approved raw schema URL>",
    schema_sha256="<reviewed schema SHA-256>",
)
```

`inspect(request)` validates without writing. `check_update(request)` returns a
deterministic comparison and never changes the pin. `install(request)` creates
the initial pin or verifies an identical pin. `provenance()` verifies and
returns the active authority. To make an explicitly reviewed update, hash the
current `active-lock.json` bytes and pass that digest to
`replace_pin(request, expected_active_lock_sha256)`.

## Verification

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest tests/test_programming_companion_consumer.py tests/test_programming_companion_transport.py -q
python -m ruff check src/affine_control/programming_companion tests/test_programming_companion_*.py
python -m black --check --line-length 100 src/affine_control/programming_companion tests/test_programming_companion_*.py
python -m mypy src/affine_control/programming_companion
```
