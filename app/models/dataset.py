from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from app.db.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(BigInteger, primary_key=True, index=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"))
    database_name = Column(String(100), nullable=False)
    schema_name = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    display_name = Column(String(150))
    description = Column(String)

    contains_company_id = Column(Boolean, default=False, nullable=False)
    contains_country_id = Column(Boolean, default=False, nullable=False)
    contains_region_id = Column(Boolean, default=False, nullable=False)
    contains_branch_id = Column(Boolean, default=False, nullable=False)
    contains_department_id = Column(Boolean, default=False, nullable=False)
    contains_team_id = Column(Boolean, default=False, nullable=False)
    contains_customer_id = Column(Boolean, default=False, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(BigInteger, primary_key=True, index=True)
    dataset_id = Column(BigInteger, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(100), nullable=False)
    data_type = Column(String(50))
    is_nullable = Column(Boolean)
    is_sensitive = Column(Boolean, default=False, nullable=False)
    is_identifier = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())