"""Weather agent — fetches current weather information."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.config import settings
from tools.weather_api import get_weather

SYSTEM_PROMPT = (
    "Você é um assistente de previsão do tempo. "
    "Quando o usuário perguntar sobre o clima ou tempo de uma cidade, "
    "use a ferramenta para consultar as condições atuais e responda "
    "de forma amigável em linguagem natural, incluindo temperatura, "
    "descrição, umidade e vento."
)


def create_weather_agent():
    """Create and return the weather ReAct agent."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    return create_react_agent(
        llm,
        tools=[get_weather],
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )
