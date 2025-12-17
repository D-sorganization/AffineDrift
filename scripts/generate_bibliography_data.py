#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


def main() -> None:
    """
    Generate JSON data for the interactive bibliography from YAML sources.
    Reads 'data/bibliography.yaml' and 'data/reading_paths.yaml',
    and converts them to JSON in 'docs/data'.
    """
    source_path = Path("data/bibliography.yaml")
    output_dir = Path("docs/data")
    output_path = output_dir / "bibliography.json"

    if not source_path.exists():
        print(f"Error: {source_path} not found.")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(source_path) as f:
            data = yaml.safe_load(f)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Successfully generated {output_path} from {source_path}")
        print(f"Entry count: {len(data)}")

    except Exception as e:
        print(f"Error processing bibliography: {e}")

    # Process Reading Paths
    paths_source = Path("data/reading_paths.yaml")
    paths_output = output_dir / "reading_paths.json"

    if paths_source.exists():
        try:
            with open(paths_source) as f:
                paths_data = yaml.safe_load(f)
            with open(paths_output, "w") as f:
                json.dump(paths_data, f, indent=2)
            print(f"Successfully generated {paths_output}")
        except Exception as e:
            print(f"Error processing reading paths: {e}")


if __name__ == "__main__":
    main()
