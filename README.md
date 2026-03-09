# 🤖 Multi-Agent Conversational Assistant

Mini-assistente conversacional RAG-based com **4 agentes especializados** orquestrados via **LangGraph**, interface **Streamlit** e infraestrutura **Docker**.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (8501)                   │
│              Chat + Debug Sidebar + Streaming            │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    LangGraph Grafo   │
              │                      │
              │  UserNode            │
              │    ↓                 │
              │  PlannerNode (LLM)   │
              │    ↓ routing         │
              │  ExecutorNode        │
              │    ↓                 │
              │  MemoryNode          │
              └──┬───┬───┬───┬──────┘
                 │   │   │   │
    ┌────────────┘   │   │   └────────────┐
    ▼                ▼   ▼                ▼
 🌐 Web Search  📚 Vector DB  🗄️ SQL   🌤️ Weather
  (Tavily)       (ChromaDB)   (Postgres) (OpenWeather)
```

### Fluxo Multi-Agent

1. **UserNode** — recebe a mensagem do usuário
2. **PlannerNode** — LLM analisa a pergunta e decide qual agente acionar (roteamento inteligente)
3. **ExecutorNode** — invoca o agente especializado selecionado
4. **MemoryNode** — armazena o contexto da conversa
5. **Fallback** — se nenhum agente é adequado, aciona busca web

---

## Stack Tecnológica

| Componente | Tecnologia | Justificativa |
|---|---|---|
| LLM | OpenAI gpt-4o-mini | Custo baixo, melhor suporte LangChain |
| UI | Streamlit | Chat nativo com streaming, rápido de desenvolver |
| Orquestração | LangGraph | Requisito do desafio; grafo de estados flexível |
| Base Vetorial | ChromaDB | Setup simples, container Docker pronto |
| Busca Web | Tavily | Integração nativa LangChain, tier gratuito |
| Banco de Dados | PostgreSQL 16 | Robusto, padrão de mercado |
| Clima | OpenWeatherMap | API gratuita e bem documentada |

### Trade-offs

- **Streamlit vs React**: Streamlit é mais rápido de implementar, mas menos flexível para UIs complexas. Para um assistente de chat, é ideal.
- **ChromaDB vs Qdrant**: ChromaDB tem setup mais simples, Qdrant tem melhor performance em produção. Para demo, ChromaDB é suficiente.
- **gpt-4o-mini vs gpt-4o**: Mini tem custo ~20x menor com qualidade adequada para roteamento e RAG.

### Segurança

- **SQL**: Queries validadas via `sqlglot` — apenas `SELECT` permitido, tabelas em whitelist.
- **Secrets**: Variáveis sensíveis em `.env`, nunca commitadas (`.gitignore`).
- **API rate-limit**: OpenWeatherMap limita 60 req/min no tier free; Tavily 1000 req/mês no free.

---

## Quick Start

### Pré-requisitos

- Docker e Docker Compose
- Chaves de API: OpenAI, Tavily, OpenWeatherMap

### Setup

```bash
git clone <repo-url>
cd ChallangeAgentsAi

cp .env.example .env
# Edite o .env com suas API keys

docker compose up --build
```

### Ingestão de documentos (base vetorial)

```bash
docker compose exec app python -m app.vector_db.ingest
```

### Acesso

**UI:** http://localhost:8501

---

## Estrutura do Projeto

```
/app
  /agents        # Agentes especializados (ReAct)
  /graph         # Nós e edges do LangGraph
  /tools         # Tools isoladas (entrada/saída tipada)
  /vector_db     # Script de ingestão
  /ui            # Interface Streamlit
/tests
  /test_tools    # Testes unitários por tool
  /test_e2e      # Testes end-to-end
/data
  /sample_docs   # Documentos para ingestão vetorial
/docs            # Diagrama de arquitetura
docker-compose.yml
Dockerfile
init.sql         # Seed do PostgreSQL
```

---

## Testes

```bash
# Unitários (com mocks, sem precisar de APIs reais)
docker compose exec app pytest tests/test_tools/ -v

# Estrutura dos testes
tests/
  test_tools/
    test_weather_api.py      # Mock HTTP → valida parsing
    test_sql_query.py        # Valida sanitização SQL (whitelist, bloqueio de DROP/DELETE)
    test_tavily_search.py    # Mock Tavily → valida formato de saída
    test_chroma_search.py    # Mock ChromaDB → valida similarity search
```

---

## Exemplos de Uso

| Pergunta | Agente acionado |
|---|---|
| "Qual o tempo em São Paulo?" | 🌤️ Weather |
| "Pesquise sobre inteligência artificial generativa" | 🌐 Web Search |
| "Qual o horário de funcionamento da loja?" | 📚 Vector DB |
| "Quantos pedidos temos com status delivered?" | 🗄️ SQL |
