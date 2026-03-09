"""Agente de pesquisa na web — pesquisa na internet por informações atuais."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.tools.tavily_search import tavily_search

SYSTEM_PROMPT = (
    "Você é um assistente especializado em pesquisa na web. "
    "Quando o usuário fizer uma pergunta, busque informações atualizadas na internet "
    "e retorne uma resposta consolidada com os links das fontes. "
    "Sempre cite as URLs de onde tirou a informação."
)


def create_web_search_agent():
    """Cria e retorna o agente ReAct de pesquisa na web."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    return create_react_agent(
        llm,
        tools=[tavily_search],
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )
