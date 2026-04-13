from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # örnekler:
    # USER_CREATED, USER_UPDATED, ROLE_ASSIGNED, SCOPE_UPDATED,
    # LOGIN_SUCCESS, LOGIN_FAILED, QUERY_EXECUTED, QUERY_DENIED
    action_type = Column(String(100), nullable=False, index=True)

    target_type = Column(String(100), nullable=True, index=True)
    target_id = Column(String(100), nullable=True, index=True)

    detail_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)