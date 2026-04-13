from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base import Base


class RoleDatasetAccess(Base):
    __tablename__ = "role_dataset_access"
    __table_args__ = (
        UniqueConstraint("role_id", "dataset_id", name="uq_role_dataset_access"),
    )

    id = Column(BigInteger, primary_key=True, index=True)

    role_id = Column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dataset_id = Column(
        BigInteger,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    granted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UserDatasetAccess(Base):
    __tablename__ = "user_dataset_access"
    __table_args__ = (
        UniqueConstraint("user_id", "dataset_id", name="uq_user_dataset_access"),
    )

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dataset_id = Column(
        BigInteger,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    granted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )