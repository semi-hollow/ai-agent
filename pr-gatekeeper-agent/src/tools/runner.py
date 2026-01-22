from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import List


@dataclass
class ToolResult:
    cmd: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool


def run(cmd: List[str], cwd: str, timeout: int) -> ToolResult:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        return ToolResult(
            cmd=cmd,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=duration_ms,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        stdout = exc.stdout if exc.stdout is not None else ""
        stderr = exc.stderr if exc.stderr is not None else ""
        return ToolResult(
            cmd=cmd,
            returncode=124,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            timed_out=True,
        )
