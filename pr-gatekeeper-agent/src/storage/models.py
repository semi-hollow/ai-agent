from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunRecord:
    run_id: str
    repo_path: str
    base_ref: str
    head_ref: str
    created_at: str
    decision_result: str
    blocked: int
    duration_ms: int
