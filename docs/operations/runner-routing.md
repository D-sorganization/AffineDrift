# Runner routing

Where this repository's GitHub Actions jobs run, how to switch, and why the
choice is constrained.

## The rule

| Repository visibility | Where jobs run | Can it be changed? |
|---|---|---|
| **public** | GitHub-hosted (`ubuntu-latest`) by default | Yes — set `RUNNER_TARGET` |
| **private / internal** | Self-hosted `d-sorg-fleet`, always | No |

Two different reasons, pointing the same way:

**Cost.** GitHub-hosted standard runners are free and unmetered on public
repositories. On private and internal repositories every minute bills against
the org quota. So the fleet saves money on private repos and saves nothing on
public ones.

**Safety.** GitHub advises against pairing self-hosted runners with public
repositories: a fork pull request can execute attacker-controlled code on a
persistent machine you own, and the machine survives the job. Hosted runners
are ephemeral. So on a public repo the fleet is not merely pointless, it is a
liability.

## Switching a public repo between hosted and local

Set the `RUNNER_TARGET` repository variable:

```bash
gh variable set RUNNER_TARGET --repo D-sorganization/AffineDrift --body local
```

```bash
gh variable set RUNNER_TARGET --repo D-sorganization/AffineDrift --body hosted
```

Any value other than `local` means hosted, so deleting the variable also
returns to hosted. The change takes effect on the next workflow run; nothing
needs to be committed and no workflow file changes.

Jobs read it through one of two mechanisms:

- Most jobs inline the toggle:
  `runs-on: ${{ vars.RUNNER_TARGET == 'local' && 'd-sorg-fleet' || 'ubuntu-latest' }}`
- The `ci-standard.yml` and `deploy-website.yml` job graphs route through a
  `pick-runner` job that resolves the label once and publishes it as an output,
  so the whole graph stays on one runner type.

`local-only-runner-guard.yml` is deliberately excluded and pinned to
`ubuntu-latest`. It is the canary that has to stay operable when the fleet
itself is down, which is exactly when you need to be told about routing.

## Why the variable cannot be used to move a private repo to hosted runners

`RUNNER_TARGET` is a preference, not a security control — anyone who can set a
repository variable could change routing without touching a workflow file or
passing review. So the billing rule is enforced in two places that do not
depend on it:

1. **`pick-runner` checks visibility at runtime.** On a non-public repository
   it selects `d-sorg-fleet` and ignores `RUNNER_TARGET` entirely.

2. **`local-only-runner-guard.yml` fails the build at merge time.** On a
   non-public repository, any job that *can* reach a hosted runner is a
   violation — including a toggle currently pointing at the fleet, because
   "currently" is not a guarantee. Its job is named `Reject hosted runner
   routing` and is the required status check for the
   `block-hosted-runner-merge` ruleset.

The practical consequence: if this repository is ever made private again, the
guard will fail every workflow carrying the toggle until they are pinned back
to `d-sorg-fleet`. That is intended. It fails closed.

The guard treats a `pick-runner` job that reads
`github.event.repository.visibility` as trusted, since such a job is
structurally incapable of emitting a hosted label on a repo that would be
billed for it.

## Known gap: system libraries differ between the two

The fleet machines are desktops and carry libraries the hosted images do not.
The Qt tests were the first casualty of the migration — `pip install PyQt6`
provides the Python bindings but not the shared objects Qt links against, so
on hosted runners the import failed with `libEGL.so.1: cannot open shared
object file` and pytest aborted during collection.

`ci-standard.yml` now installs the EGL/GL, D-Bus and xcb libraries explicitly
and sets `QT_QPA_PLATFORM=offscreen`. If you switch back to `local` these steps
are redundant but harmless. If you add a dependency that needs system packages,
install them in the workflow rather than relying on what a fleet machine
happens to have — otherwise the job works locally and breaks the next time
routing flips.

## Related

- Fork pull requests from outside contributors require approval before any
  workflow runs (`all_external_contributors`). This matters most while any job
  can still reach the fleet.
- `scripts/check_local_only_workflows.py` is a second, unwired implementation
  of the same ban. It is visibility-aware for consistency, but
  `local-only-runner-guard.yml` is the enforcement that actually runs.
