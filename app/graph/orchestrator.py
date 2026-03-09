"""Orquestrador LangGraph — constrói e compila o grafo multi-agente."""

import logging
from typing import Any

from langgraph.graph import StateGraph, START, END

from app.graph.nodes import user_node, planner_node, executor_node, memory_node
from app.graph.edges import route_to_executor

logger = logging.getLogger(__name__)


def build_graph():
    """Constroi e compila o grafo multi-agente.

    Fluxo:
        START → user → planner → executor → memory → END
    """
    graph = StateGraph(dict)

    graph.add_node("user", user_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("memory", memory_node)

    graph.add_edge(START, "user")
    graph.add_edge("user", "planner")
    graph.add_conditional_edges("planner", route_to_executor, {"executor": "executor"})
    graph.add_edge("executor", "memory")
    graph.add_edge("memory", END)

    compiled = graph.compile()
    logger.info("Multi-agent graph compiled successfully")
    return compiled
