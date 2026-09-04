"""Local PDF build via latexmk, run inside the project's clone.

Output goes to `<project>/.build/` which is git-excluded and never listed, so a
compile never pollutes what gets pushed back to Overleaf. This uses whatever TeX
distribution is on the host PATH; that can differ from Overleaf's, so a clean
build here is a strong signal but not a guarantee the Overleaf compile matches.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from pathlib import Path

from .errors import CompileError
from .workspace import BUILD_DIRNAME

_ENGINES = {
    "pdflatex": "-pdf",
    "xelatex": "-xelatex",
    "lualatex": "-lualatex",
}
_MAGIC_RE = re.compile(r"%\s*!TEX\s+program\s*=\s*([A-Za-z]+)", re.IGNORECASE)
_LINE_ERR_RE = re.compile(r"^.+?:\d+: .+")


def _iter_tex_files(repo: Path):
    for path in sorted(repo.rglob("*.tex")):
        parts = path.relative_to(repo).parts
        if ".git" in parts or BUILD_DIRNAME in parts:
            continue
        yield path


def detect_root(repo: Path) -> str:
    for preferred in ("main.tex", "paper.tex"):
        if (repo / preferred).is_file():
            return preferred
    candidates = [
        p.relative_to(repo).as_posix()
        for p in _iter_tex_files(repo)
        if "\\documentclass" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    if not candidates:
        raise CompileError(
            "No root .tex file found (none contain \\documentclass). "
            "Pass root_file explicitly."
        )
    if len(candidates) > 1:
        raise CompileError(
            f"Multiple candidate root files: {', '.join(candidates)}. "
            "Pass root_file explicitly."
        )
    return candidates[0]


def detect_engine(repo: Path, root_file: str) -> str:
    text = (repo / root_file).read_text(encoding="utf-8", errors="ignore")
    match = _MAGIC_RE.search(text)
    if match and match.group(1).lower() in _ENGINES:
        return match.group(1).lower()
    return "pdflatex"


def _parse_errors(log_text: str) -> list[str]:
    errors: list[str] = []
    for raw in log_text.splitlines():
        line = raw.rstrip()
        if (line.startswith("! ") or _LINE_ERR_RE.match(line)) and line not in errors:
            errors.append(line)
    return errors[:50]


def compile_project(
    repo: Path,
    root_file: str | None,
    engine: str | None,
    timeout: int,
) -> dict:
    if shutil.which("latexmk") is None:
        raise CompileError(
            "latexmk not found on PATH. Install a TeX distribution (TeX Live, "
            "MacTeX, MiKTeX) that provides latexmk."
        )

    root = root_file or detect_root(repo)
    if not (repo / root).is_file():
        raise CompileError(f"root_file '{root}' not found in project.")

    eng = (engine or detect_engine(repo, root)).lower()
    if eng not in _ENGINES:
        raise CompileError(
            f"Unsupported engine '{eng}'. Choose one of: {', '.join(sorted(_ENGINES))}."
        )

    build = repo / BUILD_DIRNAME
    build.mkdir(exist_ok=True)
    cmd = [
        "latexmk",
        _ENGINES[eng],
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-outdir={BUILD_DIRNAME}",
        root,
    ]

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise CompileError(f"Compilation timed out after {timeout}s.") from exc
    duration = round(time.monotonic() - start, 1)

    stem = Path(root).stem
    log_path = build / f"{stem}.log"
    log_text = (
        log_path.read_text(encoding="utf-8", errors="ignore")
        if log_path.is_file()
        else (proc.stdout + proc.stderr)
    )
    pdf_path = build / f"{stem}.pdf"
    success = proc.returncode == 0 and pdf_path.is_file()

    return {
        "success": success,
        "root_file": root,
        "engine": eng,
        "pdf_path": str(pdf_path) if pdf_path.is_file() else None,
        "duration_s": duration,
        "errors": [] if success else _parse_errors(log_text),
        "log_tail": "\n".join(log_text.splitlines()[-100:]),
    }
