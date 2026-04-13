from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.db.base import Base


class UserCompany(Base):
    __tablename__ = "user_companies"
    __table_args__= (
        UniqueConstraint("user_id", "company_id", name="uq_user_companies_user_company"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", "role_id", name="uq_user_roles_user_company_role"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class UserCompanyAccess(Base):
    __tablename__ = "user_company_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserCountryAccess(Base):
    __tablename__= "user_country_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    country_id = Column(BigInteger, ForeignKey("countries.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserRegionAccess(Base):
    __tablename__ = "user_region_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    region_id = Column(BigInteger, ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserBranchAccess(Base):
    __tablename__ = "user_branch_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    branch_id = Column(BigInteger, ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserDepartmentAccess(Base):
    __tablename__ = "user_department_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    department_id = Column(BigInteger, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserTeamAccess(Base):
    __tablename__ = "user_team_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    team_id = Column(BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserCustomerAccess(Base):
    __tablename__ = "user_customer_access"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)
    granted_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)