from sqlalchemy.orm import Session
from app.security.sql_quard import SQLGuard
from app.services.row_security_service import RowSecurityService
from app.services.column_security_service import ColumnSecurityService
from app.services.query_executor import QueryExecutor
from app.services.permission_service import PermissionService
from app.security.user_context import UserContext


class SecureQueryPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.sql_guard = SQLGuard()
        self.permission_service = PermissionService(db)
        self.row_security_service = RowSecurityService(db)
        self.column_security_service = ColumnSecurityService(db)
        self.query_executor = QueryExecutor()

    def run(self, sql: str, context: UserContext, limit: int = 100) -> dict:
        # 0) permission yükle ve kontrol et
        context = self.permission_service.load_permissions_into_context(context)
        self.permission_service.require_sql_run(context)

        # 1) validator + dataset guard
        guard_result = self.sql_guard.check_sql(sql)
        validated_sql = guard_result["sql"]

        # 2) RLS
        rls_sql = self.row_security_service.apply_rls(validated_sql, context)

        # 3) column security
        column_result = self.column_security_service.apply_column_security(rls_sql, context)
        final_sql = column_result["rewritten_sql"]

        # 4) query execute
        rows = self.query_executor.execute_query(final_sql, limit=limit)

        return {
            "original_sql": sql,
            "validated_sql": validated_sql,
            "rls_sql": rls_sql,
            "final_sql": final_sql,
            "tables": guard_result["tables"],
            "restricted_columns": column_result.get("restricted_columns", []),
            "effective_permissions": context.permission_codes,
            "row_count": len(rows),
            "rows": rows,
        }