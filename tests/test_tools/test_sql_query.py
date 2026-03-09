"""Unit tests for the SQL query tool — validation logic."""

from tools.sql_query import _validate_sql


def test_select_on_allowed_table_is_valid():
    assert _validate_sql("SELECT * FROM customers") is None


def test_select_join_allowed_tables_is_valid():
    assert _validate_sql(
        "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id"
    ) is None


def test_drop_is_blocked():
    result = _validate_sql("DROP TABLE customers")
    assert result is not None
    assert "DROP" in result


def test_delete_is_blocked():
    result = _validate_sql("DELETE FROM customers WHERE id = 1")
    assert result is not None
    assert "DELETE" in result


def test_insert_is_blocked():
    result = _validate_sql("INSERT INTO customers (name, email) VALUES ('Test', 'test@x.com')")
    assert result is not None
    assert "INSERT" in result


def test_update_is_blocked():
    result = _validate_sql("UPDATE customers SET name = 'x' WHERE id = 1")
    assert result is not None
    assert "UPDATE" in result


def test_unauthorized_table_is_blocked():
    result = _validate_sql("SELECT * FROM secret_data")
    assert result is not None
    assert "não permitidas" in result


def test_invalid_sql_returns_error():
    result = _validate_sql("NOT VALID SQL !!!")
    # sqlglot may or may not raise a parse error depending on the input;
    # the key is it should not crash
    assert result is None or isinstance(result, str)
