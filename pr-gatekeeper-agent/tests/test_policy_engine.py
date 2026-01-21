from src.graph.state import Finding
from src.policies.policy_engine import evaluate
from src.policies.schemas import PolicyConfig, Thresholds


def test_policy_pass_warn_fail():
    policy = PolicyConfig(thresholds=Thresholds(block_on_severity_at_or_above="HIGH"))

    decision = evaluate([], {}, policy)
    assert decision.result == "PASS"

    findings = [
        Finding(tool="ruff", severity="LOW", rule_id="X", message="Minor"),
    ]
    decision = evaluate(findings, {}, policy)
    assert decision.result == "WARN"

    findings.append(
        Finding(tool="pytest", severity="HIGH", rule_id=None, message="Failure")
    )
    decision = evaluate(findings, {}, policy)
    assert decision.result == "FAIL"
