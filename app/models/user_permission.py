from sqlalchemy import Column, BigInteger, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"
    __table_args__= (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permissions_user_permission"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    allow = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)