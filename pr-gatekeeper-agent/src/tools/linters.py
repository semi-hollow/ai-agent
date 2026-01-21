from __future__ import annotations

from src.tools.runner import ToolResult, run


def run_ruff(repo_path: str, timeout: int) -> ToolResult:
    return run(["ruff", "check", "--output-format", "json", "."], cwd=repo_path, timeout=timeout)
