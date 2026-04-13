from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.dataset import Dataset
from app.models.dataset_access import RoleDatasetAccess, UserDatasetAccess


class AdminDatasetAccessService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self):
        result = []

        role_rows = (
            self.db.query(RoleDatasetAccess, Role, Dataset)
            .join(Role, Role.id == RoleDatasetAccess.role_id)
            .join(Dataset, Dataset.id == RoleDatasetAccess.dataset_id)
            .all()
        )

        for access, role, dataset in role_rows:
            result.append({
                "id": int(access.id),
                "dataset_id": int(dataset.id),
                "table_name": dataset.table_name,
                "role_code": role.code,
                "user_id": None,
            })

        user_rows = (
            self.db.query(UserDatasetAccess, Dataset)
            .join(Dataset, Dataset.id == UserDatasetAccess.dataset_id)
            .all()
        )

        for access, dataset in user_rows:
            result.append({
                "id": int(access.id),
                "dataset_id": int(dataset.id),
                "table_name": dataset.table_name,
                "role_code": None,
                "user_id": int(access.user_id),
            })

        return result

    def replace_access(self, dataset_id: int, role_codes: list[str], user_ids: list[int]):
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError("Dataset bulunamadı.")

        self.db.query(RoleDatasetAccess).filter(RoleDatasetAccess.dataset_id == dataset_id).delete()
        self.db.query(UserDatasetAccess).filter(UserDatasetAccess.dataset_id == dataset_id).delete()

        if role_codes:
            roles = self.db.query(Role).filter(Role.code.in_(role_codes)).all()
            for role in roles:
                self.db.add(RoleDatasetAccess(role_id=role.id, dataset_id=dataset_id))

        for user_id in user_ids:
            self.db.add(UserDatasetAccess(user_id=user_id, dataset_id=dataset_id))

        self.db.commit()
        return {"status": "ok"}
