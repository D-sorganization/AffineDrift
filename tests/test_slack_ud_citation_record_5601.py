"""Guard the UpstreamDrift citation record for the two Slack articles (Refs #5601).

The record ``docs/development/technical-review/ud-citation-verification-5601-slack.md``
states that every UpstreamDrift permalink in the Slack articles was checked against
its pinned commit. This test fails if an article gains, drops or re-pins a permalink
without the record being updated, so the claim cannot silently go stale.
"""

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/development/technical-review/ud-citation-verification-5601-slack.md"
MANAGEMENT = ROOT / "articles/slack-management-linked-systems.qmd"
TAKEUP = ROOT / "articles/slack-takeup-identifiability.qmd"
ARTICLES = (MANAGEMENT, TAKEUP)

# Loose on purpose: capture *every* UpstreamDrift URL, whatever its ref, so a
# shortened SHA or a branch name cannot drop out of the inventory unnoticed.
ANY_UD_URL = re.compile(r"github\.com/D-sorganization/UpstreamDrift[^)\s\"'>]*")
# Strict: the only accepted shape is blob|tree + 40-hex commit + path (+ anchor).
PINNED_UD_URL = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:blob|tree)/([0-9a-f]{40})/([^#\s]+)(?:#\S+)?"
)

_UD = "github.com/D-sorganization/UpstreamDrift"
_PIN_NEW = "3fd2a59e390523169df846a3bbb395a6203c382c"
_PIN_OLD = "92100115ea0be0d6744dcf7a4504ec8453fae6fa"
_RESEARCH = "docs/research"
_LOOP = f"{_RESEARCH}/loop_nullspace"
_PDET = f"{_RESEARCH}/proximal_distal_energy_transfer"


def _u(pin: str, path: str, kind: str = "blob") -> str:
    return f"{_UD}/{kind}/{pin}/{path}"


# Verified inventory: (article, full permalink incl. anchor), one entry per
# occurrence. Change an article link only together with this list AND the record.
EXPECTED: tuple[tuple[str, str], ...] = (
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_LOOP}/publication_gate.md#scope-and-current-status")),
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_LOOP}/closure_alternatives_report.md#summary-of-findings")),
    (MANAGEMENT.name, _u(_PIN_OLD, f"{_PDET}/data/typed_slack_dynamic_study.json")),
    (MANAGEMENT.name, _u(_PIN_OLD, f"{_PDET}/data/typed_slack_dynamic_study.json")),
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_PDET}/MODEL_COMPLETION_FALSIFICATION_MATRIX.md")),
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_PDET}/data/articulated_distributed_grip_atlas.json")),
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_LOOP}/closure_alternatives_report.md")),
    (MANAGEMENT.name, _u(_PIN_NEW, f"{_LOOP}/loop_nullspace.tex")),
    (TAKEUP.name, _u(_PIN_NEW, f"{_LOOP}/loop_nullspace.tex#L524")),
    (TAKEUP.name, _u(_PIN_NEW, f"{_LOOP}/publication_gate.md#L279")),
    (TAKEUP.name, _u(_PIN_NEW, _RESEARCH, "tree")),
)


def extract_ud_urls(text: str) -> list[str]:
    """Return every UpstreamDrift URL in *text* in document order."""
    return ANY_UD_URL.findall(text)


def unpinned_urls(urls: list[str]) -> list[str]:
    """Return URLs that are not a blob/tree permalink with a full 40-hex pin."""
    return [u for u in urls if not PINNED_UD_URL.fullmatch(u)]


