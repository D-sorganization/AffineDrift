"""Contracts for turning nightly cross-browser Playwright failures into issues."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import scripts.report_e2e_browser_failures as report_e2e_browser_failures
from scripts.report_e2e_browser_failures import (
    ISSUE_LABELS,
    ISSUE_TITLE_PREFIX,
    MAX_INDIVIDUAL_ISSUES,
    MISSING_REPORT_TITLE,
    build_issue_body,
    build_issue_title,
    build_summary_issue_body,
    build_summary_issue_title,
    create_issue,
    derive_project_from_report_path,
    fetch_existing_open_titles,
    filter_cross_browser_titles,
    iter_failed_specs,
    load_report_failures,
    main,
    missing_report_failure,
    select_new_failures,
)


def _report(*, suites: list[dict]) -> dict:
    return {"suites": suites}


def _spec(title: str, *, project: str, status: str) -> dict:
    return {
        "title": title,
        "tests": [{"projectName": project, "status": status}],
    }


class TestIterFailedSpecs:
    def test_yields_only_unexpected_status(self):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [
                        _spec("homepage renders", project="firefox", status="unexpected"),
                        _spec("about page renders", project="firefox", status="expected"),
                    ],
                }
            ]
        )

        failures = list(iter_failed_specs(report))

        assert failures == [
            {"title": "homepage renders", "project": "firefox", "file": "tests/e2e/smoke.spec.js"}
        ]

    def test_skips_flaky_and_skipped(self):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [
                        _spec("a", project="webkit", status="flaky"),
                        _spec("b", project="webkit", status="skipped"),
                    ],
                }
            ]
        )

        assert list(iter_failed_specs(report)) == []

    def test_recurses_into_nested_describe_suites(self):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [],
                    "suites": [
                        {
                            "specs": [
                                _spec(
                                    "nested behavioral test",
                                    project="webkit",
                                    status="unexpected",
                                ),
                            ],
                        }
                    ],
                }
            ]
        )

        failures = list(iter_failed_specs(report))

        assert failures == [
            {
                "title": "nested behavioral test",
                "project": "webkit",
                "file": "tests/e2e/smoke.spec.js",
            }
        ]

    def test_empty_report_yields_nothing(self):
        assert list(iter_failed_specs(_report(suites=[]))) == []


class TestBuildIssueTitle:
    def test_includes_project_and_spec_title(self):
        title = build_issue_title("firefox", "homepage renders and has core structure")

        assert title == ("[Cross-Browser Nightly] firefox: homepage renders and has core structure")

    def test_same_inputs_always_produce_the_same_title(self):
        # This is the dedup key, so it must be pure and stable.
        assert build_issue_title("webkit", "x") == build_issue_title("webkit", "x")


class TestBuildIssueBody:
    def test_includes_test_file_and_run_link(self):
        failure = {
            "title": "homepage renders",
            "project": "firefox",
            "file": "tests/e2e/smoke.spec.js",
        }

        body = build_issue_body(failure, "https://github.com/example/run/1")

        assert "firefox" in body
        assert "homepage renders" in body
        assert "tests/e2e/smoke.spec.js" in body
        assert "https://github.com/example/run/1" in body


class TestSelectNewFailures:
    def test_drops_failures_already_covered_by_an_open_issue(self):
        failures = [{"title": "homepage renders", "project": "firefox", "file": "f.js"}]
        existing_titles = ["[Cross-Browser Nightly] firefox: homepage renders"]

        assert select_new_failures(failures, existing_titles) == []

    def test_keeps_failures_with_no_matching_open_issue(self):
        failures = [{"title": "homepage renders", "project": "firefox", "file": "f.js"}]

        assert select_new_failures(failures, []) == failures

    def test_deduplicates_repeated_failures_within_the_same_batch(self):
        # e.g. the same spec failing on retry appears twice in one report.
        failure = {"title": "homepage renders", "project": "firefox", "file": "f.js"}

        assert select_new_failures([failure, failure], []) == [failure]

    def test_does_not_cross_dedup_different_browsers(self):
        failures = [
            {"title": "homepage renders", "project": "firefox", "file": "f.js"},
            {"title": "homepage renders", "project": "webkit", "file": "f.js"},
        ]

        assert select_new_failures(failures, []) == failures


class TestIssueLabels:
    def test_only_uses_labels_that_already_exist_in_the_repo(self):
        # "cross-browser" does not exist in the repo and must never be created.
        assert ISSUE_LABELS == ("ci", "automation")


class TestFilterCrossBrowserTitles:
    def test_keeps_titles_starting_with_the_prefix(self):
        titles = [f"{ISSUE_TITLE_PREFIX} firefox: homepage renders", "unrelated issue"]

        assert filter_cross_browser_titles(titles) == [
            f"{ISSUE_TITLE_PREFIX} firefox: homepage renders"
        ]

    def test_drops_titles_that_merely_mention_the_prefix(self):
        titles = [f"Fix flaky test ({ISSUE_TITLE_PREFIX} firefox: x)"]

        assert filter_cross_browser_titles(titles) == []


class TestFetchExistingOpenTitles:
    def test_searches_by_title_instead_of_filtering_by_label(self):
        fake_result = SimpleNamespace(
            stdout=json.dumps(
                [
                    {"title": f"{ISSUE_TITLE_PREFIX} firefox: homepage renders"},
                    {"title": "unrelated issue"},
                ]
            )
        )

        with patch(
            "scripts.report_e2e_browser_failures.subprocess.run", return_value=fake_result
        ) as mock_run:
            titles = fetch_existing_open_titles("org/repo")

        args = mock_run.call_args.args[0]
        assert "--label" not in args
        assert "--search" in args
        search_value = args[args.index("--search") + 1]
        assert search_value == f'"{ISSUE_TITLE_PREFIX}" in:title'
        assert titles == [f"{ISSUE_TITLE_PREFIX} firefox: homepage renders"]


class TestCreateIssue:
    def test_only_applies_labels_that_already_exist(self):
        with patch("scripts.report_e2e_browser_failures.subprocess.run") as mock_run:
            create_issue("org/repo", "title", "body")

        args = mock_run.call_args.args[0]
        label_value = args[args.index("--label") + 1]
        assert label_value == "ci,automation"
        assert "cross-browser" not in label_value


class TestDeriveProjectFromReportPath:
    def test_extracts_browser_from_standard_filename(self):
        assert derive_project_from_report_path(Path("playwright-report-webkit.json")) == "webkit"

    def test_falls_back_to_stem_for_unexpected_filenames(self):
        assert derive_project_from_report_path(Path("weird-name.json")) == "weird-name"


class TestMissingReportFailure:
    def test_builds_a_synthetic_failure_entry(self):
        failure = missing_report_failure(Path("playwright-report-firefox.json"))

        assert failure == {
            "title": MISSING_REPORT_TITLE,
            "project": "firefox",
            "file": "playwright-report-firefox.json",
        }


class TestLoadReportFailures:
    def test_missing_file_yields_synthetic_failure(self, tmp_path):
        missing_path = tmp_path / "playwright-report-webkit.json"

        failures = load_report_failures(missing_path)

        assert failures == [missing_report_failure(missing_path)]

    def test_empty_file_yields_synthetic_failure(self, tmp_path):
        empty_path = tmp_path / "playwright-report-firefox.json"
        empty_path.write_text("", encoding="utf-8")

        failures = load_report_failures(empty_path)

        assert failures == [missing_report_failure(empty_path)]

    def test_unparseable_json_yields_synthetic_failure(self, tmp_path):
        bad_path = tmp_path / "playwright-report-webkit.json"
        bad_path.write_text("{not valid json", encoding="utf-8")

        failures = load_report_failures(bad_path)

        assert failures == [missing_report_failure(bad_path)]

    def test_valid_report_parses_normally(self, tmp_path):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [_spec("homepage renders", project="firefox", status="unexpected")],
                }
            ]
        )
        report_path = tmp_path / "playwright-report-firefox.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        failures = load_report_failures(report_path)

        assert failures == [
            {"title": "homepage renders", "project": "firefox", "file": "tests/e2e/smoke.spec.js"}
        ]


class TestBuildSummaryIssueTitle:
    def test_includes_count_and_date(self):
        title = build_summary_issue_title(6, "2026-10-01")

        assert title == f"{ISSUE_TITLE_PREFIX} 6 failures on 2026-10-01"


class TestBuildSummaryIssueBody:
    def test_lists_every_failure(self):
        failures = [
            {"title": "test a", "project": "firefox", "file": "a.js"},
            {"title": "test b", "project": "webkit", "file": "b.js"},
        ]

        body = build_summary_issue_body(failures, "https://example/run/1")

        assert "firefox" in body
        assert "test a" in body
        assert "a.js" in body
        assert "webkit" in body
        assert "test b" in body
        assert "b.js" in body
        assert "https://example/run/1" in body


class TestMainIssueCap:
    def test_opens_one_summary_issue_when_more_than_five_new_failures(self, tmp_path, monkeypatch):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [
                        _spec(f"test {i}", project="firefox", status="unexpected") for i in range(6)
                    ],
                }
            ]
        )
        report_path = tmp_path / "playwright-report-firefox.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        created = []
        monkeypatch.setattr(
            report_e2e_browser_failures, "fetch_existing_open_titles", lambda repo: []
        )
        monkeypatch.setattr(
            report_e2e_browser_failures,
            "create_issue",
            lambda repo, title, body: created.append((title, body)),
        )

        exit_code = main(
            [
                "--report",
                str(report_path),
                "--repo",
                "org/repo",
                "--run-url",
                "https://example/run/1",
            ]
        )

        assert exit_code == 0
        assert len(created) == 1
        title, body = created[0]
        assert title.startswith(f"{ISSUE_TITLE_PREFIX} 6 failures on ")
        for i in range(6):
            assert f"test {i}" in body

    def test_opens_one_issue_per_failure_when_five_or_fewer(self, tmp_path, monkeypatch):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [
                        _spec(f"test {i}", project="firefox", status="unexpected")
                        for i in range(MAX_INDIVIDUAL_ISSUES)
                    ],
                }
            ]
        )
        report_path = tmp_path / "playwright-report-firefox.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        created = []
        monkeypatch.setattr(
            report_e2e_browser_failures, "fetch_existing_open_titles", lambda repo: []
        )
        monkeypatch.setattr(
            report_e2e_browser_failures,
            "create_issue",
            lambda repo, title, body: created.append((title, body)),
        )

        main(
            [
                "--report",
                str(report_path),
                "--repo",
                "org/repo",
                "--run-url",
                "https://example/run/1",
            ]
        )

        assert len(created) == MAX_INDIVIDUAL_ISSUES

    def test_dry_run_prints_summary_without_creating(self, tmp_path, monkeypatch, capsys):
        report = _report(
            suites=[
                {
                    "file": "tests/e2e/smoke.spec.js",
                    "specs": [
                        _spec(f"test {i}", project="firefox", status="unexpected") for i in range(6)
                    ],
                }
            ]
        )
        report_path = tmp_path / "playwright-report-firefox.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        created = []
        monkeypatch.setattr(
            report_e2e_browser_failures, "fetch_existing_open_titles", lambda repo: []
        )
        monkeypatch.setattr(
            report_e2e_browser_failures,
            "create_issue",
            lambda repo, title, body: created.append((title, body)),
        )

        main(
            [
                "--report",
                str(report_path),
                "--repo",
                "org/repo",
                "--run-url",
                "https://example/run/1",
                "--dry-run",
            ]
        )

        assert created == []
        assert "Would create issue:" in capsys.readouterr().out


class TestMainMissingReport:
    def test_missing_report_file_is_filed_as_a_single_failure(self, tmp_path, monkeypatch):
        missing_path = tmp_path / "playwright-report-webkit.json"

        created = []
        monkeypatch.setattr(
            report_e2e_browser_failures, "fetch_existing_open_titles", lambda repo: []
        )
        monkeypatch.setattr(
            report_e2e_browser_failures,
            "create_issue",
            lambda repo, title, body: created.append((title, body)),
        )

        main(
            [
                "--report",
                str(missing_path),
                "--repo",
                "org/repo",
                "--run-url",
                "https://example/run/1",
            ]
        )

        assert len(created) == 1
        title, body = created[0]
        assert title == build_issue_title("webkit", MISSING_REPORT_TITLE)
        assert MISSING_REPORT_TITLE in body
