"""Content contracts for AffineDrift #5611 (PDE monograph limits and citations)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONOGRAPH = ROOT / "articles/proximal_distal_energy_transfer"
BIB = MONOGRAPH / "references.bib"
CH05 = MONOGRAPH / "chapters/_ch05_two_hand_wrench.qmd"
CH06_METHODS = MONOGRAPH / "chapters/_ch06_methods.qmd"
CH06CD = MONOGRAPH / "chapters/_ch06cd_articulated_attribution.qmd"
CH06BC = MONOGRAPH / "chapters/_ch06bc_torque_allocation_preload.qmd"
CH07C = MONOGRAPH / "chapters/_ch07c_transmission_robustness.qmd"
CH07_RESULTS = MONOGRAPH / "chapters/_ch07_results.qmd"
INDEX = MONOGRAPH / "index.qmd"
WRAPPER = ROOT / "articles/proximal-distal-energy-transfer.qmd"


def test_monograph_bibliography_first_authors_and_dois() -> None:
    """Registered bibliography records match publisher metadata (#5611)."""
    text = BIB.read_text(encoding="utf-8")
    assert "@article{kao1995," in text
    assert "Kao, John T." in text
    assert "jobe1995" not in text
    assert "@article{borzelli2018," in text
    assert "Borzelli, Daniele" in text
    assert "10.1371/journal.pone.0205911" in text
    assert "deRugy2018" not in text
    assert "@article{tucker2013," in text
    assert "10.1080/14763141.2013.784350" in text
    assert "year    = {2013}" in text
    assert "tucker2014" not in text


def test_monograph_chapters_use_corrected_citation_keys() -> None:
    """In-text keys match the corrected bibliography records."""
    assert "[@kao1995]" in CH06BC.read_text(encoding="utf-8")
    assert "jobe1995" not in CH06BC.read_text(encoding="utf-8")
    ch07c = CH07C.read_text(encoding="utf-8")
    assert "[@borzelli2018]" in ch07c
    assert "[@tucker2013]" in ch07c
    assert "deRugy2018" not in ch07c
    assert "tucker2014" not in ch07c


def test_wscg_two_hand_trace_discloses_event_timing() -> None:
    """Archived Simscape export states peak speed time and absent impact registration."""
    ch05 = CH05.read_text(encoding="utf-8")
    for phrase in (
        "no registered ball-impact or delivery-crossing event",
        "0.1933 s",
        "0.2801 s",
        "after peak clubhead speed",
    ):
        assert phrase in ch05
    abstract = INDEX.read_text(encoding="utf-8")
    assert "after peak clubhead speed" in abstract


def test_planar_double_pendulum_discloses_unbounded_wrist_range() -> None:
    """Reference programs report minimum relative wrist angles without joint stops."""
    methods = CH06_METHODS.read_text(encoding="utf-8")
    results = CH07_RESULTS.read_text(encoding="utf-8")
    assert "no hard joint stop" in methods
    assert "Minimum relative wrist angle" in results
    for value in ("2.52", "2.47", "2.33", "2.30"):
        assert value in results


def test_articulated_attribution_engine_versions_match_evidence() -> None:
    """Engine versions in prose match articulated_drift_contact_attribution.json."""
    text = CH06CD.read_text(encoding="utf-8")
    assert "MuJoCo 3.8.0" in text
    assert "Pinocchio 3.8.0" in text
    assert "3.12.0" not in text
    assert "4.1.0" not in text
    assert "engine version fields" in text.lower()


def test_site_wrapper_cites_kao_for_scapular_emg() -> None:
    """Lay wrapper uses first-author Kao et al. (1995) for PMID 7726345."""
    text = WRAPPER.read_text(encoding="utf-8")
    assert "Kao et al., 1995" in text
    assert "Jobe et al., 1995" not in text
