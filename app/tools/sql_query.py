"""SQL query tool using SQLAlchemy with safety checks via sqlglot."""

from typing import Any

import sqlglot
from langchain_core.tools import tool
from sqlalchemy import create_engine, text

from app.config import settings

ALLOWED_TABLES = {"customers", "products", "orders"}
BLOCKED_KEYWORDS = {"DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE", "CREATE"}


def _validate_sql(query: str) -> str | None:
    """Validate SQL query for safety. Returns error message or None if safe."""
    try:
        parsed = sqlglot.parse(query)
    except sqlglot.errors.ParseError:
        return "Query SQL inválida. Verifique a sintaxe."

    for statement in parsed:
        stmt_type = statement.key.upper()
        if stmt_type in BLOCKED_KEYWORDS:
            return f"Operação '{stmt_type}' não é permitida. Apenas SELECT é aceito."

        referenced_tables = {
            table.name.upper()
            for table in statement.find_all(sqlglot.exp.Table)
        }
        invalid = referenced_tables - {t.upper() for t in ALLOWED_TABLES}
        if invalid:
            return f"Tabelas não permitidas: {invalid}. Tabelas disponíveis: {ALLOWED_TABLES}"

    return None


@tool
def sql_query(query: str) -> dict[str, Any]:
    """Execute a read-only SQL query on the PostgreSQL database.

    The database has three tables: customers, products, orders.
    Only SELECT queries are allowed.

    Args:
        query: A SQL SELECT query to execute.

    Returns:
        Query results with columns and rows, or an error message.
    """
    validation_error = _validate_sql(query)
    if validation_error:
        return {"error": validation_error}

    engine = create_engine(settings.postgres_uri)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {
                "query": query,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
    except Exception as e:
        return {"error": f"Erro ao executar query: {str(e)}"}
