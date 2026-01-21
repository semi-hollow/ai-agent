from __future__ import annotations

from src.tools.runner import ToolResult, run


def search(repo_path: str, pattern: str, timeout: int = 30) -> ToolResult:
    return run(["rg", "-n", pattern, "."], cwd=repo_path, timeout=timeout)
