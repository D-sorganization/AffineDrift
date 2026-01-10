import os
import re

def fix_superposition(content):
    # Fix broken math block
    content = content.replace("[\n  x(t) \\neq", "$$\n  x(t) \\neq")

    # Fix stray commas and single backslashes
    replacements = [
        (r"m,\\dot v", r"m \\dot v"),
        (r"m,g\^B", r"m g^B"),
        (r"R,\\widehat{\\omega}\^B", r"R \\widehat{\\omega}^B"),
        (r"I,\\ddot q", r"I \\ddot q"),
        (r"M\(q\),\\ddot q", r"M(q) \\ddot q"),
        (r"C\(q,\\dot q\),V", r"C(q,\\dot q) V"),
        (r"L\(q,\\dot q\),u", r"L(q,\\dot q) u"),
        (r"L\(q,\\dot q\),\\tau", r"L(q,\\dot q) \\tau"),
        (r"\\mathcal\{M\}\(q\),\\dot V", r"\\mathcal{M}(q) \\dot V"),
        (r"\\mathcal\{C\}\(q,\\dot q\),V", r"\\mathcal{C}(q,\\dot q) V"),
        (r"u_i ,\\bar f\^\{\(i\)\}", r"u_i \\bar f^{(i)}"),
        (r"u_i, \\bar Q\^\{\(i\)\}", r"u_i \\bar Q^{(i)}"),
        # Fix align environment newlines: ` \` -> ` \\`
        (r" \\(\n)", r" \\\\\1"),
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    return content

def fix_units_wrist(content):
    # We want to replace "X kg·m²" with "$X \text{ kg}\cdot\text{m}^2$"
    # Regex: (\d+(?:-\d+(?:\.\d+)?)?) -> Captures numbers like "0.004-0.006" or "5" or "0.005"
    # Actually just match the number preceding the unit.

    # Pattern 1: kg·m²
    # Capture the number before it.

    def repl_kgm2(m):
        return f"${m.group(1)} \\text{{ kg}}\\cdot\\text{{m}}^2$"

    # Matches "0.004-0.006 kg·m²" or "0.005 kg·m^2"
    content = re.sub(r"([0-9\.\-]+) kg·m²", repl_kgm2, content)
    content = re.sub(r"([0-9\.\-]+) kg·m\^2", repl_kgm2, content)

    # Pattern 2: N·m
    def repl_nm(m):
        return f"${m.group(1)} \\text{{ N}}\\cdot\\text{{m}}$"

    content = re.sub(r"([0-9\.\-]+) N·m", repl_nm, content)

    return content

def fix_theory_part5(content):
    # Fix Note on parameter validity
    if "**Note on parameter validity.**" in content:
        content = content.replace(
            "**Note on parameter validity.**\nThe stiffness",
            "::: {.callout-note}\n## Note on parameter validity\nThe stiffness"
        )
        end_marker = 'Plant" for the swing.'
        if end_marker in content:
            content = content.replace(end_marker, end_marker + "\n:::")
        else:
            # Fallback for case sensitivity issue observed in review
            end_marker_effective = 'Effective Plant" for the swing.'
            if end_marker_effective in content:
                content = content.replace(end_marker_effective, end_marker_effective + "\n:::")
    return content

def main():
    files = [f for f in os.listdir("articles") if f.endswith(".qmd") or f.endswith(".md")]

    for f in files:
        path = os.path.join("articles", f)
        with open(path, "r") as fl:
            content = fl.read()

        original_content = content

        # Specific fixes
        if f == "superposition.qmd":
            content = fix_superposition(content)
        elif f == "wrist-universal-joint.qmd":
            content = fix_units_wrist(content)
        elif f == "theory-part5.qmd":
            content = fix_theory_part5(content)

        if content != original_content:
            print(f"Fixing {f}")
            with open(path, "w") as fl:
                fl.write(content)

if __name__ == "__main__":
    main()
