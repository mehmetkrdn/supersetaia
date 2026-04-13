from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Role(Base):

    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True)

    code = Column(String(50), unique=True, nullable=False)

    name = Column(String(100), unique=True, nullable=False)

    description = Column(String)

    priority = Column(Integer, default=100)

    is_system = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())