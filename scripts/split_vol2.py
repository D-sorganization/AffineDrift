"""Split the Volume II main.tex file into per-chapter includes."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.cli_output import write_stdout


def _chapter_filename(title: str, chapter_num: int) -> str:
    """Return a filesystem-safe chapter filename."""
    clean_title = re.sub(r"[^a-zA-Z0-9]", "_", title.lower())
    clean_title = re.sub(r"_+", "_", clean_title).strip("_")
    return f"ch{chapter_num:02d}_{clean_title[:30]}.tex"


def main(repo_root: Path | None = None) -> int:
    """Split the compiled Volume II manuscript into chapter files."""
    repo_root = repo_root or Path(__file__).resolve().parent.parent
    base_dir = repo_root / "articles" / "The_Geometry_of_Motion"
    main_tex_path = base_dir / "Volume_II" / "main.tex"
    chapters_dir = base_dir / "Volume_II" / "chapters"

    lines = main_tex_path.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines: list[str] = []
    in_chapter = False
    current_chapter_title = ""
    current_chapter_lines: list[str] = []
    chapter_num = 1

    chapters_dir.mkdir(parents=True, exist_ok=True)

    for line in lines:
        match = re.match(r"\\chapter\{(.*?)\}", line)
        if match:
            if in_chapter:
                filename = _chapter_filename(current_chapter_title, chapter_num)
                (chapters_dir / filename).write_text(
                    "".join(current_chapter_lines), encoding="utf-8"
                )
                new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")
                chapter_num += 1

            in_chapter = True
            current_chapter_title = match.group(1)
            current_chapter_lines = [line]
        elif line.strip() == r"\backmatter":
            if in_chapter:
                filename = _chapter_filename(current_chapter_title, chapter_num)
                (chapters_dir / filename).write_text(
                    "".join(current_chapter_lines), encoding="utf-8"
                )
                new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")
                in_chapter = False
            new_lines.append(line)
        elif in_chapter:
            current_chapter_lines.append(line)
        else:
            new_lines.append(line)

    if in_chapter:
        filename = _chapter_filename(current_chapter_title, chapter_num)
        (chapters_dir / filename).write_text("".join(current_chapter_lines), encoding="utf-8")
        new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")

    main_tex_path.write_text("".join(new_lines), encoding="utf-8")
    write_stdout(f"Split {chapter_num} chapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
