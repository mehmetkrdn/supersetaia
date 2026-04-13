from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission
from app.models.access import (
    UserCompany,
    UserRole,
    UserCompanyAccess,
    UserCountryAccess,
    UserRegionAccess,
    UserBranchAccess,
    UserDepartmentAccess,
    UserTeamAccess,
    UserCustomerAccess,
)


class ContextRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_default_company_id(self, user_id: int) -> int | None:
        row = (
            self.db.query(UserCompany)
            .filter(
                UserCompany.user_id == user_id,
                UserCompany.is_default == True,
                UserCompany.is_active == True,
            )
            .first()
        )
        return int(row.company_id) if row else None

    def get_role_codes(self, user_id: int, company_id: int | None) -> list[str]:
        query = (
            self.db.query(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                Role.is_active == True,
            )
        )

        if company_id is not None:
            query = query.filter(UserRole.company_id == company_id)

        rows = query.distinct().all()
        return [row[0] for row in rows]

    def get_permission_codes(self, user_id: int, active_company_id: int | None) -> list[str]:
        # 1) Rol bazlı permissionlar
        role_query = (
            self.db.query(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                Role.is_active == True,
            )
        )

        if active_company_id is not None:
            role_query = role_query.filter(UserRole.company_id == active_company_id)

        role_rows = role_query.distinct().all()
        final_permissions = {row[0] for row in role_rows}

        # 2) Kullanıcı bazlı override
        user_rows = (
            self.db.query(UserPermission, Permission)
            .join(Permission, Permission.id == UserPermission.permission_id)
            .filter(UserPermission.user_id == user_id)
            .all()
        )

        for user_permission, permission in user_rows:
            if user_permission.allow:
                final_permissions.add(permission.code)
            else:
                final_permissions.discard(permission.code)

        return sorted(final_permissions)

    def get_company_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserCompanyAccess.company_id)
            .filter(UserCompanyAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_country_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserCountryAccess.country_id)
            .filter(UserCountryAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_region_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserRegionAccess.region_id)
            .filter(UserRegionAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_branch_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserBranchAccess.branch_id)
            .filter(UserBranchAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_department_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserDepartmentAccess.department_id)
            .filter(UserDepartmentAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_team_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserTeamAccess.team_id)
            .filter(UserTeamAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]

    def get_customer_ids(self, user_id: int) -> list[int]:
        rows = (
            self.db.query(UserCustomerAccess.customer_id)
            .filter(UserCustomerAccess.user_id == user_id)
            .all()
        )
        return [int(row[0]) for row in rows]