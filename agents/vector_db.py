"""Vector DB agent — searches internal knowledge base."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.config import settings
from tools.chroma_search import chroma_search

SYSTEM_PROMPT = (
    "Você é um assistente que consulta a base de conhecimento interna da empresa. "
    "Use a ferramenta de busca para encontrar documentos relevantes e responda "
    "com base nas informações encontradas. Se não encontrar nada relevante, "
    "diga que não há informações disponíveis na base interna."
)


def create_vector_db_agent():
    """Create and return the vector DB ReAct agent."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    return create_react_agent(
        llm,
        tools=[chroma_search],
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )
