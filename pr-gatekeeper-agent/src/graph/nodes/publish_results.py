from __future__ import annotations

import os
import time
from typing import Dict

from src.graph.state import GatekeeperState
from src.storage.db import record_run


def publish_results(state: GatekeeperState) -> Dict:
    artifacts_dir = os.path.join(state.repo_path, "artifacts", state.run_id)
    os.makedirs(artifacts_dir, exist_ok=True)

    report_md = state.metrics.get("report_md", "")
    report_json = state.metrics.get("report_json", "")

    report_md_path = os.path.join(artifacts_dir, "report.md")
    report_json_path = os.path.join(artifacts_dir, "report.json")

    with open(report_md_path, "w", encoding="utf-8") as handle:
        handle.write(report_md)
    with open(report_json_path, "w", encoding="utf-8") as handle:
        handle.write(report_json)

    duration_ms = int(state.metrics.get("duration_ms", 0))
    if not duration_ms and state.metrics.get("start_time"):
        duration_ms = int((time.time() - state.metrics["start_time"]) * 1000)

    record_run(
        repo_path=state.repo_path,
        run_id=state.run_id,
        base_ref=state.base_ref,
        head_ref=state.head_ref,
        decision=state.decision,
        duration_ms=duration_ms,
        tool_results=state.tool_results,
        findings=state.findings,
    )

    artifacts = dict(state.artifacts)
    artifacts["report_md"] = report_md_path
    artifacts["report_json"] = report_json_path

    metrics = dict(state.metrics)
    metrics["duration_ms"] = duration_ms

    return {"artifacts": artifacts, "metrics": metrics}
