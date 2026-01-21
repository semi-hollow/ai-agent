from src.tools.runner import run


def test_tool_runner_basic():
    result = run(["python", "-c", "print('ok')"], cwd=".", timeout=5)
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert result.duration_ms >= 0
    assert result.timed_out is False
