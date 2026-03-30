import os
import re

directories = [
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf",
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion",
]

for d in directories:
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".tex") or f.endswith(".sty"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as file_obj:
                    content = file_obj.read()

                # Check if it has documentclass changing
                if r"\documentclass" in content or r"\usepackage" in content:
                    new_content = re.sub(
                        r"\\documentclass\[([^\]]*)11pt([^\]]*)\]\{book\}",
                        r"\\documentclass[\g<1>10pt\g<2>]{book}",
                        content,
                    )
                    new_content = re.sub(
                        r"\\documentclass\[([^\]]*)12pt([^\]]*)\]\{book\}",
                        r"\\documentclass[\g<1>10pt\g<2>]{book}",
                        new_content,
                    )

                    # Update margin using geometry package
                    new_content = re.sub(
                        r"\\usepackage\[margin=[0-9.]+in\]\{geometry\}",
                        r"\\usepackage[margin=1.5in]{geometry}",
                        new_content,
                    )
                    new_content = re.sub(
                        r"\\geometry\{margin=[0-9.]+in\}", r"\\geometry{margin=1.5in}", new_content
                    )
                    new_content = re.sub(
                        r"\\geometry\{a4paper, margin=[0-9.]+in\}",
                        r"\\geometry{a4paper, margin=1.5in}",
                        new_content,
                    )

                    if new_content != content:
                        with open(path, "w", encoding="utf-8") as file_obj:
                            file_obj.write(new_content)
                        print(f"Updated {path}")
