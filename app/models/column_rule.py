from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class RoleColumnRule(Base):
    __tablename__ = "role_column_rules"

    id = Column(BigInteger, primary_key=True, index=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(BigInteger, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(100), nullable=False)
    rule_type = Column(String(20), nullable=False)   # allow, deny, mask
    mask_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserColumnRule(Base):
    __tablename__ = "user_column_rules"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(BigInteger, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(100), nullable=False)
    rule_type = Column(String(20), nullable=False)   # allow, deny, mask
    mask_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())