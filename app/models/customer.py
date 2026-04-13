from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True, index=True)
    customer_code = Column(String(100), unique=True, nullable=True)
    name = Column(String(200), nullable=False)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)