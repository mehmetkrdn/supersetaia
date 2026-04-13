from sqlalchemy import Column, BigInteger, String
from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), unique=True, nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(String, nullable=True)