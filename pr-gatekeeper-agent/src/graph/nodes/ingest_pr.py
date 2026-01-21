from __future__ import annotations

from typing import Dict

from src.graph.state import GatekeeperState
from src.tools import git


def ingest_pr(state: GatekeeperState) -> Dict:
    files, files_result = git.changed_files(
        state.repo_path, state.base_ref, state.head_ref
    )
    summary, stat_result, diff_result = git.diff_summary(
        state.repo_path, state.base_ref, state.head_ref
    )
    tool_results = dict(state.tool_results)
    tool_results["git_changed_files"] = {
        "returncode": files_result.returncode,
        "stdout": files_result.stdout,
        "stderr": files_result.stderr,
        "duration_ms": files_result.duration_ms,
        "timed_out": files_result.timed_out,
        "error": files_result.returncode != 0 or files_result.timed_out,
    }
    tool_results["git_diff_stat"] = {
        "returncode": stat_result.returncode,
        "stdout": stat_result.stdout,
        "stderr": stat_result.stderr,
        "duration_ms": stat_result.duration_ms,
        "timed_out": stat_result.timed_out,
        "error": stat_result.returncode != 0 or stat_result.timed_out,
    }
    tool_results["git_diff"] = {
        "returncode": diff_result.returncode,
        "stdout": diff_result.stdout,
        "stderr": diff_result.stderr,
        "duration_ms": diff_result.duration_ms,
        "timed_out": diff_result.timed_out,
        "error": diff_result.returncode != 0 or diff_result.timed_out,
    }
    return {
        "changed_files": files,
        "diff_summary": summary,
        "tool_results": tool_results,
    }
