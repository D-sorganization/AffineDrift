"""Deterministic generator for AffineDrift's Programming Companion catalog (ISSUE-4023).

Transforms the pinned UpstreamDrift companion manifest into structured, accessible,
single-H1 Quarto markdown pages adhering to DbC, LoD, and DRY design principles.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _record_id(record: Mapping[str, Any]) -> str:
    """Sort key: the record's string identifier."""
    return str(record.get("id", ""))


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

    # AffineDrift #4123 / UpstreamDrift #9416: until the provider publishes a real
    # companion artifact, every generated page must say where its data comes from.
    FIXTURE_MANIFEST_PATH = "tests/fixtures/companion/manifest_v1_0_0_authoritative.json"
    PREVIEW_TRACKING = (
        ("AffineDrift #4123", "https://github.com/D-sorganization/AffineDrift/issues/4123"),
        ("UpstreamDrift #9416", "https://github.com/D-sorganization/UpstreamDrift/issues/9416"),
    )

    @classmethod
    def preview_notice_markdown(cls) -> str:
        """Return the Quarto callout shown at the top of every Markdown catalog page."""
        tracking = " / ".join(f"[{label}]({url})" for label, url in cls.PREVIEW_TRACKING)
        return (
            '::: {.callout-warning title="Preview"}\n'
            "PREVIEW \u2014 this catalog is generated from a fixture manifest "
            f"(`{cls.FIXTURE_MANIFEST_PATH}`), not yet from a provider-published UpstreamDrift "
            f"artifact. Tracking: {tracking}.\n"
            ":::\n"
        )

    @classmethod
    def preview_notice_html(cls) -> str:
        """Return the same notice as a site card for the raw-HTML hub page."""
        tracking = " / ".join(
            f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
            for label, url in cls.PREVIEW_TRACKING
        )
        return (
            '        <div class="site-card site-card--callout u-mb-4" role="note">\n'
            '          <h2 class="u-mb-1">Preview</h2>\n'
            "          <p>\n"
            "            <strong>PREVIEW</strong> \u2014 this catalog is generated from a fixture "
            "manifest\n"
            f"            (<code>{cls.FIXTURE_MANIFEST_PATH}</code>), not yet from a\n"
            f"            provider-published UpstreamDrift artifact. Tracking: {tracking}.\n"
            "          </p>\n"
            "        </div>\n"
        )

    def __init__(
        self,
        manifest: Mapping[str, Any],
        *,
        preview: bool = True,
        provenance: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize the catalog generator with a validated manifest mapping.

        ``preview=True`` (the fixture path) stamps every page with the PREVIEW
        notice. ``preview=False`` requires ``provenance`` describing the
        installed provider artifact (``artifact_name``, ``manifest_sha256``,
        ``fetched_on``, ``attestation``) and stamps a provider-pin notice
        instead (#4123 Phase 1).
        """
        if not self.REQUIRED_ROOT_KEYS.issubset(manifest.keys()):
            missing = sorted(self.REQUIRED_ROOT_KEYS - set(manifest.keys()))
            raise CatalogGeneratorError(
                f"invalid manifest structure; missing required keys: {missing}"
            )
        if not preview:
            required = {"artifact_name", "manifest_sha256", "fetched_on", "attestation"}
            if provenance is None or not required.issubset(provenance.keys()):
                raise CatalogGeneratorError(
                    "provider mode requires provenance with "
                    "artifact_name, manifest_sha256, fetched_on, attestation"
                )
        self._preview = preview
        self._provenance: Mapping[str, Any] = provenance or {}
        self._manifest = manifest
        self._source: Mapping[str, Any] = manifest.get("source", {})
        self._engines: list[Mapping[str, Any]] = list(manifest.get("engines", []))
        self._programs: list[Mapping[str, Any]] = list(manifest.get("programs", []))
        self._features: list[Mapping[str, Any]] = list(manifest.get("features", []))
        self._workflows: list[Mapping[str, Any]] = list(manifest.get("workflows", []))
        self._compatibility: Mapping[str, Any] = manifest.get("compatibility", {})
        self._summary: Mapping[str, Any] = manifest.get("summary", {})

    def _publication_sentence(self) -> str:
        """State the provider's own publication verdict without upgrading it."""
        publication: Mapping[str, Any] = self._manifest.get("publication", {})
        state = str(publication.get("state", "unknown"))
        blockers = [str(item) for item in publication.get("blockers", [])]
        if blockers:
            return f"The provider marks this catalog **{state}**: " + " ".join(blockers)
        return f"The provider marks this catalog **{state}**."

    def _notice_markdown(self) -> str:
        """Return the PREVIEW notice or the provider-pin notice for Markdown pages."""
        if self._preview:
            return self.preview_notice_markdown()
        prov = self._provenance
        return (
            '::: {.callout-note title="Provider Pin"}\n'
            f"Generated from the provider-published UpstreamDrift artifact "
            f"`{prov['artifact_name']}` (manifest SHA-256 `{prov['manifest_sha256']}`; "
            f"attestation: {prov['attestation']}; installed {prov['fetched_on']}). "
            f"{self._publication_sentence()} "
            "See the [freshness dashboard](freshness.html).\n"
            ":::\n"
        )

    def _notice_html(self) -> str:
        """Return the PREVIEW notice or the provider-pin notice for the HTML hub."""
        if self._preview:
            return self.preview_notice_html()
        prov = self._provenance
        sentence = self._publication_sentence().replace("**", "")
        return (
            '        <div class="site-card site-card--callout u-mb-4" role="note">\n'
            '          <h2 class="u-mb-1">Provider Pin</h2>\n'
            "          <p>\n"
            "            Generated from the provider-published UpstreamDrift artifact\n"
            f"            <code>{prov['artifact_name']}</code> (manifest SHA-256\n"
            f"            <code>{prov['manifest_sha256']}</code>;\n"
            f"            attestation: {prov['attestation']};\n"
            f"            installed {prov['fetched_on']}). {sentence}\n"
            '            See the <a href="freshness.html">freshness dashboard</a>.\n'
            "          </p>\n"
            "        </div>\n"
        )

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

{self._notice_html()}
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
            Parity state per feature across the desktop (PyQt), API, and web surfaces with
            explicit gap accounting.
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

        <article class="resource-card">
          <h3><a href="freshness.html">Software Freshness Dashboard</a></h3>
          <p class="resource-description">
            Which UpstreamDrift revision this site represents, every pinned SHA across the
            site, review dates, and the provider's own publication state.
          </p>
          <a href="freshness.html" class="resource-link">Check Freshness →</a>
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

{self._notice_markdown()}
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

{self._notice_markdown()}
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
        rows = [self._feature_row(feat) for feat in sorted(self._features, key=_record_id)]
        feat_table = "\n".join(rows) if rows else "| None | - | - | - | - | - |"

        desc = (
            "Parity state of each UpstreamDrift feature across its "
            "desktop (PyQt), API, and web surfaces"
        )
        return f"""---
title: "Feature Parity Matrix"
description: "{desc}"
---

{self._notice_markdown()}
## Authority Boundary

> [!NOTE]
> **This establishes** which execution surfaces (desktop PyQt, API, web) each feature is
> registered on and the provider's parity state for it.
> **This does not establish** scientific validation or equivalence between solver implementations.

## Feature Surface Parity ({len(self._features)} Records)

Parity state is the provider's own classification: `parity` (all registered surfaces agree),
`gap` (a surface is missing or partial; the tracking issue is linked), or `exempt` (parity is
not expected for this feature). Scientific qualification is reported exactly as the provider
declares it; every record here is `unqualified`, meaning catalog inclusion is a software fact,
not validation.

| Feature ID | Title | Surfaces | Parity State | Parity Issue | Scientific Qualification |
| :--- | :--- | :--- | :---: | :---: | :--- |
{feat_table}
"""

    @staticmethod
    def _feature_row(feat: Mapping[str, Any]) -> str:
        """Render one feature as a table row from its structured manifest fields."""
        fid = str(feat.get("id", ""))
        title = str(feat.get("title", fid))
        surfaces = sorted({str(s.get("surface", "")) for s in feat.get("surfaces", [])} - {""})
        surface_text = ", ".join(f"`{surface}`" for surface in surfaces) or "\u2014"
        parity = feat.get("parity", {})
        parity_state = str(parity.get("state", "unspecified"))
        issue = parity.get("issue")
        issue_text = (
            f"[#{issue}](https://github.com/D-sorganization/UpstreamDrift/issues/{issue})"
            if isinstance(issue, int)
            else "\u2014"
        )
        qualification = feat.get("scientific_qualification", {})
        if not isinstance(qualification, Mapping):
            qualification = {"state": str(qualification)}
        qual_state = str(qualification.get("state", "unqualified"))
        qual_scope = str(qualification.get("scope", "")).strip()
        qual_text = f"`{qual_state}`" + (f" \u2014 {qual_scope}" if qual_scope else "")
        return (
            f"| `{fid}` | {title} | {surface_text} | `{parity_state}` | "
            f"{issue_text} | {qual_text} |"
        )

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

{self._notice_markdown()}
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

{self._notice_markdown()}
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
            target.write_text(f.content, encoding="utf-8", newline="\n")
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
