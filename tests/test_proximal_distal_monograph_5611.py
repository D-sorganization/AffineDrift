"""Content contracts for AffineDrift #5611 (PDE monograph limits and citations)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONOGRAPH = ROOT / "articles/proximal_distal_energy_transfer"
BIB = MONOGRAPH / "references.bib"
CH03B = MONOGRAPH / "chapters/_ch03b_hand_path_attribution.qmd"
CH05 = MONOGRAPH / "chapters/_ch05_two_hand_wrench.qmd"
CH05B = MONOGRAPH / "chapters/_ch05b_forward_two_hand.qmd"
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


def test_monograph_unifies_differential_force_convention() -> None:
    """Chapters 3b, 5, and 5b share one differential-force symbol and sign (#5611 F9)."""
    ch03b = CH03B.read_text(encoding="utf-8")
    assert r"\mathbf F_d=\frac{\mathbf F_L-\mathbf F_T}{2}" in ch03b
    assert r"\mathbf F_d=\frac{\mathbf F_R-\mathbf F_L}{2}" not in ch03b
    assert "lead-hand (left) contact" in ch03b
    assert "trail-hand (right) contact" in ch03b
    assert "right-minus-left convention" not in ch03b

    ch05 = CH05.read_text(encoding="utf-8")
    assert r"\mathbf F_d=\frac{\mathbf F_L-\mathbf F_T}{2}" in ch05
    assert r"\Delta\mathbf F=(\mathbf F_T-\mathbf F_L)/2" not in ch05
    assert r"-\mathbf F_d\cdot\Delta\mathbf v" in ch05
    assert r"+\Delta\mathbf F\cdot\Delta\mathbf v" not in ch05

    ch05b = CH05B.read_text(encoding="utf-8")
    assert r"F_d=\tfrac12(F_L-F_R)" in ch05b
    assert r"D=\tfrac12(F_R-F_L)" not in ch05b
    assert "differential mode $F_d$" in ch05b
    assert "differential mode $D$" not in ch05b


def test_ch05_differential_normal_mode_sign_wording() -> None:
    """Ch05 states the +258.0 N positive differential normal mode that yields negative couple (F17)."""
    ch05 = CH05.read_text(encoding="utf-8")
    assert "differential normal mode" in ch05
    assert "+258.0 N" in ch05
    assert "large and negative under @eq-normal-force-couple" not in ch05


def test_lee2026_bibliography_record_matches_crossref_doi() -> None:
    """Verify @article{lee2026} (CVE-A8) matches Crossref DOI 10.1177/17479541261429479."""
    text = BIB.read_text(encoding="utf-8")
    assert "@article{lee2026," in text
    assert "10.1177/17479541261429479" in text
    assert "Ehrlich, Justin and Cain, Christopher" in text
