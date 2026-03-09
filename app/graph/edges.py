"""Lógica de roteamento de arestas do LangGraph."""


def route_to_executor(state: dict) -> str:
    """Sempre roteia do planejador para o executor.

    O planejador já define `selected_agent` no estado,
    então o nó executor irá pegá-lo.
    """
    return "executor"   
