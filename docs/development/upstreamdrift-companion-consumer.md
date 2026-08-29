# UpstreamDrift Companion Consumer

The companion consumer imports software facts from one reviewed UpstreamDrift
manifest without importing UpstreamDrift runtime code or inspecting a mutable
branch. It is a supply-chain boundary, not a scientific-validation shortcut.

## Authority and ownership

- UpstreamDrift owns its manifest schema, generator, feature inventory, and
  protected source revision.
- AffineDrift owns the consumer, lock schema, immutable vendored snapshot, and
  publication state.
- A valid snapshot establishes only the provenance of provider-owned software
  facts. It does not establish model validity, human biomechanics, coaching
  advice, clinical safety, or engineering approval.

The provider identity is fixed to `D-sorganization/UpstreamDrift`. Every pin
must contain a nonzero 40-character commit, exact SHA-256 digests for the
manifest and schema, the approved provider artifact path, the provider
generator command, and the immutable raw URL for the committed schema.

## Immutable layout

The default consumer root is `data/upstreamdrift_companion`:

```text
data/upstreamdrift_companion/
├── lock.json
└── snapshots/
    └── <40-hex-provider-commit>/
        ├── provenance.qmd
        ├── upstreamdrift-companion-v1.schema.json
        └── upstreamdrift-companion.v1.json
```

`lock.json` is the sole active pointer. Snapshot directories are immutable: a
second byte sequence for the same provider commit is a hard conflict. The
consumer validates all candidate bytes before staging, moves the complete
snapshot into place, and replaces the lock last. A staging or lock-swap failure
leaves every previously active byte unchanged.

## Acquisition modes

`protected-local-export` is the current publication mode. UpstreamDrift creates
the ignored release artifact from an exact protected merge; a reviewer transfers
those bytes to AffineDrift and records the exact generator command. The lock
sets `manifest_url` to `null` because the artifact is not hosted at a raw GitHub
path.

`immutable-url` is reserved for a future governed release asset. Its URL must
resolve to the approved path at the pinned commit. The downloader uses bounded
temporary storage and rejects mutable branches, redirects outside the approved
host/path, traversal, query strings, fragments, credentials, ports, and
oversized responses.

## Commands

Install a reviewed local export:

```powershell
python scripts/manage_upstreamdrift_companion.py install-local `
  --commit <PROTECTED_MERGE_SHA> `
  --manifest-sha256 <MANIFEST_SHA256> `
  --schema-sha256 <SCHEMA_SHA256> `
  --schema-url <IMMUTABLE_RAW_SCHEMA_URL> `
  --generator-command "python -m scripts.companion_catalog --output dist/companion/upstreamdrift-companion.v1.json" `
  --manifest <PATH_TO_EXPORTED_MANIFEST> `
  --schema <PATH_TO_PROVIDER_SCHEMA>
```

Verify the active lock and all referenced bytes:

```powershell
python scripts/manage_upstreamdrift_companion.py verify
```

Compare a reviewed local candidate without changing the active pin:

```powershell
python scripts/manage_upstreamdrift_companion.py check-local `
  --commit <CANDIDATE_PROTECTED_SHA> `
  --manifest-sha256 <CANDIDATE_MANIFEST_SHA256> `
  --schema-sha256 <CANDIDATE_SCHEMA_SHA256> `
  --schema-url <CANDIDATE_IMMUTABLE_SCHEMA_URL> `
  --generator-command "python -m scripts.companion_catalog --output dist/companion/upstreamdrift-companion.v1.json" `
  --manifest <PATH_TO_CANDIDATE_MANIFEST> `
  --schema <PATH_TO_CANDIDATE_SCHEMA>
```

The check command emits deterministic JSON containing `wrote_files: false`.
It never advances the lock. Installation is a separate, explicit review action.

## Python API

`src.companion.manifest_consumer.CompanionConsumer` is the typed boundary:

- `install_from_local_export(...)` reads bounded local provider artifacts and
  atomically activates a validated snapshot.
- `install_from_urls(...)` downloads a future immutable release asset through a
  small `Fetcher` adapter and revalidates its final redirect URL.
- `verify_active()` validates the lock, path containment, byte counts, digests,
  provider schema, embedded repository/commit, and generated provenance view.
- `check_local_export_update(...)` and `check_update(...)` compare candidates
  without writing.

All contract failures raise `CompanionImportError`; callers must treat the
operation as failed and must not publish candidate facts.
