"""Deterministic generic Quarto research preview, never a release attestation."""

import re
from html import escape
from typing import Any

from .admission import admit_package
from .models import HistoricalResearchPackage, HistoricalResearchRecord


def _text(value: str) -> str:
    """Escape untrusted labels as visible text, not Markdown/QMD instructions."""
    return re.sub(r"([\\`*_{}\[\]#|!])", r"\\\1", escape(value)).replace("\n", " ")


def _package_intro(package: HistoricalResearchPackage) -> list[str]:
    return [
        "---",
        "title: Historical-Player Local Research",
        "---",
        "",
        "::: {.callout-warning}",
        "## Local Research Only",
        "Publication is not authorized. No original footage or person media is included.",
        "Scientific acceptance remains rejected; computation and finite targets are separate.",
        "::: ",
        "",
        f"Provider commit: `{package.source_commit}`",
        f"Package SHA-256: `{package.manifest_sha256}`",
        "",
    ]


def _record_intro(record: HistoricalResearchRecord, value: dict[str, Any]) -> list[str]:
    identity = record.identity
    return [
        f"## {_text(identity.player_name)}",
        "",
        f"Fit: `{identity.fit_id}`; Swing: `{identity.swing_id}`",
        f"Producer commit: `{record.producer_commit}`",
        "",
        "| Evidence Boundary | Recorded State |",
        "|---|---|",
        "| Execution | succeeded |",
        "| Scientific Acceptance | rejected |",
        "| Qualification | monocular_research_hypothesis |",
        "| Physical Time | unknown |",
        "| Continuous Nonlinear Certification | false |",
        "| Optimizer Converged | false |",
        f"| Rights | {value['rights']['status']}; not_authorized |",
        "",
        f"Source presentation interval: {record.source_clock.start} "
        f"to {record.source_clock.end} s; "
        f"{record.source_clock.frame_count} original frames.",
        "",
        "### Recorded Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]


def _record_metrics(value: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for name, number in sorted(value["metrics"].items()):
        lines.append(f"| `{name}` | {number:.9g} |")
    lines.extend(
        [
            "",
            _text(value["metric_definition"]),
            "Unknown visibility weight: 0.5.",
            "",
            "### Finite Research Targets",
            "",
        ]
    )
    return lines


def _record_tail(value: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for target in sorted(value["targets"], key=lambda item: item["id"]):
        lines.append(f"- `{target['id']}`: {'pass' if target['passed'] else 'fail'}")
    lines.extend(["", "### Limitations", ""])
    lines.extend(f"- {_text(text)}" for text in value["limitations"])
    lines.extend(["", "### Bound Evidence Hashes", ""])
    lines.extend(f"- `{name}`: `{digest}`" for name, digest in sorted(value["hashes"].items()))
    lines.append("")
    return lines


def render_research_page(package: HistoricalResearchPackage) -> str:
    """Render every admitted player with explicit independent status boundaries."""
    if not isinstance(package, HistoricalResearchPackage):
        raise TypeError("Rendering requires an admitted typed research package")
    package = admit_package(
        package.manifest_bytes,
        package.manifest_sha256,
        len(package.manifest_bytes),
        package.source_commit,
    )
    lines = _package_intro(package)
    for record in package.records:
        value = record.to_record()
        lines.extend(_record_intro(record, value))
        lines.extend(_record_metrics(value))
        lines.extend(_record_tail(value))
    return "\n".join(lines) + "\n"
