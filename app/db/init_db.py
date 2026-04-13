from app.db.base import Base
from app.db.session import engine

# Modellerin import edilmesi lazım ki SQLAlchemy hepsini tanısın
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission

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

from app.models.dataset import Dataset, DatasetColumn
from app.models.column_security import ColumnSecurity
from app.models.audit_log import AuditLog
from app.models.dataset_access import RoleDatasetAccess, UserDatasetAccess
from app.models.user_permission import UserPermission


def init_db():
    Base.metadata.create_all(bind=engine)