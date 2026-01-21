from __future__ import annotations

import os
from typing import Dict

from src.graph.state import GatekeeperState
from src.policies.policy_engine import load_policy
from src.tools import ripgrep


def _read_file_snippet(path: str, max_lines: int = 20) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            lines = [line.rstrip("\n") for _, line in zip(range(max_lines), handle)]
        return "\n".join(lines)
    except OSError:
        return ""


def collect_context(state: GatekeeperState) -> Dict:
    context = {}
    for file_path in state.changed_files:
        abs_path = os.path.join(state.repo_path, file_path)
        snippet = _read_file_snippet(abs_path)
        if snippet:
            context[file_path] = snippet

    policy = load_policy(os.path.join(state.repo_path, "config", "policy.yaml"))
    tool_results = dict(state.tool_results)

    if policy.enabled_tools.ripgrep:
        rg_result = ripgrep.search(
            state.repo_path,
            "TODO|FIXME",
            timeout=policy.tool_timeouts.ripgrep,
        )
        tool_results["ripgrep"] = {
            "returncode": rg_result.returncode,
            "stdout": rg_result.stdout,
            "stderr": rg_result.stderr,
            "duration_ms": rg_result.duration_ms,
            "timed_out": rg_result.timed_out,
            "error": rg_result.returncode not in (0, 1) or rg_result.timed_out,
        }
        if rg_result.stdout.strip():
            context["ripgrep_todo"] = rg_result.stdout.strip()

    return {"context_snippets": context, "tool_results": tool_results}
