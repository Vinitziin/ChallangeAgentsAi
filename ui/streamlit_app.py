"""Interface do chat com o usuário"""

import logging
import json
import time

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from graph.orchestrator import build_graph

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

AGENT_LABELS = {
    "web_search": "🌐 Busca Web",
    "vector_db": "📚 Base de Conhecimento",
    "sql_agent": "🗄️ Banco de Dados",
    "weather": "🌤️ Previsão do Tempo",
}


def render_sidebar(debug_logs: list[dict]):
    """Renderizar o painel de debug."""
    with st.sidebar:
        st.header("🔍 Debug Panel")
        st.caption("Logs de execução do multi-agent system")
        st.divider()

        if not debug_logs:
            st.info("Faça uma pergunta para ver os logs aqui.")
            return

        for i, log in enumerate(reversed(debug_logs)):
            agent_key = log.get("agent", "unknown")
            label = AGENT_LABELS.get(agent_key, agent_key)
            elapsed = log.get("elapsed", 0)

            with st.expander(f"#{len(debug_logs) - i} — {label} ({elapsed:.1f}s)", expanded=(i == 0)):
                st.markdown(f"**Agente:** {label}")
                st.markdown(f"**Raciocínio:** {log.get('reasoning', 'N/A')}")
                st.markdown(f"**Tempo:** {elapsed:.2f}s")
                if log.get("error"):
                    st.error(log["error"])


def extract_last_ai_message(messages: list) -> str:
    """Extrai a última mensagem de IA da saída do grafo."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "Desculpe, não consegui gerar uma resposta."


def run_app():
    """Aplicação principal do Streamlit."""
    st.set_page_config(
        page_title="Multi-Agent Assistant",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 Multi-Agent Assistant")
    st.caption("Assistente conversacional com agentes especializados: Web Search, Knowledge Base, SQL e Weather")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "debug_logs" not in st.session_state:
        st.session_state.debug_logs = []
    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()

    render_sidebar(st.session_state.debug_logs)

    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])
            if role == "assistant" and msg.get("agent"):
                label = AGENT_LABELS.get(msg["agent"], msg["agent"])
                st.caption(f"Respondido por: {label}")

    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                start = time.time()

                graph_input = {
                    "messages": [HumanMessage(content=user_input)],
                }

                try:
                    result = st.session_state.graph.invoke(graph_input)
                    elapsed = time.time() - start

                    response_text = extract_last_ai_message(result.get("messages", []))
                    agent_used = result.get("agent_used", "unknown")
                    reasoning = result.get("reasoning", "")

                    st.markdown(response_text)
                    label = AGENT_LABELS.get(agent_used, agent_used)
                    st.caption(f"Respondido por: {label}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "agent": agent_used,
                    })

                    st.session_state.debug_logs.append({
                        "agent": agent_used,
                        "reasoning": reasoning,
                        "elapsed": elapsed,
                        "query": user_input,
                    })
                    st.rerun()

                except Exception as e:
                    elapsed = time.time() - start
                    error_msg = f"Erro ao processar: {str(e)}"
                    st.error(error_msg)
                    logger.exception("Error in graph execution")

                    st.session_state.debug_logs.append({
                        "agent": "error",
                        "reasoning": error_msg,
                        "elapsed": elapsed,
                        "query": user_input,
                        "error": str(e),
                    })
                    st.rerun()
