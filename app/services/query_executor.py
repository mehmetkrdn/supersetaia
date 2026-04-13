import re
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings


class QueryExecutor:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.NORTHWIND_DB_HOST,
            port=settings.NORTHWIND_DB_PORT,
            database=settings.NORTHWIND_DB_NAME,
            user=settings.NORTHWIND_DB_USER,
            password=settings.NORTHWIND_DB_PASSWORD,
            sslmode="require",
        )

    def _apply_limit_if_missing(self, sql: str, limit: int = 100) -> str:
        sql_clean = sql.strip().rstrip(";")

        if not limit or limit <= 0:
            return sql_clean

        if re.search(r"\bLIMIT\s+\d+\b", sql_clean, re.IGNORECASE):
            return sql_clean

        return f"{sql_clean} LIMIT {limit}"

    def execute_query(self, sql: str, limit: int = 100) -> list[dict]:
        sql_clean = self._apply_limit_if_missing(sql, limit=limit)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql_clean)
            rows = cursor.fetchall()

        return [dict(row) for row in rows]