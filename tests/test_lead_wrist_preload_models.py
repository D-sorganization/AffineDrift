"""Reproduction tests for the firm-lead-wrist preload models (#5134).

Expected values were produced by running the original UpstreamDrift modules
``torque_allocation_preload.py`` and ``advanced_biological_bridge.py`` at
3fd2a59e390523169df846a3bbb395a6203c382c; the AffineDrift port must agree with them.
"""

import json
from pathlib import Path

import pytest

from src.tools import lead_wrist_preload_models as models


@pytest.mark.parametrize(
    ("program", "preloaded", "impulse", "arm_gap", "wrist_gap"),
    [
        (models.PERSISTENT, True, 0.0717103076307577, 0.0, 0.0),
        (models.REVERSAL, True, 0.19540693388776567, 0.0115, 0.022),
        (models.PERSISTENT, False, 0.20107138073005523, 0.0067, 0.0142),
        (models.REVERSAL, False, 0.20107138073005523, 0.0067, 0.0142),
    ],
)
def test_dead_zone_reproduces_upstream(program, preloaded, impulse, arm_gap, wrist_gap) -> None:
    trace = models.simulate_dead_zone(program, models.DEAD_ZONE_CHANNEL, preloaded=preloaded)
    assert trace["error_impulse_nms"] == pytest.approx(impulse, rel=1e-12)
    assert trace["arm_gap_s"] == pytest.approx(arm_gap, abs=1e-12)
    assert trace["wrist_gap_s"] == pytest.approx(wrist_gap, abs=1e-12)


@pytest.mark.parametrize(
    ("program", "impulse"),
    [(models.PERSISTENT, 0.08998329105737461), (models.REVERSAL, 0.0908399207197984)],
)
def test_muscle_bridge_reproduces_upstream(program, impulse) -> None:
    trace = models.simulate_muscle(program)
    assert trace["error_impulse_nms"] == pytest.approx(impulse, rel=1e-12)


def test_muscle_step_audit_shrinks_but_keeps_sign() -> None:
    audit = models.muscle_step_audit()
    expected = [0.00276966, 0.00155305, 0.00085663, 0.00062807, 0.0005144]
    assert audit["difference_nms"] == pytest.approx(expected, abs=1e-8)


def test_muscle_limit_gap_is_under_half_a_percent() -> None:
    audit = models.muscle_step_audit()
    assert audit["limit_persistent_nms"] == pytest.approx(0.09203, abs=1e-5)
    assert audit["limit_reversal_nms"] == pytest.approx(0.09243, abs=1e-5)
    assert 0.0 < audit["limit_relative_difference"] < 0.005


def test_larger_delivery_target_reverses_the_sign() -> None:
    audit = models.muscle_step_audit((models.PERSISTENT_LARGE, models.REVERSAL_LARGE))
    assert audit["limit_persistent_nms"] == pytest.approx(0.1918, abs=1e-4)
    assert audit["limit_reversal_nms"] == pytest.approx(0.1505, abs=1e-4)
    assert all(difference < 0.0 for difference in audit["difference_nms"])


def test_reversal_overshoots_while_persistent_does_not() -> None:
    reversal = models.simulate_muscle(models.REVERSAL)
    persistent = models.simulate_muscle(models.PERSISTENT)
    assert reversal["peak_net_nm"] > 10.0 >= persistent["peak_net_nm"]
    assert reversal["signed_error_nms"] < 0.0 < persistent["signed_error_nms"]


def test_dead_zone_sensitivity_counts() -> None:
    grid = models.dead_zone_sensitivity()
    assert (grid["persistent_favored"], grid["equivalent"], grid["reversal_favored"]) == (9, 3, 0)


def test_shaft_round_trip_matches_heavy_hit_article() -> None:
    assert models.shaft_round_trip_s() == pytest.approx(445e-6, abs=1e-6)


def test_dead_zone_rejects_invalid_channel() -> None:
    with pytest.raises(ValueError, match="dead_zone_rad"):
        models.DeadZoneChannel(stiffness_nm_rad=600.0, dead_zone_rad=-1.0, time_constant_s=0.018)


def test_muscle_rejects_unstable_step() -> None:
    with pytest.raises(ValueError, match="step_s"):
        models.simulate_muscle(models.PERSISTENT, step_s=0.002)


def test_write_results_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    models.write_results(path)
    assert json.loads(path.read_text(encoding="utf-8")) == json.loads(
        json.dumps(models.build_results())
    )
