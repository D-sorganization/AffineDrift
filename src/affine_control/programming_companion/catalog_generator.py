"""Deterministic generator for AffineDrift's Programming Companion catalog (ISSUE-4023).

Transforms the pinned UpstreamDrift companion manifest into structured, accessible,
single-H1 Quarto markdown pages adhering to DbC, LoD, and DRY design principles.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CatalogGeneratorError(Exception):
    """Raised when catalog generation fails due to missing or invalid inputs."""


@dataclass(frozen=True)
class GeneratedFile:
    """One deterministically generated file with its relative path and content."""

    relative_path: Path
    content: str


@dataclass(frozen=True)
class DriftItem:
    """One observed difference between generated memory and disk state."""

    path: Path
    reason: str


class CatalogGenerator:
    """Pure deterministic transform from companion manifest JSON to Quarto pages."""

    REQUIRED_ROOT_KEYS = frozenset(
        {
            "manifest_id",
            "schema_version",
            "source",
            "engines",
            "programs",
            "features",
            "workflows",
            "compatibility",
            "summary",
        }
    )

    def __init__(self, manifest: Mapping[str, Any]) -> None:
        """Initialize the catalog generator with a validated manifest mapping."""
        if not self.REQUIRED_ROOT_KEYS.issubset(manifest.keys()):
            missing = sorted(self.REQUIRED_ROOT_KEYS - set(manifest.keys()))
            raise CatalogGeneratorError(
                f"invalid manifest structure; missing required keys: {missing}"
            )
        self._manifest = manifest
        self._source: Mapping[str, Any] = manifest.get("source", {})
        self._engines: list[Mapping[str, Any]] = list(manifest.get("engines", []))
        self._programs: list[Mapping[str, Any]] = list(manifest.get("programs", []))
        self._features: list[Mapping[str, Any]] = list(manifest.get("features", []))
        self._workflows: list[Mapping[str, Any]] = list(manifest.get("workflows", []))
        self._compatibility: Mapping[str, Any] = manifest.get("compatibility", {})
        self._summary: Mapping[str, Any] = manifest.get("summary", {})

    def generate_index(self) -> str:
        """Build the main programming companion hub index."""
        commit = str(self._source.get("commit", "unknown"))
        short_commit = commit[:8]
        prog_count = len(self._programs)
        feat_count = len(self._features)
        wf_count = len(self._workflows)
        engine_count = len(self._engines)

        desc = (
            "Authoritative software facts, engines, programs, "
            "features, and workflows from UpstreamDrift"
        )
        tree_url = f"https://github.com/D-sorganization/UpstreamDrift/tree/{commit}"
        return f"""---
title: "Programming Companion Catalog"
description: "{desc}"
page-layout: full
---

```{{=html}}
<section class="resources-section">
  <div class="programming-hub" data-layout-contract="standard-page-layout--content-first-compact">
    <div class="main-content-area">
      <div class="resource-grid">
        <header class="site-card site-card--feature site-card--brand u-mb-4">
          <p class="u-text-muted u-mb-1"><strong>Governed Software Authority</strong></p>
          <h1 class="u-mb-2">Programming Companion Catalog</h1>
          <p class="page-lede">
            Deterministic reference for UpstreamDrift computational engines, programs, feature
            interfaces, and executable workflows pinned to exact revision
            <code>{short_commit}</code>.
          </p>
        </header>

        <div class="site-card site-card--callout u-mb-4">
          <h2 class="u-mb-1">Authority Boundary</h2>
          <p>
            <strong>This establishes</strong> verified software facts, support tiers, and execution
            parameters exported from UpstreamDrift exact commit
            <a href="{tree_url}" target="_blank" rel="noopener"><code>{commit}</code></a>.
          </p>
          <p>
            <strong>This does not establish</strong> independent scientific consensus, coaching
            recommendations, anatomical claims, or measured participant-level human validation.
          </p>
        </div>
      </div>

      <div class="resource-grid resource-grid--wide u-mb-5">
        <article class="resource-card">
          <h3><a href="engines.html">Engines and Runtime Support ({engine_count})</a></h3>
          <p class="resource-description">
            Physics solvers, dependency tiers (MuJoCo, Drake, Pinocchio, OpenSim, MyoSuite),
            and Python 3.11/3.12 compatibility matrices.
          </p>
          <a href="engines.html" class="resource-link">View Engine Matrix →</a>
        </article>

        <article class="resource-card">
          <h3><a href="programs.html">Programs and Models ({prog_count})</a></h3>
          <p class="resource-description">
            The full 70-record program and local model directory with interfaceKind, maturity,
            and surface parity classifications.
          </p>
          <a href="programs.html" class="resource-link">Browse Programs →</a>
        </article>

        <article class="resource-card">
          <h3><a href="features.html">Feature Parity Matrix ({feat_count})</a></h3>
          <p class="resource-description">
            Cross-surface parity tracking across CLI, GUI, API, and Web interfaces with explicit
            gap accounting.
          </p>
          <a href="features.html" class="resource-link">Inspect Features →</a>
        </article>

        <article class="resource-card">
          <h3><a href="workflows.html">Governed Workflows ({wf_count})</a></h3>
          <p class="resource-description">
            Deterministic execution tasks, verification methods, exit codes, and artifact
            validation contracts.
          </p>
          <a href="workflows.html" class="resource-link">Explore Workflows →</a>
        </article>

        <article class="resource-card">
          <h3><a href="provenance.html">Provenance and Digests</a></h3>
          <p class="resource-description">
            Cryptographic SHA-256 signatures, generator metadata, and input file hashes for
            uncompromising supply-chain auditability.
          </p>
          <a href="provenance.html" class="resource-link">Review Provenance →</a>
        </article>
      </div>
    </div>
  </div>
</section>
```
"""

    def generate_engines(self) -> str:
        """Build the engines and runtime support page."""
        rows: list[str] = []
        for engine in self._engines:
            eid = engine.get("id", "")
            title = engine.get("title", eid)
            tier = engine.get("support_tier", "unspecified").capitalize()
            status = engine.get("maturity", "unspecified").capitalize()
            notes = engine.get("notes", "None")
            rows.append(f"| `{eid}` | **{title}** | {tier} | {status} | {notes} |")
        engine_table = "\n".join(rows) if rows else "| None | - | - | - | - |"

        req_py = self._compatibility.get("requires_python", ">=3.11")
        minors = ", ".join(self._compatibility.get("supported_python_minors", ["3.11", "3.12"]))
        verify_cmd = (
            "python -m scripts.companion_workflows execute "
            "--workflow-id installation-verification"
        )

        return f"""---
