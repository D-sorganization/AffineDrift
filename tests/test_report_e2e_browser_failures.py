"""Contracts for turning nightly cross-browser Playwright failures into issues."""

from scripts.report_e2e_browser_failures import (
    build_issue_body,
    build_issue_title,
    iter_failed_specs,
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
