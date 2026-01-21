import os
from pathlib import Path

from src.graph.build_graph import build_graph
from src.graph.state import GatekeeperState
from src.tools.runner import run


def _run(cmd, cwd):
    result = run(cmd, cwd=cwd, timeout=10)
    assert result.returncode == 0, result.stderr
    return result


def test_graph_smoke(tmp_path: Path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    _run(["git", "init"], cwd=str(repo_path))
    _run(["git", "config", "user.email", "tester@example.com"], cwd=str(repo_path))
    _run(["git", "config", "user.name", "Tester"], cwd=str(repo_path))

    (repo_path / "config").mkdir()
    (repo_path / "config" / "policy.yaml").write_text(
        """
        tool_timeouts:
          ruff: 1
          pytest: 1
          ripgrep: 1
        fail_strategy:
          on_tool_error: "open"
        thresholds:
          block_on_severity_at_or_above: "HIGH"
        enabled_tools:
          ruff: false
          pytest: false
          ripgrep: false
        report:
          max_stdout_chars: 2000
        """.strip()
    )

    file_path = repo_path / "hello.txt"
    file_path.write_text("hello")
    _run(["git", "add", "hello.txt"], cwd=str(repo_path))
    _run(["git", "commit", "-m", "initial"], cwd=str(repo_path))

    file_path.write_text("hello world")
    _run(["git", "add", "hello.txt"], cwd=str(repo_path))
    _run(["git", "commit", "-m", "update"], cwd=str(repo_path))

    graph = build_graph()
    state = GatekeeperState(
        run_id="test-run",
        repo_path=str(repo_path),
        base_ref="HEAD~1",
        head_ref="HEAD",
    )
    final_state = graph.invoke(state)

    report_path = Path(final_state.artifacts["report_md"])
    assert report_path.exists()
    json_path = Path(final_state.artifacts["report_json"])
    assert json_path.exists()
