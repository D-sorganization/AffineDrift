"""Benchmarks for API and module loading performance.

Measures the performance of critical module imports and utility functions:
- Core module import times
- API response time proxies (query-like operations)
- Serialization/deserialization of results
"""

from __future__ import annotations

import importlib
import sys
from typing import Any

import numpy as np
import pytest


@pytest.mark.benchmark(group="api")
class TestAPIAndModuleLoadBenchmarks:
    """Benchmark suite for module loading and API-like operations."""

    def test_benchmark_core_module_import(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark core module import time.

        Module imports are critical for startup performance of any
        command-line tools or API servers built on top of this library.
        """

        def import_core() -> Any:
            """Import src.core from scratch, bypassing the module cache."""
            # Remove from cache to force fresh import
            if "src.core" in sys.modules:
                del sys.modules["src.core"]
            return importlib.import_module("src.core")

        module = benchmark(import_core)
        assert module is not None

    def test_benchmark_contracts_module_import(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark contracts module import.

        The contracts module is imported by many other modules, so its
        import time affects overall startup performance.
        """

        def import_contracts() -> Any:
            """Import src.core.contracts from scratch, bypassing the module cache."""
            if "src.core.contracts" in sys.modules:
                del sys.modules["src.core.contracts"]
            return importlib.import_module("src.core.contracts")

        module = benchmark(import_contracts)
        assert module is not None

    def test_benchmark_swing_optimizer_import(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark swing optimizer module import.

        The swing optimizer is a performance-critical module that may be
        imported multiple times during optimization.
        """

        def import_optimizer() -> Any:
            """Import swing_optimizer from scratch, bypassing the module cache."""
            if "src.affine_control.swing_optimizer" in sys.modules:
                del sys.modules["src.affine_control.swing_optimizer"]
            return importlib.import_module("src.affine_control.swing_optimizer")

        module = benchmark(import_optimizer)
        assert module is not None

    def test_benchmark_ball_flight_import(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark ball flight dynamics module import.

        The ball flight dynamics are used in simulation queries, so their
        import time affects response latency.
        """

        def import_ball_flight() -> Any:
            """Import ball_flight from scratch, bypassing the module cache."""
            if "src.golf_simulation.ball_flight" in sys.modules:
                del sys.modules["src.golf_simulation.ball_flight"]
            return importlib.import_module("src.golf_simulation.ball_flight")

        module = benchmark(import_ball_flight)
        assert module is not None

    def test_benchmark_numpy_serialization_small(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark serialization of small NumPy array (100 elements).

        Serialization is important for API responses that contain
        trajectories and state vectors.
        """
        data = np.random.randn(100)

        def serialize_small() -> bytes:
            """Serialize the small array to raw bytes."""
            return data.tobytes()

        result = benchmark(serialize_small)
        assert isinstance(result, bytes)
        assert len(result) == 100 * 8  # 8 bytes per float64

    def test_benchmark_numpy_serialization_large(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark serialization of large NumPy array (10000 elements).

        This tests serialization performance for high-resolution trajectory
        results that might be returned from API queries.
        """
        data = np.random.randn(10000)

        def serialize_large() -> bytes:
            """Serialize the large array to raw bytes."""
            return data.tobytes()

        result = benchmark(serialize_large)
        assert isinstance(result, bytes)

    def test_benchmark_numpy_deserialization_small(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark deserialization of small NumPy array (100 elements).

        Deserialization is the inverse of serialization, important for
        processing incoming API requests.
        """
        data = np.random.randn(100).tobytes()

        def deserialize_small() -> np.ndarray:
            """Deserialize the small byte buffer back to a NumPy array."""
            return np.frombuffer(data, dtype=np.float64)

        result = benchmark(deserialize_small)
        assert len(result) == 100

    def test_benchmark_numpy_deserialization_large(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark deserialization of large NumPy array (10000 elements).

        This tests deserialization performance for large API payloads.
        """
        data = np.random.randn(10000).tobytes()

        def deserialize_large() -> np.ndarray:
            """Deserialize the large byte buffer back to a NumPy array."""
            return np.frombuffer(data, dtype=np.float64)

        result = benchmark(deserialize_large)
        assert len(result) == 10000

    def test_benchmark_json_serialization_trajectory_metadata(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark JSON serialization of trajectory metadata.

        Typical API responses include trajectory metadata (timestamps,
        costs, convergence info) as JSON, which is slower than binary
        serialization but more human-readable.
        """
        import json

        metadata = {
            "trajectory_id": "opt_2024_04_29_001",
            "n_steps": 100,
            "horizon_seconds": 1.0,
            "dt_seconds": 0.01,
            "final_cost": 42.5,
            "convergence_iterations": 15,
            "solver": "ddp",
            "status": "converged",
        }

        def serialize_json() -> str:
            """Serialize the metadata dict to a JSON string."""
            return json.dumps(metadata)

        result = benchmark(serialize_json)
        assert isinstance(result, str)

    def test_benchmark_trajectory_length_query(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark computing trajectory summary statistics.

        API queries often return summaries (length, cost, duration) that
        require scanning the trajectory data.
        """
        trajectory = np.random.randn(4, 100)  # 4D state, 100 timesteps

        def compute_summary() -> dict[str, Any]:
            """Compute summary statistics for the trajectory."""
            return {
                "n_states": trajectory.shape[1],
                "state_dim": trajectory.shape[0],
                "trajectory_cost": float(np.sum(trajectory**2)),
                "max_position": float(np.max(np.linalg.norm(trajectory[:2], axis=0))),
                "max_velocity": float(np.max(np.linalg.norm(trajectory[2:], axis=0))),
            }

        summary = benchmark(compute_summary)
        assert "n_states" in summary


@pytest.mark.benchmark(group="api")
def test_benchmark_full_module_startup(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark full startup time loading core modules.

    This is a module-level benchmark measuring the time to import all
    essential modules, simulating API server startup or CLI initialization.
    """

    def startup() -> None:
        """Import all essential modules in dependency order."""
        # Import core modules in dependency order
        importlib.import_module("src.core.constants")
        importlib.import_module("src.core.contracts")
        importlib.import_module("src.affine_control.swing_types")
        importlib.import_module("src.affine_control.swing_optimizer")
        importlib.import_module("src.golf_simulation.ball_flight")

    benchmark(startup)


@pytest.mark.benchmark(group="api")
def test_benchmark_result_preparation_query_response(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark preparing a complete query response with trajectory data.

    This measures the end-to-end time to format and serialize a typical
    optimization result for return to an API client.
    """
    import json

    # Simulate a realistic optimization result
    trajectory = np.random.randn(4, 50)
    controls = np.random.randn(2, 49)

    def prepare_response() -> str:
        """Format and JSON-serialize a complete optimization result."""
        response = {
            "status": "success",
            "trajectory": {
                "positions": trajectory[:2].tolist(),
                "velocities": trajectory[2:].tolist(),
            },
            "controls": controls.tolist(),
            "metadata": {
                "n_steps": 50,
                "solver": "ddp",
                "iterations": 12,
                "final_cost": 25.5,
                "convergence_time_seconds": 0.42,
            },
        }
        return json.dumps(response)

    result = benchmark(prepare_response)
    assert isinstance(result, str)
    assert "trajectory" in result
