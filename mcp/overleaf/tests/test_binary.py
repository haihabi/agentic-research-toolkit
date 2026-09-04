from __future__ import annotations

import base64

import pytest

from overleaf_mcp.errors import FileTooLargeError, OverleafMCPError

# A minimal 1x1 transparent PNG.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture
def project(service):
    service.add_project("project.git", "paper")
    return service


def test_binary_round_trip(project):
    project.add_binary_file(
        "paper", "figures/pixel.png", base64.b64encode(PNG_BYTES).decode()
    )
    result = project.read_binary_file("paper", "figures/pixel.png")
    assert result["size_bytes"] == len(PNG_BYTES)
    assert base64.b64decode(result["content_base64"]) == PNG_BYTES


def test_binary_add_replaces_existing(project):
    project.add_binary_file("paper", "f.bin", base64.b64encode(b"one").decode())
    project.add_binary_file("paper", "f.bin", base64.b64encode(b"two").decode())
    assert base64.b64decode(
        project.read_binary_file("paper", "f.bin")["content_base64"]
    ) == b"two"


def test_rejects_invalid_base64(project):
    with pytest.raises(OverleafMCPError):
        project.add_binary_file("paper", "f.bin", "not!base64!!")


def test_rejects_oversize_write(project):
    too_big = base64.b64encode(b"x" * (1 * 1024 * 1024 + 1)).decode()
    with pytest.raises(FileTooLargeError):
        project.add_binary_file("paper", "big.bin", too_big)
