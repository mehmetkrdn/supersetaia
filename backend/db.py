import os
import re

import psycopg
from dotenv import load_dotenv


load_dotenv()

FORBIDDEN_SQL_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "create",
    "alter",
    "truncate",
    "grant",
    "revoke",
    "copy",
}


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "northwind"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def get_query_timeout_ms() -> int:
    return int(os.getenv("QUERY_TIMEOUT_MS", "10000"))


def get_default_row_limit() -> int:
    return int(os.getenv("DEFAULT_ROW_LIMIT", "100"))


def get_max_row_limit() -> int:
    return int(os.getenv("MAX_ROW_LIMIT", "1000"))


def resolve_row_limit(requested_limit: int | None) -> int:
    default_limit = get_default_row_limit()
    max_limit = get_max_row_limit()

    if requested_limit is None:
        return default_limit

    if requested_limit < 0:
        raise ValueError("Limit negatif olamaz.")

    # 0 => tüm sonuçlar
    if requested_limit == 0:
        return 0

    return min(requested_limit, max_limit)


def normalize_sql(sql: str) -> str:
    return sql.strip().rstrip(";")


def validate_sql_for_execution(sql: str) -> str:
    cleaned_sql = normalize_sql(sql)

    if not cleaned_sql:
        raise ValueError("SQL boş olamaz.")

    lowered = cleaned_sql.lower()

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise ValueError("Sadece SELECT veya WITH sorgularına izin verilir.")

    if ";" in cleaned_sql:
        raise ValueError("Birden fazla SQL statement çalıştırılamaz.")

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, lowered):
            raise ValueError(f"Yasak SQL ifadesi tespit edildi: {keyword}")

    return cleaned_sql


def execute_select_query(sql: str, limit: int | None = None) -> dict:
    safe_sql = validate_sql_for_execution(sql)
    effective_limit = resolve_row_limit(limit)
    timeout_ms = get_query_timeout_ms()
    db_config = get_db_config()

    with psycopg.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {timeout_ms};")
            cur.execute(safe_sql)

            columns = [desc.name for desc in cur.description] if cur.description else []

            if effective_limit == 0:
                fetched_rows = cur.fetchall()
                truncated = False
                visible_rows = fetched_rows
            else:
                fetched_rows = cur.fetchmany(effective_limit + 1)
                truncated = len(fetched_rows) > effective_limit
                visible_rows = fetched_rows[:effective_limit]

    rows = [list(row) for row in visible_rows]

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "total_row_count": None,
        "truncated": truncated,
    }