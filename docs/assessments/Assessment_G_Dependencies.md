# Assessment: Dependencies

## Grade: 7.5/10

## Details

- `requirements.txt` is present; 18 of 22 dependencies are pinned.
- `package.json` is present for JavaScript dependencies.
- CI quality gate installs from `requirements.txt` and uses `pip install`.
- Supply-chain scanning (`pip-audit`) is not configured, so known vulnerabilities in pinned packages may go undetected.
- 4 unpinned dependencies in `requirements.txt` could introduce unexpected breakage on fresh installs.

## Contradiction Note

The previous grade of 10.0/10 was inconsistent: having unpinned dependencies and no vulnerability scanning is not a perfect score. The recommendation to "pin dependencies" also contradicts the claimed 10/10 if pinning was incomplete.

## Recommendations

- Pin all remaining 4 unpinned dependencies in `requirements.txt`.
- Add `pip-audit` to the CI quality gate to detect known vulnerabilities.
- Consider using `pip-compile` (via `pip-tools`) to generate fully-pinned lockfiles from loose constraints.
