"""Testes End-to-End para o orquestrador Multi-Agent.

Estes testes validam o fluxo completo do LangGraph:
User -> Planner -> Executor -> Memory

Utilizamos mocks para o LLM (ChatOpenAI) e para os agentes (create_react_agent)
para evitar chamadas de rede e custos de API durante os testes, garantindo
apenas que a lógica de roteamento e transição de estado funcione corretamente.
"""

from unittest.mock import patch, MagicMock

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from graph.orchestrator import build_graph


@pytest.fixture
def graph():
    """Fixture que retorna o grafo compilado."""
    return build_graph()


@patch("graph.nodes.ChatOpenAI")
@patch("agents.weather.create_weather_agent")
def test_e2e_weather_flow(mock_create_weather, mock_chat_openai, graph):
    """Testa o fluxo completo para uma pergunta sobre o clima."""
    # 1. Mock do PlannerNode (LLM decidindo usar 'weather')
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = AIMessage(
        content='{"agent": "weather", "reasoning": "User asked for weather"}'
    )
    mock_chat_openai.return_value = mock_llm_instance

    # 2. Mock do ExecutorNode (Simulando o retorno do Weather Agent)
    mock_weather_agent = MagicMock()
    mock_weather_agent.invoke.return_value = {
        "messages": [AIMessage(content="O tempo em São Paulo é 25°C.")]
    }
    mock_create_weather.return_value = mock_weather_agent

    # 3. Execução do Grafo
    inputs = {"messages": [HumanMessage(content="Qual o clima em São Paulo?")]}
    result = graph.invoke(inputs)

    # 4. Validações
    assert result["selected_agent"] == "weather", "O Planner sub-selecionou o agente errado."
    assert result["agent_used"] == "weather", "O Executor invocou o agente errado."
    
    # Verifica a resposta final presente na memória
    messages = result.get("messages", [])
    assert len(messages) == 1, "Apenas a mensagem final de IA deveria substituir/estar no estado mockado (ou 2 se o agente mantivesse o contexto)."
    assert isinstance(messages[-1], AIMessage)
    assert "25°C" in messages[-1].content


@patch("graph.nodes.ChatOpenAI")
@patch("agents.sql_agent.create_sql_agent")
def test_e2e_sql_flow(mock_create_sql, mock_chat_openai, graph):
    """Testa o fluxo completo para uma pergunta sobre dados do banco (SQL)."""
    # 1. Mock do PlannerNode (LLM decidindo usar 'sql_agent')
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = AIMessage(
        content='{"agent": "sql_agent", "reasoning": "User asked for database counts"}'
    )
    mock_chat_openai.return_value = mock_llm_instance

    # 2. Mock do ExecutorNode (Simulando o retorno do SQL Agent)
    mock_sql_agent = MagicMock()
    mock_sql_agent.invoke.return_value = {
        "messages": [AIMessage(content="Temos um total de 150 clientes.")]
    }
    mock_create_sql.return_value = mock_sql_agent

    # 3. Execução do Grafo
    inputs = {"messages": [HumanMessage(content="Quantos clientes temos?")]}
    result = graph.invoke(inputs)

    # 4. Validações
    assert result["selected_agent"] == "sql_agent"
    assert result["agent_used"] == "sql_agent"
    
    messages = result.get("messages", [])
    assert isinstance(messages[-1], AIMessage)
    assert "150 clientes" in messages[-1].content


@patch("graph.nodes.ChatOpenAI")
@patch("agents.web_search.create_web_search_agent")
def test_e2e_fallback_flow(mock_create_web_search, mock_chat_openai, graph):
    """Testa o fluxo de fallback quando o Planner falha em gerar JSON válido."""
    # 1. Mock do PlannerNode falhando (Retorna string zoada ao invés de JSON)
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = AIMessage(
        content="Eu acho que você deveria usar o agente... ops, quebrou formato."
    )
    mock_chat_openai.return_value = mock_llm_instance

    # 2. Mock do ExecutorNode (O fallback deve chamar o 'web_search')
    mock_web_search_agent = MagicMock()
    mock_web_search_agent.invoke.return_value = {
        "messages": [AIMessage(content="Aqui estão os resultados da busca na web.")]
    }
    mock_create_web_search.return_value = mock_web_search_agent

    # 3. Execução do Grafo
    inputs = {"messages": [HumanMessage(content="O que é teste E2E?")]}
    result = graph.invoke(inputs)

    # 4. Validações
    # O nó do Planner atual tem fallback para 'web_search' se falhar o parsing do JSON.
    assert result["selected_agent"] == "web_search", "Fallback falhou ao lidar com JSON inválido."
    assert result["agent_used"] == "web_search"
    
    messages = result.get("messages", [])
    assert isinstance(messages[-1], AIMessage)
    assert "busca na web" in messages[-1].content
