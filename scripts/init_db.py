"""Initializes the PostgreSQL database with schema and seed data.

Reads init.sql and executes it against the configured database.
Uses ON CONFLICT / IF NOT EXISTS to be safely idempotent.
"""

import os
import sys
from pathlib import Path

import psycopg2


def _build_connection_string() -> str:
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "assistant_db")
    return f"host={host} port={port} user={user} password={password} dbname={db}"


def init_database() -> None:
    sql_path = Path(__file__).resolve().parent.parent / "init.sql"
    if not sql_path.exists():
        print("[init_db] init.sql not found, skipping database initialization.")
        return

    conn_str = _build_connection_string()
    print(f"[init_db] Connecting to PostgreSQL at {os.getenv('POSTGRES_HOST', 'postgres')}...")

    try:
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cur = conn.cursor()

        # Check if tables already exist to avoid duplicate inserts
        cur.execute(
            "SELECT EXISTS ("
            "  SELECT FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = 'customers'"
            ")"
        )
        tables_exist = cur.fetchone()[0]

        if tables_exist:
            print("[init_db] Tables already exist — skipping initialization.")
        else:
            sql = sql_path.read_text(encoding="utf-8")
            cur.execute(sql)
            print("[init_db] Database initialized successfully with schema and seed data.")

        cur.close()
        conn.close()
    except Exception as exc:
        print(f"[init_db] WARNING: Could not initialize database: {exc}", file=sys.stderr)


if __name__ == "__main__":
    init_database()
