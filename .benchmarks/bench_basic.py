def test_benchmark_basic(benchmark):
    """Baseline benchmark: measure overhead of an empty callable via pytest-benchmark."""

    def run():
        """No-op target used to establish the benchmark floor."""
        # Intentionally empty — measures raw benchmark harness overhead
        return None

    benchmark(run)
