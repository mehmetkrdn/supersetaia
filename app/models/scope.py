from sqlalchemy import Column, BigInteger, String, Integer

from app.db.base import Base


class ScopeType(Base):

    __tablename__ = "scope_types"

    id = Column(BigInteger, primary_key=True)

    code = Column(String(50), unique=True)

    name = Column(String(100))

    level_order = Column(Integer)