import os
import re

BASE_DIR = r"c:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion"
main_tex_path = os.path.join(BASE_DIR, r"Volume_II\main.tex")
chapters_dir = os.path.join(BASE_DIR, r"Volume_II\chapters")

with open(main_tex_path, encoding="utf-8") as f:
    lines = f.readlines()

new_lines: list[str] = []
in_chapter = False
current_chapter_title = ""
current_chapter_lines: list[str] = []
chapter_num = 1

# Make sure directory exists
os.makedirs(chapters_dir, exist_ok=True)

for line in lines:
    match = re.match(r"\\chapter\{(.*?)\}", line)
    if match:
        if in_chapter:
            # Save the previous chapter
            clean_title = re.sub(r"[^a-zA-Z0-9]", "_", current_chapter_title.lower())
            clean_title = re.sub(r"_+", "_", clean_title).strip("_")
            filename = f"ch{chapter_num:02d}_{clean_title[:30]}.tex"
            with open(os.path.join(chapters_dir, filename), "w", encoding="utf-8") as cf:
                cf.writelines(current_chapter_lines)
            new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")
            chapter_num += 1

        in_chapter = True
        current_chapter_title = match.group(1)
        current_chapter_lines = [line]
    elif line.strip() == r"\backmatter":
        if in_chapter:
            # Save the last chapter
            clean_title = re.sub(r"[^a-zA-Z0-9]", "_", current_chapter_title.lower())
            clean_title = re.sub(r"_+", "_", clean_title).strip("_")
            filename = f"ch{chapter_num:02d}_{clean_title[:30]}.tex"
            with open(os.path.join(chapters_dir, filename), "w", encoding="utf-8") as cf:
                cf.writelines(current_chapter_lines)
            new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")
            in_chapter = False
        new_lines.append(line)
    elif in_chapter:
        current_chapter_lines.append(line)
    else:
        new_lines.append(line)

if in_chapter:
    clean_title = re.sub(r"[^a-zA-Z0-9]", "_", current_chapter_title.lower())
    clean_title = re.sub(r"_+", "_", clean_title).strip("_")
    filename = f"ch{chapter_num:02d}_{clean_title[:30]}.tex"
    with open(os.path.join(chapters_dir, filename), "w", encoding="utf-8") as cf:
        cf.writelines(current_chapter_lines)
    new_lines.append(f"\\include{{chapters/{filename[:-4]}}}\n")

with open(main_tex_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Split {chapter_num} chapters.")
