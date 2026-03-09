"""SQL agent — queries the PostgreSQL database."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.config import settings
from tools.sql_query import sql_query

SYSTEM_PROMPT = (
    "Você é um assistente especializado em consultas SQL no banco de dados PostgreSQL. "
    "O banco possui três tabelas: customers (clientes), products (produtos) e orders (pedidos). "
    "Converta a pergunta do usuário em uma query SQL SELECT e use a ferramenta para executá-la. "
    "Retorne os resultados de forma clara e bem formatada em linguagem natural. "
    "NUNCA execute operações destrutivas (DELETE, DROP, UPDATE, INSERT)."
)


def create_sql_agent():
    """Create and return the SQL ReAct agent."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    return create_react_agent(
        llm,
        tools=[sql_query],
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )
