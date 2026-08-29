"""Deterministic manufactured fixtures for the neural-timing protocol."""

from __future__ import annotations

import numpy as np

from src.affine_control.neural_timing_analysis import (
    EvidenceProvenance,
    IntervalDecision,
    LayerObservation,
    Modality,
    TimingLayer,
    classify_interval,
)
from src.affine_control.neural_timing_protocol import (
    EvidenceSource,
    HumanStudyBoundary,
    Hypothesis,
    NeuralTimingProtocol,
    PerturbationDeclaration,
    PhaseDeclaration,
    PowerPlan,
    ResponseWindow,
    ShamDeclaration,
    SignalChannel,
    SynchronizationContract,
)


def _sources() -> tuple[EvidenceSource, ...]:
    """Build the bounded primary-source evidence map."""
    return (
        EvidenceSource(
            "kurtzer-2009-mechanical",
            "kurtzer2009multijoint",
            "10.1152/jn.00453.2009",
            "general-upper-limb",
            "mechanical",
            "primary-experiment",
            "mechanical perturbation and separately analyzed upper-limb EMG response windows",
            "golf transport, universal latency bands, or unique cortical-pathway attribution",
        ),
        EvidenceSource(
            "saunders-knill-2003-visual",
            "saunders2003visual",
            "10.1007/s00221-003-1525-2",
            "general-upper-limb",
            "visual",
            "primary-experiment",
            "online correction after virtual-hand position perturbations during reaching",
            "golf transfer or a universal visual-response latency",
        ),
        EvidenceSource(
            "boyer-2020-auditory",
            "boyer2020sonification",
            "10.1007/s00221-020-05770-6",
            "general-upper-limb",
            "auditory",
            "primary-experiment",
            "movement change after a perturbed movement-to-sound mapping",
            "golf transfer, auditory-pathway identity, or online correction timing",
        ),
        EvidenceSource(
            "causer-2017-golf-vision",
            "causer2017quieteye",
            "10.1007/s10339-016-0783-4",
            "golf-specific",
            "visual",
            "primary-experiment",
            "visual-occlusion effects in novice golf putting at two distances",
            "full-swing transfer, elite populations, or pathway-specific neural timing",
        ),
        EvidenceSource(
            "piskin-2024-expectation",
            "piskin2024anticipatory",
            "10.3389/fnhum.2024.1423821",
            "general-upper-limb",
            "mechanical",
            "primary-experiment",
            "anticipatory upper-limb changes under predictable and partly predictable loads",
            "golf transfer or causal identification of a neural strategy",
        ),
    )


def _phases() -> tuple[PhaseDeclaration, ...]:
    """Build the registered perturbation phases."""
    return (
        PhaseDeclaration("transition", "top-of-motion", "mid-downswing"),
        PhaseDeclaration("pre-impact", "mid-downswing", "nominal-impact"),
    )


def _shams() -> tuple[ShamDeclaration, ...]:
    """Build blinded same-modality sham declarations."""
    return (
        ShamDeclaration(
            "mechanical-sham",
            "mechanical",
            "trigger, device sound, and trial duration",
            "commanded load pulse",
            "condition-m",
        ),
        ShamDeclaration(
            "visual-sham",
            "visual",
            "display refresh and cursor visibility",
            "cursor displacement",
            "condition-v",
        ),
        ShamDeclaration(
            "auditory-sham",
            "auditory",
            "sound level, duration, and carrier spectrum",
            "movement-to-sound mapping change",
            "condition-a",
        ),
    )


def _channels() -> tuple[SignalChannel, ...]:
    """Build calibrated shared-clock signal declarations."""
    calibration = "manufactured-calibration/v1"
    return (
        SignalChannel("command", "command", "normalized", 2000.0, "device", calibration),
        SignalChannel("photodiode", "command", "V", 2000.0, "display", calibration),
        SignalChannel("microphone", "command", "Pa", 48000.0, "laboratory", calibration),
        SignalChannel("hand-motion", "kinematic", "m", 500.0, "laboratory", calibration),
        SignalChannel("club-load", "kinetic", "N", 2000.0, "club", calibration),
        SignalChannel("emg-envelope", "emg", "normalized", 2000.0, "participant", calibration),
        SignalChannel("task-error", "task", "m", 500.0, "target", calibration),
    )


def _perturbations() -> tuple[PerturbationDeclaration, ...]:
    """Build phase-specific perturbation declarations."""
    revision = "synthetic-device-calibration/v1"
    stop = "abort on saturation, trigger disagreement, limit crossing, or unexpected contact"
    return (
        PerturbationDeclaration(
            "transition-load-pulse",
            "mechanical",
            "transition",
            "registered-phase-crossing",
            "club-frame transverse",
            1.0,
            "normalized load",
            20.0,
            "unexpected",
            "mechanical-sham",
            revision,
            stop,
        ),
        PerturbationDeclaration(
            "transition-cursor-jump",
            "visual",
            "transition",
            "photodiode-verified refresh",
            "target-frame lateral",
            1.0,
            "normalized cursor displacement",
            50.0,
            "cued-direction-unknown",
            "visual-sham",
            revision,
            stop,
        ),
        PerturbationDeclaration(
            "pre-impact-sonification-shift",
            "auditory",
            "pre-impact",
            "microphone-verified onset",
            "mapping slope increase",
            1.0,
            "normalized mapping gain",
            80.0,
            "fully-predictable",
            "auditory-sham",
            revision,
            stop,
        ),
    )


def _window(
    modality: Modality,
    layer: TimingLayer,
    start_ms: float,
    end_ms: float,
    onset_method: str,
    metric: str,
) -> ResponseWindow:
    """Build one operational response window."""
    return ResponseWindow(
        f"{modality}-{layer}",
        modality,
        layer,
        start_ms,
        end_ms,
        onset_method,
        metric,
    )


