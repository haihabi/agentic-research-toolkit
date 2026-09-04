from __future__ import annotations

import shutil

import pytest

from overleaf_mcp.errors import CompileError

pytestmark = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk not installed on host"
)


@pytest.fixture
def project(service):
    service.add_project("project.git", "paper")
    return service


def test_compile_seed_project_succeeds(project):
    result = project.compile_project("paper")
    assert result["success"] is True
    assert result["root_file"] == "main.tex"
    assert result["engine"] == "pdflatex"
    assert result["pdf_path"] and result["pdf_path"].endswith("main.pdf")
    assert result["errors"] == []


def test_compile_output_is_not_pushed(project, fake_overleaf):
    project.compile_project("paper")
    # .build/ must be excluded — nothing new on the remote, no dirty tree
    assert project.list_files("paper") == ["main.tex"]
    status = project._git.run(
        ["status", "--porcelain"], cwd=project._ws.project_dir("paper")
    ).stdout
    assert status.strip() == ""


def test_compile_reports_latex_errors(project):
    project.edit_file("paper", "main.tex", "\\documentclass{article}\n\\begin{document}\n\\undefinedmacro\n\\end{document}\n")
    result = project.compile_project("paper")
    assert result["success"] is False
    assert any("undefinedmacro" in e.lower() or "Undefined control sequence" in e for e in result["errors"]) or result["log_tail"]


def test_compile_bad_root_file_rejected(project):
    with pytest.raises(CompileError):
        project.compile_project("paper", root_file="nonexistent.tex")