title: "Engines and Runtime Support"
description: "Physics solvers, support tiers, and runtime environments supported by UpstreamDrift"
---

## Authority Boundary

> [!NOTE]
> **This establishes** software support tiers and runtime execution boundaries.
> **This does not establish** that a physics engine has been validated on human data.

## Runtime Compatibility Matrix

| Runtime Dimension | Specification | Verification Command |
| :--- | :--- | :--- |
| **Python Requirement** | `{req_py}` | `python -V` |
| **Supported Minors** | {minors} | `python scripts/ci/verify_installation.py` |
| **Verification Entrypoint** | `scripts/ci/verify_installation.py` | `{verify_cmd}` |

## Physics Engines & Support Tiers

| Engine ID | Engine Name | Support Tier | Maturity | Operational Notes |
| :--- | :--- | :--- | :--- | :--- |
{engine_table}

### Support Tier Definitions

- **Supported (`F0`):** Core stack (e.g. MuJoCo). Fully tested across operating systems.
- **Extended (`F1`):** Extended stack (e.g. Drake, Pinocchio). Tested in simulation suites.
- **Experimental (`F2`):** Research-grade experimental interfaces (e.g. OpenSim, MyoSuite).
"""

    def generate_programs(self) -> str:
        """Build the programs and model directory page."""
        rows: list[str] = []
        for prog in sorted(self._programs, key=lambda p: str(p.get("id", ""))):
            pid = prog.get("id", "")
            title = prog.get("title", pid)
            kind = prog.get("kind", "program")
            engine = prog.get("engine", "core")
            maturity = prog.get("maturity", "unspecified")
            surfaces = ", ".join(prog.get("surfaces", [])) or "cli"
            rows.append(
                f"| `{pid}` | {title} | `{kind}` | `{engine}` | `{maturity}` | {surfaces} |"
            )
        prog_table = "\n".join(rows) if rows else "| None | - | - | - | - | - |"

        return f"""---
title: "Programs and Models Directory"
description: "Authoritative inventory of 70 UpstreamDrift simulation programs, solvers, and models"
---

## Authority Boundary

> [!NOTE]
> **This establishes** the inventory of registered UpstreamDrift programs, models, and interfaces.
> **This does not establish** experimental validation or clinical applicability.

## Program Registry ({len(self._programs)} Records)

| Program ID | Title | Kind | Engine | Maturity | Surfaces |
| :--- | :--- | :--- | :--- | :--- | :--- |
{prog_table}
"""

    def generate_features(self) -> str:
        """Build the feature parity matrix page."""
        rows: list[str] = []
        for feat in sorted(self._features, key=lambda f: str(f.get("id", ""))):
            fid = feat.get("id", "")
            title = feat.get("title", fid)
            parity = feat.get("parity", {})
            cli_state = "✓" if parity.get("cli") else "—"
            gui_state = "✓" if parity.get("gui") else "—"
            api_state = "✓" if parity.get("api") else "—"
            web_state = "✓" if parity.get("web") else "—"
            qual = feat.get("scientific_qualification", "unqualified")
            rows.append(
                f"| `{fid}` | {title} | {cli_state} | {gui_state} | "
                f"{api_state} | {web_state} | `{qual}` |"
            )
        feat_table = "\n".join(rows) if rows else "| None | - | - | - | - | - | - |"

        desc = (
            "Cross-surface parity tracking for CLI, GUI, API, "
            "and Web interfaces across UpstreamDrift features"
        )
        return f"""---
title: "Feature Parity Matrix"
description: "{desc}"
---

## Authority Boundary