def _windows() -> tuple[ResponseWindow, ...]:
    """Build the complete modality-by-layer window matrix."""
    rows: tuple[tuple[Modality, float, float, float, float, float, float, float, float], ...] = (
        ("mechanical", 0.0, 10.0, 20.0, 120.0, 0.0, 80.0, 80.0, 250.0),
        ("visual", 0.0, 20.0, 80.0, 240.0, 80.0, 260.0, 100.0, 320.0),
        ("auditory", 0.0, 20.0, 60.0, 220.0, 60.0, 260.0, 80.0, 320.0),
    )
    windows: list[ResponseWindow] = []
    for modality, d0, d1, m0, m1, e0, e1, t0, t1 in rows:
        windows.extend(
            (
                _window(modality, "perturbation-detection", d0, d1, "physical onset", "ms"),
                _window(modality, "muscle-response", m0, m1, "EMG threshold", "ms"),
                _window(modality, "mechanical-effect", e0, e1, "state divergence", "ms"),
                _window(modality, "task-correction", t0, t1, "task contrast", "ms"),
            )
        )
    return tuple(windows)


def _hypotheses() -> tuple[Hypothesis, ...]:
    """Build the preregistered hierarchy of bounded contrasts."""
    return (
        Hypothesis(
            "h1-mechanical-effect",
            "primary",
            "mechanical",
            "transition",
            "mechanical-mechanical-effect",
            "club-frame state divergence",
            "load pulse minus paired sham",
            "primary-timing",
            "Holm-adjusted interval excludes the minimum relevant effect",
            "the complete interval remains inside the equivalence region",
        ),
        Hypothesis(
            "h2-visual-task-correction",
            "secondary",
            "visual",
            "transition",
            "visual-task-correction",
            "target-frame correction",
            "cursor jump minus paired sham",
            "secondary-timing",
            "Holm-adjusted interval excludes the minimum relevant effect",
            "the complete interval remains inside the equivalence region",
        ),
        Hypothesis(
            "h3-auditory-mechanical-effect",
            "exploratory",
            "auditory",
            "pre-impact",
            "auditory-mechanical-effect",
            "club-frame speed change",
            "mapping change minus paired sham",
            "exploratory-timing",
            "report the interval without confirmatory promotion",
            "mapping direction and mechanical response are inconsistent",
        ),
    )


def _power_plans() -> tuple[PowerPlan, ...]:
    """Build multiplicity-controlled plans without recruitment authority."""
    return tuple(
        PowerPlan(
            family,
            0.05,
            0.8,
            minimum,
            units,
            "external pilot variance required before recruitment",
            "simulation-plan/v1",
            "holm-step-down",
        )
        for family, minimum, units in (
            ("primary-timing", 0.01, "normalized state"),
            ("secondary-timing", 0.01, "normalized correction"),
            ("exploratory-timing", 0.01, "normalized speed"),
        )
    )


def build_neural_timing_protocol() -> NeuralTimingProtocol:
    """Return the complete manufactured protocol declaration."""
    channels = _channels()
    synchronization = SynchronizationContract(
        "hardware-shared-clock",
        "synthetic-loopback-calibration/v1",
        0.02,
        0.10,
        0.50,
        tuple(channel.channel_id for channel in channels),
        True,
        True,
        True,
    )
    return NeuralTimingProtocol(
        "affinedrift.neural-timing-feedback/v1",
        "synthetic-feasibility-only/v1",
        _sources(),
        _phases(),
        _shams(),
        channels,
        synchronization,
        _perturbations(),
        _windows(),
        _hypotheses(),
        _power_plans(),
        "phase, magnitude, direction, expectation, trial index, and prior perturbation history",
        "clock skew, onset threshold, window edge, filter, expectation, history, and model family",
        HumanStudyBoundary("unavailable", False, False),
    )


def synthetic_onset_trace() -> tuple[np.ndarray, np.ndarray]:
    """Return a manufactured 1 ms trace with a persistent crossing at 12 ms."""
    times_ms = np.arange(0.0, 30.0, 1.0, dtype=float)
    signal = np.zeros_like(times_ms)
    signal[12:] = 0.75
    return times_ms, signal


def synthetic_layer_observations() -> tuple[LayerObservation, ...]:
    """Return parallel manufactured latencies, including a direct mechanical effect."""
    provenance = EvidenceProvenance("synthetic-fixture", "parallel-layer-fixture", "v1", True)
    rows: tuple[tuple[Modality, float, float, float, float], ...] = (
        ("mechanical", 2.0, 52.0, 16.0, 138.0),
        ("visual", 8.0, 132.0, 148.0, 176.0),
        ("auditory", 5.0, 104.0, 120.0, 168.0),
    )
    observations: list[LayerObservation] = []
    for modality, detection, muscle, effect, correction in rows:
        observations.extend(
            (
                LayerObservation(modality, "perturbation-detection", detection, provenance),
                LayerObservation(modality, "muscle-response", muscle, provenance),
                LayerObservation(modality, "mechanical-effect", effect, provenance),
                LayerObservation(modality, "task-correction", correction, provenance),
            )
        )
    return tuple(observations)


def synthetic_result_ledger() -> tuple[IntervalDecision, ...]:
    """Return supported, negative, null, and unavailable manufactured results."""
    synthetic = EvidenceProvenance("synthetic-fixture", "timing-ledger", "v1", True)
    return (
        classify_interval(1.5, 2.5, 1.0, synthetic),
        classify_interval(-0.4, 0.4, 1.0, synthetic),
        classify_interval(0.5, 1.5, 1.0, synthetic),
        classify_interval(None, None, 1.0, EvidenceProvenance.unavailable("human-tier")),
    )
