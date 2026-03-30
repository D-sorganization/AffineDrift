import os
import subprocess
import re

def create_issue(title, body):
    print(f"Creating issue: {title}")
    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], check=True)

# 1. Formatting and constraint field issues
create_issue(
    "Replace 'Zero-Torque Constraint Field' with 'Zero-Torque Counterfactual'",
    "The zero torque counterfactual is incorrectly called the 'Zero Torque Constraint Field' in some parts of the text (e.g., ch19_aerodynamic_drag). This needs to be corrected globally."
)

create_issue(
    "Decrease text size across both textbooks",
    "The size of the text on the pages seems huge. While easier to read, it makes the books seem less substantial. Please decrease the global text size (e.g., in Quarto/LaTeX configurations) to be more in line with professional texts."
)

create_issue(
    "Increase page margins across both textbooks",
    "Evaluate and modify the margins around the book pages in both The Physics of Golf and The Geometry of Motion. The current margins are too tight to the edges and need to be larger."
)

# 2. Parse the magic numbers report and create issues per chapter
with open("magic_numbers_report.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Split by file
blocks = content.split("--- ")[1:]
for block in blocks:
    lines = block.strip().split("\n")
    if not lines:
        continue
    
    filename = lines[0].replace(" ---", "").strip()
    stats_line = lines[1] if len(lines) > 1 else ""
    instances = lines[2:]
    
    # We only care if there actually are instances
    if "Total instances found: 0" in stats_line:
        continue
        
    issue_title = f"Add explicit sources for magic numbers/studies in {filename}"
    
    body = f"**File**: `{filename}`\n"
    body += f"**{stats_line}**\n\n"
    body += "We need to track down instances of numbers, magic numbers, or 'studies' that are referenced without an explicit source in the text. We cannot make up numbers or reference studies without citing them. Please write from a point of humility.\n\n"
    body += "### Examples found in this file:\n"
    for instance in instances[:5]:
        body += f"- `{instance}`\n"
        
    if len(instances) > 5:
        body += "\n*(See scripts/find_magic_numbers.py output for more)*\n"
        
    create_issue(issue_title, body)

print("All issues created.")
