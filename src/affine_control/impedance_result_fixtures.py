"""Manufactured result-ledger fixtures with explicit evidence provenance."""

from __future__ import annotations

from src.affine_control.impedance_evidence import EvidenceProvenance, ImpedanceResult


def manufactured_results() -> tuple[ImpedanceResult, ...]:
    """Return all evidence tiers and adverse outcomes without suppression."""
    return (
        ImpedanceResult(
            "phase-specific effective joint stiffness",
            "effective-mechanical",
            96.0,
            (90.0, 103.0),
            "Nm/rad",
            "supported",
            ("passive tissue basis", "perturbation bandwidth"),
            "The synthetic mechanical response closes inside its declared interval.",
            EvidenceProvenance(
                "synthetic-fixture",
                "active-impedance-transition-v1",
                "manufactured-fixture/v1",
                True,
            ),
        ),
        ImpedanceResult(
            "reflex-basis recovery error",
            "model-partitioned",
            0.18,
            (0.11, 0.26),
            "normalized RMS error",
            "negative",
            ("reflex delay", "passive basis", "voluntary basis"),
            "The adverse synthetic basis exceeds its preregistered recovery tolerance.",
            EvidenceProvenance(
                "synthetic-fixture",
                "active-impedance-confounded-v1",
                "manufactured-fixture/v1",
                True,
            ),
        ),
        ImpedanceResult(
            "agonist-antagonist envelope overlap",
            "emg-proxy",
            0.46,
            (0.28, 0.61),
            "normalized proxy",
            "null",
            ("electrode placement", "EMG normalization", "muscle-pair selection"),
            "The synthetic proxy interval supports no unique mechanical partition.",
            EvidenceProvenance(
                "synthetic-fixture",
                "active-impedance-emg-pair-v1",
                "manufactured-fixture/v1",
                True,
            ),
        ),
        ImpedanceResult(
            "individual biological actuator contribution",
            "unavailable",
            None,
            None,
            "N",
            "unavailable",
            (),
            "No declared observation identifies the requested biological source.",
            EvidenceProvenance(
                "unavailable",
                "active-impedance-unavailable-actuator-v1",
                "result-ledger/v1",
                False,
            ),
        ),
    )
