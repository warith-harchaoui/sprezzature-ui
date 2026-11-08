"""
A gate that reports on files it never read is worse than no gate.

Each of these answered "0 findings" and exit 0, or a 500, for a reason that had
nothing to do with the source: the name of a directory above the project, a
mistyped path, a filename chosen by whoever called the route.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import audit_i18n  # noqa: E402 — via tests/conftest.py sys.path
import pytest
from fastapi.testclient import TestClient

from sprezzature_ui.api import app

TABLE = 'const i18n = { en: "Save", fr: "Enregistrer" };\n'


def test_a_project_under_a_directory_called_build_is_audited(tmp_path: Path) -> None:
    """``/home/ci/build/project`` is where a runner may well put a checkout."""
    source = tmp_path / "build" / "project" / "src"
    source.mkdir(parents=True)
    (source / "app.js").write_text(TABLE, encoding="utf-8")
    assert audit_i18n.gather([str(source)]) == [source / "app.js"]


def test_a_build_directory_inside_the_project_is_still_skipped(tmp_path: Path) -> None:
    """The skip list keeps its job below the directory that was named."""
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "app.js").write_text(TABLE, encoding="utf-8")
    assert audit_i18n.gather([str(tmp_path)]) == []


def test_a_path_that_does_not_exist_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A typo in a pre-commit or CI line must not read as a clean tree."""
    with pytest.raises(SystemExit) as stopped:
        audit_i18n.main([str(tmp_path / "nope")])
    assert stopped.value.code == 2
    assert "0 findings" not in capsys.readouterr().out


@pytest.mark.parametrize("filename", ["", "..", "a.j\u0000s", "x" * 5000 + ".js", "a." + "y" * 5000])
def test_no_filename_makes_the_route_fail(filename: str) -> None:
    """The name is the caller's: it is reported back, and never becomes a path."""
    response = TestClient(app).post(
        "/v1/i18n-audit", json={"source": "X = 1\n", "filename": filename}
    )
    assert response.status_code == 200


def test_a_lone_surrogate_in_the_source_does_not_fail_the_route() -> None:
    """Valid JSON, not encodable as UTF-8."""
    response = TestClient(app).post(
        "/v1/i18n-audit",
        content=b'{"source": "\\ud800", "filename": "a.js"}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_the_filename_is_still_what_comes_back() -> None:
    """Writing under a neutral name changes nothing the caller can see."""
    response = TestClient(app).post(
        "/v1/i18n-audit", json={"source": TABLE, "filename": "web/App.JS"}
    )
    assert response.json()["findings"][0]["path"] == "web/App.JS"


def test_the_mcp_server_announces_its_version_as_a_version() -> None:
    """fastapi-mcp passes the description into the version slot."""
    from sprezzature_ui import __version__
    from sprezzature_ui.mcp import mcp

    options = mcp.server.create_initialization_options()
    assert options.server_version == __version__
    assert options.instructions == mcp.description
