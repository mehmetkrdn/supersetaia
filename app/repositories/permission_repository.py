from sqlalchemy.orm import Session
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.access import UserRole


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_permission_codes_for_user(self, user_id: int, company_id: int | None) -> list[str]:
        if company_id is None:
            return []

        rows = (
            self.db.query(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user_id,
                UserRole.company_id == company_id,
                UserRole.is_active == True,
                Role.is_active == True
                # RolePermission.allow == True satırını sildik!
            )
            .distinct()
            .all()
        )

        return [row[0] for row in rows]