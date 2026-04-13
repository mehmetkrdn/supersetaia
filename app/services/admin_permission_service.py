from sqlalchemy.orm import Session
from app.models.permission import Permission


class AdminPermissionService:
    def __init__(self, db: Session):
        self.db = db

    def list_permissions(self):
        permissions = self.db.query(Permission).order_by(Permission.code.asc()).all()

        result = []
        for permission in permissions:
            result.append({
                "id": int(permission.id),
                "code": permission.code,
                "name": permission.name,
                "description": permission.description,
                "is_active": True,
            })

        return result