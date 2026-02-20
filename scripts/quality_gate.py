#!/usr/bin/env python3
"""Lightweight local quality gate for stability hardening."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", "backups"}


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        parts = set(path.parts)
        if SKIP_DIRS & parts:
            continue
        files.append(path)
    return sorted(files)


def run_py_compile() -> int:
    files = iter_python_files()
    errors = 0
    for file_path in files:
        try:
            source = file_path.read_text(encoding="utf-8")
            compile(source, str(file_path), "exec")
        except Exception as err:
            errors += 1
            print(f"[compile] FAIL {file_path}: {err}")
    if errors:
        print(f"[compile] Failed files: {errors}")
        return 1
    print(f"[compile] OK ({len(files)} files)")
    return 0


def run_unit_tests() -> int:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env)
    if proc.returncode == 0:
        print("[tests] OK")
    else:
        print(f"[tests] FAIL (exit={proc.returncode})")
    return proc.returncode


def main() -> int:
    compile_status = run_py_compile()
    tests_status = run_unit_tests()
    if compile_status == 0 and tests_status == 0:
        print("[quality-gate] PASS")
        return 0
    print("[quality-gate] FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
