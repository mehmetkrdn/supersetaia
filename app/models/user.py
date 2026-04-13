from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)

    email = Column(String(255), unique=True)

    full_name = Column(String(200))

    password_hash = Column(String, nullable=False)

    is_superadmin = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), server_default=func.now())