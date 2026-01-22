from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    tool: str
    severity: str
    rule_id: Optional[str] = None
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    evidence: Optional[str] = None


class GateDecision(BaseModel):
    result: str
    reasons: List[str]
    blocked: bool


class GatekeeperState(BaseModel):
    run_id: str
    repo_path: str
    base_ref: str
    head_ref: str
    changed_files: List[str] = Field(default_factory=list)
    diff_summary: str = ""
    context_snippets: Dict[str, str] = Field(default_factory=dict)
    tool_results: Dict[str, Dict] = Field(default_factory=dict)
    findings: List[Finding] = Field(default_factory=list)
    decision: GateDecision = Field(
        default_factory=lambda: GateDecision(result="PASS", reasons=[], blocked=False)
    )
    artifacts: Dict[str, str] = Field(default_factory=dict)
    metrics: Dict[str, object] = Field(default_factory=dict)
