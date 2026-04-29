# Bibliography & PR Quick Reference
## The Geometry of Motion - Scientific Rigor Audit

**Last Updated**: 2026-03-27

---

## Files Created
1. **PR_INSTRUCTIONS.md** - Complete PR workflow and git commands
2. **BIBLIOGRAPHY_AUDIT_REPORT.md** - Detailed findings and analysis
3. **QUICK_REFERENCE.md** - This file

---

## Critical Fixes Needed (Do These First)

### 1. Add Missing Bibliography Entries (7 keys)
Add these to `geometry_of_motion.bib`:

```bibtex
@book{Arnold1989,
  title={Mathematical Methods of Classical Mechanics},
  author={Arnold, V. I.},
  edition={2nd},
  year={1989},
  publisher={Springer-Verlag}
}

@book{Bellman1961,
  title={Adaptive Control Processes: A Guided Tour},
  author={Bellman, R. E.},
  year={1961},
  publisher={Princeton University Press}
}

@article{Featherstone1983,
  title={The calculation of robot dynamics using articulated-body inertias},
  author={Featherstone, R.},
  journal={The International Journal of Robotics Research},
  volume={2},
  number={1},
  pages={13--30},
  year={1983}
}

@article{Flash1985,
  title={The coordination of arm movements: an experimentally confirmed mathematical model},
  author={Flash, T. and Hogan, N.},
  journal={The Journal of Neuroscience},
  volume={5},
  number={7},
  pages={1688--1703},
  year={1985}
}

@book{Goldstein2002,
  title={Classical Mechanics},
  author={Goldstein, H. and Poole, C. and Safko, J.},
  edition={3rd},
  year={2002},
  publisher={Addison Wesley}
}

@book{Lynch2017,
  title={Modern Robotics: Mechanics, Planning, and Control},
  author={Lynch, K. M. and Park, F. C.},
  year={2017},
  publisher={Cambridge University Press}
}

@book{Westervelt2007,
  title={Feedback Control of Dynamic Bipedal Robot Locomotion},
  author={Westervelt, E. R. and Grizzle, J. W. and Chevallereau, C. and Choi, J. H. and Morris, B.},
  year={2007},
  publisher={CRC Press}
}
```

### 2. Fix [CITE:] Placeholders (6 locations)

Replace these in chapter files:

| File | Line | Replace | With |
|------|------|---------|------|
| Volume_I/chapters/ch02_variational.tex | 334 | `[CITE: Peano-Baker history...]` | `\cite{Magnus1954}` |
| Volume_II/chapters/ch05_underactuation...tex | 22 | `[CITE: empirical golf swing...]` | `\cite{Zheng2008}` |
| Volume_II/chapters/ch09_stochastic...tex | 18 | `[CITE: Henneman motor unit...]` | `\cite{Henneman1957}` |
| Volume_II/chapters/ch09_stochastic...tex | 18 | `[CITE: signal-dependent noise...]` | `\cite{Harris1998}` |
| Volume_II/chapters/ch09_stochastic...tex | 36 | `[CITE: Harris and Wolpert...]` | `\cite{Harris1998}` |
| Volume_II/chapters/ch09_stochastic...tex | 92 | `[CITE: Fitts 1954...]` | `\cite{Fitts1954}` |
| Volume_IV/chapters/ch01_dof_problem.tex | 15 | `[CITE: Bernstein1967]` | `\cite{Bernstein1967}` |

---

## Verification Checklist

- [ ] Read BIBLIOGRAPHY_AUDIT_REPORT.md
- [ ] Add 7 missing bibliography entries to geometry_of_motion.bib
- [ ] Convert 6 [CITE:] placeholders to \cite{} commands
- [ ] Run validation script below
- [ ] Compile each volume
- [ ] Follow PR_INSTRUCTIONS.md for git workflow

---

## Quick Commands

### 1. Check for [CITE:] Markers (should be empty)
```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion
grep -rn '\[CITE:' --include="*.tex"
```

### 2. Validate Bibliography Consistency
```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion

# Extract citation keys from chapters
grep -rho '\(cite\|citep\|citet\){[^}]*}' --include="*.tex" \
  | grep -o '{[^}]*}' | tr -d '{}' | tr ',' '\n' \
  | sed 's/^[ \t]*//;s/[ \t]*$//' | sort -u > /tmp/citation_keys.txt

# Extract bibliography keys
grep "^@" geometry_of_motion.bib | grep -o '{[^,]*' | tr -d '{' | sort -u > /tmp/bib_keys.txt

# Check for missing entries (should return nothing)
echo "=== Missing Bibliography Entries ==="
comm -23 /tmp/citation_keys.txt /tmp/bib_keys.txt

# Check for unused entries
echo "=== Unused Bibliography Entries ==="
comm -13 /tmp/citation_keys.txt /tmp/bib_keys.txt | head -20
```

### 3. Compile Volume (example: Volume_0)
```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_0
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex
```

### 4. Start PR Process (Read PR_INSTRUCTIONS.md for full details)
```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift

# Create branch
git checkout main
git pull origin main
git checkout -b textbook/gom-scientific-rigor-audit

# Stage changes
git add articles/The_Geometry_of_Motion/

# Commit
git commit -m "refactor: The Geometry of Motion scientific rigor audit

- Added 60+ bibliography entries
- Resolved 6 [CITE:] placeholders
- Added ~55 TikZ diagrams
- Enhanced pedagogical clarity"

# Push and create PR
git push -u origin textbook/gom-scientific-rigor-audit
gh pr create --title "refactor: The Geometry of Motion scientific rigor audit" \
  --body "See articles/The_Geometry_of_Motion/PR_INSTRUCTIONS.md for details"
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total Chapters | 77 |
| Total Volumes | 6 |
| Bibliography Entries | 114 |
| Unique Citation Keys | 84 |
| Missing Entries | 7 (CRITICAL) |
| [CITE:] Placeholders | 6 (CRITICAL) |
| Files Modified | 136 |
| TikZ Diagrams Added | ~55 |
| New Bibliography Entries | 60+ |
| Citation Consistency | 88.1% |

---

## File Locations

```
Repository Root:
/sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/

Textbook Directory:
/articles/The_Geometry_of_Motion/

Bibliography File:
geometry_of_motion.bib

Chapter Directories:
Volume_0/chapters/
Volume_I/chapters/
Volume_II/chapters/
Volume_III/chapters/
Volume_IV/chapters/
Volume_V/chapters/
```

---

## References

1. **PR_INSTRUCTIONS.md** - Complete workflow with all git commands
2. **BIBLIOGRAPHY_AUDIT_REPORT.md** - Detailed analysis and recommendations
3. **geometry_of_motion.bib** - Main bibliography file (update with 7 entries)

---

## Support

For detailed instructions, see:
- Git workflow: PR_INSTRUCTIONS.md
- Audit findings: BIBLIOGRAPHY_AUDIT_REPORT.md
- Compilation help: PR_INSTRUCTIONS.md (Verification Steps section)

**Status**: Ready for fixes and PR submission
