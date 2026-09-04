from __future__ import annotations

import pytest

from overleaf_mcp.errors import MergeConflictError
from tests.conftest import read_remote_file


@pytest.fixture
def project(service):
    service.add_project("project.git", "paper")
    return service


def test_read_pulls_remote_changes(project, other_clone):
    other_clone("main.tex", "Edited in the web editor.\n")
    assert project.read_file("paper", "main.tex") == "Edited in the web editor.\n"


def test_sync_project_pulls_remote_changes(project, other_clone):
    other_clone("notes.tex", "Remote note.\n")
    project.sync_project("paper")
    assert "notes.tex" in project.list_files("paper")


def test_edit_merges_nonconflicting_remote_change(project, other_clone, fake_overleaf):
    # Remote adds a new file; local edits a different file. Should merge cleanly.
    other_clone("refs.bib", "@book{x, title={X}}\n")
    project.edit_file("paper", "main.tex", "Local change.\n")
    assert read_remote_file(fake_overleaf, "main.tex") == "Local change.\n"
    assert read_remote_file(fake_overleaf, "refs.bib") == "@book{x, title={X}}\n"


def test_edit_aborts_cleanly_on_divergent_conflict(project, other_clone, fake_overleaf):
    # Simulate a local clone that diverged in a prior session: an un-pushed local
    # commit touching a line that Overleaf then also changed.
    repo = project._ws.project_dir("paper")
    (repo / "main.tex").write_text("Local wins.\n", encoding="utf-8")
    project._git.run(["commit", "-am", "local"], cwd=repo)
    other_clone("main.tex", "Remote wins.\n")

    with pytest.raises(MergeConflictError):
        project.edit_file("paper", "main.tex", "Third version.\n")

    # Remote untouched, local edit not applied, tree not left half-merged.
    assert read_remote_file(fake_overleaf, "main.tex") == "Remote wins.\n"
    assert project._git.conflicted_files(repo) == []
    assert (repo / "main.tex").read_text() == "Local wins.\n"