def inventory_diff(
    actual: list[tuple[str, str]], expected: tuple[tuple[str, str], ...] = EXPECTED
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (unexpected, missing) occurrences as multiset differences."""
    a, e = Counter(actual), Counter(expected)
    return sorted((a - e).elements()), sorted((e - a).elements())


def _actual_inventory() -> list[tuple[str, str]]:
    return [
        (article.name, url)
        for article in ARTICLES
        for url in extract_ud_urls(article.read_text(encoding="utf-8"))
    ]


def test_record_exists() -> None:
    assert RECORD.is_file()


def test_every_article_url_has_a_full_commit_pin() -> None:
    bad = unpinned_urls([url for _, url in _actual_inventory()])
    assert not bad, f"UpstreamDrift URLs without a 40-hex commit pin: {bad}"


def test_article_citations_match_verified_inventory_exactly() -> None:
    unexpected, missing = inventory_diff(_actual_inventory())
    assert not unexpected, f"citations not in the verified inventory: {unexpected}"
    assert not missing, f"verified citations no longer in the articles: {missing}"


def test_every_verified_citation_is_recorded_with_its_pin_and_path() -> None:
    record = RECORD.read_text(encoding="utf-8")
    for _, url in EXPECTED:
        match = PINNED_UD_URL.fullmatch(url)
        assert match, url
        sha, path = match.groups()
        assert sha[:8] in record, f"pin {sha[:8]} missing from record"
        assert path in record, f"path {path} missing from record"


def test_record_documents_the_var05_discrepancy() -> None:
    record = RECORD.read_text(encoding="utf-8")
    assert "VAR-05" in record
    assert "Impedance is declared, not measured" in record


# --- Negative tests: prove the guard fails on each drift the review named. ---


def _mutated(mutate) -> list[tuple[str, str]]:
    return mutate(list(EXPECTED))


def test_guard_passes_on_unmutated_inventory() -> None:
    assert inventory_diff(list(EXPECTED)) == ([], [])


def test_guard_fails_when_a_citation_is_removed() -> None:
    unexpected, missing = inventory_diff(_mutated(lambda a: a[:-1]))
    assert missing == [EXPECTED[-1]] and not unexpected


def test_guard_fails_when_one_of_two_duplicate_citations_is_removed() -> None:
    dup = EXPECTED[2]
    actual = list(EXPECTED)
    actual.remove(dup)
    assert inventory_diff(actual) == ([], [dup])


def test_guard_fails_when_a_citation_is_added() -> None:
    extra = (TAKEUP.name, _u(_PIN_NEW, f"{_LOOP}/new_file.md"))
    unexpected, missing = inventory_diff(_mutated(lambda a: [*a, extra]))
    assert unexpected == [extra] and not missing


def test_guard_fails_when_an_anchor_changes() -> None:
    idx = next(i for i, (_, u) in enumerate(EXPECTED) if u.endswith("#L524"))

    def change(a: list[tuple[str, str]]) -> list[tuple[str, str]]:
        a[idx] = (a[idx][0], a[idx][1].replace("#L524", "#L525"))
        return a

    unexpected, missing = inventory_diff(_mutated(change))
    assert len(unexpected) == 1 and len(missing) == 1


def test_guard_fails_when_an_anchor_is_dropped() -> None:
    idx = next(i for i, (_, u) in enumerate(EXPECTED) if u.endswith("#L279"))

    def drop(a: list[tuple[str, str]]) -> list[tuple[str, str]]:
        a[idx] = (a[idx][0], a[idx][1].split("#")[0])
        return a

    assert inventory_diff(_mutated(drop)) != ([], [])


def test_guard_fails_when_a_pin_is_swapped_to_another_full_sha() -> None:
    def repin(a: list[tuple[str, str]]) -> list[tuple[str, str]]:
        a[0] = (a[0][0], a[0][1].replace(_PIN_NEW, _PIN_OLD))
        return a

    unexpected, missing = inventory_diff(_mutated(repin))
    assert len(unexpected) == 1 and len(missing) == 1


def test_shortened_pin_is_detected_not_silently_ignored() -> None:
    text = f"[x](https://{_UD}/blob/{_PIN_NEW[:8]}/{_LOOP}/publication_gate.md)"
    urls = extract_ud_urls(text)
    assert len(urls) == 1, "short-SHA link must still be extracted"
    assert unpinned_urls(urls) == urls


def test_branch_ref_is_detected_as_unpinned() -> None:
    for ref in ("main", "master", "HEAD"):
        urls = extract_ud_urls(f"https://{_UD}/blob/{ref}/README.md")
        assert unpinned_urls(urls) == urls


def test_uppercase_or_overlong_pin_is_unpinned() -> None:
    for pin in (_PIN_NEW.upper(), _PIN_NEW + "0"):
        urls = extract_ud_urls(f"https://{_UD}/blob/{pin}/README.md")
        assert unpinned_urls(urls) == urls


def test_full_pin_with_anchor_is_accepted() -> None:
    urls = extract_ud_urls(f"(https://{_UD}/blob/{_PIN_NEW}/a/b.md#L9)")
    assert urls and unpinned_urls(urls) == []
