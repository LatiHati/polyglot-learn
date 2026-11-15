"""Run every example and compare its real output with expected.txt.

An example is never reported as passing unless it was actually executed:
when no toolchain is available the result is `skipped`, and `--strict`
turns a skip into a failure (used in CI).
"""

from __future__ import annotations

import difflib
import functools
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .model import Example, Project, Runner

PASS = "pass"
FAIL = "fail"
SKIPPED = "skipped"

MODES = ("auto", "local", "docker")


@dataclass(frozen=True)
class Result:
    card_id: str
    language: str
    status: str
    mode: str
    detail: str = ""


def normalize(text: str) -> str:
    """Line endings and trailing whitespace do not count as a difference."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).rstrip("\n") + "\n"


def local_available(runner: Runner) -> bool:
    if not runner.local:
        return False
    for command in runner.local:
        program = command[0]
        if program.startswith("{"):
            continue
        if shutil.which(program) is None:
            return False
    return True


@functools.lru_cache(maxsize=1)
def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        done = subprocess.run(["docker", "info"], capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


def _tail(text: str, lines: int = 12) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def _run(command: list[str], cwd: Path | None, timeout: float) -> tuple[int | None, str, str]:
    try:
        done = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout:g} s"
    except OSError as exc:
        return None, "", f"cannot start {command[0]}: {exc}"
    return done.returncode, done.stdout, done.stderr


def _run_local(example: Example, runner: Runner, timeout: float) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="polyglot-") as tmp:
        workdir = Path(tmp) / "example"
        shutil.copytree(example.directory, workdir)
        binary = str(workdir / ("main.out.exe" if sys.platform == "win32" else "main.out"))
        values = {"{python}": sys.executable, "{source}": runner.source, "{out}": binary}
        stdout = ""
        for command in runner.local:
            resolved = [values.get(part, part) for part in command]
            code, stdout, stderr = _run(resolved, workdir, timeout)
            if code != 0:
                return False, _tail(stderr) or f"exit code {code}"
        return True, stdout


def _run_docker(example: Example, runner: Runner, timeout: float) -> tuple[bool, str]:
    command = [
        "docker", "run", "--rm", "--network", "none",
        "-v", f"{example.directory.resolve()}:/src:ro", "-w", "/src",
        runner.image, "sh", "-c", runner.docker,
    ]
    code, stdout, stderr = _run(command, None, timeout)
    if code != 0:
        return False, _tail(stderr) or f"exit code {code}"
    return True, stdout


def run_example(example: Example, runner: Runner | None, mode: str = "auto", timeout: float = 60.0) -> Result:
    if mode not in MODES:
        raise ValueError(f"unknown mode '{mode}'")

    def result(status: str, used: str, detail: str = "") -> Result:
        return Result(example.card_id, example.language, status, used, detail)

    if runner is None:
        return result(FAIL, mode, "no runner for this language in languages.yaml")
    if example.source is None or not example.source.is_file():
        return result(FAIL, mode, f"missing source file {runner.source}")
    if not example.expected.is_file():
        return result(FAIL, mode, "missing expected.txt")

    if mode == "local" or (mode == "auto" and local_available(runner)):
        if not local_available(runner):
            return result(SKIPPED, "local", "toolchain is not installed")
        used = "local"
        ok, output = _run_local(example, runner, timeout)
    elif docker_available():
        used = "docker"
        ok, output = _run_docker(example, runner, max(timeout, 300.0))
    else:
        reason = "Docker is not running" if mode == "docker" else "no local toolchain and Docker is not running"
        return result(SKIPPED, mode, reason)

    if not ok:
        return result(FAIL, used, output)
    expected = normalize(example.expected.read_text(encoding="utf-8"))
    actual = normalize(output)
    if actual == expected:
        return result(PASS, used)
    diff = difflib.unified_diff(
        expected.splitlines(), actual.splitlines(), "expected.txt", "actual output", lineterm="", n=1
    )
    return result(FAIL, used, "output differs:\n" + "\n".join(list(diff)[:30]))


def verify_project(
    project: Project,
    mode: str = "auto",
    cards: list[str] | None = None,
    languages: list[str] | None = None,
    timeout: float = 60.0,
) -> list[Result]:
    results = []
    for card in project.cards:
        if cards and card.id not in cards:
            continue
        for example in card.examples:
            if languages and example.language not in languages:
                continue
            results.append(run_example(example, project.runners.get(example.language), mode, timeout))
    return results
