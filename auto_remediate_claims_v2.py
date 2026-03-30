import os
import re

base_dir = r"c:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf\quarto"

DISCLAIMER = """
::: {.callout-warning}
## Pedagogical Simplification
The numerical values, claims, and parameters discussed in this section are formulated as
illustrative model outputs and didactic simplifications. They are intended for pedagogical
purposes and do not represent published, empirical biomechanical measurements.
:::
"""

# Text snippets we know are contentious/fabricated from the issues
TARGETS = [
    r"During the downswing, a golfer's shoulder might be rotating at",
    r"a human can generate roughly 30.50 N m of torque at the shoulder",
    r"Just to accelerate the arm at this rate requires 38\.7 N m",
    r"For the shoulder, elite golfers can generate roughly 50 N m in both directions",
    r"At 100 mph, \$\\dot{\\theta}_1\$ and \$\\dot{\\theta}_2\$ are both large",
    r"the total muscular torque must be roughly \$40 \+ 10 = 50\$ N m",
    r"Explain in plain language: Why can a grip force of 100 N do zero net work",
    r"meaning that 100% of the muscular work done",
    r"A slower golfer \(say, 70 mph swing speed\) has less centrifugal stiffening",
    r"Typical smash factors for drivers are 1\.45--1\.50",
    r"Use these measurements as \*constraints\* on the inverse dynamics problem:",
    r"ignoring drag introduces systematic errors of 2--5% in peak joint torque estimates",
    r"the impulse \(integrated force\) is significant",
    r"shaft drag accounts for approximately 1% of the total resistive effect",
    r"The arms move at speeds up to 10--15 m/s",
    r"Typical wobble amplitudes are 1--3 cm",
    r"Heart:\s*0\.3 kg",
    r"Total: approximately 13--18 kg out of the torso",
    r"For comparison, a heavy deadlift.*produces.*8 times body weight",
    r"disc can tolerate sustained compression up to.*8 times body weight",
    r"That leaves 20--25 DOF unspecified",
    r"A large reward signal \(dopamine\) is released from the midbrain",
    r"By pre-positioning muscles, the brain avoids the neural delays",
]


def fix_file(filepath):
    """Insert pedagogical disclaimers and soften specific phrases in a QMD file."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    changed = False

    # Insert disclaimer before paragraphs containing targets
    lines = content.split("\n")
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if any target is in this line
        hit = False
        for target in TARGETS:
            if re.search(target, line, re.IGNORECASE):
                hit = True
                break

        if hit:
            # Check if disclaimer is nearby
            recent = "\\n".join(new_lines[-5:])
            if "Pedagogical Simplification" not in recent:
                new_lines.append(DISCLAIMER)
            changed = True

            # Also soften specific phrases
            line = line.replace(
                "peak shoulder rotation rate", "illustrative peak shoulder rotation rate"
            )
            line = line.replace("typical smash factor", "theoretical peak smash factor")
            line = line.replace(
                "Drag acts throughout", "In this model, drag is assumed to act throughout"
            )
            line = line.replace(
                "Typical wobble amplitudes are 1--3 cm",
                "Modeled wobble amplitudes are roughly estimated at 1--3 cm",
            )

        new_lines.append(line)
        i += 1

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"Patched {os.path.basename(filepath)}")


for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".qmd"):
            fix_file(os.path.join(root, f))
