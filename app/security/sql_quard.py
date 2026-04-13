from app.security.sql_validator import SQLValidator
from app.security.dataset_guard import DatasetGuard


class SQLGuard:
    def __init__(self):
        self.validator = SQLValidator()
        self.dataset_guard = DatasetGuard()

    def check_sql(self, sql: str) -> dict:
        # 1) basic SQL validation
        self.validator.validate(sql)

        # 2) dataset / table whitelist check
        tables = self.dataset_guard.check_tables(sql)

        return {
            "sql": sql,
            "tables": tables,
        }