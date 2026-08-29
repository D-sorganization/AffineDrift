"""Primary-source register for active impedance protocol fixtures."""

from __future__ import annotations

from src.affine_control.impedance_protocol import EvidenceSource


def primary_sources() -> tuple[EvidenceSource, ...]:
    """Return source records with explicit scientific authority limits."""
    return (
        EvidenceSource(
            "westwick-perreault-2012",
            "primary-literature",
            "Westwick and Perreault (2012), IEEE TBME, doi:10.1109/TBME.2012.2213339",
            "input bandwidth, noise, causality, and impedance-identification limits",
            "does not validate this fixture, device, movement phase, or participant protocol",
        ),
        EvidenceSource(
            "lipps-et-al-2020",
            "primary-literature",
            "Lipps et al. (2020), Ann Biomed Eng, doi:10.1007/s10439-020-02509-w",
            "multidimensional shoulder-impedance measurement precedent",
            "volitional posture experiment is not swing-phase or endpoint-to-joint equivalence",
        ),
        EvidenceSource(
            "vant-veld-et-al-2021",
            "primary-literature",
            "van 't Veld et al. (2021), JNER, doi:10.1186/s12984-021-00809-3",
            "parallel-cascade intrinsic/reflex model and EMG association precedent",
            "association and model partition are not unique physiological identification",
        ),
        EvidenceSource(
            "li-et-al-2021",
            "primary-literature",
            "Li et al. (2021), Front Bioeng Biotechnol, doi:10.3389/fbioe.2020.588908",
            "co-contraction-index sensitivity to delay, muscle pair, and formulation",
            "gait associations do not establish stiffness or swing-specific validity",
        ),
        EvidenceSource(
            "carey-et-al-2026",
            "primary-literature",
            "Carey et al. (2026), PLOS ONE, doi:10.1371/journal.pone.0343081",
            "synthetic comparison of co-contraction-index interpretation and normalization",
            "synthetic index behavior is not mechanical impedance or participant evidence",
        ),
        EvidenceSource(
            "hermens-et-al-2000",
            "method-recommendation",
            "Hermens et al. (2000), J Electromyogr Kinesiol, " "doi:10.1016/S1050-6411(00)00027-4",
            "surface-EMG sensor and placement recommendations",
            "placement guidance does not eliminate crosstalk or identify muscle force",
        ),
    )
