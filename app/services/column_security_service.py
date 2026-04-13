import re
from sqlalchemy.orm import Session

from app.security.user_context import UserContext
from app.repositories.column_security_repository import ColumnSecurityRepository
from app.security.column_policy_resolver import ColumnPolicyResolver
from app.security.column_sql_rewriter import ColumnSQLRewriter
from app.security.table_extractor import TableExtractor  # <-- Yeni ekledik


class ColumnSecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ColumnSecurityRepository(db)
        self.policy_resolver = ColumnPolicyResolver(self.repo)
        self.sql_rewriter = ColumnSQLRewriter()
        self.table_extractor = TableExtractor()  # <-- Yeni ekledik

    def apply_column_security(self, sql: str, context: UserContext) -> dict:
        # 1. Admin kontrolü
        if context.is_superadmin or "admin" in context.role_codes:
            return {
                "original_sql": sql,
                "rewritten_sql": sql,
                "restricted_columns": [],
            }

        # 2. SQL içindeki TÜM tabloları bul (Sadece ilkini değil!)
        tables = self.table_extractor.extract_tables(sql)
        if not tables:
            return {"original_sql": sql, "rewritten_sql": sql, "restricted_columns": []}

        main_table = tables[0]
        
        # 3. Tüm tablolardaki izin verilen ve kısıtlanan kolonları birleştir
        combined_allowed = set()
        combined_all = set()

        for table_name in tables:
            policy = self.policy_resolver.resolve_allowed_columns(context, table_name)
            combined_allowed.update(policy.get("allowed_columns", []))
            combined_all.update(policy.get("all_columns", []))

        # 4. Birleştirilmiş allow listesini rewriter'a ver
        rewritten_sql = self.sql_rewriter.rewrite_select(
            sql=sql,
            allowed_columns=list(combined_allowed),
        )

        restricted = sorted(combined_all - combined_allowed)

        return {
            "original_sql": sql,
            "rewritten_sql": rewritten_sql,
            "restricted_columns": restricted,
            "allowed_columns": list(combined_allowed),
            "table_name": main_table,
        }