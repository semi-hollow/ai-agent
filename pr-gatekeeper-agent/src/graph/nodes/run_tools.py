from __future__ import annotations

import os
from typing import Dict

from src.graph.state import GatekeeperState
from src.policies.policy_engine import load_policy
from src.tools.linters import run_ruff
from src.tools.tests import run_pytest


def _is_python_repo(repo_path: str) -> bool:
    return any(
        os.path.exists(os.path.join(repo_path, marker))
        for marker in ("pyproject.toml", "requirements.txt")
    )


def run_tools(state: GatekeeperState) -> Dict:
    policy = load_policy(os.path.join(state.repo_path, "config", "policy.yaml"))
    tool_results = dict(state.tool_results)
    metrics = dict(state.metrics)

    python_repo = _is_python_repo(state.repo_path)
    metrics["python_repo"] = python_repo

    if python_repo and policy.enabled_tools.ruff:
        ruff_result = run_ruff(state.repo_path, timeout=policy.tool_timeouts.ruff)
        tool_results["ruff"] = {
            "returncode": ruff_result.returncode,
            "stdout": ruff_result.stdout,
            "stderr": ruff_result.stderr,
            "duration_ms": ruff_result.duration_ms,
            "timed_out": ruff_result.timed_out,
            "error": ruff_result.returncode not in (0, 1) or ruff_result.timed_out,
        }

    if python_repo and policy.enabled_tools.pytest:
        pytest_result = run_pytest(state.repo_path, timeout=policy.tool_timeouts.pytest)
        tool_results["pytest"] = {
            "returncode": pytest_result.returncode,
            "stdout": pytest_result.stdout,
            "stderr": pytest_result.stderr,
            "duration_ms": pytest_result.duration_ms,
            "timed_out": pytest_result.timed_out,
            "error": pytest_result.returncode not in (0, 1, 5) or pytest_result.timed_out,
        }

    return {"tool_results": tool_results, "metrics": metrics}
