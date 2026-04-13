from sqlalchemy.orm import Session

from app.models.role import Role

# permission modellerini burada varsayıyorum
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.schemas.admin import AdminRoleCreateRequest, AdminRoleUpdateRequest


class AdminRoleService:
    def __init__(self, db: Session):
        self.db = db

    def _serialize_role(self, role: Role) -> dict:
        role_permissions = (
            self.db.query(RolePermission, Permission)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .filter(RolePermission.role_id == role.id)
            .all()
        )

        permission_codes = [permission.code for _, permission in role_permissions]

        return {
            "id": int(role.id),
            "code": role.code,
            "name": role.name,
            "description": role.description,
            "priority": int(role.priority),
            "is_system": bool(role.is_system),
            "is_active": bool(role.is_active),
            "permission_codes": permission_codes,
        }

    def list_roles(self):
        roles = self.db.query(Role).order_by(Role.priority.asc(), Role.id.asc()).all()
        return [self._serialize_role(role) for role in roles]

    def create_role(self, payload: AdminRoleCreateRequest):
        existing = self.db.query(Role).filter(Role.code == payload.code).first()
        if existing:
            raise ValueError("Bu rol kodu zaten mevcut.")

        role = Role(
            code=payload.code,
            name=payload.name,
            description=payload.description,
            priority=payload.priority,
            is_system=payload.is_system,
            is_active=payload.is_active,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self._serialize_role(role)

    def update_role(self, role_id: int, payload: AdminRoleUpdateRequest):
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Rol bulunamadı.")

        role.name = payload.name
        role.description = payload.description
        role.priority = payload.priority
        role.is_system = payload.is_system
        role.is_active = payload.is_active

        self.db.commit()
        self.db.refresh(role)
        return self._serialize_role(role)

    def update_role_permissions(self, role_id: int, permission_codes: list[str]):
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Rol bulunamadı.")

        self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()

        if permission_codes:
            permissions = self.db.query(Permission).filter(Permission.code.in_(permission_codes)).all()
            for permission in permissions:
                self.db.add(RolePermission(role_id=role_id, permission_id=permission.id))

        self.db.commit()
        return {"status": "ok"}