from __future__ import annotations

import pytest

from overleaf_mcp.errors import OverleafMCPError
from tests.conftest import read_remote_file


@pytest.fixture
def project(service):
    service.add_project("project.git", "paper")
    return service


def test_get_conflicts_clean_reports_and_syncs(project, other_clone):
    other_clone("extra.tex", "extra\n")
    result = project.get_conflicts("paper")
    assert result == {"conflicted": False, "message": "No conflicts — in sync with Overleaf."}
    assert "extra.tex" in project.list_files("paper")


def test_get_conflicts_returns_three_way(project, other_clone):
    # Diverge: local edits main.tex without pushing, remote edits the same line.
    p = project._ws.project_dir("paper")
    (p / "main.tex").write_text("LOCAL VERSION\n", encoding="utf-8")
    project._git.run(["commit", "-am", "local edit"], cwd=p)

    other_clone("main.tex", "REMOTE VERSION\n")

    result = project.get_conflicts("paper")
    assert result["conflicted"] is True
    versions = result["files"]["main.tex"]
    assert versions["mine"] == "LOCAL VERSION\n"
    assert versions["theirs"] == "REMOTE VERSION\n"
    assert "Hello world." in versions["base"]
    # get_conflicts must not leave a half-merged tree
    assert (p / "main.tex").read_text() == "LOCAL VERSION\n"


def test_resolve_conflict_applies_and_pushes(project, other_clone, fake_overleaf):
    p = project._ws.project_dir("paper")
    (p / "main.tex").write_text("LOCAL VERSION\n", encoding="utf-8")
    project._git.run(["commit", "-am", "local edit"], cwd=p)
    other_clone("main.tex", "REMOTE VERSION\n")

    project.get_conflicts("paper")  # populate nothing, just confirm it conflicts
    out = project.resolve_conflict(
        "paper", {"main.tex": "MERGED: local + remote\n"}, message="resolve"
    )
    assert "synced to Overleaf" in out
    assert read_remote_file(fake_overleaf, "main.tex") == "MERGED: local + remote\n"


def test_resolve_conflict_missing_file_is_rejected(project, other_clone):
    p = project._ws.project_dir("paper")
    (p / "main.tex").write_text("LOCAL\n", encoding="utf-8")
    project._git.run(["commit", "-am", "local"], cwd=p)
    other_clone("main.tex", "REMOTE\n")

    with pytest.raises(OverleafMCPError):
        project.resolve_conflict("paper", {})  # nothing for main.tex
    # working tree not left half-merged
    assert project._git.conflicted_files(p) == []
