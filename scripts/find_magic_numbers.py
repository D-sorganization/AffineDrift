import os
import re

directories = [
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf",
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion"
]

patterns = [
    r'\b\d+(?:\.\d+)?\s*(?:N|Nm|N·m|kg|m/s|mph|degrees|rad/s|ms|%)\b',  # physical units
    r'\b(?:a study|studies|researchers|experiments|measurements|data shows)\b'
]
cite_pattern = r'\\cite(?:p|t)?\{[^}]+\}|@\w+'  # \cite{...} or @Smith2020

findings = {}

for d in directories:
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith((".tex", ".qmd")):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8") as file_obj:
                        lines = file_obj.readlines()
                except UnicodeDecodeError:
                    continue
                
                for i, line in enumerate(lines):
                    # check if line is a comment in latex/html
                    clean_line = line.strip()
                    if clean_line.startswith("%") or clean_line.startswith("<!-"):
                        continue
                    
                    # exclude math environment lines partially or if it's an equation
                    if clean_line.startswith("\\") or clean_line.startswith("$$"):
                        continue
                    
                    found_pattern = False
                    for p in patterns:
                        if re.search(p, line, re.IGNORECASE):
                            found_pattern = True
                            break
                    
                    if found_pattern:
                        # Check if no citation exists
                        if not re.search(cite_pattern, line):
                            # Ensure there actually is a number or study word, maybe rule out single digits
                            # Actually, let's just log it
                            if path not in findings:
                                findings[path] = []
                            findings[path].append((i+1, line.strip()))

# Output summary to a file to read it easily
with open("magic_numbers_report.txt", "w", encoding="utf-8") as out:
    for path, matches in findings.items():
        if matches:
            out.write(f"\n--- {os.path.basename(path)} ---\n")
            # Only output first 3 per file to avoid massive output, but count total
            out.write(f"Total instances found: {len(matches)}\n")
            for line_num, text in matches[:10]:
                out.write(f"L{line_num}: {text[:150]}...\n")
