"""Unit tests for the runtime performance budget configuration and gate (issue #4570)."""

from __future__ import annotations

from pathlib import Path

import scripts.check_runtime_performance_budget as budget_gate
from scripts.check_runtime_performance_budget import (
    evaluate_runtime_metrics,
    load_runtime_performance_budget,
    validate_budget_config,
)
from scripts.public_site_manifest import REPRESENTATIVE_ROUTES

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_representative_routes_count():
    """Verify that canonical REPRESENTATIVE_ROUTES contains exactly ten routes."""
    assert len(REPRESENTATIVE_ROUTES) == 10


def test_load_and_validate_committed_config():
    """Verify that committed config/runtime_performance_budget.json is valid."""
    config_path = REPO_ROOT / "config" / "runtime_performance_budget.json"
    assert config_path.is_file(), f"Missing config file at {config_path}"

    config = load_runtime_performance_budget(config_path)
    errors = validate_budget_config(config, REPRESENTATIVE_ROUTES)
    assert errors == [], f"Validation errors: {errors}"


def test_validate_budget_config_missing_route():
    """Verify that validate_budget_config flags missing routes from representative manifest."""
    incomplete_config = {
        "defaults": {
            "max_lcp_ms": 3000,
            "max_cls": 0.1,
            "max_tbt_ms": 300,
            "max_transfer_bytes": 2500000,
        },
        "routes": {
            "/": {
                "family": "home",
                "max_lcp_ms": 2500,
                "max_cls": 0.1,
                "max_tbt_ms": 300,
                "max_transfer_bytes": 1500000,
            }
        },
    }
    errors = validate_budget_config(incomplete_config, REPRESENTATIVE_ROUTES)
    assert any(
        "Missing runtime performance budget for representative route" in err for err in errors
    )


def test_validate_budget_config_invalid_metric_value():
    """Verify that validate_budget_config flags non-positive or invalid threshold values."""
    invalid_config = {
        "defaults": {
            "max_lcp_ms": -10,
            "max_cls": 0.1,
            "max_tbt_ms": 300,
            "max_transfer_bytes": 2500000,
        },
        "routes": {
            route_info["route"]: {
                "family": route_info["family"],
                "max_lcp_ms": 0,
                "max_cls": -0.5,
                "max_tbt_ms": -1,
                "max_transfer_bytes": 0,
            }
            for route_info in REPRESENTATIVE_ROUTES
        },
    }
    errors = validate_budget_config(invalid_config, REPRESENTATIVE_ROUTES)
    assert len(errors) > 0


def test_evaluate_runtime_metrics_passes_under_budget():
    """Verify that evaluation succeeds when metrics are well within budget."""
    config = {
        "routes": {
            "/": {
                "max_lcp_ms": 2500,
                "max_cls": 0.1,
                "max_tbt_ms": 300,
                "max_transfer_bytes": 1500000,
            }
        }
    }
    sample_metrics = {
        "/": {
            "lcp": 1200.0,
            "cls": 0.02,
            "tbt": 50.0,
            "transfer_bytes": 450000,
        }
    }
    details, errors = evaluate_runtime_metrics(sample_metrics, config)
    assert errors == []
    assert len(details) == 1


def test_evaluate_runtime_metrics_fails_when_exceeding_thresholds():
    """Verify that evaluation fails when LCP, CLS, TBT, or transfer_bytes exceed budget."""
    config = {
        "routes": {
            "/": {
                "max_lcp_ms": 2500,
                "max_cls": 0.1,
                "max_tbt_ms": 300,
                "max_transfer_bytes": 1500000,
            }
        }
    }
    regressed_metrics = {
        "/": {
            "lcp": 3200.0,
            "cls": 0.25,
            "tbt": 450.0,
            "transfer_bytes": 2000000,
        }
    }
    details, errors = evaluate_runtime_metrics(regressed_metrics, config)
    assert len(errors) == 4
    assert any("LCP" in e for e in errors)
    assert any("CLS" in e for e in errors)
    assert any("TBT" in e for e in errors)
    assert any("transfer_bytes" in e for e in errors)


def test_main_cli_success():
    """Verify that running the budget gate main() returns 0 for valid config."""
    exit_code = budget_gate.main([])
    assert exit_code == 0


def test_playwright_e2e_spec_exists():
    """Verify that tests/e2e/performance_budget.spec.js exists and is non-empty."""
    spec_path = REPO_ROOT / "tests" / "e2e" / "performance_budget.spec.js"
    assert spec_path.is_file(), f"Missing Playwright E2E spec at {spec_path}"
    content = spec_path.read_text(encoding="utf-8")
    assert "Runtime Performance Budgets" in content
    assert "runtime_performance_budget.json" in content
