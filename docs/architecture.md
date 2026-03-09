# Arquitetura do Sistema (Mermaid)

Este documento contém o diagrama visual da arquitetura do `Multi-Agent Conversational Assistant`, modelado com a linguagem Mermaid para renderização nativa no GitHub.

```mermaid
graph TD
    %% Nós principais e atores
    User((💬 Usuário))
    
    subgraph Frontend
        UI[💻 Streamlit App]
    end
    
    subgraph Orquestrador LangGraph
        UN[📥 User Node]
        PN[🧠 Planner Node]
        EN[⚙️ Executor Node]
        MN[💾 Memory Node]
    end
    
    subgraph Agentes Especialistas ReAct
        WSA[🔍 Web Search]
        VDA[📚 Vector DB]
        SQA[🗄️ SQL Agent]
        WEA[🌤️ Weather]
    end
    
    subgraph Infraestrutura e Bancos
        PG[(🐘 PostgreSQL)]
        CB[(🔢 ChromaDB)]
    end
    
    subgraph APIs Externas
        TAV[🌐 Tavily API]
        OWM[☁️ OpenWeatherMap]
        GPT[🤖 OpenAI GPT-4o]
    end

    %% Roteamento do Usuário
    User -->|Pergunta| UI
    UI -->|Envia Chat| UN
    UN -->|Histórico| PN
    
    %% O Cérebro Roteador
    PN -.->|Chama LLM para decidir rota| GPT
    PN -->|JSON c/ Destino| EN
    
    %% A Execução
    EN ==>|Rota Dinâmica| WSA
    EN ==>|Rota Dinâmica| VDA
    EN ==>|Rota Dinâmica| SQA
    EN ==>|Rota Dinâmica| WEA
    
    %% Retorno pro Usuário
    WSA & VDA & SQA & WEA -->|Resultado| MN
    MN -->|Histórico Atualizado| UI
    
    %% Integrações dos Agentes com o Mundo Real
    WSA -.->|Scraping / Search| TAV
    VDA -.->|Embeddings| GPT
    VDA -.->|Similarity Search| CB
    SQA -.->|Read-Only SQL| PG
    WEA -.->|Temperature / City| OWM
    
    %% Conexão Genérica da Mente dos Agentes
    WSA & SQA & WEA -.->|ReAct Reasoning| GPT

    %% Estilização do Grafo
    classDef llm fill:#e6f3ff,stroke:#0066cc,stroke-width:2px;
    classDef agent fill:#f9f2ec,stroke:#d9822b,stroke-width:2px;
    classDef db fill:#e6ffe6,stroke:#009933,stroke-width:2px;
    classDef api fill:#ffe6e6,stroke:#cc0000,stroke-width:2px;
    
    class GPT llm;
    class WSA,VDA,SQA,WEA agent;
    class PG,CB db;
    class TAV,OWM api;
```
