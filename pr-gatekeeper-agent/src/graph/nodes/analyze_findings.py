from __future__ import annotations

import json
import os
import re
from typing import Dict, List

from src.graph.state import Finding, GateDecision, GatekeeperState
from src.policies.policy_engine import evaluate, load_policy


FAILED_PATTERN = re.compile(r"^FAILED\s+(.+?)\s+-\s+(.*)$")


def _parse_ruff(output: str) -> List[Finding]:
    findings = []
    if not output.strip():
        return findings
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return findings
    for entry in data:
        findings.append(
            Finding(
                tool="ruff",
                severity="MEDIUM",
                rule_id=entry.get("code"),
                message=entry.get("message", "Ruff finding"),
                file=entry.get("filename"),
                line=entry.get("location", {}).get("row"),
                evidence=entry.get("source"),
            )
        )
    return findings


def _parse_pytest(stdout: str, stderr: str) -> List[Finding]:
    findings = []
    for line in (stdout + "\n" + stderr).splitlines():
        match = FAILED_PATTERN.match(line.strip())
        if match:
            findings.append(
                Finding(
                    tool="pytest",
                    severity="HIGH",
                    rule_id=None,
                    message=match.group(2),
                    file=None,
                    line=None,
                    evidence=match.group(1),
                )
            )
    return findings


def _parse_ripgrep(output: str) -> List[Finding]:
    findings = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) >= 3:
            file_path, line_no, content = parts[0], parts[1], parts[2]
            try:
                line_int = int(line_no)
            except ValueError:
                line_int = None
            findings.append(
                Finding(
                    tool="ripgrep",
                    severity="LOW",
                    rule_id=None,
                    message=content.strip(),
                    file=file_path,
                    line=line_int,
                    evidence=line.strip(),
                )
            )
    return findings


def analyze_findings(state: GatekeeperState) -> Dict:
    findings: List[Finding] = []
    ruff_result = state.tool_results.get("ruff")
    if ruff_result:
        findings.extend(_parse_ruff(ruff_result.get("stdout", "")))

    pytest_result = state.tool_results.get("pytest")
    if pytest_result:
        findings.extend(
            _parse_pytest(
                pytest_result.get("stdout", ""), pytest_result.get("stderr", "")
            )
        )

    ripgrep_result = state.tool_results.get("ripgrep")
    if ripgrep_result:
        findings.extend(_parse_ripgrep(ripgrep_result.get("stdout", "")))

    if not state.metrics.get("python_repo", False):
        findings.append(
            Finding(
                tool="gatekeeper",
                severity="LOW",
                rule_id="NON_PYTHON",
                message="Non-Python repository detected; skipped ruff/pytest.",
            )
        )

    policy = load_policy(os.path.join(state.repo_path, "config", "policy.yaml"))
    decision = evaluate(findings, state.tool_results, policy)

    return {"findings": findings, "decision": decision}
