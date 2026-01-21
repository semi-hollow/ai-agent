from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from src.graph.state import Finding, GateDecision
from src.policies.schemas import PolicyConfig


SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


def load_policy(path: str) -> PolicyConfig:
    data = {}
    policy_path = Path(path)
    if policy_path.exists():
        with policy_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    return PolicyConfig.from_dict(data)


def _severity_index(value: str) -> int:
    try:
        return SEVERITY_ORDER.index(value)
    except ValueError:
        return 0


def evaluate(
    findings: List[Finding],
    tool_results: Dict[str, Dict],
    policy: PolicyConfig,
) -> GateDecision:
    reasons: List[str] = []
    decision_result = "PASS"
    blocked = False

    if policy.fail_strategy.on_tool_error == "closed":
        for tool_name, result in tool_results.items():
            if result.get("timed_out"):
                reasons.append(f"{tool_name} timed out")
                decision_result = "FAIL"
                blocked = True
            elif result.get("error"):
                reasons.append(f"{tool_name} failed to run")
                decision_result = "FAIL"
                blocked = True

    threshold = policy.thresholds.block_on_severity_at_or_above
    threshold_index = _severity_index(threshold)
    highest = max((_severity_index(f.severity) for f in findings), default=-1)

    if decision_result != "FAIL":
        if highest >= threshold_index and highest >= 0:
            decision_result = "FAIL"
            blocked = True
            reasons.append("Findings exceed severity threshold")
        elif findings:
            decision_result = "WARN"
            blocked = False
            reasons.append("Findings present but below threshold")
        else:
            decision_result = "PASS"
            blocked = False
            reasons.append("No findings detected")

    return GateDecision(result=decision_result, reasons=reasons, blocked=blocked)
