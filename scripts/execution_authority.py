#!/usr/bin/env python3
"""Bounded external-execution authority for project-owned Python programs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AuthorityViolation(RuntimeError):
    pass


ALLOWED_ROLES = (
    "cmake.version",
    "cmake.configure",
    "cmake.build",
    "ctest.run",
    "git.remote",
    "git.head",
    "git.status",
    "git.diff_check",
    "git.praxis_head",
    "git.praxis_status",
    "python.collector",
    "python.praxis_validator",
    "probe.run",
)


@dataclass(frozen=True)
class ExecutionContext:
    root: Path
    praxis_root: Path | None = None


def _within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _resolved_executable(raw: str) -> Path:
    if "/" in raw:
        return Path(raw).resolve()
    located = shutil.which(raw)
    if located is None:
        raise AuthorityViolation(f"external executable not found: {raw}")
    return Path(located).resolve()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorityViolation(message)


def authorize(context: ExecutionContext, role: str, command: list[str]) -> None:
    """Reject every external command not matching one explicit role and shape."""
    _require(bool(command), "empty external command")
    root = context.root.resolve()
    executable = _resolved_executable(command[0])
    arguments = command[1:]

    if role == "cmake.version":
        _require(executable == _resolved_executable("cmake"), "cmake executable identity")
        _require(arguments == ["--version"], "cmake version argument shape")
        return

    if role == "cmake.configure":
        _require(executable == _resolved_executable("cmake"), "cmake executable identity")
        _require(len(arguments) == 6, "cmake configure argument count")
        _require(arguments[0] == "-S" and Path(arguments[1]).resolve() == root,
                 "cmake source must be project root")
        build = Path(arguments[3]).resolve()
        _require(arguments[2] == "-B" and _within(build, root / ".build"),
                 "cmake build must be below .build")
        _require(
            arguments[4:] == [
                "-DCMAKE_BUILD_TYPE=Debug",
                "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            ],
            "cmake configure options",
        )
        return

    if role == "cmake.build":
        _require(executable == _resolved_executable("cmake"), "cmake executable identity")
        _require(len(arguments) == 3 and arguments[0] == "--build"
                 and _within(Path(arguments[1]), root / ".build")
                 and arguments[2] == "--parallel", "cmake build argument shape")
        return

    if role == "ctest.run":
        _require(executable == _resolved_executable("ctest"), "ctest executable identity")
        _require(len(arguments) == 3 and arguments[0] == "--test-dir"
                 and _within(Path(arguments[1]), root / ".build")
                 and arguments[2] == "--output-on-failure", "ctest argument shape")
        return

    if role == "git.remote":
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(arguments == ["remote"], "git remote argument shape")
        return

    if role == "git.head":
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(arguments == ["rev-parse", "--verify", "HEAD"], "git head argument shape")
        return

    if role == "git.status":
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(arguments == ["status", "--porcelain", "--untracked-files=all"],
                 "git status argument shape")
        return

    if role == "git.diff_check":
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(arguments == ["diff", "--check"], "git diff argument shape")
        return

    if role == "git.praxis_head":
        _require(context.praxis_root is not None, "Praxis root required")
        praxis = context.praxis_root.resolve()
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(arguments == ["-C", str(praxis), "rev-parse", "HEAD"],
                 "Praxis Git HEAD argument shape")
        return

    if role == "git.praxis_status":
        _require(context.praxis_root is not None, "Praxis root required")
        praxis = context.praxis_root.resolve()
        _require(executable == _resolved_executable("git"), "git executable identity")
        _require(
            arguments
            == ["-C", str(praxis), "status", "--porcelain", "--untracked-files=all"],
            "Praxis Git status argument shape",
        )
        return

    if role == "python.collector":
        _require(executable == Path(sys.executable).resolve(), "Python executable identity")
        _require(len(arguments) == 3, "collector argument count")
        _require(Path(arguments[0]).resolve() == root / "scripts/collect_rf_a0_evidence.py",
                 "collector script identity")
        _require(_within(Path(arguments[1]), root / ".build"), "collector probe identity")
        _require(_within(Path(arguments[2]), root / "docs/experiments/evidence/rf-a0/runs"),
                 "collector evidence destination")
        return

    if role == "python.praxis_validator":
        _require(context.praxis_root is not None, "Praxis root required")
        praxis = context.praxis_root.resolve()
        _require(executable == Path(sys.executable).resolve(), "Python executable identity")
        _require(len(arguments) == 2, "Praxis validator argument count")
        _require(Path(arguments[0]).resolve() == praxis / "scripts/validate_governed_project.py",
                 "Praxis validator script identity")
        _require(Path(arguments[1]).resolve() == root, "Praxis validator workspace")
        return

    if role == "probe.run":
        _require(executable.name == "srf-runtime-probe"
                 and _within(executable, root / ".build"), "probe executable identity")
        _require(len(arguments) == 4 and arguments[0] == "--file"
                 and _within(Path(arguments[1]), root / ".build")
                 and arguments[2:] == ["--port", "0"], "probe argument shape")
        return

    raise AuthorityViolation(f"external execution role is not allowlisted: {role}")


def run_external(
    context: ExecutionContext,
    role: str,
    command: list[str],
    **options: Any,
) -> subprocess.CompletedProcess[Any]:
    _require("shell" not in options, "shell execution option is forbidden")
    authorize(context, role, command)
    return subprocess.run(command, shell=False, **options)


def spawn_external(
    context: ExecutionContext,
    role: str,
    command: list[str],
    **options: Any,
) -> subprocess.Popen[Any]:
    _require("shell" not in options, "shell execution option is forbidden")
    authorize(context, role, command)
    return subprocess.Popen(command, shell=False, **options)
