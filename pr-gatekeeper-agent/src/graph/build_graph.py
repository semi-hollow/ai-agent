from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.graph.nodes.analyze_findings import analyze_findings
from src.graph.nodes.collect_context import collect_context
from src.graph.nodes.ingest_pr import ingest_pr
from src.graph.nodes.publish_results import publish_results
from src.graph.nodes.render_report import render_report
from src.graph.nodes.run_tools import run_tools
from src.graph.state import GatekeeperState


def build_graph():
    graph = StateGraph(GatekeeperState)

    graph.add_node("ingest_pr", ingest_pr)
    graph.add_node("collect_context", collect_context)
    graph.add_node("run_tools", run_tools)
    graph.add_node("analyze_findings", analyze_findings)
    graph.add_node("render_report", render_report)
    graph.add_node("publish_results", publish_results)

    graph.set_entry_point("ingest_pr")
    graph.add_edge("ingest_pr", "collect_context")
    graph.add_edge("collect_context", "run_tools")
    graph.add_edge("run_tools", "analyze_findings")
    graph.add_edge("analyze_findings", "render_report")
    graph.add_edge("render_report", "publish_results")
    graph.add_edge("publish_results", END)

    return graph.compile()
