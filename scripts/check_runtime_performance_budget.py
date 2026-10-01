#!/usr/bin/env python3
"""Validate runtime performance budgets for representative routes (WEB-10.1 / #4570)."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from scripts.cli_output import write_stderr, write_stdout
from scripts.public_site_manifest import REPRESENTATIVE_ROUTES

DEFAULT_CONFIG_PATH = Path("config/runtime_performance_budget.json")
REQUIRED_METRIC_KEYS = ("max_lcp_ms", "max_cls", "max_tbt_ms", "max_transfer_bytes")


def load_runtime_performance_budget(config_path: Path) -> dict[str, Any]:
    """Load and parse the runtime performance budget JSON."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Runtime performance budget config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid runtime performance budget format in {config_path}: expected dict"
        )
    return data


def validate_budget_config(
    config: dict[str, Any],
    representative_routes: Iterable[dict[str, Any]] = REPRESENTATIVE_ROUTES,
) -> list[str]:
    """Validate that budget config covers all representative routes with positive limits."""
    errors: list[str] = []

    defaults = config.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("Config missing valid 'defaults' mapping.")
    else:
        for key in REQUIRED_METRIC_KEYS:
            val = defaults.get(key)
            if not isinstance(val, (int, float)) or val <= 0:
                errors.append(f"Default metric '{key}' must be a positive number; got {val!r}")

    routes = config.get("routes")
    if not isinstance(routes, dict):
        errors.append("Config missing valid 'routes' mapping.")
        return errors

    for route_info in representative_routes:
        route = route_info.get("route")
        if not route or route not in routes:
            errors.append(f"Missing runtime performance budget for representative route: '{route}'")
            continue

        route_budget = routes[route]
        if not isinstance(route_budget, dict):
            errors.append(
                f"Route '{route}' budget must be an object; got {type(route_budget).__name__}"
            )
            continue

        for key in REQUIRED_METRIC_KEYS:
            val = route_budget.get(key)
            if val is not None:
                if (
                    not isinstance(val, (int, float))
                    or (key != "max_cls" and val <= 0)
                    or (key == "max_cls" and val < 0)
                ):
                    errors.append(
                        f"Route '{route}' metric '{key}' must be a valid positive number; got {val!r}"
                    )

    return errors


def evaluate_runtime_metrics(
    metrics_by_route: dict[str, dict[str, float]],
    config: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Evaluate measured runtime performance metrics against route budgets.

    Returns (details, errors).
    """
    details: list[str] = []
    errors: list[str] = []
    defaults = config.get("defaults", {})
    routes = config.get("routes", {})

    for route, measured in sorted(metrics_by_route.items()):
        route_cfg = routes.get(route, {})
        max_lcp = route_cfg.get("max_lcp_ms", defaults.get("max_lcp_ms", 3000))
        max_cls = route_cfg.get("max_cls", defaults.get("max_cls", 0.1))
        max_tbt = route_cfg.get("max_tbt_ms", defaults.get("max_tbt_ms", 300))
        max_bytes = route_cfg.get("max_transfer_bytes", defaults.get("max_transfer_bytes", 2500000))

        lcp = measured.get("lcp", 0.0)
        cls = measured.get("cls", 0.0)
        tbt = measured.get("tbt", 0.0)
        transfer_bytes = measured.get("transfer_bytes", 0.0)

        details.append(
            f"Route '{route}': LCP={lcp:.1f}ms (max {max_lcp}ms), "
            f"CLS={cls:.3f} (max {max_cls}), "
            f"TBT={tbt:.1f}ms (max {max_tbt}ms), "
            f"Transfer={transfer_bytes/1024:.1f}KB (max {max_bytes/1024:.1f}KB)"
        )

        if lcp > max_lcp:
            errors.append(f"Route '{route}' exceeded LCP budget: {lcp:.1f}ms > {max_lcp}ms")
        if cls > max_cls:
            errors.append(f"Route '{route}' exceeded CLS budget: {cls:.3f} > {max_cls}")
        if tbt > max_tbt:
            errors.append(f"Route '{route}' exceeded TBT budget: {tbt:.1f}ms > {max_tbt}ms")
        if transfer_bytes > max_bytes:
            errors.append(
                f"Route '{route}' exceeded transfer_bytes budget: {transfer_bytes} > {max_bytes}"
            )

    return details, errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI options for the runtime performance budget checker."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to runtime_performance_budget.json (default: config/runtime_performance_budget.json)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path to measured runtime performance JSON report to evaluate",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Validate runtime performance budget configuration and optional metrics report."""
    args = parse_args(argv)
    try:
        config = load_runtime_performance_budget(args.config)
    except Exception as exc:
        write_stderr(f"Error loading budget config: {exc}\n")
        return 1

    validation_errors = validate_budget_config(config, REPRESENTATIVE_ROUTES)
    if validation_errors:
        write_stderr("Runtime performance budget config validation failed:\n")
        for err in validation_errors:
            write_stderr(f"  - {err}\n")
        return 1

    if args.report is not None:
        if not args.report.is_file():
            write_stderr(f"Metrics report file not found: {args.report}\n")
            return 1
        with args.report.open("r", encoding="utf-8") as f:
            metrics_data = json.load(f)
        if not isinstance(metrics_data, dict):
            write_stderr("Metrics report must be a JSON object mapping route -> metrics.\n")
            return 1

        details, errors = evaluate_runtime_metrics(metrics_data, config)
        for line in details:
            write_stdout(f"  {line}\n")
        if errors:
            write_stderr("Runtime performance budget evaluation failed:\n")
            for err in errors:
                write_stderr(f"  - {err}\n")
            return 1
        write_stdout("All runtime performance metrics are within budget.\n")
    else:
        write_stdout(
            f"Runtime performance budget config '{args.config}' is valid across all "
            f"{len(REPRESENTATIVE_ROUTES)} representative routes.\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