> [!NOTE]
> **This establishes** interface availability across execution surfaces (CLI, GUI, API, Web).
> **This does not establish** scientific validation or equivalence between solver implementations.

## Feature Surface Parity ({len(self._features)} Records)

| Feature ID | Title | CLI | GUI | API | Web | Scientific Qualification |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
{feat_table}
"""

    def generate_workflows(self) -> str:
        """Build the governed workflows page."""
        rows: list[str] = []
        for wf in sorted(self._workflows, key=lambda w: str(w.get("id", ""))):
            wid = wf.get("id", "")
            title = wf.get("title", wid)
            kind = wf.get("kind", "workflow")
            tier = wf.get("support_tier", "supported")
            avail = wf.get("availability", {}).get("state", "available")
            method = wf.get("verification_method", "exit-code")
            rows.append(f"| `{wid}` | {title} | `{kind}` | `{tier}` | `{avail}` | {method} |")
        wf_table = "\n".join(rows) if rows else "| None | - | - | - | - | - |"

        desc = (
            "Authoritative catalog of 15 executable workflows "
            "and deterministic verification tasks"
        )
        return f"""---
title: "Governed Workflows and Verification Tasks"
description: "{desc}"
---

## Authority Boundary

> [!NOTE]
> **This establishes** executable commands and verification contracts governed by UpstreamDrift CI.
> **This does not establish** execution safety outside the sandboxed repository environment.

## Workflow Registry ({len(self._workflows)} Records)

| Workflow ID | Title | Kind | Support Tier | Availability | Verification Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
{wf_table}
"""

    def generate_provenance(self) -> str:
        """Build the publication and provenance ledger page."""
        commit = str(self._source.get("commit", "unknown"))
        ts = str(self._source.get("commit_timestamp", "unknown"))
        pkg_ver = str(self._source.get("package_version", "unknown"))
        gen_info = self._source.get("generator", {})
        gen_path = str(gen_info.get("path", "scripts/companion_catalog.py"))
        gen_ver = str(gen_info.get("version", "1.0.0"))

        input_rows: list[str] = []
        for inp in self._source.get("inputs", []):
            path = inp.get("path", "")
            sha = inp.get("sha256", "")
            input_rows.append(f"| `{path}` | `{sha}` |")
        inputs_table = "\n".join(input_rows) if input_rows else "| None | - |"

        repo_url = "https://github.com/D-sorganization/UpstreamDrift"
        schema_url = "https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"

        return f"""---
title: "Companion Provenance and Cryptographic Digests"
description: "Exact-commit provenance, generator versions, and cryptographic input digests"
---

## Authority Boundary

> [!NOTE]
> **This establishes** the immutable supply-chain lineage and SHA-256 digest ledger.
> **This does not establish** scientific validation of the underlying algorithms.

## Provenance Metadata

| Metadata Field | Recorded Value |
| :--- | :--- |
| **Provider Repository** | [`{repo_url}`]({repo_url}) |
| **Source Commit SHA** | [`{commit}`]({repo_url}/tree/{commit}) |
| **Commit Timestamp** | `{ts}` |
| **Provider Package Version** | `{pkg_ver}` |
| **Catalog Generator** | `{gen_path}` (v{gen_ver}) |
| **Schema Identity** | [`{schema_url}`]({schema_url}) |

## Source Input Digests

| Input Relative Path | Cryptographic SHA-256 Digest |
| :--- | :--- |
{inputs_table}
"""

    def generate_all(self, output_dir: Path) -> list[GeneratedFile]:
        """Generate all QMD files and write them to output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        files = [
            GeneratedFile(Path("index.qmd"), self.generate_index()),
            GeneratedFile(Path("engines.qmd"), self.generate_engines()),
            GeneratedFile(Path("programs.qmd"), self.generate_programs()),
            GeneratedFile(Path("features.qmd"), self.generate_features()),
            GeneratedFile(Path("workflows.qmd"), self.generate_workflows()),
            GeneratedFile(Path("provenance.qmd"), self.generate_provenance()),
        ]
        for f in files:
            target = output_dir / f.relative_path
            target.write_text(f.content, encoding="utf-8")
        return files

    def check(self, output_dir: Path) -> tuple[bool, list[DriftItem]]:
        """Check if output_dir matches the deterministic generator output."""
        expected_files = [
            GeneratedFile(Path("index.qmd"), self.generate_index()),
            GeneratedFile(Path("engines.qmd"), self.generate_engines()),
            GeneratedFile(Path("programs.qmd"), self.generate_programs()),
            GeneratedFile(Path("features.qmd"), self.generate_features()),
            GeneratedFile(Path("workflows.qmd"), self.generate_workflows()),
            GeneratedFile(Path("provenance.qmd"), self.generate_provenance()),
        ]
        drifts: list[DriftItem] = []
        for ef in expected_files:
            target = output_dir / ef.relative_path
            if not target.exists():
                drifts.append(DriftItem(ef.relative_path, "missing_file"))
                continue
            actual = target.read_text(encoding="utf-8")
            if actual != ef.content:
                drifts.append(DriftItem(ef.relative_path, "content_mismatch"))
        return len(drifts) == 0, drifts
