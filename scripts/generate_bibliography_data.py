#!/usr/bin/env python3
import json
import re
import yaml
from pathlib import Path

def extract_yaml_from_markdown(file_path: Path):
    """Extracts YAML content from a markdown file's code block."""
    try:
        content = file_path.read_text()
        # Look for ```yaml ... ``` blocks
        # We assume the largest yaml block or the one explicitly under Bibliography is what we want.
        # But simply finding all yaml blocks and trying to parse them as list of dicts with 'id' is safer.

        matches = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)

        extracted_items = []
        for match in matches:
            try:
                data = yaml.safe_load(match)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'id' in item:
                            extracted_items.append(item)
            except yaml.YAMLError:
                continue

        return extracted_items
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def normalize_item(item):
    """Normalizes keys to match what the frontend expects."""
    if 'scholar_link' in item and 'scholar_url' not in item:
        item['scholar_url'] = item['scholar_link']
        del item['scholar_link']

    # Ensure arrays
    if 'authors' in item and isinstance(item['authors'], str):
        item['authors'] = [item['authors']]
    if 'concepts' in item and isinstance(item['concepts'], str):
        item['concepts'] = [item['concepts']]

    return item

def main() -> None:
    """
    Generate JSON data for the interactive bibliography from YAML sources.
    Reads 'data/bibliography.yaml' and 'articles/*-bibliography.md',
    and converts them to JSON in 'docs/data'.
    """
    output_dir = Path("docs/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_refs = {}

    # 1. Load base bibliography.yaml
    base_bib_path = Path("data/bibliography.yaml")
    if base_bib_path.exists():
        try:
            with open(base_bib_path) as f:
                base_data = yaml.safe_load(f)
                if base_data:
                    for item in base_data:
                        if 'id' in item:
                            all_refs[item['id']] = normalize_item(item)
        except Exception as e:
            print(f"Error processing {base_bib_path}: {e}")

    # 2. Load from articles/*-bibliography.md
    articles_dir = Path("articles")
    if articles_dir.exists():
        for md_file in articles_dir.glob("*-bibliography.md"):
            print(f"Processing {md_file}...")
            items = extract_yaml_from_markdown(md_file)
            for item in items:
                norm_item = normalize_item(item)
                # Overwrite or merge? For now, let's assume if ID exists, we keep the one we have
                # OR we prefer the one from markdown if it has more info?
                # Let's trust the one we have, but if it's new, add it.
                if norm_item['id'] not in all_refs:
                    all_refs[norm_item['id']] = norm_item
                else:
                    # Optional: merge fields if missing
                    existing = all_refs[norm_item['id']]
                    for k, v in norm_item.items():
                        if k not in existing or not existing[k]:
                            existing[k] = v

    # Convert to list
    final_refs = list(all_refs.values())

    # Sort by year (desc) then title
    final_refs.sort(key=lambda x: (-int(x.get('year', 0)), x.get('title', '')))

    # Write bibliography.json
    bib_output_path = output_dir / "bibliography.json"
    with open(bib_output_path, "w") as f:
        json.dump(final_refs, f, indent=2)

    print(f"Successfully generated {bib_output_path}")
    print(f"Total entries: {len(final_refs)}")

    # 3. Process Reading Paths
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
