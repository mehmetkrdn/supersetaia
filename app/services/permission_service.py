from sqlalchemy.orm import Session
from app.repositories.permission_repository import PermissionRepository
from app.security.permission_checker import PermissionChecker
from app.security.user_context import UserContext

class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PermissionRepository(db)
        self.checker = PermissionChecker()

    def load_permissions_into_context(self, context: UserContext) -> UserContext:
        # Veritabanından izin kodlarını getir
        permissions = self.repo.get_permission_codes_for_user(
            user_id=context.user_id,
            company_id=context.active_company_id,
        )

        print("LOADED PERMISSIONS FROM DB:", permissions, flush=True)

        # Context nesnesine izinleri ata
        context.permission_codes = permissions
        return context

    def require_sql_run(self, context: UserContext) -> None:
        self.checker.require(context, "sql.run")