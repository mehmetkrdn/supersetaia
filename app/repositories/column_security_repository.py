from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetColumn
from app.models.column_rule import RoleColumnRule, UserColumnRule
from app.models.role import Role
from app.models.access import UserRole


class ColumnSecurityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dataset_by_table_name(self, table_name: str) -> Dataset | None:
        return (
            self.db.query(Dataset)
            .filter(
                Dataset.table_name == table_name,
                Dataset.is_active == True,
            )
            .first()
        )

    def get_dataset_columns(self, dataset_id: int) -> list[DatasetColumn]:
        return (
            self.db.query(DatasetColumn)
            .filter(
                DatasetColumn.dataset_id == dataset_id,
                DatasetColumn.is_active == True,
            )
            .all()
        )

    def get_user_rules(self, user_id: int, dataset_id: int) -> list[UserColumnRule]:
        return (
            self.db.query(UserColumnRule)
            .filter(
                UserColumnRule.user_id == user_id,
                UserColumnRule.dataset_id == dataset_id,
            )
            .all()
        )

    def get_role_rules(self, user_id: int, company_id: int | None, dataset_id: int) -> list[RoleColumnRule]:
        if company_id is None:
            return []

        return (
            self.db.query(RoleColumnRule)
            .join(Role, Role.id == RoleColumnRule.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user_id,
                UserRole.company_id == company_id,
                UserRole.is_active == True,
                RoleColumnRule.dataset_id == dataset_id,
            )
            .all()
        )