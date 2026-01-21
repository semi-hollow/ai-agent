from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from src.graph.state import Finding, GateDecision


def _db_path(repo_path: str) -> str:
    return os.getenv("PR_GATEKEEPER_DB_PATH", os.path.join(repo_path, "artifacts", "gatekeeper.db"))


def init_db(repo_path: str) -> sqlite3.Connection:
    path = _db_path(repo_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            repo_path TEXT,
            base_ref TEXT,
            head_ref TEXT,
            created_at TEXT,
            decision_result TEXT,
            blocked INTEGER,
            duration_ms INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tool_results (
            run_id TEXT,
            tool_name TEXT,
            returncode INTEGER,
            duration_ms INTEGER,
            timed_out INTEGER,
            stdout_snippet TEXT,
            stderr_snippet TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS findings (
            run_id TEXT,
            tool TEXT,
            severity TEXT,
            rule_id TEXT,
            file TEXT,
            line INTEGER,
            message TEXT
        )
        """
    )
    return conn


def record_run(
    repo_path: str,
    run_id: str,
    base_ref: str,
    head_ref: str,
    decision: GateDecision,
    duration_ms: int,
    tool_results: Dict[str, Dict],
    findings: List[Finding],
) -> None:
    conn = init_db(repo_path)
    created_at = datetime.utcnow().isoformat()
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO runs
            (run_id, repo_path, base_ref, head_ref, created_at, decision_result, blocked, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                repo_path,
                base_ref,
                head_ref,
                created_at,
                decision.result,
                int(decision.blocked),
                duration_ms,
            ),
        )
        for tool_name, result in tool_results.items():
            if not isinstance(result, dict):
                continue
            conn.execute(
                """
                INSERT INTO tool_results
                (run_id, tool_name, returncode, duration_ms, timed_out, stdout_snippet, stderr_snippet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    tool_name,
                    result.get("returncode"),
                    result.get("duration_ms"),
                    int(bool(result.get("timed_out"))),
                    (result.get("stdout") or "")[:2000],
                    (result.get("stderr") or "")[:2000],
                ),
            )
        for finding in findings:
            conn.execute(
                """
                INSERT INTO findings
                (run_id, tool, severity, rule_id, file, line, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    finding.tool,
                    finding.severity,
                    finding.rule_id,
                    finding.file,
                    finding.line,
                    finding.message,
                ),
            )
    conn.close()
