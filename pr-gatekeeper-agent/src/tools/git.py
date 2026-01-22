from __future__ import annotations

from typing import List, Tuple

from src.tools.runner import ToolResult, run


def changed_files(repo_path: str, base_ref: str, head_ref: str, timeout: int = 30) -> Tuple[List[str], ToolResult]:
    result = run(
        ["git", "diff", "--name-only", f"{base_ref}..{head_ref}"],
        cwd=repo_path,
        timeout=timeout,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return files, result


def diff_summary(repo_path: str, base_ref: str, head_ref: str, timeout: int = 30) -> Tuple[str, ToolResult, ToolResult]:
    stat_result = run(
        ["git", "diff", "--stat", f"{base_ref}..{head_ref}"],
        cwd=repo_path,
        timeout=timeout,
    )
    diff_result = run(
        ["git", "diff", f"{base_ref}..{head_ref}"],
        cwd=repo_path,
        timeout=timeout,
    )
    summary_lines = diff_result.stdout.splitlines()[:20]
    summary = stat_result.stdout
    if summary_lines:
        summary = f"{summary}\n---\n" + "\n".join(summary_lines)
    return summary.strip(), stat_result, diff_result
