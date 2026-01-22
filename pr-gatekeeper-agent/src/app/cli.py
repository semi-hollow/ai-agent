from __future__ import annotations

import argparse
import time
import uuid

from src.graph.build_graph import build_graph
from src.graph.state import GatekeeperState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PR Gatekeeper Agent")
    parser.add_argument("--repo", required=True, help="Path to repository")
    parser.add_argument("--base", required=True, help="Base git ref")
    parser.add_argument("--head", required=True, help="Head git ref")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = str(uuid.uuid4())
    start_time = time.time()

    graph = build_graph()
    state = GatekeeperState(
        run_id=run_id,
        repo_path=args.repo,
        base_ref=args.base,
        head_ref=args.head,
        metrics={"start_time": start_time},
    )
    final_state = graph.invoke(state)

    decision = final_state.decision
    findings_count = len(final_state.findings)
    duration_ms = final_state.metrics.get("duration_ms")

    print("PR Gatekeeper Summary")
    print(f"Run ID: {final_state.run_id}")
    print(f"Decision: {decision.result} (Blocked: {decision.blocked})")
    print(f"Findings: {findings_count}")
    print(f"Duration: {duration_ms} ms")
    print(f"Report: {final_state.artifacts.get('report_md')}")


if __name__ == "__main__":
    main()
