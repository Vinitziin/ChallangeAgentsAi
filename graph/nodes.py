"""Nodes do LangGraph — cada nó é uma função que processa o estado do grafo."""

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """Você é um roteador inteligente. Analise a pergunta do usuário e decida qual agente especializado deve responder.

Agentes disponíveis:
- "web_search": Para perguntas sobre eventos atuais, notícias, informações gerais da internet.
- "vector_db": Para perguntas sobre documentação interna da empresa (TechStore), FAQs da empresa, base de conhecimento.
- "sql_agent": Para perguntas sobre dados do banco (clientes, produtos, pedidos), relatórios, métricas.
- "weather": Para perguntas sobre clima, temperatura, previsão do tempo de cidades.

Responda APENAS com um JSON no formato: {"agent": "<nome_do_agente>", "reasoning": "<motivo>"}

Se não tiver certeza, use "web_search" como fallback."""


def user_node(state: dict[str, Any]) -> dict[str, Any]:
    """Recebe a entrada do usuário e a passa para o estado."""
    logger.info("UserNode: processing user message")
    return state


def planner_node(state: dict[str, Any]) -> dict[str, Any]:
    """Analisa a pergunta do usuário e decide qual agente deve responder."""
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    if not last_message:
        state["selected_agent"] = "web_search"
        state["reasoning"] = "No message found, defaulting to web search."
        return state

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )

    query = last_message.content if hasattr(last_message, "content") else str(last_message)

    response = llm.invoke([
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": query},
    ])

    try:
        decision = json.loads(response.content)
        agent = decision.get("agent", "web_search")
        reasoning = decision.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        agent = "web_search"
        reasoning = "Could not parse planner response, falling back to web search."

    valid_agents = {"web_search", "vector_db", "sql_agent", "weather"}
    if agent not in valid_agents:
        agent = "web_search"
        reasoning = f"Unknown agent '{agent}', falling back to web search."

    state["selected_agent"] = agent
    state["reasoning"] = reasoning
    logger.info("PlannerNode: selected '%s' — %s", agent, reasoning)
    return state


def executor_node(state: dict[str, Any]) -> dict[str, Any]:
    """Execute the selected agent and store the result."""
    from agents.web_search import create_web_search_agent
    from agents.vector_db import create_vector_db_agent
    from agents.sql_agent import create_sql_agent
    from agents.weather import create_weather_agent

    agent_map = {
        "web_search": create_web_search_agent,
        "vector_db": create_vector_db_agent,
        "sql_agent": create_sql_agent,
        "weather": create_weather_agent,
    }

    selected = state.get("selected_agent", "web_search")
    agent_factory = agent_map.get(selected, create_web_search_agent)

    logger.info("ExecutorNode: invoking agent '%s'", selected)

    agent = agent_factory()
    messages = state.get("messages", [])

    result = agent.invoke({"messages": messages})

    state["messages"] = result.get("messages", messages)
    state["agent_used"] = selected
    logger.info("ExecutorNode: agent '%s' completed", selected)
    return state


def memory_node(state: dict[str, Any]) -> dict[str, Any]:
    """Store conversation context for multi-turn support."""
    logger.info("MemoryNode: storing context (agent=%s)", state.get("agent_used"))
    return state
