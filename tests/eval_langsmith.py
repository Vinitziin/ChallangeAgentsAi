"""
Avaliação Automatizada (Prompt Eval) utilizando LangSmith.

Este script define um golden dataset e avalia a capacidade do PlannerNode
de rotear diferentes tipos de perguntas para o agente correto.
Ele envia os resultados de avaliação para a sua conta do LangSmith.

Como rodar:
- Preencha LANGCHAIN_API_KEY no seu .env
- Execute dentro do container: docker compose exec app python tests/eval_langsmith.py
"""

import os
import uuid
from typing import Any

from langsmith import Client
from langsmith.evaluation import evaluate

# Carregar o node que queremos testar (A infra do LangGraph de roteamento)
from graph.nodes import planner_node


def setup_dataset(client: Client, dataset_name: str):
    """Cria e alimenta o dataset de golden examples no LangSmith se não existir."""
    if client.has_dataset(dataset_name=dataset_name):
        return client.read_dataset(dataset_name=dataset_name)

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Dataset validando o roteamento do PlannerNode para múltiplos agentes.",
    )

    examples = [
        ("Qual o clima em São Paulo hoje?", "weather"),
        ("Quantos pedidos estão pendentes?", "sql_agent"),
        ("Mostre informações dos últimos 5 clientes cadastrados.", "sql_agent"),
        ("Onde fica o RH e a impressora?", "vector_db"),
        ("Como solicito reembolso no ERP interno?", "vector_db"),
        ("Notícias sobre a eleição na Europa.", "web_search"),
        ("Quais times chegaram na final do campeonato ano passado?", "web_search"),
    ]

    for user_input, expected_agent in examples:
        client.create_example(
            inputs={"question": user_input},
            outputs={"expected_agent": expected_agent},
            dataset_id=dataset.id,
        )

    return dataset


def predict_route(inputs: dict) -> dict:
    """Wrapper para rodar o planner_node na assinatura esperada pelo LangSmith evaluator."""
    # Monta o "extrato de state" simulando a última mensagem humana
    from langchain_core.messages import HumanMessage
    
    question = inputs["question"]
    state: dict[str, Any] = {
        "messages": [HumanMessage(content=question)]
    }
    
    # Chama a lógica pura do planner_node para ver qual JSON o ChatOpenAI nos retorna
    output_state = planner_node(state)
    
    return {"predicted_agent": output_state.get("selected_agent", "unknown_error")}


def exact_match_evaluator(run, example) -> dict:
    """Avaliador customizado validando equivalência de Agent Routes."""
    predicted = run.outputs.get("predicted_agent")
    expected = example.outputs.get("expected_agent")
    
    score = 1 if predicted == expected else 0
    
    return {
        "key": "correct_routing",
        "score": score,
        "comment": f"Expected: {expected} | Got: {predicted}"
    }


def main():
    if not os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGCHAIN_API_KEY") == "your_langchain_api_key_here":
        print("❌ ERRO: Necessário configurar a LANGCHAIN_API_KEY no arquivo .env para o LangSmith Eval funcionar.")
        print("Obtenha em: https://smith.langchain.com/")
        return

    client = Client()
    # Nome unico para o dataset (pode ser hardcoded, mas com sufixo ajuda caso haja colisão de tenants)
    dataset_name = "MultiAgentRoutingDataset"

    print(f"✅ Preparando Dataset: {dataset_name}")
    setup_dataset(client, dataset_name)
    
    project_name = f"PlannerEval_{uuid.uuid4().hex[:6]}"
    
    print(f"🚀 Iniciando Avaliação via LangSmith no Projeto: {project_name}")
    print("Aguarde, a LLM está julgando e o LangSmith coletando os traços...")
    
    evaluate(
        predict_route,
        data=dataset_name,
        evaluators=[exact_match_evaluator],
        experiment_prefix="PlannerRoutes",
        metadata={"model": os.getenv("LLM_MODEL", "gpt-4o-mini")},
    )
    
    print(f"\n🎉 Avaliação concluída com sucesso!")
    print(f"Veja o painel com os scores exatos e visualizações gráficas no portal:")
    print("https://smith.langchain.com/")


if __name__ == "__main__":
    main()
