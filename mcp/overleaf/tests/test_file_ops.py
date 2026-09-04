from __future__ import annotations

import subprocess

import pytest

from overleaf_mcp.errors import OverleafMCPError, PathEscapeError
from tests.conftest import read_remote_file


@pytest.fixture
def project(service):
    service.add_project("project.git", "paper")
    return service


def test_add_and_list_projects(project):
    projects = project.list_projects()
    assert projects == [{"local_name": "paper", "overleaf_project_id": "project.git"}]


def test_add_project_twice_is_rejected(project):
    with pytest.raises(OverleafMCPError):
        project.add_project("project.git", "paper")


def test_list_files(project):
    assert project.list_files("paper") == ["main.tex"]


def test_read_file(project):
    assert "Hello world." in project.read_file("paper", "main.tex")


def test_add_file_pushes_to_remote(project, fake_overleaf):
    out = project.add_file("paper", "sections/intro.tex", "Intro.\n")
    assert "synced to Overleaf" in out
    assert read_remote_file(fake_overleaf, "sections/intro.tex") == "Intro.\n"
    assert "sections/intro.tex" in project.list_files("paper")


def test_edit_file_pushes_to_remote(project, fake_overleaf):
    project.edit_file("paper", "main.tex", "Changed.\n")
    assert read_remote_file(fake_overleaf, "main.tex") == "Changed.\n"


def test_edit_missing_file_is_rejected(project):
    with pytest.raises(OverleafMCPError):
        project.edit_file("paper", "nope.tex", "x")


def test_edit_no_op_reports_no_change(project):
    same = project.read_file("paper", "main.tex")
    assert project.edit_file("paper", "main.tex", same) == (
        "No change — the project already matches this content."
    )


def test_delete_file_pushes_to_remote(project, fake_overleaf):
    project.add_file("paper", "scratch.tex", "tmp\n")
    project.delete_file("paper", "scratch.tex")
    with pytest.raises(subprocess.CalledProcessError):
        read_remote_file(fake_overleaf, "scratch.tex")


def test_move_file_preserves_and_pushes(project, fake_overleaf):
    original = project.read_file("paper", "main.tex")
    project.move_file("paper", "main.tex", "paper.tex")
    assert read_remote_file(fake_overleaf, "paper.tex") == original
    assert "paper.tex" in project.list_files("paper")
    assert "main.tex" not in project.list_files("paper")


@pytest.mark.parametrize("bad", ["../escape.tex", "/etc/passwd", ".git/config", ".build/x"])
def test_path_escape_is_blocked(project, bad):
    with pytest.raises(PathEscapeError):
        project.read_file("paper", bad)
