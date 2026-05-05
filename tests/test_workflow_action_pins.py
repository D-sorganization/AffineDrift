from scripts.check_workflow_action_pins import find_unpinned_actions


def test_find_unpinned_actions_flags_tag_refs(tmp_path):
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        "steps:\n"
        "  - uses: actions/checkout@v4\n"
        "  - uses: actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830\n",
        encoding="utf-8",
    )

    findings = find_unpinned_actions(workflow_dir)

    assert findings == [f"{workflow_dir / 'ci.yml'}:2: pin actions/checkout@v4 to a 40-char SHA"]


def test_find_unpinned_actions_allows_local_and_docker_refs(tmp_path):
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        "steps:\n" "  - uses: ./actions/local\n" "  - uses: docker://alpine:3.20\n",
        encoding="utf-8",
    )

    assert find_unpinned_actions(workflow_dir) == []
