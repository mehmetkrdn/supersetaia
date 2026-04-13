from sqlalchemy.orm import Session
from app.models.dataset import Dataset


class AdminDatasetService:
    def __init__(self, db: Session):
        self.db = db

    def list_datasets(self):
        datasets = self.db.query(Dataset).order_by(Dataset.id.asc()).all()
        result = []

        for ds in datasets:
            result.append({
                "id": int(ds.id),
                "table_name": ds.table_name,
                "display_name": getattr(ds, "display_name", None),
                "contains_company_id": bool(getattr(ds, "contains_company_id", False)),
                "contains_country_id": bool(getattr(ds, "contains_country_id", False)),
                "contains_region_id": bool(getattr(ds, "contains_region_id", False)),
                "contains_branch_id": bool(getattr(ds, "contains_branch_id", False)),
                "contains_department_id": bool(getattr(ds, "contains_department_id", False)),
                "contains_team_id": bool(getattr(ds, "contains_team_id", False)),
                "contains_customer_id": bool(getattr(ds, "contains_customer_id", False)),
            })

        return result