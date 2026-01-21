from __future__ import annotations

import json
import os
from typing import Dict, List

from src.graph.state import Finding, GatekeeperState
from src.policies.policy_engine import load_policy


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def _findings_table(findings: List[Finding]) -> str:
    if not findings:
        return "No findings detected."
    lines = ["| Severity | Rule | File:Line | Message |", "|---|---|---|---|"]
    for finding in findings:
        file_ref = ""
        if finding.file and finding.line:
            file_ref = f"{finding.file}:{finding.line}"
        elif finding.file:
            file_ref = finding.file
        lines.append(
            f"| {finding.severity} | {finding.rule_id or ''} | {file_ref} | {finding.message} |"
        )
    return "\n".join(lines)


def render_report(state: GatekeeperState) -> Dict:
    policy = load_policy(os.path.join(state.repo_path, "config", "policy.yaml"))
    max_stdout = policy.report.max_stdout_chars

    tool_lines = []
    for name, result in state.tool_results.items():
        if not isinstance(result, dict):
            continue
        stdout = _truncate(result.get("stdout", ""), max_stdout)
        stderr = _truncate(result.get("stderr", ""), max_stdout)
        tool_lines.append(
            f"### {name}\n"
            f"* Return code: {result.get('returncode')}\n"
            f"* Duration: {result.get('duration_ms')} ms\n"
            f"* Timed out: {result.get('timed_out')}\n"
            f"* Stdout (truncated):\n```\n{stdout}\n```\n"
            f"* Stderr (truncated):\n```\n{stderr}\n```\n"
        )

    summary = (
        f"**Result:** {state.decision.result}\n\n"
        f"**Blocked:** {state.decision.blocked}\n\n"
        f"**Reasons:** {', '.join(state.decision.reasons)}"
    )

    report_md = "\n\n".join(
        [
            "# PR Gatekeeper Report",
            "## Summary",
            summary,
            "## Changed Files",
            "\n".join([f"- {file}" for file in state.changed_files]) or "No changes detected.",
            "## Tool Results",
            "\n".join(tool_lines) or "No tool results.",
            "## Findings",
            _findings_table(state.findings),
            "## Next Steps",
            _next_steps(state.decision.result),
        ]
    )

    report_json = json.dumps(
        {
            "run_id": state.run_id,
            "inputs": {
                "repo": state.repo_path,
                "base": state.base_ref,
                "head": state.head_ref,
            },
            "changed_files": state.changed_files,
            "tool_results": state.tool_results,
            "findings": [finding.model_dump() for finding in state.findings],
            "decision": state.decision.model_dump(),
            "metrics": state.metrics,
        },
        indent=2,
    )

    metrics = dict(state.metrics)
    metrics["report_md"] = report_md
    metrics["report_json"] = report_json

    return {"metrics": metrics}


def _next_steps(result: str) -> str:
    if result == "FAIL":
        return (
            "1. Address the HIGH/CRITICAL findings.\n"
            "2. Re-run the gatekeeper CLI.\n"
            "3. Ensure tests and lint pass before merge."
        )
    if result == "WARN":
        return (
            "1. Review findings and decide whether to fix now.\n"
            "2. Document any accepted risks.\n"
            "3. Re-run gatekeeper if changes are made."
        )
    return "1. Proceed with merge.\n2. Keep monitoring CI for regressions."
