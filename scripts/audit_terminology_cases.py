#!/usr/bin/env python3
"""Enumerate concrete remediation sites for each AffineDrift terminology conflict.

Read-only reporting tool for docs/development/terminology-decision-record.md.
Not a CI gate: it counts and locates, it does not pass or fail.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROOTS = ["articles", "books", "pages", "resources", "models", "repositories"]
EXTS = {".qmd", ".tex"}
SKIP = ("docs/", "node_modules/", "Drafts_Original_Articles/", "articles/motion-control/")

QUALIFIERS = ("pointwise", "forward", "branched", "stitched", "trajectory")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)


def files() -> list[Path]:
    out: list[Path] = []
    for r in ROOTS:
        for p in sorted((ROOT / r).rglob("*")):
            rel = str(p.relative_to(ROOT))
            if p.suffix in EXTS and not any(s in rel for s in SKIP):
                out.append(p)
    for name in ("index.qmd", "NOTATION.md"):
        if (ROOT / name).exists():
            out.append(ROOT / name)
    return out


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def scan() -> None:
    bare_ztcf: Counter[str] = Counter()
    qual_ztcf: Counter[str] = Counter()
    zvcf: Counter[str] = Counter()
    dcr_variants: dict[str, list[str]] = defaultdict(list)
    gx: Counter[str] = Counter()
    gx_lower: Counter[str] = Counter()
    no_muscle: list[str] = []
    drift_inventory: list[str] = []
    traj_super: list[str] = []

    dcr_pats = {
        "Drift-Control Ratio (canonical)": re.compile(r"Drift[–—-]Control Ratio", re.I),
        "Drift-to-Control Ratio": re.compile(r"Drift[-\s]to[-\s]Control Ratio", re.I),
        "Drift coefficient ratio": re.compile(r"Drift coefficient ratio", re.I),
    }
    no_muscle_pat = re.compile(
        r"(no[- ]muscle|purely passive|all muscle torques (?:are |were )?set to zero|"
        r"muscles produce no torque|without any muscle)",
        re.I,
    )
    drift_pat = re.compile(
        r"drift.{0,80}(passive joint|joint impedance|shaft (?:stiffness|damping)|"
        r"structural impedance|constraint force)",
        re.I,
    )
    traj_pat = re.compile(
        r"(total motion.{0,40}=.{0,40}(ztcf|passive|drift)|"
        r"(ztcf|drift).{0,25}\+.{0,25}control correction)",
        re.I,
    )

    for p in files():
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body = FENCE.sub("", raw)
        r = rel(p)

        for i, line in enumerate(body.splitlines(), 1):
            low = line.lower()
            for m in re.finditer(r"\bZTCF\b", line):
                before = low[max(0, m.start() - 22) : m.start()]
                if any(q in before for q in QUALIFIERS):
                    qual_ztcf[r] += 1
                else:
                    bare_ztcf[r] += 1
            if re.search(r"\bZVCF\b", line):
                zvcf[r] += len(re.findall(r"\bZVCF\b", line))
            for name, pat in dcr_pats.items():
                if pat.search(line):
                    dcr_variants[name].append(f"{r}:{i}")
            gx[r] += len(re.findall(r"\bG\(\\?[qx]\)", line))
            gx_lower[r] += len(re.findall(r"\bg\(\\?[qx]\)", line))
            if no_muscle_pat.search(line) and ("ztcf" in low or "counterfactual" in low):
                no_muscle.append(f"{r}:{i}")
            if drift_pat.search(line):
                drift_inventory.append(f"{r}:{i}")
            if traj_pat.search(line):
                traj_super.append(f"{r}:{i}")

    def block(title: str, counter: Counter[str], top: int = 25) -> None:
        total = sum(counter.values())
        print(f"\n## {title} — {total} occurrences across {len(counter)} files")
        for f, n in counter.most_common(top):
            print(f"  {n:5d}  {f}")
        if len(counter) > top:
            print(f"  ... and {len(counter) - top} more files")

    block("BARE ZTCF (no qualifier within 22 chars before)", bare_ztcf)
    block("QUALIFIED ZTCF", qual_ztcf, top=15)
    block("ZVCF", zvcf, top=15)

    print("\n## DCR EXPANSION VARIANTS")
    for name, hits in dcr_variants.items():
        print(f"\n  {name}: {len(hits)}")
        for h in hits[:12]:
            print(f"    {h}")
        if len(hits) > 12:
            print(f"    ... and {len(hits) - 12} more")

    print("\n## INPUT-MATRIX SYMBOL")
    gx = Counter({k: v for k, v in gx.items() if v})
    gx_lower = Counter({k: v for k, v in gx_lower.items() if v})
    print(f"  G(x)/G(q): {sum(gx.values())} across {len(gx)} files")
    print(f"  g(x)/g(q): {sum(gx_lower.values())} across {len(gx_lower)} files")
    gx = Counter({k: v for k, v in gx.items() if v})
    gx_lower = Counter({k: v for k, v in gx_lower.items() if v})
    both = sorted(set(gx) & set(gx_lower))
    print(f"  files using BOTH forms: {len(both)}")
    for f in both[:20]:
        print(f"    {f}  (G:{gx[f]} g:{gx_lower[f]})")

    for title, hits in (
        ("NO-MUSCLE / PURELY-PASSIVE CLAIMS NEAR ZTCF", no_muscle),
        ("DRIFT-INVENTORY STATEMENTS (impedance / shaft / constraint)", drift_inventory),
        ("TRAJECTORY-SUPERPOSITION IDENTITY PATTERN", traj_super),
    ):
        print(f"\n## {title} — {len(hits)}")
        for h in hits[:30]:
            print(f"  {h}")
        if len(hits) > 30:
            print(f"  ... and {len(hits) - 30} more")


if __name__ == "__main__":
    scan()
