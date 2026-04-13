from sqlalchemy.orm import Session
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.access import (
    UserRole,
    UserCompanyAccess,
    UserCountryAccess,
    UserRegionAccess,
    UserBranchAccess,
    UserDepartmentAccess,
    UserTeamAccess,
    UserCustomerAccess,
)
from app.schemas.admin import (
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
    AdminUserScopeUpdateRequest,
)
from app.services.admin_audit_service import AdminAuditService


class AdminUserService:
    def __init__(self, db: Session):
        self.db = db

    def _serialize_user(self, user: User) -> dict:
        user_roles = (
            self.db.query(UserRole, Role)
            .join(Role, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user.id, UserRole.is_active == True)
            .all()
        )

        role_assignments = [
            {
                "role_code": role.code,
                "company_id": int(user_role.company_id),
            }
            for user_role, role in user_roles
        ]

        company_ids = [
            int(x.company_id)
            for x in self.db.query(UserCompanyAccess)
            .filter(UserCompanyAccess.user_id == user.id)
            .all()
        ]

        country_ids = [
            int(x.country_id)
            for x in self.db.query(UserCountryAccess)
            .filter(UserCountryAccess.user_id == user.id)
            .all()
        ]

        region_ids = [
            int(x.region_id)
            for x in self.db.query(UserRegionAccess)
            .filter(UserRegionAccess.user_id == user.id)
            .all()
        ]

        branch_ids = [
            int(x.branch_id)
            for x in self.db.query(UserBranchAccess)
            .filter(UserBranchAccess.user_id == user.id)
            .all()
        ]

        department_ids = [
            int(x.department_id)
            for x in self.db.query(UserDepartmentAccess)
            .filter(UserDepartmentAccess.user_id == user.id)
            .all()
        ]

        team_ids = [
            int(x.team_id)
            for x in self.db.query(UserTeamAccess)
            .filter(UserTeamAccess.user_id == user.id)
            .all()
        ]

        customer_ids = [
            str(x.customer_id)
            for x in self.db.query(UserCustomerAccess)
            .filter(UserCustomerAccess.user_id == user.id)
            .all()
        ]

        return {
            "id": int(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": bool(user.is_active),
            "is_superadmin": bool(user.is_superadmin),
            "role_assignments": role_assignments,
            "company_ids": company_ids,
            "country_ids": country_ids,
            "region_ids": region_ids,
            "branch_ids": branch_ids,
            "department_ids": department_ids,
            "team_ids": team_ids,
            "customer_ids": customer_ids,
        }

    def list_users(self):
        users = self.db.query(User).order_by(User.id.asc()).all()
        return [self._serialize_user(user) for user in users]

    def get_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")
        return self._serialize_user(user)

    def create_user(self, payload: AdminUserCreateRequest):
        existing = self.db.query(User).filter(User.username == payload.username).first()
        if existing:
            raise ValueError("Bu kullanıcı adı zaten mevcut.")

        if payload.email:
            existing_email = self.db.query(User).filter(User.email == payload.email).first()
            if existing_email:
                raise ValueError("Bu e-posta zaten kullanımda.")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=get_password_hash(payload.password),
            is_active=payload.is_active,
            is_superadmin=payload.is_superadmin,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return self._serialize_user(user)

    def update_user(self, user_id: int, payload: AdminUserUpdateRequest):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        if payload.email and payload.email != user.email:
            existing_email = self.db.query(User).filter(User.email == payload.email).first()
            if existing_email:
                raise ValueError("Bu e-posta zaten kullanımda.")

        user.email = payload.email
        user.full_name = payload.full_name
        user.is_active = payload.is_active
        user.is_superadmin = payload.is_superadmin

        self.db.commit()
        self.db.refresh(user)

        return self._serialize_user(user)

    def update_user_status(self, user_id: int, is_active: bool):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        user.is_active = is_active
        self.db.commit()

        return {"status": "ok"}

    def reset_user_password(self, user_id: int, password: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        user.password_hash = get_password_hash(password)
        self.db.commit()

        return {"status": "ok"}

    def update_user_roles(self, user_id: int, role_items: list):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()

        for item in role_items:
            role = self.db.query(Role).filter(Role.code == item.role_code).first()
            if not role:
                raise ValueError(f"Rol bulunamadı: {item.role_code}")

            self.db.add(
                UserRole(
                    user_id=user_id,
                    company_id=item.company_id,
                    role_id=role.id,
                    assigned_by=None,
                    is_active=True,
                )
            )

        self.db.commit()

        assigned_roles = [
            {
                "role_code": item.role_code,
                "company_id": item.company_id,
            }
            for item in role_items
        ]

        AdminAuditService(self.db).log_action(
            action_type="USER_ROLES_UPDATED",
            user_id=None,
            target_type="user",
            target_id=str(user_id),
            detail_json={"roles": assigned_roles},
        )

        return {"status": "ok"}

    def update_user_scopes(self, user_id: int, payload: AdminUserScopeUpdateRequest):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        self.db.query(UserCompanyAccess).filter(UserCompanyAccess.user_id == user_id).delete()
        self.db.query(UserCountryAccess).filter(UserCountryAccess.user_id == user_id).delete()
        self.db.query(UserRegionAccess).filter(UserRegionAccess.user_id == user_id).delete()
        self.db.query(UserBranchAccess).filter(UserBranchAccess.user_id == user_id).delete()
        self.db.query(UserDepartmentAccess).filter(UserDepartmentAccess.user_id == user_id).delete()
        self.db.query(UserTeamAccess).filter(UserTeamAccess.user_id == user_id).delete()
        self.db.query(UserCustomerAccess).filter(UserCustomerAccess.user_id == user_id).delete()

        for company_id in payload.company_ids:
            self.db.add(
                UserCompanyAccess(
                    user_id=user_id,
                    company_id=company_id,
                    granted_by=None,
                )
            )

        for country_id in payload.country_ids:
            self.db.add(
                UserCountryAccess(
                    user_id=user_id,
                    country_id=country_id,
                    granted_by=None,
                )
            )

        for region_id in payload.region_ids:
            self.db.add(
                UserRegionAccess(
                    user_id=user_id,
                    region_id=region_id,
                    granted_by=None,
                )
            )

        for branch_id in payload.branch_ids:
            self.db.add(
                UserBranchAccess(
                    user_id=user_id,
                    branch_id=branch_id,
                    granted_by=None,
                )
            )

        for department_id in payload.department_ids:
            self.db.add(
                UserDepartmentAccess(
                    user_id=user_id,
                    department_id=department_id,
                    granted_by=None,
                )
            )

        for team_id in payload.team_ids:
            self.db.add(
                UserTeamAccess(
                    user_id=user_id,
                    team_id=team_id,
                    granted_by=None,
                )
            )

        for customer_id in payload.customer_ids:
            self.db.add(
                UserCustomerAccess(
                    user_id=user_id,
                    customer_id=customer_id,
                    granted_by=None,
                )
            )

        self.db.commit()

        return {"status": "ok"}

    def get_user_permissions(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        rows = (
            self.db.query(UserPermission, Permission)
            .join(Permission, Permission.id == UserPermission.permission_id)
            .filter(UserPermission.user_id == user_id)
            .order_by(Permission.code.asc())
            .all()
        )

        return [
            {
                "permission_code": permission.code,
                "allow": bool(user_permission.allow),
            }
            for user_permission, permission in rows
        ]

    def update_user_permissions(self, user_id: int, permission_items: list):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")

        self.db.query(UserPermission).filter(UserPermission.user_id == user_id).delete()

        for item in permission_items:
            permission = self.db.query(Permission).filter(Permission.code == item.permission_code).first()
            if not permission:
                raise ValueError(f"Permission bulunamadı: {item.permission_code}")

            self.db.add(
                UserPermission(
                    user_id=user_id,
                    permission_id=permission.id,
                    allow=bool(item.allow),
                )
            )

        self.db.commit()
        return {"status": "ok"}