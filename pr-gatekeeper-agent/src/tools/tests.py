from __future__ import annotations

from src.tools.runner import ToolResult, run


def run_pytest(repo_path: str, timeout: int) -> ToolResult:
    return run(["pytest", "-q"], cwd=repo_path, timeout=timeout)
