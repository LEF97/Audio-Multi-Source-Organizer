"""Tests du script scripts/check_file_sizes.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_file_sizes.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_file_sizes", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("body_lines", "expected"), [(5, 0), (70, 1)])
def test_long_functions_detects_only_oversized(tmp_path: Path, body_lines: int, expected: int) -> None:
    src = tmp_path / "mod.py"
    src.write_text("def f():\n" + "    x = 1\n" * body_lines, encoding="utf-8")
    assert len(_load().long_functions(src, 60)) == expected


def test_long_functions_ignores_invalid_syntax(tmp_path: Path) -> None:
    src = tmp_path / "bad.py"
    src.write_text("def (:\n", encoding="utf-8")
    assert _load().long_functions(src, 60) == []


def test_iter_sources_skips_ignored_dirs(tmp_path: Path) -> None:
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("x = 1\n", encoding="utf-8")
    names = [p.name for p in _load().iter_sources(tmp_path)]
    assert names == ["b.py"]
