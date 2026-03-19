# AffineDrift scripts package - enables `from scripts.xxx import ...` in tests.
#
# DRY NOTE (#1614): ~14 check_*.py scripts each contain the identical one-liner:
#   repo_root = Path(__file__).resolve().parent.parent
# plus similar argparse boilerplate (description, --verbose flag, sys.exit logic).
# Consolidation opportunity: extract a shared `scripts/_helpers.py` with:
#   - get_repo_root() -> Path
#   - make_parser(description: str) -> argparse.ArgumentParser
#   - run_check(fn, parser) -> int  (standard exit-code wrapper)
# This would reduce ~50 duplicated blocks across the scripts directory.
# Tracked in issue #1614.
